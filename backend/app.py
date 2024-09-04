from flask import Flask, request, jsonify,g
# from docker_manager import DockerManager
from flask_cors import CORS  # 添加 CORS 支持
from userManager.user_routes import user_bp  # 导入 user_bp
from botManager.bot_routes import bot_bp  # 导入 bot_bp
import sys
import os
from config import get_data_dir
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app,supports_credentials=True,resources={r"/api/*": {"origins": "http://127.0.0.1:5173"}})  # 启用 CORS


# 创建全局数据库连接
db_path = os.path.join(get_data_dir(), 'app.db')
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


app.register_blueprint(user_bp, url_prefix='/api')  # 注册 user_bp 蓝图

# 注册机器人路由蓝图
app.register_blueprint(bot_bp)  


@app.errorhandler(404)
def not_found_error(error):
    app.logger.error('404 error: %s', request.url)
    return jsonify(error="Not found"), 404

if __name__ == '__main__':
    db_path = os.path.join(get_data_dir(), 'app.db')
    app.run(host='0.0.0.0', port=5002)
