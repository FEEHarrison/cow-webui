from flask import jsonify, request,current_app
from functools import wraps
import jwt
from config import config

def make_response(code=200, success=True, data=None, message="操作成功"):
    return jsonify({
        "code": code,
        "success": success,
        "data": data,
        "message": message
    })

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            print(f"Received Authorization header: {auth_header}")
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': '无效的 Authorization 头部'}), 401
        if not token:
            return jsonify({'message': '缺少令牌'}), 401
        try:
            print(f"Decoding token: {token}")
            data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
            print(f"Decoded token data: {data}")
            docker_manager = current_app.config['docker_manager']
            current_user = docker_manager.get_user_by_id(data['id'])
            if not current_user:
                return jsonify({'message': '用户不存在'}), 401
            current_user['role'] = data['role']  # 添加这行，确保角色信息可用
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '令牌已过期'}), 401
        except jwt.InvalidTokenError as e:
            print(f"Invalid token error: {str(e)}")
            return jsonify({'message': '无效的令牌'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

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