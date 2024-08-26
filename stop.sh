#!/bin/bash
# 查找并杀死Python服务的进程

# 定义要结束的进程关键字
process_keyword="gunicorn -w 4 -b 0.0.0.0:5002 app:app"

# 使用 pgrep 找到符合条件的进程 ID
pids=$(pgrep -f "$process_keyword")

if [ -z "$pids" ]; then
    echo "未找到符合条件的进程"
else
    # 循环终止每个进程
    for pid in $pids; do
        echo "终止进程 $pid"
        kill $pid
    done
fi