#!/bin/sh

# # 启动 Nginx
# nginx -g 'daemon off;' &

# 确保在backend目录下执行
# 确保在正确的目录下
cd /app/backend

# 创建日志目录
mkdir -p logs

# 设置日志文件路径
ACCESS_LOG="logs/access.log"
ERROR_LOG="logs/error.log"
# source venv/bin/activate

# 创建空的日志文件（如果不存在）
touch $ACCESS_LOG $ERROR_LOG
echo "日志文件创建/确认: $ACCESS_LOG, $ERROR_LOG"

# 设置环境变量
export SECRET_KEY="your_secret_key_here"
# export CORS_ORIGINS="http://localhost:5173"


# 替换 Nginx 配置中的环境变量
sed -i "s/\${BACKEND_PORT}/$BACKEND_PORT/g" /etc/nginx/nginx.conf

# 检查 Nginx 配置
echo "检查 Nginx 配置..."
nginx -t

if [ $? -ne 0 ]; then
    echo "Nginx 配置错误，请检查 nginx.conf 文件"
    exit 1
fi

# 启动 Gunicorn
echo "正在启动 Gunicorn..."
gunicorn --timeout 120 --log-level debug -w 4 -b 0.0.0.0:$BACKEND_PORT "app:create_app()" --daemon \
    --access-logfile $ACCESS_LOG --error-logfile $ERROR_LOG

# 检查 Gunicorn 是否成功启动
if [ $? -eq 0 ]; then
    echo "Gunicorn 已成功启动"
    echo "访问日志: $ACCESS_LOG"
    echo "错误日志: $ERROR_LOG"
else
    echo "Gunicorn 启动失败，请检查错误日志"
    cat $ERROR_LOG
    exit 1
fi

# 在 Docker 环境中运行，启动 Nginx
echo "在 Docker 环境中运行，启动 Nginx..."
nginx -g 'daemon off;' &


# 显示日志
echo "正在显示日志..."
tail -f $ACCESS_LOG $ERROR_LOG
