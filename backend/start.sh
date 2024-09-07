#!/bin/bash

# 确保在backend目录下执行
cd "$(dirname "$0")"


source venv/bin/activate

# 设置环境变量
export SECRET_KEY="your_secret_key_here"
export CORS_ORIGINS="http://localhost:5173"
# 打印当前工作目录
echo "当前工作目录: $(pwd)"

# 列出目录内容
echo "目录内容:"
ls -la

# 检查并创建日志目录
LOG_DIR="logs"
mkdir -p $LOG_DIR

# 设置日志文件路径
ACCESS_LOG="$LOG_DIR/access.log"
ERROR_LOG="$LOG_DIR/error.log"

# 启动 Gunicorn
echo "正在启动 Gunicorn..."
gunicorn --timeout 120 --log-level debug -w 4 -b 0.0.0.0:5002 app:app --daemon \
    --access-logfile $ACCESS_LOG --error-logfile $ERROR_LOG

# 检查 Gunicorn 是否成功启动
if [ $? -eq 0 ]; then
    echo "Gunicorn 已成功启动"
    echo "访问日志: $ACCESS_LOG"
    echo "错误日志: $ERROR_LOG"
    echo "正在显示日志..."
    tail -f $ACCESS_LOG $ERROR_LOG
else
    echo "Gunicorn 启动失败,请检查错误日志"
fi