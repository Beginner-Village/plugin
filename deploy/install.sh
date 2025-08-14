#!/bin/bash

# HiAgent Plugin Runtime 一键安装脚本
# 适用于全新服务器快速部署

set -e

REPO_URL="https://github.com/Beginner-Village/plugin.git"
INSTALL_DIR="hiagent-plugin-runtime"

echo "🚀 HiAgent Plugin Runtime 一键安装"
echo "========================================="

# 检查系统
check_system() {
    echo "📋 检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "✅ Linux 系统"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "✅ macOS 系统"  
    else
        echo "❌ 不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    # 检查必要工具
    for tool in git curl; do
        if ! command -v $tool &> /dev/null; then
            echo "❌ $tool 未安装，请先安装"
            exit 1
        fi
    done
    
    echo "✅ 系统检查通过"
}

# 安装Docker
install_docker() {
    if command -v docker &> /dev/null; then
        echo "✅ Docker 已安装"
        return
    fi
    
    echo "📦 安装 Docker..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux安装
        curl -fsSL https://get.docker.com | sh
        sudo usermod -aG docker $USER
        echo "⚠️  请重新登录以应用Docker组权限"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS提示
        echo "❌ 请手动安装 Docker Desktop for Mac"
        echo "   下载地址: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
}

# 安装Docker Compose
install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose 已安装"
        return
    fi
    
    echo "📦 安装 Docker Compose..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
}

# 克隆项目
clone_project() {
    echo "📥 下载项目代码..."
    
    if [ -d "$INSTALL_DIR" ]; then
        echo "⚠️  目录 $INSTALL_DIR 已存在，是否删除并重新下载? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            echo "❌ 安装取消"
            exit 1
        fi
    fi
    
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    echo "✅ 项目下载完成"
}

# 部署服务
deploy_service() {
    echo "🚀 部署服务..."
    
    # 设置执行权限
    chmod +x deploy/*.sh
    
    # 执行部署
    ./deploy/deploy.sh
}

# 主执行流程
main() {
    check_system
    install_docker
    install_docker_compose
    clone_project
    deploy_service
    
    echo ""
    echo "🎉 安装完成!"
    echo "   项目目录: $(pwd)"
    echo "   API文档: http://localhost:8000/docs"
    echo ""
}

# 错误处理
trap 'echo "❌ 安装失败，请查看错误信息"; exit 1' ERR

# 执行安装
main "$@"