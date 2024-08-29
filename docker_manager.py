import os
import json
import docker
import subprocess
from config import get_config_dir, get_template_dir,get_data_dir
import re
import uuid
from datetime import datetime, timedelta
from flask import jsonify
import fcntl
import logging
import time

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.bots_file = os.path.join(get_data_dir(), "bots.json")
        self.bots=self.load_bots()
    def get_container_id(self,data,target_value):
        for key, value in data.items():
            if isinstance(value, dict) and value.get('service_id') == target_value:
                return key
        return None
    def process_config_and_generate_compose(self, service_id, config_data):
        """处理配置并生成 Docker Compose 文件"""
        # 生成或更新配置文件
        bots_file_path = os.path.join(get_data_dir(), 'bots.json')
        with open(bots_file_path, 'r') as file:
            bots_data = json.load(file)
        container_id=self.get_container_id(bots_data,service_id)
  
        try:
            if container_id in bots_data:
                bots_data[container_id]["name"] = config_data["BOT_NAME"]
                with open(bots_file_path, 'w') as file:
                    json.dump(bots_data, file, indent=4)
        except KeyError as e:
            print(f"KeyError: {e} - Check if all required keys are present in your data.")
        except IOError as e:
            print(f"IOError: {e} - Check file path and permissions.")
        except Exception as e:
            print(f"Unexpected error: {e}")

        config_path = self.generate_config(service_id, config_data)
        # 生成Docker Compose文件
        compose_file_path = self.generate_docker_compose_file(service_id, config_path)
        
        return compose_file_path,config_path
    
    def generate_config(self, service_id, config_data):
        template_path = os.path.join(get_template_dir(), "config-template.json")
        with open(template_path, 'r') as template_file:
            config_template = json.load(template_file)

        config_template = {key.upper(): value for key, value in config_template.items()}
        config_template.update(config_data)
        config_template= json.dumps(config_template, indent=4,ensure_ascii=False)

        replacements = {
            # "BOT_NAME":config_data.get("BOT_NAME", "default_bot"),
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
    
    def load_bots(self):
        bots = {}
        if os.path.exists(self.bots_file):
            with open(self.bots_file, 'r') as file:
                fcntl.flock(file, fcntl.LOCK_SH)  # 共享锁，防止文件同时被写入
                try:
                    if os.path.getsize(self.bots_file) > 0:
                        try:
                            bots = json.load(file)
                            logging.info(f"Loaded bots from {self.bots_file} at {time.time()}: {bots}")
                        except json.JSONDecodeError:
                            logging.error(f"Failed to decode JSON from {self.bots_file} at {time.time()}")
                            bots = {}
                    else:
                        logging.warning(f"Bots file {self.bots_file} is empty at {time.time()}, initializing empty bots")
                        bots = {}
                finally:
                    fcntl.flock(file, fcntl.LOCK_UN)  # 解锁文件
        else:
            logging.warning(f"Bots file {self.bots_file} does not exist at {time.time()}, initializing empty bots")
            bots = {}
        
        return bots

    
    
    def generate_uuid(self):

        return str(uuid.uuid4())[:8]
   
    
    def restart_bots(self, container_id):
        bots_file_path = os.path.join(get_data_dir(), 'bots.json')
        with open(bots_file_path, 'r') as file:
            bots_data = json.load(file)
        
        if container_id in bots_data:
            service_id = bots_data[container_id]["service_id"]
            config_dir = os.path.join(get_config_dir(), service_id)
            compose_file_path = os.path.join(config_dir, 'docker-compose.yml')
            
            try:
                # Stop and remove the old container
                old_container = self.client.containers.get(container_id)
                old_container.stop()
                old_container.remove()

                # Start new container using docker-compose
                subprocess.run(['docker-compose', '-f', compose_file_path, 'up', '-d'], check=True)

                # Get the ID of the newly created container
                new_container = self.client.containers.get(service_id)  # You can fetch it by the service ID
                new_container_id = new_container.id[:12]

                # Update bots.json with the new container ID
                bots_data[new_container_id] = bots_data.pop(container_id)

                with open(bots_file_path, 'w') as file:
                    json.dump(bots_data, file, indent=4)

                return "容器重启成功，并已更新 bots.json"
            
            except subprocess.CalledProcessError as e:
                return f"容器启动失败: {str(e)}"
            except Exception as e:
                return f"操作失败: {str(e)}"
        else:
            return '找不到对应的 bots 对象'       
            
    def manage_container(self, container_id, action):
        container = self.client.containers.get(container_id)
        if action == "start":
            container.start()
        elif action == "stop":
            container.stop()
        elif action == "restart":
            self.restart_bots(container_id)
            # container.stop()
            # container.remove()
            
        elif action == "remove":
            self.delete_bot(container_id)
            container.stop()
            container.remove()
            
        return container.status

    def add_bots(self, container_id, data):

        try:
            bots_file_path = os.path.join(get_data_dir(), 'bots.json')
            
            with open(bots_file_path, 'r') as file:
                bots_data = json.load(file)
            
            bots_data[container_id] = data
            
            with open(bots_file_path, 'w') as file:
                json.dump(bots_data, file, indent=4)
            
        except Exception as e:
            print(f"Failed to change bots.json: {e}")
            return False
    
    def del_bots(self, container_id):
        try:
            bots_file_path = os.path.join(get_data_dir(), 'bots.json')
            
            with open(bots_file_path, 'r') as file:
                bots_data = json.load(file)
            
            # bots_data[container_id] = data
            if container_id in bots_data:
                del bots_data[container_id]
                # bots_data[container_id] = data
            
            with open(bots_file_path, 'w') as file:
                json.dump(bots_data, file, indent=4)
            
        except Exception as e:
            print(f"Failed to change bots.json: {e}")
            return False
    
    def start_docker_container(self, config_data):
        # 清理未使用的Docker网络
        try:
            subprocess.run(["docker", "network", "prune", "-f"], check=True)
            print("未使用的Docker网络已清理")
        except subprocess.CalledProcessError as e:
            print(f"清理Docker网络失败: {e}")

        service_id = self.generate_uuid()  # 每次调用都生成一个新的 UUID

        # 使用通用方法处理配置并生成 Compose 文件
        compose_file_path,config_path = self.process_config_and_generate_compose(service_id, config_data)
        # print(compose_file_path,'compose_file_path')
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
                "config": current_config,
                # "logs": log_data,
                "container_id": container_id,
                "service_id": service_id
            }
            self.add_bots(container_id,body)
            

            return self.bots[container_id]
        except Exception as e:
            print(f"Failed to start container: {e}")
            return {}
       

    def get_bot_list(self):
        
        bots_file_path = os.path.join(get_data_dir(), 'bots.json')
        try:
            with open(bots_file_path, 'r') as file:
                bots_data = json.load(file)
        except Exception as e:
            print(f"Error loading bots.json: {e}")
            return []

        bot_list = []
        for container_id, value in bots_data.items():
            try:
                container = self.client.containers.get(container_id)  # 使用完整容器 ID
                status = container.status
            except docker.errors.NotFound:
                status = "not found"

            bot_list.append({
                "id": container_id,
                "service_id": value['service_id'],
                "name": value['name'],
                "status": status,
                "config": value['config']
            })

        return bot_list

    def get_container_logs(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            # 通过设置 `since` 为较早的时间来确保获取到历史日志
            # since_time = (datetime.now() - timedelta(hours=1)).timestamp()
            since_time = (datetime.now() - timedelta(seconds=60)).timestamp()
            logs = container.logs(stream=False, follow=False,since=int(since_time))
            
            # 确保日志内容被正确解码
            try:
                decoded_logs = logs.decode('utf-8')
            except Exception as decode_error:
                print(f"Decoding error: {str(decode_error)}")
                return jsonify({"error": "Failed to decode logs"}), 500
            # 正则表达式匹配 https:// 到 == 之间的链接
            pattern = r'https://api.qrserver.com/v1.*?=='
            matches = re.findall(pattern, decoded_logs)
            # 格式化返回的数据
            response_data = {
                "code": 200,
                "success": "true",
                "message": "Logs retrieved successfully",
                "data": matches
            }
            
            # print(decoded_logs, matches, '打印出当前获取的decoded_logs和匹配结果')
            return jsonify(response_data)
        except docker.errors.NotFound:
            return jsonify({"error": "Container not found"}), 404
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    def delete_bot(self, container_id):
        bots_file_path = os.path.join(get_data_dir(), 'bots.json')
        try:
            with open(bots_file_path, 'r') as file:
                bots_data = json.load(file)
                if container_id in bots_data:
                    # 删除配置文件和目录
                    config_dir = os.path.join(get_config_dir(),bots_data[container_id]["service_id"])
                    if os.path.exists(config_dir):
                        for root, dirs, files in os.walk(config_dir, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        os.rmdir(config_dir)
                        print(f"Config directory {config_dir} removed successfully.")
                    self.del_bots(container_id)
                    
                    print(f"Bot {container_id} deleted successfully.")
                    return True
                else:
                    print(f"Bot with service_id {container_id} not found.")
                    return False
        except Exception as e:
            print(f"Error loading bots.json: {e}")
            return []
        
        
   
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
    
    