# 🌐 Docker 构建代理问题解决方案

如果您在构建 Docker 镜像时遇到代理相关的网络错误，本文档提供多种解决方案。

## 🚨 常见错误

```
Cannot connect to proxy.', NewConnectionError...
Connection refused
Unable to connect to 127.0.0.1:17890
```

## 🔧 解决方案

### 方案 1: 使用无代理构建命令 (推荐)

```bash
# 使用专门的无代理构建命令
make build-x86-no-proxy
```

这个命令会临时禁用所有代理设置进行构建。

### 方案 2: 手动禁用代理

#### 2.1 临时禁用代理环境变量

```bash
# 在当前终端会话中禁用代理
unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY
unset ALL_PROXY

# 然后正常构建
make build-x86
```

#### 2.2 为单个命令禁用代理

```bash
# 仅为这一次构建禁用代理
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
docker buildx build --platform linux/amd64 -t hiagent-plugin-runtime:latest-amd64 .
```

### 方案 3: 配置 Docker 代理设置

#### 3.1 Docker Desktop 设置

1. 打开 Docker Desktop
2. 进入 Settings → Resources → Proxies
3. 选择 "Manual proxy configuration"
4. 配置您的代理服务器地址

#### 3.2 Docker daemon 配置

创建或编辑 `~/.docker/daemon.json`:

```json
{
  "proxies": {
    "http-proxy": "http://127.0.0.1:17890",
    "https-proxy": "http://127.0.0.1:17890",
    "no-proxy": "localhost,127.0.0.1,.local"
  }
}
```

然后重启 Docker Desktop。

### 方案 4: 检查代理软件设置

如果您使用 Clash、V2Ray 等代理软件:

1. **关闭代理**: 临时关闭代理软件
2. **允许局域网**: 确保代理软件允许局域网连接
3. **检查端口**: 确认代理端口 (如 17890) 是否正确

### 方案 5: 离线构建 (最后手段)

如果网络问题无法解决，可以考虑离线构建:

1. 在有网络的环境中拉取基础镜像
2. 使用 `docker save` 导出镜像
3. 在目标环境中 `docker load` 导入镜像

## 🧪 测试网络连接

### 测试 Docker 网络

```bash
# 测试 Docker 是否能正常访问网络
docker run --rm alpine:latest wget -q --spider http://www.google.com && echo "Network OK" || echo "Network Failed"
```

### 测试代理设置

```bash
# 检查当前代理设置
echo "HTTP_PROXY: $HTTP_PROXY"
echo "HTTPS_PROXY: $HTTPS_PROXY"
echo "http_proxy: $http_proxy"
echo "https_proxy: $https_proxy"
```

## 📋 可用的构建命令

| 命令 | 说明 | 适用场景 |
|------|------|----------|
| `make build-x86` | 标准 x86 构建 | 网络正常 |
| `make build-x86-no-proxy` | 无代理构建 | 代理冲突 |
| `make build-x86-simple` | 简化构建 | 网络受限 |
| `make build` | 本地架构构建 | ARM Mac |

## 🎯 推荐流程

1. **首先尝试**: `make build-x86-no-proxy`
2. **如果失败**: 检查代理软件设置
3. **仍然失败**: 临时关闭代理软件
4. **最后选择**: 使用 `make build` 构建 ARM 版本

## ⚠️ 注意事项

- 构建时的网络设置不会影响运行时
- 禁用代理只在构建过程中生效
- 构建完成后代理设置会自动恢复
- 如果您的网络环境必须使用代理，建议配置 Docker 的代理设置

## 🚀 快速解决

如果您急需构建镜像，最快的解决方法:

```bash
# 1. 临时关闭代理软件 (如 Clash)
# 2. 运行构建命令
make build-x86-no-proxy
# 3. 重新启动代理软件
```

现在您应该可以成功构建 x86 镜像了！