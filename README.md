# 项目名称: cow-webui

## 项目简介

cow-webui 是一个基于 Flask 和 Vue.js 的 Web 应用程序,用于管理和控制 Docker 容器中运行的机器人。该项目提供了用户管理、机器人创建、配置和监控等功能。

## 项目结构

```
cow-webui/
│
├── backend/ # 后端 Flask 应用
│ ├── app.py # 主应用程序入口
│ ├── config.py # 配置文件
│ ├── utils.py # 工具函数
│ ├── docker_manager.py # Docker 管理相关脚本
│ ├── requirements.txt # Python 项目依赖文件
│ ├── userManager/ # 用户管理模块
│ │ └── user_routes.py # 用户相关路由
│ └── botManager/ # 机器人管理模块
│ ├── bot_routes.py # 机器人相关路由
│ ├── configs/ # 机器人配置文件夹
│ └── templates/ # 配置模板文件夹
│
├── frontend/ # 前端 Vue.js 应用
│ ├── index.html # 前端入口文件
│ ├── vite.config.js # Vite 配置文件
│ ├── package.json # 前端项目依赖文件
│ └── src/ # 前端源代码文件夹
│ ├── App.vue # Vue 主组件文件
│ ├── main.js # 前端入口 JavaScript 文件
│ ├── components/ # Vue 组件文件夹
│ ├── utils/ # 工具函数文件夹
│ └── hooks/ # 自定义 Hooks 文件夹
│
└── README.md # 项目说明文件
```

## 功能特性

- 用户注册、登录和身份验证
- 管理员用户设置和管理
- 创建、管理和监控 Docker 容器中的机器人
- 查看机器人日志
- 更新机器人配置

## 安装和运行

### 后端设置

1. 进入后端目录:
   ```bash
   cd backend
   ```

2. 创建虚拟环境并激活:
   ```bash
   python -m venv venv
   source venv/bin/activate  # 在 Windows 上使用 venv\Scripts\activate
   ```

3. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

4. 运行后端服务:
   ```bash
   python app.py
   ```

### 前端设置

1. 进入前端目录:
   ```bash
   cd frontend
   ```

2. 安装依赖:
   ```bash
   npm install
   ```

3. 运行开发服务器:
   ```bash
   npm run dev
   ```




### 服务器部署指引

#### 前端部署

1. 打包前端项目:
   ```bash
   cd frontend
   npm run build
   ```

2. 配置环境变量:
   ```bash
   touch .env.production
   echo "VITE_BASE_API=http://api-your-domain.com/" >> .env.production
   ```

3. 配置Nginx:
   将以下配置添加到Nginx的server块中:
   ```nginx
   location / {
       root /path/to/your/frontend/dist;
       try_files $uri $uri/ /index.html;
   }
   ```

#### 后端部署

1. 使用脚本启动项目（推荐）:
   ```bash
   chmod +x start.sh
   ./start.sh  # 启动服务

   tail -f access.log  # 查看运行日志
   tail -f error.log   # 查看错误日志

   chmod +x stop.sh 
   ./stop.sh  # 关闭服务
   ```

2. 直接启动Flask服务（不推荐）:
   ```bash
   nohup python3 app.py & tail -f nohup.out  # 启动服务
   ps -ef | grep app.py | grep -v grep       # 查看后台进程
   kill <进程id>                             # 关闭进程
   tail -f nohup.out                         # 查看日志
   ```

## 使用 Docker(后续支持)

项目提供了 Docker 支持，使用以下命令启动：

```bash
#进入项目根目录cow-webui
docker compose up -d
```

## QA
1.第一次启动项目可以稍等几分钟，需要等服务拉取容器镜像成功后才可以正常操作，相当于初始化过程。

2.如果本地启动后端服务报错，请检查本地环境是否安装了docker环境。

3.如果启动后端成功，但是第一次创建机器人失败，请检查是否是docker拉取镜像失败，可以使用我代理的docker镜像地址进行拉取，可以在docker操作界面配置镜像源。

4.进入项目默认管理员账号为admin

```bash
#为了加速镜像拉取,你可以使用以下命令设置registery mirror:
    sudo tee /etc/docker/daemon.json <<EOF
    {
        "registry-mirrors": ["https://cloudflare.casuallychat.cn"]
    }
    EOF
```

## 项目配置

配置文件位于 `templates/` 目录下，您可以根据需要编辑 `config.json` 和 `docker-compose.yml` 模版文件。

## 贡献

个人能力有限，如果您想为项目做出贡献，请 fork 本项目，创建您的分支，进行修改后提交 pull request，非常期待您的贡献。

## 交流群
![GitHub Sponsors](https://github.com/FEEHarrison/cow-webui/blob/main/sponsor/WechatIMG395.jpeg)

## 赞助我一杯咖啡 ☕️

如果你喜欢我的工作，可以通过wxpay来赞助我一杯咖啡。
![GitHub Sponsors](https://github.com/FEEHarrison/cow-webui/blob/main/sponsor/WechatIMG.jpeg)


