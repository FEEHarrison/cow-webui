import os
import json
import docker
import subprocess
import re
import uuid
import sqlite3
import logging
import psutil
import bcrypt
from config import config
from platform_config import PlatformConfig
import traceback

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DockerManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
            print("Docker client 初始化成功")
        except docker.errors.DockerException as e:
            print(f"Docker client 初始化失败: {e}")
            self.client = None

        self.db_path = os.path.abspath(config.DB_PATH)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_tables()
        print("DockerManager 初始化完成")

    def __del__(self):
        if self.conn:
            self.conn.close()

    def connect_db(self):
        # db_path = os.path.join(config.get_data_dir(), 'app.db')
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # 创建 users 表
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT,
                        platform TEXT,
                        model TEXT,
                        max_bots INTEGER)''')

        # 创建 bots 表
        cursor.execute('''CREATE TABLE IF NOT EXISTS bots
                    (container_id TEXT PRIMARY KEY,
                    bot_name TEXT,
                    config TEXT,
                    model TEXT,
                    platform TEXT,
                    service_id TEXT UNIQUE,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')

        self.conn.commit()
        print("数据库表结构检查和更新完成")

    

    def is_admin_setup(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE role = 'root'")
        admin = cursor.fetchone()
        return admin is not None

    def setup_admin(self, password):
        try:
            logger.info("Starting admin setup")
            self.print_table_schema()
            
            logger.info("Checking if admin is already setup")
            print('是否出错')
            if self.is_admin_setup():
                raise ValueError("管理员已经设置")
            
            logger.info("Validating password")
            if not isinstance(password, str):
                raise ValueError("密码必须是字符串")

            logger.info("Generating admin ID and hashing password")
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            logger.info("Inserting admin into database")
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role, max_bots) VALUES (?, ?, ?, ?)",
                ('admin', hashed_password, 'root', -1)
            )
            self.conn.commit()
            
            logger.info("Admin setup successful")
            return {
                'id': cursor.lastrowid,
                'username': 'admin',
                'role': 'root',
                'max_bots': -1
            }
        except sqlite3.Error as e:
            logger.error(f"SQLite error in setup_admin: {e}")
            self.conn.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in setup_admin: {e}")
            self.conn.rollback()
            raise


    def clear_user_data(self):
        try:
            self.print_table_schema()  # 打印表结构
            cursor = self.conn.cursor()
            
            # 删除 users 表中的所有数据
            cursor.execute('DELETE FROM users')
            
            # 重置自增 ID（如果存在）
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
            if cursor.fetchone():
                cursor.execute('DELETE FROM sqlite_sequence WHERE name=?', ('users',))
            
            self.conn.commit()
            logger.info("所有用户数据已清空，包括管理员账号")
            return True, "所有用户数据已清空，包括管理员账号"
        except sqlite3.Error as e:
            logger.error(f"清空用户数据时发生错误: {e}")
            self.conn.rollback()
            return False, f"清空用户数据时发生错误: {e}"
    

    def create_user(self, username, password, role='user', max_bots=5):
        if role != 'user':
            raise ValueError("只能创建普通用户账号")
        
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role, max_bots) VALUES (?, ?, ?, ?)",
                (username, hashed_password, role, max_bots)
            )
            self.conn.commit()
            user_id = cursor.lastrowid
            logger.info(f"成功创建用户: {username}")
            return user_id
        except sqlite3.IntegrityError as e:
            logger.error(f"创建用户失败，可能是用户名已存在: {e}")
            self.conn.rollback()
            raise ValueError("用户名已存在")
        except Exception as e:
            logger.error(f"创建用户时发生未知错误: {e}")
            self.conn.rollback()
            raise

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return {
                'id': user[0],
                'username': user[1],
                'role': user[3],
                'max_bots': user[4]
            }
        return None
    
    def get_all_users(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''SELECT id, username, role, max_bots FROM users''')
            users = cursor.fetchall()
            return [{"id": user[0], "username": user[1], "role": user[2], "max_bots": user[3]} for user in users]
        except sqlite3.Error as e:
            logger.error(f"获取用户列表时发生错误: {e}")
            return []

    def delete_user(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"成功删除用户 ID: {user_id}")
                return True
            else:
                logger.warning(f"未找到用户 ID: {user_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"删除用户时发生数据库错误: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            logger.error(f"删除用户时发生未知错误: {e}")
            self.conn.rollback()
            return False
                    
    def get_container_id(self,data,target_value):
        for key, value in data.items():
            if isinstance(value, dict) and value.get('service_id') == target_value:
                return key
        return None

    def process_config_and_generate_compose(self, service_id, config_data):
        print(f"处理配置并生成 Docker Compose 文件，服务数据: {config_data}")
        
        
        # 生成 Docker Compose 文件
        compose_file_path = self.generate_docker_compose_file(service_id, config_data)
        print(f"生成的 Docker Compose 文件路径: {compose_file_path}")
        return compose_file_path
        
    def generate_config(self, service_id, config_data):
        template_path = os.path.join(config.get_template_dir(), "config-template.json")
        with open(template_path, 'r', encoding='utf-8') as template_file:
            config_template = json.load(template_file)

        # 合并配置数据，保持原有的大小写
        for key, value in config_data.items():
            config_template[key] = value

        # 确保所有必要的字段都存在
        required_fields = [
            "CONVERSATION_MAX_TOKENS", "SPEECH_RECOGNITION", "CHARACTER_DESC",
            "EXPIRES_IN_SECONDS", "USE_GLOBAL_PLUGIN_CONFIG", "USE_LINKAI",
            "MODEL", "PROXY", "SINGLE_CHAT_PREFIX", "SINGLE_CHAT_REPLY_PREFIX",
            "GROUP_CHAT_PREFIX", "GROUP_NAME_WHITE_LIST", "IMAGE_CREATE_PREFIX",
            "LINKAI_API_KEY", "LINKAI_APP_CODE", "TEMPERATURE",
            "ZHIPU_AI_API_KEY", "ZHIPU_AI_API_BASE"
        ]

        for field in required_fields:
            if field not in config_template:
                config_template[field] = config_data.get(field, "")

        # 保存配置文件
        config_dir = os.path.join(config.get_config_dir(), service_id)
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, 'config.json')
        with open(config_path, 'w', encoding='utf-8') as config_file:
            json.dump(config_template, config_file, indent=4, ensure_ascii=False)

        return config_path
    
    def generate_docker_compose_file(self, service_id, config_data):
        print(f"生成 Docker Compose 文件，服务ID: {service_id}")
        print(f"配置数据: {config_data}")
        
        compose_template_path = os.path.join(config.get_template_dir(), 'docker-compose.template.yml')
        with open(compose_template_path, 'r', encoding='utf-8') as file:
            compose_content = file.read()

        # 替换服务名
        compose_content = compose_content.replace('{{service_name}}', service_id)

        # 准备环境变量
        env_vars = {}
        for key, value in config_data.items():
            if key in ['CONVERSATION_MAX_TOKENS', 'TEMPERATURE']:
                # 确保这些值是数字格式
                try:
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                    env_vars[key] = f'{value}'
                except ValueError:
                    env_vars[key] = f'"{value}"'
            elif isinstance(value, (list, dict)):
                env_vars[key] = f"'{json.dumps(value, ensure_ascii=False)}'"
            else:
                env_vars[key] = f'"{value}"'

        # 添加平台特定的环境变量
        platform = config_data.get('PLATFORM', '').lower()
        platform_env = PlatformConfig.get_platform_env_vars(platform, config_data)
        for key, value in platform_env.items():
            if value and key not in env_vars:
                env_vars[key] = f'"{value}"'

        # 将所有环境变量插入到 compose 文件中
        env_string = '\n'.join(f'      {key}: {value}' for key, value in env_vars.items())
        
        # 使用正则表达式替换环境变量部分
        import re
        pattern = re.compile(r'environment:.*?(?=\n\w|$)', re.DOTALL)
        compose_content = pattern.sub(f'environment:\n{env_string}', compose_content)

        # 写入生成的 Docker Compose 文件
        compose_dir = os.path.join(config.get_config_dir(), service_id)
        os.makedirs(compose_dir, exist_ok=True)
        compose_file_path = os.path.join(compose_dir, 'docker-compose.yml')
        with open(compose_file_path, 'w', encoding='utf-8') as file:
            file.write(compose_content)

        print(f"生成的 Docker Compose 文件内容:\n{compose_content}")
        return compose_file_path

    def get_bot_list(self, user_id=None, page=1, per_page=10):
        cursor = self.conn.cursor()

        try:
            if user_id:
                query = "SELECT DISTINCT container_id, bot_name, config, service_id, user_id, platform, model FROM bots WHERE user_id = ?"
                params = (user_id,)
            else:
                query = "SELECT DISTINCT container_id, bot_name, config, service_id, user_id, platform, model FROM bots"
                params = ()

            # 添加分页
            query += " LIMIT ? OFFSET ?"
            params += (per_page, (page - 1) * per_page)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            bot_list = []
            for row in rows:
                container_id, bot_name, config, service_id, bot_user_id, platform, model = row
                status = "unknown"
                if container_id:
                    try:
                        container = self.client.containers.get(container_id)
                        status = container.status
                    except docker.errors.NotFound:
                        status = "not found"
                    except Exception as e:
                        logger.error(f"获取容器状态时出错 (ID: {container_id}): {e}")
                        status = "error"

                # 解析配置并移除敏感信息
                filtered_config = {}
                if config:
                    try:
                        config_dict = json.loads(config)
                        filtered_config = {k: v for k, v in config_dict.items() if not k.endswith('_API_KEY')}
                    except json.JSONDecodeError:
                        logger.error(f"解析配置 JSON 时出错 (ID: {container_id})")
                    except TypeError:
                        logger.error(f"配置不是有效的 JSON 字符串 (ID: {container_id})")

                bot_list.append({
                    "id": container_id or "",
                    "service_id": service_id or "",
                    "bot_name": bot_name or "",
                    "status": status,
                    "config": filtered_config,
                    "user_id": bot_user_id,
                    "platform": platform or "",
                    "model": model or ""
                })

            return bot_list
        except Exception as e:
            logger.error(f"从数据库加载机器人列表时出错: {e}")
            return []

      

    def generate_uuid(self):
        return str(uuid.uuid4())[:8]
   
    def restart_bots(self, container_id):
        # db_path = os.path.join(config.get_data_dir(), 'app.db')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT service_id FROM bots WHERE container_id = ?", (container_id,))
            result = cursor.fetchone()
            
            if result:
                service_id = result[0]
                config_dir = os.path.join(config.get_config_dir(), service_id)
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
    
    def start_docker_container(self, config_data, user_id):
        print(f"开始创建机器人，用户ID: {user_id}")
        print(f"配置数据: {config_data}")
        # 检查服务器资源是否足够
        can_create, message = self.can_create_bot()
        if not can_create:
            return {"error": message}

        service_id = self.generate_uuid()
        compose_file_path = self.process_config_and_generate_compose(service_id, config_data)

        try:
            # 清理未使用的Docker网络
            subprocess.run(["docker", "network", "prune", "-f"], check=True)
            
            # 启动容器
            subprocess.run(['docker-compose', '-f', compose_file_path, 'up', '-d'], check=True)
            
            container_name = config_data.get("CONTAINER_NAME", service_id)
            container = self.client.containers.get(container_name)
            container_id = container.id[:12]
            
            bot_data = {
                "container_id": container_id,
                "bot_name": config_data.get("BOT_NAME", "default_bot"),
                "config": json.dumps(config_data),
                "service_id": service_id,
                "user_id": user_id,
                "platform": config_data.get("PLATFORM", ""),
                "model": config_data.get("MODEL", "")
            }
            
            # 保存到数据库
            self.save_bot_to_db(bot_data)
            print(f"机器人创建成功，用户ID: {user_id}")
            return bot_data
        
        except Exception as e:
            logger.error(f"启动容器失败: {e}")
            logging.error(traceback.format_exc())  # 这将打印完整的堆栈跟踪
            return {"error": str(e)}

    def save_bot_to_db(self, bot_data):
        cursor = self.conn.cursor()
        print(f"Saving bot data: {bot_data}")
        try:
            # 确保 config 是有效的 JSON 字符串
            if isinstance(bot_data['config'], dict):
                bot_data['config'] = json.dumps(bot_data['config'])
            elif not isinstance(bot_data['config'], str):
                raise ValueError("Config must be a dict or a JSON string")

            cursor.execute('''INSERT OR REPLACE INTO bots
                            (container_id, bot_name, config, service_id, user_id, platform, model)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (bot_data['container_id'], bot_data['bot_name'], bot_data['config'], 
                            bot_data['service_id'], bot_data['user_id'], bot_data['platform'], bot_data['model']))
            self.conn.commit()
            print(f"保存机器人数据到数据库，用户ID: {bot_data['user_id']}")
        except sqlite3.IntegrityError as e:
            print(f"数据库插入错误（可能是重复数据）: {e}")
            self.conn.rollback()
        except Exception as e:
            print(f"保存机器人数据时发生错误: {e}")
            self.conn.rollback()

    def get_bot_list(self, user_id=None, page=1, per_page=10):
        cursor = self.conn.cursor()

        try:
            if user_id:
                query = "SELECT container_id, bot_name, config, service_id, user_id, platform, model FROM bots WHERE user_id = ?"
                params = (user_id,)
            else:
                query = "SELECT container_id, bot_name, config, service_id, user_id, platform, model FROM bots"
                params = ()

            # 添加分页
            query += " LIMIT ? OFFSET ?"
            params += (per_page, (page - 1) * per_page)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            bot_list = []
            for row in rows:
                container_id, bot_name, config, service_id, bot_user_id, platform, model = row
                status = "unknown"
                if container_id:
                    try:
                        container = self.client.containers.get(container_id)
                        status = container.status
                    except docker.errors.NotFound:
                        status = "not found"
                    except Exception as e:
                        logger.error(f"获取容器状态时出错 (ID: {container_id}): {e}")
                        status = "error"

                # 解析配置并移除敏感信息
                filtered_config = {}
                if config:
                    try:
                        config_dict = json.loads(config)
                        filtered_config = {k: v for k, v in config_dict.items() if not k.endswith('_API_KEY')}
                    except json.JSONDecodeError:
                        logger.error(f"解析配置 JSON 时出错 (ID: {container_id})")

                bot_list.append({
                    "id": container_id or "",
                    "service_id": service_id or "",
                    "bot_name": bot_name or "",
                    "status": status,
                    "config": filtered_config,
                    "user_id": bot_user_id,
                    "platform": platform or "",
                    "model": model or ""
                })

            return bot_list
        except Exception as e:
            logger.error(f"从数据库加载机器人列表时出错: {e}")
            return []
    
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
            qr_pattern = r'(https://api\.pwmqr\.com/qrcode/create/\?url=https://login\.weixin\.qq\.com/l/[A-Za-z0-9-]+==|https://my\.tv\.sohu\.com/user/a/wvideo/getQRCode\.do\?text=https://login\.weixin\.qq\.com/l/[A-Za-z0-9-]+==|https://api\.qrserver\.com/v1/create-qr-code/\?size=400×400&data=https://login\.weixin\.qq\.com/l/[A-Za-z0-9-]+==)'
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
            print(result["qr_code"])
            return result
        
        except docker.errors.NotFound:
            print(f"容器 {container_id} 不存在")
            return None
        except Exception as e:
            print(f"获取容器日志时发生错误: {str(e)}")
            return None

    

    def delete_bot(self, container_id):
        try:
            cursor = self.conn.cursor()
            
            # 查询机器人信息
            cursor.execute("SELECT service_id FROM bots WHERE container_id = ?", (container_id,))
            result = cursor.fetchone()
            
            if result:
                service_id = result[0]
                
                # 删除配置文件和目录
                config_dir = os.path.join(config.get_config_dir(), service_id)
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
                self.conn.commit()
                
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
            self.conn.rollback()
            return False
        
        
   
    def get_bot_config(self, bot_id):
        """根据机器人 ID 从数据库中获取其配置数据"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT config FROM bots WHERE service_id = ?", (bot_id,))
        result = cursor.fetchone()
        
        if not result:
            return {}

        config_data = result[0]
        
        if config_data is None:
            logger.warning(f"机器人 ID {bot_id} 的配置为 None")
            return {}

        try:
            config_dict = json.loads(config_data)
        except json.JSONDecodeError:
            logger.error(f"解析机器人 ID {bot_id} 的配置 JSON 时出错")
            return {}
        except TypeError:
            logger.error(f"机器人 ID {bot_id} 的配置不是有效的 JSON 字符串")
            return {}
        
        # 只保留当前平台的 API 参数
        platform = config_dict.get('PLATFORM', '').lower()
        api_keys_to_keep = PlatformConfig.get_platform_api_keys(platform)
        
        filtered_config = {k: v for k, v in config_dict.items() if not k.endswith('_API_KEY') and not k.endswith('_API_BASE')}
        filtered_config.update({k: v for k, v in config_dict.items() if k.upper() in api_keys_to_keep})
        
        return filtered_config
    
    

    def save_config(self, service_id, config_data):
        print(f"保存配置，服务ID: {service_id}")
        print(f"配置数据: {config_data}")
        
        # 验证平台
        platform = config_data.get('PLATFORM', '').lower()
        if not PlatformConfig.is_valid_platform(platform):
            raise ValueError(f"无效的平台: {platform}")
        
        # 获取平台特定的API密钥
        api_keys = PlatformConfig.get_platform_api_keys(platform)
        print(f"平台 {platform} 需要的 API 密钥: {api_keys}")
        
        # 验证必要的API密钥是否存在
        missing_keys = [key for key in api_keys if not config_data.get(key)]
        if missing_keys:
            print(f"缺少的 API 密钥: {missing_keys}")
            raise ValueError(f"缺少必要的API密钥: {', '.join(missing_keys)}")
        
        # 确保 config_data 是 JSON 字符串
        config_json = json.dumps(config_data)
        
        # 更新数据库
        cursor = self.conn.cursor()
        cursor.execute("UPDATE bots SET platform = ?, model = ?, bot_name = ?, config = ? WHERE service_id = ?", 
                    (config_data.get('PLATFORM', ''), config_data.get('MODEL', ''), 
                    config_data.get('BOT_NAME', ''), config_json, service_id))
        self.conn.commit()

        # 生成新的compose文件
        self.process_config_and_generate_compose(service_id, config_data)

        return config_data

    
    
    def get_server_resources(self):
        """获取服务器当前资源状态"""
        try:
            # 获取CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 获取内存使用情况
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 获取磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'disk_usage': disk_usage
            }
        except Exception as e:
            print(f"获取服务器资源状态时出错：{e}")
            return None

    def can_create_bot(self):
        """判断是否可以创建新的机器人"""
        resources = self.get_server_resources()
        if resources is None:
            return False, "无法获取服务器资源状态"
        
        if resources['cpu_usage'] > 80 or resources['memory_usage'] > 80 or resources['disk_usage'] > 80:
            return False, "服务器资源使用率超过80%，无法创建新的机器人。请考虑删除一些现有的机器人后再尝试。"
        
        return True, "可以创建新的机器人"

    def print_table_schema(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
            schema = cursor.fetchone()[0]
            logger.info(f"Users table schema: {schema}")
        except sqlite3.Error as e:
            logger.error(f"获取表结构时发生错误: {e}")

    def get_user_by_id(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'role': user[3],
                'max_bots': user[6]
            }
        return None