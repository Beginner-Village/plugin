# HiAgent Plugin Runtime Makefile
.PHONY: build up down clean logs status test install-plugin

# 变量定义
IMAGE_NAME = hiagent-plugin-runtime
IMAGE_TAG = latest
COMPOSE_FILE = docker-compose.yml

# 构建镜像 (本地架构)
build:
	@echo "🔨 Building HiAgent Plugin Runtime image..."
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "✅ Build completed!"

# 构建 x86/amd64 镜像 (适用于 ARM Mac)
build-x86:
	@echo "🔨 Building x86/amd64 HiAgent Plugin Runtime image on ARM Mac..."
	docker buildx build --platform linux/amd64 -t $(IMAGE_NAME):$(IMAGE_TAG)-amd64 .
	@echo "✅ x86/amd64 build completed!"

# 使用正确代理构建 x86 镜像
build-x86-with-proxy:
	@echo "🔨 Building x86 image with correct proxy settings..."
	@echo "🌐 Using proxy: http://127.0.0.1:10902"
	export https_proxy=http://127.0.0.1:10902 && \
	export http_proxy=http://127.0.0.1:10902 && \
	export all_proxy=socks5://127.0.0.1:10021 && \
	docker buildx build --platform linux/amd64 \
		--build-arg https_proxy=http://127.0.0.1:10902 \
		--build-arg http_proxy=http://127.0.0.1:10902 \
		--build-arg all_proxy=socks5://127.0.0.1:10021 \
		-t $(IMAGE_NAME):$(IMAGE_TAG)-amd64 .
	@echo "✅ Proxy-enabled x86 build completed!"

# 构建简化版 x86 镜像 (网络受限环境)
build-x86-simple:
	@echo "🔨 Building simple x86/amd64 image for network-restricted environments..."
	env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
	docker buildx build --platform linux/amd64 -f Dockerfile.simple -t $(IMAGE_NAME):$(IMAGE_TAG)-amd64-simple .
	@echo "✅ Simple x86/amd64 build completed!"

# 无代理构建 (解决网络代理问题)
build-x86-no-proxy:
	@echo "🔨 Building x86 image without proxy..."
	@echo "🌐 Temporarily disabling proxy settings for Docker build"
	env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
	docker buildx build --platform linux/amd64 --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG)-amd64 .
	@echo "✅ No-proxy x86 build completed!"

# 最小化构建 (完全避免网络问题)
build-x86-minimal:
	@echo "🔨 Building minimal x86 image (no network dependencies)..."
	@echo "📦 Using pure Python base image without system packages"
	docker buildx build --platform linux/amd64 -f Dockerfile.minimal -t $(IMAGE_NAME):$(IMAGE_TAG)-amd64-minimal .
	@echo "✅ Minimal x86 build completed!"

# 快速构建 (轻量级依赖)
build-x86-fast:
	@echo "🚀 Building fast x86 image (lightweight dependencies)..."
	@echo "📦 Using minimal system packages for faster build"
	export https_proxy=http://127.0.0.1:10902 && \
	export http_proxy=http://127.0.0.1:10902 && \
	export all_proxy=socks5://127.0.0.1:10021 && \
	docker buildx build --platform linux/amd64 -f Dockerfile.fast -t $(IMAGE_NAME):$(IMAGE_TAG)-amd64-fast .
	@echo "✅ Fast x86 build completed!"

# 构建多平台镜像 (x86 + ARM)
build-multi:
	@echo "🔨 Building multi-platform HiAgent Plugin Runtime image..."
	docker buildx build --platform linux/amd64,linux/arm64 -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "✅ Multi-platform build completed!"

# 构建并推送多平台镜像到仓库
build-push:
	@echo "🔨 Building and pushing multi-platform image..."
	docker buildx build --platform linux/amd64,linux/arm64 -t $(IMAGE_NAME):$(IMAGE_TAG) --push .
	@echo "✅ Multi-platform build and push completed!"

# 设置 Docker Buildx (首次使用需要)
setup-buildx:
	@echo "🔧 Setting up Docker Buildx for cross-platform builds..."
	docker buildx create --name multiarch --driver docker-container --use
	docker buildx inspect --bootstrap
	@echo "✅ Buildx setup completed!"

# 启动所有服务
up: build
	@echo "🚀 Starting HiAgent Plugin Runtime services..."
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@make status

# 启动 x86 架构服务 (适用于 ARM Mac 运行 x86 镜像)
up-x86: build-x86
	@echo "🚀 Starting x86 HiAgent Plugin Runtime services..."
	docker-compose -f docker-compose-x86.yml up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@make status-x86

# 停止所有服务
down:
	@echo "🛑 Stopping HiAgent Plugin Runtime services..."
	docker-compose -f $(COMPOSE_FILE) down

# 停止 x86 架构服务
down-x86:
	@echo "🛑 Stopping x86 HiAgent Plugin Runtime services..."
	docker-compose -f docker-compose-x86.yml down

# 重启服务
restart: down up

# 重启 x86 架构服务
restart-x86: down-x86 up-x86

# 清理资源
clean:
	@echo "🧹 Cleaning up resources..."
	docker-compose -f $(COMPOSE_FILE) down -v
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) 2>/dev/null || true
	docker system prune -f

# 查看日志
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

# 查看 API 日志
logs-api:
	docker-compose -f $(COMPOSE_FILE) logs -f api

# 查看 Worker 日志
logs-worker:
	docker-compose -f $(COMPOSE_FILE) logs -f worker

# 查看 Redis 日志
logs-redis:
	docker-compose -f $(COMPOSE_FILE) logs -f redis

# 检查服务状态
status:
	@echo "📊 Service Status:"
	@docker-compose -f $(COMPOSE_FILE) ps
	@echo ""
	@echo "🏥 Health Checks:"
	@docker inspect hiagent-api --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/API: /' || echo "API: not running"
	@docker inspect hiagent-worker --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/Worker: /' || echo "Worker: not running"
	@docker inspect hiagent-redis --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/Redis: /' || echo "Redis: not running"

# 检查 x86 架构服务状态
status-x86:
	@echo "📊 x86 Service Status:"
	@docker-compose -f docker-compose-x86.yml ps
	@echo ""
	@echo "🏥 Health Checks:"
	@docker inspect hiagent-api --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/API: /' || echo "API: not running"
	@docker inspect hiagent-worker --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/Worker: /' || echo "Worker: not running"
	@docker inspect hiagent-redis --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/Redis: /' || echo "Redis: not running"

# 测试 API 连通性
test-api:
	@echo "🧪 Testing API connectivity..."
	@curl -s http://localhost:8000/ping && echo "✅ API is responding" || echo "❌ API is not responding"
	@curl -s http://localhost:8000/docs >/dev/null && echo "✅ API docs accessible" || echo "❌ API docs not accessible"

# 测试 Redis 连通性
test-redis:
	@echo "🧪 Testing Redis connectivity..."
	@docker exec hiagent-redis redis-cli ping && echo "✅ Redis is responding" || echo "❌ Redis is not responding"

# 运行所有测试
test: test-redis test-api

# 安装插件示例
install-plugin:
	@echo "📦 Installing example plugin..."
	@if [ -f "extensions/hiagent-plugin-time/0.2.0/hiagent_plugin_time-0.2.0-py3-none-any.whl" ]; then \
		curl -X POST "http://localhost:8000/v1/InstallPackage" \
			-H "Content-Type: application/json" \
			-d '{"uri": "file:///app/extensions/hiagent-plugin-time/0.2.0/hiagent_plugin_time-0.2.0-py3-none-any.whl", "filename": "hiagent_plugin_time-0.2.0-py3-none-any.whl", "force": true}'; \
	else \
		echo "❌ Example plugin not found"; \
	fi

# 开发模式启动（仅 API 和 Redis）
dev:
	@echo "🔧 Starting in development mode..."
	docker-compose -f $(COMPOSE_FILE) up -d redis api
	@sleep 5
	@make test-api

# 进入 API 容器
shell-api:
	docker exec -it hiagent-api /bin/bash

# 进入 Worker 容器
shell-worker:
	docker exec -it hiagent-worker /bin/bash

# 进入 Redis 容器
shell-redis:
	docker exec -it hiagent-redis redis-cli

# 查看实时资源使用情况
stats:
	docker stats hiagent-api hiagent-worker hiagent-redis

# 备份数据
backup:
	@echo "💾 Backing up data..."
	@mkdir -p backup/$(shell date +%Y%m%d_%H%M%S)
	@docker run --rm -v app_redis_data:/data -v $(PWD)/backup/$(shell date +%Y%m%d_%H%M%S):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
	@docker run --rm -v app_plugin_storage:/data -v $(PWD)/backup/$(shell date +%Y%m%d_%H%M%S):/backup alpine tar czf /backup/storage_backup.tar.gz -C /data .
	@echo "✅ Backup completed in backup/$(shell date +%Y%m%d_%H%M%S)/"

# 显示帮助信息
help:
	@echo "HiAgent Plugin Runtime Management Commands:"
	@echo ""
	@echo "🔨 Build & Deployment:"
	@echo "  make build       - Build Docker image (local architecture)"
	@echo "  make build-x86   - Build x86/amd64 image on ARM Mac"
	@echo "  make build-x86-with-proxy - Build x86 image with correct proxy (port 10902)"
	@echo "  make build-x86-no-proxy - Build x86 image without proxy (fix network issues)"
	@echo "  make build-multi - Build multi-platform image (x86 + ARM)"
	@echo "  make build-push  - Build and push multi-platform image"
	@echo "  make setup-buildx- Setup Docker Buildx (run once)"
	@echo "  make up          - Start all services"
	@echo "  make up-x86      - Start x86 services on ARM Mac"
	@echo "  make down        - Stop all services"
	@echo "  make down-x86    - Stop x86 services"
	@echo "  make restart     - Restart all services"
	@echo "  make restart-x86 - Restart x86 services"
	@echo "  make dev         - Start in development mode (API + Redis only)"
	@echo ""
	@echo "📊 Monitoring:"
	@echo "  make status      - Show service status"
	@echo "  make logs        - Show all logs"
	@echo "  make logs-api    - Show API logs"
	@echo "  make logs-worker - Show Worker logs"
	@echo "  make logs-redis  - Show Redis logs"
	@echo "  make stats       - Show resource usage"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test        - Run all tests"
	@echo "  make test-api    - Test API connectivity"
	@echo "  make test-redis  - Test Redis connectivity"
	@echo ""
	@echo "🔧 Utilities:"
	@echo "  make shell-api   - Enter API container"
	@echo "  make shell-worker- Enter Worker container"
	@echo "  make shell-redis - Enter Redis CLI"
	@echo "  make install-plugin - Install example plugin"
	@echo "  make backup      - Backup data"
	@echo "  make clean       - Clean up resources"
	@echo ""

# 使用最终版本的 compose 文件
up-final:
	@echo "🚀 Starting HiAgent Plugin Runtime with final configuration..."
	docker-compose -f docker-compose-final.yml up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@make status-final

down-final:
	@echo "🛑 Stopping final configuration services..."
	docker-compose -f docker-compose-final.yml down

status-final:
	@echo "📊 Final Configuration Service Status:"
	@docker-compose -f docker-compose-final.yml ps
	@echo ""
	@echo "🏥 Health Checks:"
	@docker inspect hiagent-api --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/API: /' || echo "API: not running"
	@docker inspect hiagent-worker --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/Worker: /' || echo "Worker: not running"
	@docker inspect hiagent-redis --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/Redis: /' || echo "Redis: not running"

logs-final:
	docker-compose -f docker-compose-final.yml logs -f

# 使用简化版本的 compose 文件（解决网络冲突）
up-simple:
	@echo "🚀 Starting HiAgent Plugin Runtime with simplified configuration..."
	docker-compose -f docker-compose-simple.yml up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@make status-simple

down-simple:
	@echo "🛑 Stopping simplified configuration services..."
	docker-compose -f docker-compose-simple.yml down

status-simple:
	@echo "📊 Simplified Configuration Service Status:"
	@docker-compose -f docker-compose-simple.yml ps
	@echo ""
	@echo "🏥 Health Checks:"
	@docker inspect hiagent-api --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/API: /' || echo "API: not running"
	@docker inspect hiagent-worker --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/Worker: /' || echo "Worker: not running"
	@docker inspect hiagent-redis --format='{{.State.Health.Status}}' 2>/dev/null | sed 's/^/Redis: /' || echo "Redis: not running"

logs-simple:
	docker-compose -f docker-compose-simple.yml logs -f

restart-simple: down-simple up-simple

# 原有测试命令保留
test_app:
	@poetry run pytest ./tests

test_plugin:
	@bash scripts/test_plugins.sh

build_plugins:
	@bash scripts/build_plugins.sh

# 默认目标
all: help
