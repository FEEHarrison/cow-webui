# 使用 Python 官方镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 确保 start.sh 有执行权限
RUN chmod +x start.sh

# 使用 start.sh 脚本启动应用
CMD ["./start.sh"]

# 暴露后端服务端口
EXPOSE 5002
