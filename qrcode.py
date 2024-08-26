import requests
import io
import os
import re
import uuid
from pyqrcode import QRCode

def get_wechat_uuid():
    """从微信服务器获取登录UUID"""
    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new',
        'redirect_uri': 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?mod=desktop',
        'lang': 'zh_CN'
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, params=params, headers=headers)
    
    # 使用正则表达式提取uuid
    match = re.search(r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";', response.text)
    if match and match.group(1) == '200':
        uuid = match.group(2)
        return uuid
    else:
        raise Exception("无法从微信服务器获取UUID")
def generate_qr_code():
    """使用UUID生成微信登录二维码"""
    uuid = get_wechat_uuid()
    qr_url = f'https://login.weixin.qq.com/l/{uuid}'
    qr_code = QRCode(qr_url)
    qr_storage = io.BytesIO()
    qr_code.png(qr_storage, scale=10)
    qr_storage.seek(0)
    return qr_storage

def save_qr_code(filename=None):
    """将二维码保存到 static/qrcodes 文件夹"""
    # 确保 static/qrcodes 文件夹存在
    qr_folder = os.path.join(os.getcwd(), 'static/qrcodes')
    if not os.path.exists(qr_folder):
        os.makedirs(qr_folder)
    uuid_str = str(uuid.uuid4())
    # 默认文件名为 uuid.png
    if filename is None:
        filename = f'{uuid_str}.png'
    
    # 构建完整的文件路径
    file_path = os.path.join(qr_folder, filename)
    
    # 生成二维码并保存到文件
    qr_storage = generate_qr_code()
    with open(file_path, 'wb') as f:
        f.write(qr_storage.getvalue())
    
    print(f"二维码已保存到: {file_path}")
    return file_path
