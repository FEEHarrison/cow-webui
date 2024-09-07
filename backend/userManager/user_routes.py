from flask import Flask,Blueprint, request, jsonify, session
from docker_manager import DockerManager
import jwt
from functools import wraps
from datetime import datetime, timedelta
from config import config
from utils import token_required, make_response

user_bp = Blueprint('user', __name__)
docker_manager = DockerManager()

@user_bp.route('/api/setup_admin', methods=['POST'])
def setup_admin():
    if docker_manager.is_admin_setup():
        return make_response(code=400, success=False, message="管理员已经设置")
    
    data = request.json
    password = data.get('password')
    
    if not password or not isinstance(password, str):
        return make_response(code=400, success=False, message="请提供有效的密码")
    
    try:
        admin_info = docker_manager.setup_admin(password)
        return make_response(data=admin_info, message="管理员设置成功")
    except ValueError as e:
        return make_response(code=400, success=False, message=str(e))
    except Exception as e:
        return make_response(code=500, success=False, message=f"设置管理员失败: {str(e)}")

@user_bp.route('/api/check_admin_setup', methods=['GET'])
def check_admin_setup():
    is_setup = docker_manager.is_admin_setup()
    return make_response(data={"is_setup": is_setup})

# 修改注册路由，确保所有新用户都是普通用户
@user_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return make_response(code=400, success=False, message="用户名和密码不能为空")
    
    try:
        # 明确指定角色为 'user'
        user_id = docker_manager.create_user(username, password, role='user', max_bots=5)
        return make_response(data={"id": user_id}, message="注册成功")
    except ValueError as e:
        return make_response(code=400, success=False, message=str(e))
    except Exception as e:
        return make_response(code=500, success=False, message="注册失败")

@user_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = docker_manager.authenticate_user(username, password)
    if user:
        token = jwt.encode({
            'id': user['id'],
            'role': user['role'],
            'exp': datetime.now() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
        }, config.SECRET_KEY, algorithm="HS256")
        return make_response(data={"token": token, "user": user})
    else:
        return make_response(code=401, success=False, message="Invalid username or password")
    
@user_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return make_response(message="登出成功")

@user_bp.route('/api/users', methods=['GET'])
@token_required
def get_users(current_user):
    if current_user['role'] != 'root':
        return make_response(code=403, success=False, message="无权限访问")
    users = docker_manager.get_all_users()
    return make_response(data=users)

@user_bp.route('/api/delete_user/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    if current_user['role'] != 'root':
        return make_response(code=403, success=False, message="无权限访问")
    success = docker_manager.delete_user(user_id)
    if success:
        return make_response(message="用户删除成功")
    else:
        return make_response(code=404, success=False, message="用户未找到")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return make_response(code=401, success=False, message="未提供认证令牌")
        try:
            payload = jwt.decode(token.split()[1], config.SECRET_KEY, algorithms=["HS256"])
            if payload['role'] != 'root':
                return make_response(code=403, success=False, message="需要管理员权限")
        except jwt.ExpiredSignatureError:
            return make_response(code=401, success=False, message="认证令牌已过期")
        except jwt.InvalidTokenError:
            return make_response(code=401, success=False, message="无效的认证令牌")
        return f(*args, **kwargs)
    return decorated_function
   
@user_bp.route('/api/clear_user_data', methods=['POST'])
# @admin_required
def clear_user_data():
    try:
        docker_manager.clear_user_data()
        return make_response(message="用户数据已清空")
    except Exception as e:
        return make_response(code=500, success=False, message=str(e))
    


@user_bp.route('/api/check_login', methods=['GET'])
def check_login():
    token = request.headers.get('Authorization')
    if not token:
        return make_response(success=False, message="用户未登录")
    try:
        token = token.split()[1]
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        return make_response(success=True, message="用户已登录", data={"user_id": payload['id']})
    except jwt.ExpiredSignatureError:
        return make_response(success=False, message="登录已过期")
    except jwt.InvalidTokenError:
        return make_response(success=False, message="无效的令牌")