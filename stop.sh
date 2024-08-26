#!/bin/bash
# 获取所有 gunicorn 进程的 PID
PIDS=$(ps aux | grep '[g]unicorn' | awk '{print $2}')

if [ -z "$PIDS" ]; then
  echo "没有找到正在运行的 gunicorn 进程"
else
  echo "找到以下 gunicorn 进程："
  echo "$PIDS"
  
  # 终止所有 gunicorn 进程
  kill $PIDS
  
  if [ $? -eq 0 ]; then
    echo "成功终止 gunicorn 进程"
  else
    echo "终止 gunicorn 进程时发生错误"
  fi
fi
