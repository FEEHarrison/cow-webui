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
- 管理员用户设置和管理、限制用户创建机器人个数
- 创建、重启、管理和监控 Docker 容器中的机器人
- 查看机器人日志、微信二维码
- 更新机器人配置

## demo

### UI展示
![GitHub Sponsors](https://github.com/FEEHarrison/cow-webui/blob/main/sponsor/demo-ui.jpg)
![GitHub Sponsors](https://github.com/FEEHarrison/cow-webui/blob/main/sponsor/demo-config.jpg)

### demo地址
[demo](https://bot.aigcboundless.cn)
管理员账号为admin，默认密码1234

## 环境
前端需要node环境，后端python环境和docker环境
## 本地部署
```bash
cd frontend
npm run dev

cd backend
python3 -m venv venv //创建虚拟环境
source venv/bin/activate //进入虚拟环境
pip install -r requirements.txt //拉取依赖

docker pull zhayujie/chatgpt-on-wechat //拉取镜像依赖，拉取成功才可以正常创建机器人
python app.py //启动项目

```


## 使用 Docker 线上部署

项目提供了 Docker 支持，使用以下命令启动：

```bash
#进入项目根目录cow-webui
docker compose up -d
```

## QA
1.第一次启动项目可以稍等几分钟，需要等服务拉取容器镜像成功后才可以正常操作，相当于初始化过程。

2.如果本地启动后端服务报错，请检查本地环境是否安装了docker环境。

3.如果启动后端成功，但是第一次创建机器人失败，请检查是否是docker拉取镜像失败，可以使用我代理的docker镜像地址进行拉取，可以在docker操作界面配置镜像源。

4.进入项目默认提示管理员密码已设置直接进入到登录页，如果想自己重设密码：可以进入/backend/data 删除app.db数据库重新启动即可

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
![GitHub Sponsors](https://github.com/FEEHarrison/cow-webui/blob/main/sponsor/WechatIMG404.jpeg)

## 赞助我一杯咖啡 ☕️

如果你喜欢我的工作，可以通过wxpay来赞助我一杯咖啡。
![GitHub Sponsors](https://github.com/FEEHarrison/cow-webui/blob/main/sponsor/WechatIMG.jpeg)


