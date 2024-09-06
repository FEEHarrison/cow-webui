import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'app.db')
    CONFIG_DIR = os.path.join(os.getcwd(), "botManager", "configs")
    TEMPLATE_DIR = os.path.join(os.getcwd(), "botManager", "templates")
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    JWT_EXPIRATION_HOURS = 24

    @staticmethod
    def ensure_dir(dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    @classmethod
    def get_config_dir(cls):
        return cls.ensure_dir(cls.CONFIG_DIR)

    @classmethod
    def get_template_dir(cls):
        return cls.TEMPLATE_DIR

    @classmethod
    def get_data_dir(cls):
        return os.path.dirname(cls.DB_PATH)

config = Config()