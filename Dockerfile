# 阶段 1: 构建前端
FROM node:18 as frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# 阶段 2: 构建后端并运行应用
FROM python:3.9-slim

# 安装 Node.js（用于运行前端构建）
RUN apt-get update && apt-get install -y nodejs npm

# 设置工作目录
WORKDIR /app

# 复制后端代码
COPY backend/ /app/backend/

# 复制前端构建结果
COPY --from=frontend-build /frontend/dist /app/frontend/dist

# 安装后端依赖
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 安装 gunicorn
RUN pip install gunicorn

# 设置环境变量
ENV SECRET_KEY=your_secret_key_here
ENV CORS_ORIGINS=http://localhost:5173

# 暴露端口
EXPOSE 5002

# 创建启动脚本
RUN echo '#!/bin/bash\n\
cd /app/backend\n\
gunicorn --bind 0.0.0.0:5002 app:create_app() &\n\
cd /app/frontend\n\
npm install -g serve\n\
serve -s dist -l 5173' > /app/start.sh

RUN chmod +x /app/start.sh

# 运行应用
CMD ["/app/start.sh"]