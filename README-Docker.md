# 🚀 HiAgent Plugin Runtime Docker 部署指南

基于 [HiAgent Plugin Runtime 完整使用指南](./HiAgent_Plugin_Runtime_Guide.md) 的 Docker 化部署方案。

## 🏗️ 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Service   │    │  Worker Service │    │   Redis Queue   │
│  (FastAPI)      │    │  (Background)   │    │   (Cache)       │
│  Port: 8000     │    │                 │    │   Port: 6379    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Shared Storage │
                    │  (Extensions)   │
                    └─────────────────┘
```

## 🎯 特性

- **单一镜像**: 一个 Dockerfile 构建完整的插件运行时环境
- **服务分离**: 通过环境变量控制启动 API 或 Worker 服务
- **数据持久化**: Redis 数据和插件存储持久化
- **健康检查**: 完整的健康检查和监控
- **日志管理**: 结构化日志记录和轮转
- **易于管理**: 提供 Makefile 简化操作

## 🚀 快速启动

### 1. 一键启动所有服务

```bash
# 构建并启动所有服务
make up

# 或者手动启动
docker-compose up -d --build
```

### 2. 验证服务状态

```bash
# 查看服务状态
make status

# 测试连通性
make test
```

### 3. 访问服务

- **API 文档**: http://localhost:8000/docs
- **API 健康检查**: http://localhost:8000/ping
- **Redis**: localhost:6379

## 📊 服务管理

### 基本操作

```bash
# 查看帮助
make help

# 启动服务
make up

# 停止服务
make down

# 重启服务
make restart

# 清理资源
make clean
```

### 日志查看

```bash
# 查看所有日志
make logs

# 查看特定服务日志
make logs-api
make logs-worker
make logs-redis
```

### 进入容器

```bash
# 进入 API 容器
make shell-api

# 进入 Worker 容器
make shell-worker

# 进入 Redis CLI
make shell-redis
```

## 🔧 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `SERVICE_TYPE` | `api` | 服务类型：`api` 或 `worker` |
| `CONFIG` | `/app/config.yaml` | 配置文件路径 |
| `REDIS_HOST` | `redis` | Redis 主机名 |
| `REDIS_PORT` | `6379` | Redis 端口 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

### 目录挂载

| 容器路径 | 宿主机路径 | 说明 |
|----------|------------|------|
| `/app/extensions` | `./extensions` | 插件安装目录 |
| `/tmp/hiagent_storage` | `plugin_storage` | 插件存储 |
| `/app/config.yaml` | `./config.yaml` | 配置文件 |
| `/app/logs` | `./logs` | 日志目录 |

## 📦 插件管理

### 安装插件示例

```bash
# 使用 Makefile 安装示例插件
make install-plugin

# 手动安装插件
curl -X POST "http://localhost:8000/v1/InstallPackage" \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "file:///app/extensions/hiagent-plugin-time/0.2.0/hiagent_plugin_time-0.2.0-py3-none-any.whl",
    "filename": "hiagent_plugin_time-0.2.0-py3-none-any.whl",
    "force": true
  }'
```

### 使用插件

```bash
# 调用时间工具插件
curl -X POST "http://localhost:8000/v1/RunPluginTool" \
  -H "Content-Type: application/json" \
  -d '{
    "pkg": "hiagent_plugin_time",
    "version": "0.2.0",
    "plugin": "时间工具",
    "tool": "get_current_time",
    "input": {}
  }'
```

## 🏥 监控和健康检查

### 健康检查端点

- **API**: `GET /ping`
- **Redis**: Redis PING 命令
- **Worker**: Redis 连接检查

### 监控命令

```bash
# 查看资源使用情况
make stats

# 查看服务状态
make status

# 连通性测试
make test-api
make test-redis
```

## 🔒 生产环境建议

### 安全配置

1. **网络隔离**: 生产环境建议不暴露 Redis 端口
2. **访问控制**: 配置 API 访问控制和认证
3. **日志管理**: 配置日志收集和监控
4. **资源限制**: 设置容器资源限制

### 性能优化

```yaml
# docker-compose.yml 中添加资源限制
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 🛠️ 故障排除

### 常见问题

1. **Redis 连接失败**
   ```bash
   # 检查 Redis 状态
   make test-redis
   
   # 查看 Redis 日志
   make logs-redis
   ```

2. **API 服务无响应**
   ```bash
   # 检查 API 健康状态
   make test-api
   
   # 查看 API 日志
   make logs-api
   ```

3. **插件安装失败**
   ```bash
   # 检查插件目录权限
   ls -la extensions/
   
   # 查看详细错误日志
   make logs-api
   ```

### 调试模式

```bash
# 开发模式启动（仅 API + Redis）
make dev

# 进入容器调试
make shell-api
python -c "from app.config import load; print(load())"
```

## 📋 维护操作

### 数据备份

```bash
# 备份数据
make backup

# 备份文件位置
ls backup/
```

### 更新部署

```bash
# 拉取最新代码后
make restart

# 强制重新构建
make clean
make up
```

## 🎯 总结

通过这个 Docker 化方案，您可以：

- ✅ 一键部署完整的 HiAgent Plugin Runtime 环境
- ✅ 轻松管理 API 和 Worker 服务
- ✅ 实现数据持久化和服务监控
- ✅ 支持插件的安装、管理和使用
- ✅ 提供完整的日志和健康检查机制

现在您可以直接运行 `make up` 开始使用 HiAgent Plugin Runtime！🚀