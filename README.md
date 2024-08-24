My-Cow 项目

项目简介
My-Cow 是一个开源的智能聊天机器人项目，基于 OpenAI 的 GPT 系列模型，允许用户通过 Web 界面配置和管理多个聊天机器人。项目支持通过 Docker 进行容器化部署，以便于跨平台的运行和管理。

项目的设计初衷是提供一个灵活且可扩展的平台，用户可以根据需要定制机器人的行为和配置，并通过简单的 Web 操作界面进行管理。

功能特性
支持 GPT-3.5 和 GPT-4o 模型
自定义配置文件，通过 Web UI 进行配置和管理
热重载支持，无需重启即可应用部分配置变更
Docker 容器化部署，确保跨平台兼容性和易用性
使用 LinkAI、OpenAI API 实现多种对话和生成功能
前端使用 Vite 和 Vue 3 构建，提供快速响应的用户界面
部署方式
环境要求
Docker 及 Docker Compose
Python 3.8 及以上版本
Node.js 14 及以上版本
克隆项目
bash
复制代码
git clone https://github.com/yourusername/my-cow.git
cd my-cow
安装依赖
后端
在项目根目录下执行以下命令安装 Python 依赖：

bash
复制代码
pip install -r requirements.txt
前端
进入前端项目目录 cow-webui-vite 并安装依赖：

bash
复制代码
cd cow-webui-vite
npm install
构建与启动
通过 Docker 部署
使用 Docker Compose 进行构建和启动：

bash
复制代码
docker-compose up --build -d
手动部署
如需手动部署：

启动后端服务：

bash
复制代码
python app.py
启动前端服务：

bash
复制代码
cd cow-webui-vite
npm run dev
前端服务启动后，默认将运行在 http://localhost:3000。

使用指南
打开浏览器，访问 http://localhost:3000。
在 Web 界面中，您可以创建和管理多个聊天机器人。为每个机器人配置不同的参数，包括模型、API 密钥、代理设置等。
点击“保存配置”按钮，系统会根据输入的配置生成新的配置文件和 Docker Compose 文件。
如需应用新的配置，请点击“重启”按钮以重启相应的容器，确保新的配置生效。
注意事项
容器管理：每次更新配置后，系统会生成新的 Docker Compose 文件并使用它启动容器，容器的名称和服务 ID 会保持不变，但容器 ID 可能会变化。
数据持久性：请确保重要数据通过 Docker 卷进行持久化，以避免数据在容器重启或更新后丢失。
API Key 安全性：请妥善保管 API Key，并在 Web UI 中进行加密保存，避免泄露。
常见问题
容器 ID 变化
Docker 在重新启动容器时可能会生成新的容器 ID。如果需要保持容器的状态和数据，请确保将数据存储在 Docker 卷中。

配置更新后未生效
更新配置后需要手动点击“重启”按钮以应用新的配置。如果问题仍未解决，请检查日志文件获取更多信息。

更新日志
v1.0.0
初始发布版本
支持 GPT-3.5 和 GPT-4o 模型
配置管理功能和热重载支持
v1.1.0
增加对 LinkAI 的支持
优化 Docker Compose 文件的生成和管理
改进了 Web UI 的用户体验
v1.2.0
修复了配置更新时容器 ID 变化导致的问题
增加了配置文件的自动备份功能
提高了前端界面的加载速度和响应时间
项目趋势
短期目标：增强对更多模型和 API 的支持，优化配置管理和热重载功能。
中期目标：通过社区贡献和反馈，扩展项目的功能和应用场景，支持更多的第三方服务集成。
长期目标：建立一个强大且灵活的智能聊天机器人平台，支持从个人到企业级的多种应用需求。
贡献指南
欢迎所有形式的贡献！请查看 CONTRIBUTING.md 以了解如何贡献代码、报告问题或提出新功能建议。

许可证
该项目基于 MIT License 许可证开源。
