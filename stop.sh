#!/bin/bash
# 查找并杀死Python服务的进程
pkill -f "gunicorn -w 4 -b 0.0.0.0:5002 app:app"
echo "Python服务已关闭"