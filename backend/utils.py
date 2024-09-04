from flask import jsonify,request
from functools import wraps
import jwt
SECRET_KEY = 'your_secret_key'

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