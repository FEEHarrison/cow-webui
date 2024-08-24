import os

def get_config_dir():
    config_dir = os.path.join(os.getcwd(), "configs")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return config_dir

def get_template_dir():
    return os.path.join(os.getcwd(), "templates")

def get_data_dir():
    data_dir = os.path.join(os.getcwd(), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir
