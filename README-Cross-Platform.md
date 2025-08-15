# 🚀 ARM Mac 上构建 x86 镜像指南

本指南说明如何在 ARM Mac 上构建和运行 x86/amd64 架构的 HiAgent Plugin Runtime 镜像。

## 🎯 使用场景

- 需要在 x86 服务器上部署
- 确保与 x86 环境的兼容性
- 开发和测试跨平台部署
- 构建通用镜像

## 🔧 前置条件

### 1. 启用 Docker Buildx

Docker Buildx 是 Docker 的多平台构建工具，首次使用需要设置：

```bash
# 一键设置 Buildx (仅需运行一次)
make setup-buildx

# 或手动设置
docker buildx create --name multiarch --driver docker-container --use
docker buildx inspect --bootstrap
```

### 2. 验证 Buildx 状态

```bash
# 查看可用的构建器
docker buildx ls

# 查看支持的平台
docker buildx inspect --bootstrap
```

## 🔨 构建选项

### 1. 本地架构构建 (ARM)

```bash
# 构建本地 ARM 架构镜像
make build
```

### 2. x86 架构构建

```bash
# 构建 x86/amd64 架构镜像
make build-x86
```

这会创建名为 `hiagent-plugin-runtime:latest-amd64` 的镜像。

### 3. 多平台构建

```bash
# 构建同时支持 x86 和 ARM 的镜像
make build-multi
```

### 4. 构建并推送到仓库

```bash
# 构建多平台镜像并推送到 Docker Hub
make build-push
```

## 🚀 运行 x86 镜像

### 1. 启动 x86 服务

```bash
# 构建并启动 x86 架构的服务
make up-x86
```

这会使用 `docker-compose-x86.yml` 配置文件，其中：
- 所有容器强制使用 `linux/amd64` 平台
- Redis 端口映射到 `26379` 避免冲突
- 使用 `hiagent-plugin-runtime:latest-amd64` 镜像

### 2. 管理 x86 服务

```bash
# 查看 x86 服务状态
make status-x86

# 停止 x86 服务
make down-x86

# 重启 x86 服务
make restart-x86
```

## 📊 性能注意事项

### ARM Mac 运行 x86 镜像的影响

1. **性能开销**: ARM Mac 通过 Rosetta 2 模拟运行 x86，性能会有所下降
2. **内存使用**: 模拟层会增加内存使用
3. **启动时间**: x86 容器启动时间会更长

### 推荐使用场景

- **开发测试**: ✅ 适合开发和测试跨平台兼容性
- **生产部署**: ❌ 建议在目标架构上直接构建
- **CI/CD**: ✅ 适合在 CI/CD 中构建多平台镜像

## 🔄 最佳实践

### 1. 开发流程

```bash
# 1. 本地开发使用 ARM 镜像 (快速)
make dev

# 2. 测试 x86 兼容性
make build-x86
make up-x86

# 3. 生产部署前构建多平台镜像
make build-multi
```

### 2. CI/CD 集成

```bash
# 在 CI/CD 中构建并推送多平台镜像
make setup-buildx
make build-push
```

### 3. 架构选择策略

| 场景 | 推荐架构 | 命令 |
|------|----------|------|
| 本地开发 | ARM (原生) | `make build && make up` |
| 兼容性测试 | x86 | `make build-x86 && make up-x86` |
| 生产部署 | 目标架构 | `make build-multi` |

## 🐛 故障排除

### 1. Buildx 未安装

**错误**: `docker: 'buildx' is not a docker command`

**解决**:
```bash
# 更新 Docker Desktop 到最新版本
# 或手动启用实验性功能
```

### 2. 平台不支持

**错误**: `platform not supported`

**解决**:
```bash
# 重新设置 Buildx
make setup-buildx
```

### 3. x86 镜像运行缓慢

**原因**: ARM Mac 模拟运行 x86

**解决**:
- 开发时使用 ARM 镜像: `make up`
- 仅在必要时测试 x86: `make up-x86`

### 4. 端口冲突

**错误**: `port already in use`

**解决**:
```bash
# x86 配置使用不同端口
# Redis: 26379 (默认 6379)
# API: 8000 (如需修改请编辑 docker-compose-x86.yml)
```

## 📋 完整命令列表

### 构建命令
```bash
make build         # 本地架构 (ARM)
make build-x86     # x86 架构
make build-multi   # 多平台
make build-push    # 构建并推送
make setup-buildx  # 设置 Buildx
```

### 运行命令
```bash
make up            # ARM 服务
make up-x86        # x86 服务
make down          # 停止 ARM 服务
make down-x86      # 停止 x86 服务
make restart-x86   # 重启 x86 服务
```

### 监控命令
```bash
make status        # ARM 服务状态
make status-x86    # x86 服务状态
make logs          # 查看日志
make test          # 测试连通性
```

## 🎯 总结

通过这个跨平台构建方案，您可以：

- ✅ 在 ARM Mac 上构建 x86 镜像
- ✅ 测试跨平台兼容性
- ✅ 支持多架构部署
- ✅ 保持开发和生产环境一致性

**推荐工作流程**:
1. 本地开发: `make up` (ARM, 快速)
2. 兼容性测试: `make up-x86` (x86, 验证)
3. 生产部署: `make build-multi` (多平台)