
# 🚀 HiAgent Plugin Runtime

一个高性能的AI Agent插件运行时平台，支持插件动态加载、异步执行和分布式部署。

## ✨ 特性

- 🔌 **插件化架构**: 支持动态安装、卸载和版本管理
- ⚡ **高性能执行**: 异步任务处理和流式输出
- 🔄 **Redis队列**: 支持大规模并发插件执行  
- 🐳 **Docker部署**: 开箱即用的容器化部署
- 🌐 **RESTful API**: 完整的插件管理和执行API
- 📊 **健康监控**: 内置健康检查和状态监控
- 🔒 **企业级**: 完善的错误处理和日志记录

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │    │   Web Client    │    │   API Client    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │      FastAPI Server        │
                    │   (Plugin Runtime API)     │
                    └─────────────┬──────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
    ┌───────────▼────────┐ ┌──────▼──────┐ ┌───────▼────────┐
    │  Package Manager   │ │   Runtime   │ │  Redis Queue   │
    │   (Install/Delete) │ │   Engine    │ │   (Async)      │
    └────────────────────┘ └─────────────┘ └────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │       Plugin Ecosystem     │
                    │  Bing • 飞书 • GitHub •   │
                    │  Time • Math • Weather     │
                    └────────────────────────────┘
```

## 🚀 快速开始

### 方式一: 一键安装 (推荐)

```bash
curl -fsSL https://raw.githubusercontent.com/Beginner-Village/plugin/main/deploy/install.sh | bash
```

### 方式二: 手动部署

1. **克隆项目**
```bash
git clone https://github.com/Beginner-Village/plugin.git
cd plugin
```

2. **启动服务**
```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

3. **验证部署**
```bash
curl http://localhost:8000/ping
# 返回: {"message":"pong"}
```

## 📝 API 使用

### 安装插件

```bash
curl -X POST "http://localhost:8000/v1/InstallPackage" \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "file:///path/to/plugin.whl",
    "filename": "plugin.whl",
    "force": true
  }'
```

### 调用插件工具

```bash
curl -X POST "http://localhost:8000/v1/RunPluginTool" \
  -H "Content-Type: application/json" \
  -d '{
    "pkg": "hiagent-plugin-time",
    "version": "0.2.0",
    "plugin": "时间工具", 
    "tool": "current_time",
    "input": {
      "timezone": "Asia/Shanghai"
    }
  }'
```

响应:
```json
{
  "data": "2025-08-14 18:43:59 CST",
  "error": null
}
```

## 🐳 Docker 部署

### 生产环境部署

```bash
# 构建并启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 🛠️ 本地开发

### 环境准备

```bash
# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -e ./hiagent-plugin-sdk
```

### 启动服务

```bash
# 启动Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 启动API服务
CONFIG=config.yaml python main.py

# 启动Worker (新终端)
CONFIG=config.yaml python worker.py
```

## 🔌 插件生态

目前支持的插件类型:

- **工具类**: 时间、数学、正则表达式
- **搜索类**: Bing、DuckDuckGo、Wikipedia  
- **办公类**: 飞书、钉钉、企业微信
- **开发类**: GitHub、GitLab、Jira

## 📊 监控与运维

### 健康检查

- API健康: `GET /ping`
- API文档: `GET /docs`

### 服务管理

```bash
# 查看服务状态
./deploy/deploy.sh status

# 重启服务
./deploy/deploy.sh restart

# 查看日志
./deploy/deploy.sh logs
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request!

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 📄 许可证

本项目采用 MIT License 许可证。

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！

📧 问题反馈: [Issues](https://github.com/Beginner-Village/plugin/issues)
# plugin
