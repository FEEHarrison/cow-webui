import os

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def get_config_dir():
    return ensure_dir(os.path.join(os.getcwd(), "configs"))

def get_template_dir():
    return os.path.join(os.getcwd(), "templates")

def get_data_dir():
    return ensure_dir(os.path.join(os.getcwd(), "data"))