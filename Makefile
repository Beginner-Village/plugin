# HiAgent Plugin Runtime Makefile
.PHONY: build up down clean logs status test install-plugin

# 变量定义
IMAGE_NAME = hiagent-plugin-runtime
IMAGE_TAG = latest
COMPOSE_FILE = docker-compose.yml

# 构建镜像
build:
	@echo "🔨 Building HiAgent Plugin Runtime image..."
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "✅ Build completed!"

# 启动所有服务
up: build
	@echo "🚀 Starting HiAgent Plugin Runtime services..."
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@make status

# 停止所有服务
down:
	@echo "🛑 Stopping HiAgent Plugin Runtime services..."
	docker-compose -f $(COMPOSE_FILE) down

# 重启服务
restart: down up

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
	@echo "  make build       - Build Docker image"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
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

# 原有测试命令保留
test_app:
	@poetry run pytest ./tests

test_plugin:
	@bash scripts/test_plugins.sh

build_plugins:
	@bash scripts/build_plugins.sh

# 默认目标
all: help
