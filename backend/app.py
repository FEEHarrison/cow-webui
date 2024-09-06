from flask import Flask
from flask_cors import CORS
from userManager.user_routes import user_bp
from botManager.bot_routes import bot_bp
from config import config
from docker_manager import DockerManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})

    docker_manager = DockerManager()
    app.config['docker_manager'] = docker_manager

    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(bot_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002)