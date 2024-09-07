from flask import Flask,Blueprint, json, request
from docker_manager import DockerManager
from utils import make_response ,token_required
from flask_cors import cross_origin
from config import config

bot_bp = Blueprint('bot', __name__)
docker_manager = DockerManager()

@bot_bp.route('/create_bot', methods=['POST'])
@token_required
def create_bot(current_user):
    config_data = request.json
    print("接收到的配置数据:", config_data)
    print("当前用户:", current_user)

    try:
        user_id = current_user.get('id')
        if not user_id:
            return make_response(code=400, success=False, message="无法获取用户ID")

        data = docker_manager.start_docker_container(config_data, user_id)
        if "error" in data:
            return make_response(code=400, success=False, message=data["error"])
        return make_response(data=data)
    except Exception as e:
        print(f"创建机器人时出错: {str(e)}")
        return make_response(code=500, success=False, message=str(e))


@bot_bp.route('/bots', methods=['GET'])
@cross_origin(origins=config.CORS_ORIGINS, supports_credentials=True)
@token_required
def get_bots(current_user):
    if current_user['role'] == 'root':
        bot_list = docker_manager.get_bot_list()
    else:
        bot_list = docker_manager.get_bot_list(user_id=current_user['id'])
    return make_response(data=bot_list)

@bot_bp.route('/logs/<container_id>', methods=['GET'])
def get_container_logs(container_id):
    logs_data = docker_manager.get_container_logs(container_id)
    if logs_data is None:
        return make_response(code=404, success=False, message="未找到容器或获取日志失败")
    
    return make_response(data=logs_data)
   

@bot_bp.route('/delete_bot/<container_id>', methods=['DELETE'])
def delete_bot(container_id):
    success = docker_manager.manage_container(container_id,'remove')
    if success:
        return make_response(data={"status": "success"})
    else:
        return make_response(data={"status": "bot not found"},message="bot not found",code=404)
    
@bot_bp.route('/restart_bot/<container_id>', methods=['POST'])
def restart_bot(container_id):
    """重启指定ID的机器人容器"""
    status = docker_manager.manage_container(container_id, 'restart')
    return make_response(data={"status": status})

@bot_bp.route('/save_bot_config/<bot_id>', methods=['POST'])
def save_bot_config(bot_id):
    new_config = request.json
    try:
        # 更新配置
        data = docker_manager.save_config(bot_id, new_config)
        
        return make_response(data=data, message="配置更新成功")
    except Exception as e:
        return make_response(code=500, success=False, message=f"保存配置失败: {str(e)}")

@bot_bp.route('/get_bot_config/<bot_id>', methods=['GET'])
def get_bot_config(bot_id):
    try:
        config = docker_manager.get_bot_config(bot_id)
        if config:
            return make_response(data=config, message="获取配置成功")
        else:
            return make_response(code=404, success=False, message="配置未找到")
    except Exception as e:
        return make_response(code=500, success=False, message=str(e))