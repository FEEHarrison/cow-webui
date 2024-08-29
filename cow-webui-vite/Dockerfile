# 使用 Node.js 官方镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制应用代码
COPY . .

# 构建前端项目
RUN npm run build

# 使用 serve 作为前端静态文件服务器
RUN npm install -g serve
CMD ["serve", "-s", "dist"]

# 暴露前端应用运行端口
EXPOSE 3000
