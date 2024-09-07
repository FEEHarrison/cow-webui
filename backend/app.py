from flask import Flask
from flask_cors import CORS
from userManager.user_routes import user_bp
from botManager.bot_routes import bot_bp
from config import config
from docker_manager import DockerManager
import os
import logging

def check_environment():
    required_vars = ['SECRET_KEY', 'CORS_ORIGINS']
    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"缺少必要的环境变量: {var}")
        
def create_app():
    check_environment()
    app = Flask(__name__)
    app.config.from_object(config)
    app.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    # CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://frontend:5173", "http://localhost:8081"]}}, allow_headers=["Authorization", "Content-Type"], supports_credentials=True)
    CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Authorization", "Content-Type"], supports_credentials=True)

    docker_manager = DockerManager()
    app.config['docker_manager'] = docker_manager

    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(bot_bp, url_prefix='/api')
    print(app.url_map)  # 打印路由映射，帮助调试
    # 添加日志输出以确认 Flask 应用已启动
    app.logger.info("Flask application has started.")
    
    # 打印所有注册的路由，确保它们已加载
    app.logger.info(f"Registered routes: {app.url_map}")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002)