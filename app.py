from flask import Flask, request, jsonify
from docker_manager import DockerManager
# import os
from flask_cors import CORS  # 添加 CORS 支持

def make_response(code=200, success=True, data=None, message="操作成功"):
    """统一的响应格式"""
    return jsonify({
        "code": code,
        "success": success,
        "data": data,
        "message": message
    })

app = Flask(__name__)
CORS(app)  # 启用 CORS
# Disable caching for streamed responses
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

docker_manager = DockerManager()


@app.route('/api/create_bot', methods=['POST'])
def create_bot():
    config_data = request.json
    data = docker_manager.start_docker_container(config_data)
    return make_response(data=data)

@app.route('/api/bots', methods=['GET'])
def get_bots():
    bot_list = docker_manager.get_bot_list()
    return make_response(data=bot_list)

@app.route('/api/logs/<container_id>', methods=['GET'])
def get_container_logs(container_id):
    data=docker_manager.get_container_logs(container_id)
    return data
   

@app.route('/api/delete_bot/<container_id>', methods=['DELETE'])
def delete_bot(container_id):
    success = docker_manager.manage_container(container_id,'remove')
    if success:
        return make_response(data={"status": "success"})
    else:
        return make_response(data={"status": "bot not found"},message="bot not found",code=404)
    
@app.route('/api/restart_bot/<container_id>', methods=['POST'])
def restart_bot(container_id):
    """重启指定ID的机器人容器"""
    status = docker_manager.manage_container(container_id, 'restart')
    return make_response(data={"status": status})

@app.route('/api/save_bot_config/<bot_id>', methods=['POST'])
def save_bot_config(bot_id):
    new_config = request.json
    try:
        # 复用通用配置处理逻辑
        docker_manager.process_config_and_generate_compose(bot_id, new_config)
        return make_response(message="配置部分更新并生成新的 Compose 文件成功")
    except Exception as e:
        return make_response(code=500, success=False, message=str(e))

@app.route('/api/get_bot_config/<bot_id>', methods=['GET'])
def get_bot_config(bot_id):
    try:
        config = docker_manager.get_bot_config(bot_id)
        if config:
            return make_response(data=config, message="获取配置成功")
        else:
            return make_response(code=404, success=False, message="配置未找到")
    except Exception as e:
        return make_response(code=500, success=False, message=str(e))    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
