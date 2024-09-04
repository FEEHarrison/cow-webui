from flask import Flask,Blueprint, request, jsonify, session
from docker_manager import DockerManager
from utils import make_response
import jwt
from functools import wraps
from datetime import datetime, timedelta
user_bp = Blueprint('user', __name__)
docker_manager = DockerManager()
SECRET_KEY = 'your_secret_key'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return make_response(code=401, success=False, message="缺少令牌")
        try:
            data = jwt.decode(token.split()[1], SECRET_KEY, algorithms=["HS256"])
            current_user = {'id': data['id'], 'role': data['role']}
        except:
            return make_response(code=401, success=False, message="无效或过期的令牌")
        return f(current_user, *args, **kwargs)
    return decorated

@user_bp.route('/setup_admin', methods=['POST'])
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

@user_bp.route('/check_admin_setup', methods=['GET'])
def check_admin_setup():
    is_setup = docker_manager.is_admin_setup()
    return make_response(data={"is_setup": is_setup})

# 修改注册路由，确保所有新用户都是普通用户
@user_bp.route('/register', methods=['POST'])
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

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = docker_manager.authenticate_user(username, password)
    if user:
        token = jwt.encode({
            'id': user['id'],
            'role': user['role'],
            'exp': datetime.now() + timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        return make_response(data={"token": token, "role": user['role'], "username": username}, message="登录成功")
    else:
        return make_response(code=401, success=False, message="用户名或密码错误")

@user_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return make_response(message="登出成功")

@user_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    if current_user['role'] != 'root':
        return make_response(code=403, success=False, message="无权限访问")
    users = docker_manager.get_all_users()
    return make_response(data=users)

@user_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
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
            payload = jwt.decode(token.split()[1], SECRET_KEY, algorithms=["HS256"])
            if payload['role'] != 'root':
                return make_response(code=403, success=False, message="需要管理员权限")
        except jwt.ExpiredSignatureError:
            return make_response(code=401, success=False, message="认证令牌已过期")
        except jwt.InvalidTokenError:
            return make_response(code=401, success=False, message="无效的认证令牌")
        return f(*args, **kwargs)
    return decorated_function
   
@user_bp.route('/clear_user_data', methods=['POST'])
# @admin_required
def clear_user_data():
    try:
        docker_manager.clear_user_data()
        return make_response(message="用户数据已清空")
    except Exception as e:
        return make_response(code=500, success=False, message=str(e))
    


@user_bp.route('/check_login', methods=['GET'])
def check_login():
    token = request.headers.get('Authorization')
    if not token:
        return make_response(success=False, message="用户未登录")
    try:
        # 假设令牌格式为 "Bearer <token>"
        token = token.split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return make_response(success=True, message="用户已登录", data={"user_id": payload['id']})
    except jwt.ExpiredSignatureError:
        return make_response(success=False, message="登录已过期")
    except jwt.InvalidTokenError:
        return make_response(success=False, message="无效的令牌")