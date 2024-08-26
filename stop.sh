#!/bin/bash
# 查找并杀死Python服务的进程

# 定义要结束的进程关键字
pkill -f "gunicorn --timeout 120 --log-level debug -w 4 -b 0.0.0.0:5002 app:app"

# 检查是否成功终止进程
if [ $? -eq 0 ]; then
    echo "成功终止 gunicorn 进程"
else
    echo "未能终止 gunicorn 进程"
fi