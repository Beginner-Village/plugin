#!/bin/bash

# HiAgent Plugin Runtime 部署脚本
# 适用于远程服务器快速部署

set -e

echo "🚀 Starting HiAgent Plugin Runtime Deployment..."

# 检查Docker和Docker Compose
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ Requirements check passed"
}

# 停止现有服务
stop_services() {
    echo "🛑 Stopping existing services..."
    docker-compose down --remove-orphans || true
    docker system prune -f || true
}

# 构建镜像
build_images() {
    echo "🔨 Building Docker images..."
    docker-compose build --no-cache
}

# 启动服务
start_services() {
    echo "🚀 Starting services..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Services started successfully!"
    else
        echo "❌ Failed to start services"
        docker-compose logs
        exit 1
    fi
}

# 验证部署
verify_deployment() {
    echo "🔍 Verifying deployment..."
    
    # 检查API健康状态
    local retries=0
    local max_retries=30
    
    while [ $retries -lt $max_retries ]; do
        if curl -f -s http://localhost:8000/ping > /dev/null; then
            echo "✅ API service is healthy"
            break
        else
            echo "⏳ Waiting for API service... ($((retries + 1))/$max_retries)"
            sleep 2
            retries=$((retries + 1))
        fi
    done
    
    if [ $retries -eq $max_retries ]; then
        echo "❌ API service health check failed"
        docker-compose logs api
        exit 1
    fi
    
    # 显示服务状态
    echo "📊 Service Status:"
    docker-compose ps
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉 HiAgent Plugin Runtime deployed successfully!"
    echo ""
    echo "📍 Service URLs:"
    echo "   - API Server: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Health Check: http://localhost:8000/ping"
    echo ""
    echo "🔧 Management Commands:"
    echo "   - View logs: docker-compose logs -f"
    echo "   - Stop services: docker-compose down"
    echo "   - Restart services: docker-compose restart"
    echo "   - Update services: git pull && ./deploy/deploy.sh"
    echo ""
    echo "📂 Plugin Directory: ./extensions"
    echo ""
}

# 主执行流程
main() {
    check_requirements
    stop_services
    build_images
    start_services
    verify_deployment
    show_deployment_info
}

# 处理脚本参数
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        echo "🛑 Stopping services..."
        docker-compose down
        ;;
    "restart")
        echo "🔄 Restarting services..."
        docker-compose restart
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status}"
        exit 1
        ;;
esac