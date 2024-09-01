import os
import json
import docker
import subprocess
from config import get_config_dir, get_template_dir,get_data_dir
import re
import uuid
import sqlite3
import logging
logger = logging.getLogger(__name__)

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def get_container_id(self,data,target_value):
        for key, value in data.items():
            if isinstance(value, dict) and value.get('service_id') == target_value:
                return key
        return None

    def process_config_and_generate_compose(self, service_id, config_data):
        """处理配置并生成 Docker Compose 文件"""
        # 使用sqlite数据库
        db_path = os.path.join(get_data_dir(), 'bots.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # 创建表（如果不存在）
            cursor.execute('''CREATE TABLE IF NOT EXISTS bots
                              (container_id TEXT PRIMARY KEY,
                               name TEXT,
                               config TEXT,
                               service_id TEXT)''')

            # 查找对应的container_id
            cursor.execute("SELECT container_id FROM bots WHERE service_id = ?", (service_id,))
            result = cursor.fetchone()
            container_id = result[0] if result else None

            if container_id:
                # 更新机器人名称
                cursor.execute("UPDATE bots SET name = ? WHERE container_id = ?", 
                               (config_data["BOT_NAME"], container_id))
                conn.commit()

        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
        except KeyError as e:
            print(f"键错误: {e} - 请检查数据中是否包含所有必需的键。")
        except Exception as e:
            print(f"意外错误: {e}")
        finally:
            conn.close()

        config_path = self.generate_config(service_id, config_data)
        # 生成Docker Compose文件
        compose_file_path = self.generate_docker_compose_file(service_id, config_path)
        
        return compose_file_path, config_path
        
    def generate_config(self, service_id, config_data):
        template_path = os.path.join(get_template_dir(), "config-template.json")
        with open(template_path, 'r') as template_file:
            config_template = json.load(template_file)

        config_template = {key.upper(): value for key, value in config_template.items()}
        config_template.update(config_data)
        config_template= json.dumps(config_template, indent=4,ensure_ascii=False)

        replacements = {
            "CONVERSATION_MAX_TOKENS": int(config_data.get("CONVERSATION_MAX_TOKENS", 1000)),
            "SPEECH_RECOGNITION": config_data.get("SPEECH_RECOGNITION", "False"),
            "CHARACTER_DESC": config_data.get("CHARACTER_DESC", "You are an AI assistant."),
            "EXPIRES_IN_SECONDS": int(config_data.get("EXPIRES_IN_SECONDS", 3600)),
            "USE_GLOBAL_PLUGIN_CONFIG": config_data.get("USE_GLOBAL_PLUGIN_CONFIG", "True"),
            "USE_LINKAI": config_data.get("USE_LINKAI", "False"),
            "OPEN_AI_API_KEY": config_data.get("OPEN_AI_API_KEY", ""),
            "OPEN_AI_API_BASE": config_data.get("OPEN_AI_API_BASE", ""),
            "MODEL": config_data.get("MODEL", "gpt-4o"),
            "PROXY": config_data.get("PROXY", ""),
            "SINGLE_CHAT_PREFIX": config_data.get("SINGLE_CHAT_PREFIX", "['']"),
            "SINGLE_CHAT_REPLY_PREFIX": config_data.get("SINGLE_CHAT_REPLY_PREFIX", ""),
            "GROUP_CHAT_PREFIX": config_data.get("GROUP_CHAT_PREFIX", "['']"),
            "GROUP_NAME_WHITE_LIST": config_data.get("GROUP_NAME_WHITE_LIST", "['ALL_GROUP']"),
            "IMAGE_CREATE_PREFIX": config_data.get("IMAGE_CREATE_PREFIX", "['画']"),
            "LINKAI_API_KEY": config_data.get("LINKAI_API_KEY", ""),
            "LINKAI_APP_CODE": config_data.get("LINKAI_APP_CODE", ""),
            "TEMPERATURE":config_data.get("TEMPERATURE", "0.7"),
        }

        
        for key, value in replacements.items():
            config_template = config_template.replace(f'{{{{{key}}}}}', str(value))
        
        config_dir = os.path.join(get_config_dir(), service_id)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_path = os.path.join(config_dir, 'config.json')
        with open(config_path, 'w') as config_file:
            config_file.write(config_template)
        
        return config_path
    
    def generate_docker_compose_file(self, service_id, config_path):
        """生成Docker Compose文件"""
        compose_template_path = os.path.join(get_template_dir(), 'docker-compose.template.yml')
        with open(compose_template_path, 'r', encoding='utf-8') as file:
            compose_content = file.read()
        
        compose_content = compose_content.replace('{{service_name}}', str(service_id))
        
        with open(config_path, 'r', encoding='utf-8') as config_file:
            merged_config = json.load(config_file)

        for key, value in merged_config.items():
            placeholder = f'{{{{{key}}}}}'
            if isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)
            else:
                value = str(value)
            compose_content = compose_content.replace(placeholder, value)
        
        compose_file_path = os.path.join(os.path.dirname(config_path), 'docker-compose.yml')
        with open(compose_file_path, 'w', encoding='utf-8') as file:
            file.write(compose_content)
        
        return compose_file_path

    def get_bot_list(self):
        db_path = os.path.join(get_data_dir(), 'bots.db')

        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 创建表（如果不存在）
                cursor.execute('''CREATE TABLE IF NOT EXISTS bots
                                  (container_id TEXT PRIMARY KEY,
                                   name TEXT,
                                   config TEXT,
                                   service_id TEXT)''')

                cursor.execute("""
                    SELECT container_id as id, name, config, service_id
                    FROM bots
                """)
                
                bot_list = [dict(row) for row in cursor.fetchall()]

                # 更新容器状态
                for bot in bot_list:
                    try:
                        container = self.client.containers.get(bot['id'])
                        bot['status'] = container.status
                    except docker.errors.NotFound:
                        bot['status'] = "未找到"

            return bot_list

        except Exception as e:
            print(f"从数据库加载机器人列表时出错: {e}")
            return []

    def generate_uuid(self):
        return str(uuid.uuid4())[:8]
   
    def restart_bots(self, container_id):
        db_path = os.path.join(get_data_dir(), 'bots.db')
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT service_id FROM bots WHERE container_id = ?", (container_id,))
            result = cursor.fetchone()
            
            if result:
                service_id = result[0]
                config_dir = os.path.join(get_config_dir(), service_id)
                compose_file_path = os.path.join(config_dir, 'docker-compose.yml')
                
                try:
                    # 停止并移除旧容器
                    old_container = self.client.containers.get(container_id)
                    old_container.stop()
                    old_container.remove()

                    # 使用docker-compose启动新容器
                    subprocess.run(['docker-compose', '-f', compose_file_path, 'up', '-d'], check=True)

                    # 获取新创建的容器ID
                    new_container = self.client.containers.get(service_id)
                    new_container_id = new_container.id[:12]

                    # 更新数据库中的容器ID
                    cursor.execute("UPDATE bots SET container_id = ? WHERE container_id = ?", (new_container_id, container_id))
                    conn.commit()

                    return "容器重启成功，并已更新数据库"
                
                except subprocess.CalledProcessError as e:
                    return f"容器启动失败: {str(e)}"
                except Exception as e:
                    return f"操作失败: {str(e)}"
            else:
                return '找不到对应的 bots 对象'
        
        except sqlite3.Error as e:
            return f"数据库操作失败: {str(e)}"
        finally:
            if conn:
                conn.close()
            
    def manage_container(self, container_id, action):
        try:
            container = self.client.containers.get(container_id)
            if action == "start":
                container.start()
            elif action == "stop":
                container.stop()
            elif action == "restart":
                self.restart_bots(container_id)
            elif action == "remove":
                self.delete_bot(container_id)
            
            return container.status
        except docker.errors.NotFound:
            print(f"容器 {container_id} 不存在")
            if action == "remove":
                # 如果是删除操作，即使容器不存在也继续删除数据库中的记录
                self.delete_bot(container_id)
            return "not found"
        except Exception as e:
            print(f"操作容器时发生错误: {str(e)}")
            return "error"
    
    def start_docker_container(self, config_data):
        # 清理未使用的Docker网络
        try:
            subprocess.run(["docker", "network", "prune", "-f"], check=True)
            print("未使用的Docker网络已清理")
        except subprocess.CalledProcessError as e:
            print(f"清理Docker网络失败: {e}")

        service_id = self.generate_uuid()  # 每次调用都生成一个新的 UUID

        # 使用通用方法处理配置并生成 Compose 文件
        compose_file_path, config_path = self.process_config_and_generate_compose(service_id, config_data)

        # 启动容器
        try:
            subprocess.run(['docker-compose', '-f', compose_file_path, 'up', '-d'], check=True)
            container_name = config_data.get("CONTAINER_NAME", service_id)
            container = self.client.containers.get(container_name)
            container_id = container.id[:12]
        
            with open(config_path, 'r', encoding='utf-8') as config_file:
                current_config = json.load(config_file)
            body = {
                "name": config_data.get("BOT_NAME", "default_bot"),
                "config": json.dumps(current_config),
                "container_id": container_id,
                "service_id": service_id
            }
            
            # 使用sqlite替代操作bots.json文件
            db_path = os.path.join(get_data_dir(), 'bots.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 创建表（如果不存在）
            cursor.execute('''CREATE TABLE IF NOT EXISTS bots
                                (container_id TEXT PRIMARY KEY,
                                name TEXT,
                                config TEXT,
                                service_id TEXT)''')
            
            # 插入或更新数据
            cursor.execute('''INSERT OR REPLACE INTO bots
                                (container_id, name, config, service_id)
                                VALUES (?, ?, ?, ?)''',
                            (body['container_id'], body['name'], body['config'], body['service_id']))
            
            conn.commit()
            conn.close()

            return body
        except Exception as e:
            print(f"启动容器失败: {e}")
            return {}

    def get_bot_list(self):
        db_path = os.path.join(get_data_dir(), 'bots.db')
        bot_list = []

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT container_id, name, config, service_id FROM bots")
            rows = cursor.fetchall()

            for row in rows:
                container_id, name, config, service_id = row
                try:
                    container = self.client.containers.get(container_id)
                    status = container.status
                except docker.errors.NotFound:
                    status = "not found"

                bot_list.append({
                    "id": container_id,
                    "service_id": service_id,
                    "name": name,
                    "status": status,
                    "config": config
                })

            conn.close()
        except Exception as e:
            print(f"从数据库加载机器人列表时出错: {e}")

        return bot_list
    
    def get_container_logs(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs().decode('utf-8')
            
            # 将日志分割成行
            log_lines = logs.split('\n')
            
            # 格式化日志，添加时间戳
            formatted_logs = []
            for line in log_lines:
                if line.strip():
                    # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    formatted_logs.append(f"{line}")
            
            # 将格式化后的日志重新组合成字符串
            formatted_logs_str = '\n'.join(formatted_logs)
            
            # 匹配二维码链接
            qr_pattern = r'(https://api\.qrserver\.com/v1/create-qr-code/\?size=400×400&data=https://login\.weixin\.qq\.com/l/[A-Za-z0-9-]+==)'
            matches = re.findall(qr_pattern, formatted_logs_str)
            
            result = {
                "logs": formatted_logs_str,
                "qr_code": None
            }
            
            if matches:
                # 设置最后一个匹配的二维码链接（最近生成的）
                result["qr_code"] = matches[-1]
            else:
                print(f"未在容器 {container_id} 的日志中找到二维码链接")
            
            return result
        
        except docker.errors.NotFound:
            print(f"容器 {container_id} 不存在")
            return None
        except Exception as e:
            print(f"获取容器日志时发生错误: {str(e)}")
            return None

    

    def delete_bot(self, container_id):
        try:
            conn = sqlite3.connect(os.path.join(get_data_dir(), 'bots.db'))
            cursor = conn.cursor()
            
            # 查询机器人信息
            cursor.execute("SELECT service_id FROM bots WHERE container_id = ?", (container_id,))
            result = cursor.fetchone()
            
            if result:
                service_id = result[0]
                
                # 删除配置文件和目录
                config_dir = os.path.join(get_config_dir(), service_id)
                if os.path.exists(config_dir):
                    for root, dirs, files in os.walk(config_dir, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(config_dir)
                    print(f"配置目录 {config_dir} 已成功删除。")
                
                # 从数据库中删除机器人记录
                cursor.execute("DELETE FROM bots WHERE container_id = ?", (container_id,))
                conn.commit()
                
                # 停止并删除Docker容器
                try:
                    container = self.client.containers.get(container_id)
                    container.stop()
                    container.remove()
                    print(f"Docker容器 {container_id} 已停止并删除。")
                except docker.errors.NotFound:
                    print(f"Docker容器 {container_id} 未找到，可能已被删除。")
                
                print(f"机器人 {container_id} 已成功删除。")
                return True
            else:
                print(f"未找到 ID 为 {container_id} 的机器人。")
                return False
        except Exception as e:
            print(f"删除机器人时出错：{e}")
            return False
        finally:
            if conn:
                conn.close()
            
        # 刷新机器人列表
        # self.bots = self.load_bots()
        
        
   
    def get_bot_config(self, bot_id):
        """根据机器人 ID 从生成的 config.json 文件中获取其配置数据"""
        config_dir = os.path.join(get_config_dir(), bot_id)
        config_path = os.path.join(config_dir, 'config.json')
        
        if not os.path.exists(config_path):
            return {}

        with open(config_path, 'r', encoding='utf-8') as config_file:
            config_data = json.load(config_file)
        
        return config_data
    
    

    def save_config(self,service_id,config_data):
        config_dir = os.path.join(get_config_dir(), service_id)
        config_path = os.path.join(config_dir, 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as file:
                existing_config = json.load(file)
        else:
            existing_config = {}

        new_config={**existing_config,**config_data}
        #生成新compose文件
        self.process_config_and_generate_compose(service_id, new_config)
        
        return new_config
    
    