#!/bin/bash
set -e

# 等待Redis连接
echo "Waiting for Redis..."
until python -c "import redis; redis.Redis(host='redis', port=6379).ping()"; do
  echo "Redis is unavailable - sleeping"
  sleep 1
done
echo "Redis is up - continuing..."

# 创建必要的目录
mkdir -p /app/extensions /tmp/hiagent_storage

# 根据服务类型启动不同的服务
if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Worker..."
    exec python worker.py
else
    echo "Starting API Server..."
    exec granian --interface asgi main:app --host 0.0.0.0 --port 8000
fi