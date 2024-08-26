import os
import json
import docker
import subprocess
from config import get_config_dir, get_template_dir,get_data_dir
import requests
import re
from pyqrcode import QRCode
import io
import uuid
import time
from datetime import datetime, timedelta
from flask import jsonify,Response

def get_wechat_uuid():
    """从微信服务器获取登录UUID"""
    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new',
        'redirect_uri': 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?mod=desktop',
        'lang': 'zh_CN'
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, params=params, headers=headers)
    
    # 使用正则表达式提取uuid
    match = re.search(r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";', response.text)
    if match and match.group(1) == '200':
        uuid = match.group(2)
        return uuid
    else:
        raise Exception("无法从微信服务器获取UUID")
def generate_qr_code():
    """使用UUID生成微信登录二维码"""
    uuid = get_wechat_uuid()
    qr_url = f'https://login.weixin.qq.com/l/{uuid}'
    qr_code = QRCode(qr_url)
    qr_storage = io.BytesIO()
    qr_code.png(qr_storage, scale=10)
    qr_storage.seek(0)
    return qr_storage

def save_qr_code(filename=None):
    """将二维码保存到 static/qrcodes 文件夹"""
    # 确保 static/qrcodes 文件夹存在
    # qr_folder = os.path.join(os.getcwd(), 'static/qrcodes')
    # if not os.path.exists(qr_folder):
    #     os.makedirs(qr_folder)
    # uuid_str = str(uuid.uuid4())
    # # 默认文件名为 uuid.png
    # if filename is None:
    #     filename = f'{uuid_str}.png'
    
    # # 构建完整的文件路径
    # file_path = os.path.join(qr_folder, filename)
    
    # # 生成二维码并保存到文件
    # qr_storage = generate_qr_code()
    # with open(file_path, 'wb') as f:
    #     f.write(qr_storage.getvalue())
    
    # print(f"二维码已保存到: {file_path}")
    # return file_path

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.bots_file = os.path.join(get_data_dir(), "bots.json")
        self.load_bots()

    def process_config_and_generate_compose(self, service_id, config_data):
        """处理配置并生成 Docker Compose 文件"""
        # 生成或更新配置文件
        
        config_path = self.generate_config(service_id, config_data)
        print(config_path,'config_path')
        # 生成Docker Compose文件
        compose_file_path = self.generate_docker_compose_file(service_id, config_path)
        
        return compose_file_path,config_path

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
        if os.path.exists(self.bots_file):
            if os.path.getsize(self.bots_file) > 0:  # 检查文件是否为空
                with open(self.bots_file, 'r') as file:
                    self.bots = json.load(file)
            else:
                self.bots = {}  # 文件为空时，初始化为一个空字典
        else:
            self.bots = {}

    def save_bots(self):
        with open(self.bots_file, 'w') as file:
            json.dump(self.bots, file, indent=4)

    def generate_uuid(self):

        return str(uuid.uuid4())[:8]
   
    def manage_container(self, container_id, action):
        container = self.client.containers.get(container_id)
        if action == "start":
            container.start()
        elif action == "stop":
            container.stop()
        elif action == "restart":
            container.restart()
        elif action == "remove":
            container.stop()
            container.remove()
            self.delete_bot(container_id)
        return container.status

    def generate_config(self, service_id, config_data):
        template_path = os.path.join(get_template_dir(), "config-template.json")
        with open(template_path, 'r') as template_file:
            # config_template = template_file.read()
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
        print(compose_file_path,'compose_file_path')
        # 启动容器
        try:
            subprocess.run(['docker-compose', '-f', compose_file_path, 'up', '-d'], check=True)
            container_name = config_data.get("CONTAINER_NAME", service_id)
            container = self.client.containers.get(container_name)
            container_id = container.id
            # logs_response = self.get_container_logs(container_id)
            # log_data = logs_response.json.get('data', []) if logs_response.status_code == 200 else []
            with open(config_path, 'r', encoding='utf-8') as config_file:
                current_config = json.load(config_file)
            body = {
                "name": config_data.get("bot_name", "default_bot"),
                "config": current_config,
                # "logs": log_data,
                "container_id": container_id[:12],
                "service_id": service_id
            }
            self.bots[service_id] = body
            self.save_bots()

            return self.bots[service_id]
        except Exception as e:
            print(f"Failed to start container: {e}")
            return {}
       

    def get_bot_list(self):
        # bot_list = []
        # for container_id,value in self.bots.items():
        #     try:
        #         container = self.client.containers.get(container_id)  # 使用完整容器 ID
                
        #         status = container.status
        #     except docker.errors.NotFound:
        #         status = "not found"
          
        #     bot_list.append({
        #         "id": container_id,
        #         "service_id":value['service_id'],
        #         "name": value['name'],
        #         "status": status,
        #         "config":value['config']
        #     })
        # return bot_list
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
            since_time = (datetime.now() - timedelta(hours=1)).timestamp()
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

    def delete_bot(self, service_id):
        if service_id in self.bots:
            # bot_info = self.bots[service_id]

            # 删除配置文件和目录
            config_dir = os.path.join(get_config_dir(), service_id)
            if os.path.exists(config_dir):
                for root, dirs, files in os.walk(config_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(config_dir)
                print(f"Config directory {config_dir} removed successfully.")

            # 从 bots.json 中删除记录
            del self.bots[service_id]
            self.save_bots()
            print(f"Bot {service_id} deleted successfully.")
            return True
        else:
            print(f"Bot with service_id {service_id} not found.")
            return False
        
    # def get_bot_config(self,bot_id):
    #     # print(self.bots.get(bot_id, {}))
    #     return self.bots.get(bot_id, {})
    def get_bot_config(self, bot_id):
        """根据机器人 ID 从生成的 config.json 文件中获取其配置数据"""
        config_dir = os.path.join(get_config_dir(), bot_id)
        config_path = os.path.join(config_dir, 'config.json')
        
        if not os.path.exists(config_path):
            return {}

        with open(config_path, 'r', encoding='utf-8') as config_file:
            config_data = json.load(config_file)
        
        return config_data