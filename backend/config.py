import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DB_PATH = os.path.join(BASE_DIR, 'data', 'app.db')
    CONFIG_DIR = os.path.join(BASE_DIR, "botManager", "configs")
    TEMPLATE_DIR = os.path.join(BASE_DIR, "botManager", "templates")
    # CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:8081').split(',')
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