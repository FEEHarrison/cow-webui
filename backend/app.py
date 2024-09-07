from flask import Flask
from flask_cors import CORS
from userManager.user_routes import user_bp
from botManager.bot_routes import bot_bp
from config import config
from docker_manager import DockerManager
import os

def check_environment():
    required_vars = ['SECRET_KEY', 'CORS_ORIGINS']
    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"缺少必要的环境变量: {var}")
        
def create_app():
    check_environment()
    app = Flask(__name__)
    app.config.from_object(config)
    
    CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Authorization", "Content-Type"], supports_credentials=True) 

    docker_manager = DockerManager()
    app.config['docker_manager'] = docker_manager

    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(bot_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002)