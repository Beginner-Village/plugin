#!/bin/bash
set -e

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 错误处理
handle_error() {
    log "ERROR: $1"
    exit 1
}

log "Starting HiAgent Plugin Runtime..."
log "Service Type: ${SERVICE_TYPE:-api}"
log "Config File: ${CONFIG:-/app/config.yaml}"

# 等待Redis连接
log "Waiting for Redis connection..."
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_TIMEOUT=${REDIS_TIMEOUT:-30}

for i in $(seq 1 $REDIS_TIMEOUT); do
    if python -c "import redis; redis.Redis(host='$REDIS_HOST', port=$REDIS_PORT, socket_connect_timeout=5).ping()" 2>/dev/null; then
        log "Redis is ready!"
        break
    fi
    if [ $i -eq $REDIS_TIMEOUT ]; then
        handle_error "Redis connection timeout after ${REDIS_TIMEOUT}s"
    fi
    log "Redis is unavailable - waiting (${i}/${REDIS_TIMEOUT})..."
    sleep 1
done

# 创建必要的目录
log "Creating necessary directories..."
mkdir -p /app/extensions /tmp/hiagent_storage /app/logs

# 设置权限
chmod -R 755 /app/extensions
chmod -R 755 /tmp/hiagent_storage

# 验证配置文件
if [ ! -f "${CONFIG:-/app/config.yaml}" ]; then
    log "Config file not found, using docker-config.yaml"
    export CONFIG=/app/docker-config.yaml
fi

# 验证 SDK 和应用是否正确安装
log "Validating installation..."
python -c "from hiagent_plugin_sdk import __version__; print(f'SDK version: {__version__}')" || handle_error "SDK validation failed"
python -c "from app.config import load; print('App config validation passed')" || handle_error "App config validation failed"

# 根据服务类型启动不同的服务
case "${SERVICE_TYPE:-api}" in
    "worker")
        log "Starting Worker Process..."
        log "Worker will process async tasks from Redis queue"
        exec python worker.py
        ;;
    "api")
        log "Starting API Server..."
        log "API will be available at http://0.0.0.0:8000"
        log "API documentation: http://0.0.0.0:8000/docs"
        exec granian --interface asgi main:app --host 0.0.0.0 --port 8000 --workers 1
        ;;
    *)
        handle_error "Unknown SERVICE_TYPE: ${SERVICE_TYPE}. Must be 'api' or 'worker'"
        ;;
esac