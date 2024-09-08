#!/bin/bash

# 确保在backend目录下执行
cd "$(dirname "$0")"
# 获取所有 Gunicorn 进程信息
ps_output=$(ps aux | grep gunicorn | grep -v grep)

# 打印进程信息
if [ -z "$ps_output" ]; then
  echo "No Gunicorn processes found."
else
  echo "Gunicorn 进程信息:"
  echo "$ps_output"
fi

# 获取所有 gunicorn 进程的 PID
PIDS=$(pgrep -f "gunicorn.*app:app")
sudo pkill gunicorn
if [ -z "$PIDS" ]; then
  echo "没有找到正在运行的 gunicorn 进程"
else
  echo "找到以下 gunicorn 进程："
  echo "$PIDS"
  
  # 尝试优雅地终止所有 gunicorn 进程
  echo "正在尝试优雅终止进程..."
  kill $PIDS
  
  # 等待进程终止
  sleep 5
  
  # 再次检查是否还有 gunicorn 进程
  REMAINING_PIDS=$(pgrep -f "gunicorn.*app:app")
  if [ ! -z "$REMAINING_PIDS" ]; then
    echo "部分进程未能在5秒内终止,正在强制终止..."
    kill -9 $REMAINING_PIDS
  fi
  
  echo "所有 gunicorn 进程已终止"
fi

# 显示日志文件大小
echo "当前日志文件大小:"
du -sh logs/*.log 2>/dev/null

# 询问是否要清理日志文件
read -p "是否要清理日志文件? (y/n) " answer
if [ "$answer" = "y" ]; then
  echo "正在清理日志文件..."
  rm -f logs/*.log
  echo "日志文件已清理"
else
  echo "日志文件保留"
fi

echo "停止脚本执行完毕"