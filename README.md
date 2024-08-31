# 项目名称: my-cow

## 项目结构

```
my-cow/
│
├── app.py                         # 主应用程序入口
├── config.py                      # 配置文件
├── docker_manager.py              # Docker 管理相关脚本
├── requirements.txt               # Python 项目依赖文件
├── package-lock.json              # npm 锁定文件
├── cow-webui-vite/                # 前端项目文件夹
│   ├── index.html                 # 前端入口文件
│   ├── vite.config.js             # Vite 配置文件
│   ├── package.json               # 前端项目依赖文件
│   ├── public/                    # 静态资源文件夹
│   ├── src/                       # 前端源代码文件夹
│   │   ├── App.vue                # Vue 主组件文件
│   │   ├── main.js                # 前端入口 JavaScript 文件
│   │   ├── components/            # Vue 组件文件夹
│   │   │   ├── HelloWorld.vue     # 示例组件
│   │   │   ├── Dialog.vue         # 弹窗组件
│   │   ├── utils/                 # 工具函数文件夹
│   │   │   ├── request.js         # 请求处理工具
│   │   ├── hooks/                 # 自定义 Hooks 文件夹
│   │   │   ├── useLoading.js      # 加载状态 Hook
│   ├── .vscode/                   # VSCode 配置文件夹
│   │   ├── extensions.json        # 推荐的 VSCode 扩展
│   ├── README.md                  # 前端项目 README 文件
├── configs/                       # 项目配置文件夹
│   ├── 9b1df1ee/                  # 配置文件集
│   │   ├── config.json            # 配置 JSON 文件
│   │   ├── docker-compose.yml     # Docker Compose 配置文件
├── templates/                     # 模板文件夹
│   ├── docker-compose.template.yml # Docker Compose 模板
│   ├── config-template.json       # 配置模板文件
├── data/                          # 数据文件夹
│   ├── bots.json                  # 机器人配置 JSON 文件
├── static/                        # 静态资源文件夹
│   ├── qrcodes/                   # 存储二维码图像
└── __pycache__/                   # Python 缓存文件夹
```

## 依赖安装

### 后端依赖

请确保已安装 Python 3.8 或更高版本。使用以下命令安装 Python 依赖项：

```bash
pip install -r requirements.txt
```

### 前端依赖

请确保已安装 Node.js 及 npm。使用以下命令安装前端依赖项：

```bash
cd cow-webui-vite
npm install
```

## 启动应用程序

### 本地启动后端

```bash
python app.py
```
### 本地启动前端

```bash
cd cow-webui-vite
npm run dev
#配置.env.devlopment
```

### 服务器启动后端

```bash
方式1 （推荐）
chmod +x start.sh
./start.sh //启动服务

tail -f access.log //查看运行日志
tail -f error.log //查看错误日志

chmod +x stop.sh 
./stop.sh //关闭服务


方式2 （flask后端服务，启动不稳定，不推荐）
nohup python3 app.py & tail -f nohup.out //启动服务
ps -ef | grep app.py | grep -v grep //命令可查看运行于后台的进程
kill 进程id //关闭进程
tail -f nohup.out //查看日志

```

### 服务器启动前端
#### 打包
```bash
cd cow-webui-vite
npm run build

touch .env.production //前端目录创建配置文件并配置.env.production，如下
VITE_BASE_API=http://your-domain.com/
```
#### 将dist文件部署到服务器使用nginx代理
```bash
#nginx vue
location / {
    root /your-path/cow-webui/cow-webui-vite/dist;
    try_files $uri $uri/ /index.html;
}
```


## 使用 Docker(后续支持)

项目提供了 Docker 支持，使用以下命令启动：

```bash
注意本项目是使用接口操作docker实现的，所以服务器需要先安装docker
```

## QA
1.第一次启动项目可以稍等几分钟，需要等服务拉取容器镜像成功后才可以正常操作，相当于初始化过程。

## 项目配置

配置文件位于 `templates/` 目录下，您可以根据需要编辑 `config.json` 和 `docker-compose.yml` 模版文件。

## 贡献

个人能力有限，如果您想为项目做出贡献，请 fork 本项目，创建您的分支，进行修改后提交 pull request，非常期待您的贡献。


## 赞助我一杯咖啡 ☕️

如果你喜欢我的工作，可以通过wxpay来赞助我一杯咖啡。
![GitHub Sponsors](https://github.com/FEEHarrison/cow-webui/blob/main/sponsor/WechatIMG386.jpeg)


