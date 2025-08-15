#!/bin/bash

# HiAgent Plugin Runtime 代理问题修复脚本
echo "🔧 HiAgent Plugin Runtime 代理问题修复工具"
echo "=========================================="

# 检测代理设置
echo "📊 当前代理设置检测:"
echo "HTTP_PROXY: ${HTTP_PROXY:-未设置}"
echo "HTTPS_PROXY: ${HTTPS_PROXY:-未设置}" 
echo "http_proxy: ${http_proxy:-未设置}"
echo "https_proxy: ${https_proxy:-未设置}"
echo "ALL_PROXY: ${ALL_PROXY:-未设置}"

# 检查是否能连接 Docker Hub
echo ""
echo "🌐 测试网络连接:"
if curl -s --connect-timeout 5 https://registry-1.docker.io/v2/ > /dev/null; then
    echo "✅ Docker Hub 连接正常"
    NETWORK_OK=true
else
    echo "❌ Docker Hub 连接失败"
    NETWORK_OK=false
fi

echo ""
echo "🔧 修复选项:"
echo "1. 临时关闭代理并构建 (推荐)"
echo "2. 检查并修复 Docker 代理配置"
echo "3. 使用本地 ARM 镜像构建"
echo "4. 手动配置 Docker 代理"
echo "5. 退出"

read -p "请选择修复方案 (1-5): " choice

case $choice in
    1)
        echo "🚀 方案1: 临时关闭代理构建"
        echo "正在临时禁用代理设置..."
        
        # 保存原有设置
        OLD_HTTP_PROXY=$HTTP_PROXY
        OLD_HTTPS_PROXY=$HTTPS_PROXY
        OLD_http_proxy=$http_proxy
        OLD_https_proxy=$https_proxy
        OLD_ALL_PROXY=$ALL_PROXY
        
        # 临时清除代理
        unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY
        
        echo "🔨 开始构建 x86 镜像..."
        if make build-x86; then
            echo "✅ 构建成功!"
        else
            echo "❌ 构建失败，请尝试其他方案"
        fi
        
        # 恢复代理设置
        export HTTP_PROXY=$OLD_HTTP_PROXY
        export HTTPS_PROXY=$OLD_HTTPS_PROXY
        export http_proxy=$OLD_http_proxy
        export https_proxy=$OLD_https_proxy
        export ALL_PROXY=$OLD_ALL_PROXY
        echo "🔄 代理设置已恢复"
        ;;
    2)
        echo "🔧 方案2: Docker 代理配置检查"
        echo "检查 Docker Desktop 代理设置..."
        echo "请按照以下步骤操作:"
        echo "1. 打开 Docker Desktop"
        echo "2. 进入 Settings → Resources → Proxies"
        echo "3. 选择 'Manual proxy configuration'"
        echo "4. 设置代理服务器地址"
        echo "5. 重启 Docker Desktop"
        echo ""
        echo "或者编辑 ~/.docker/daemon.json:"
        echo '{'
        echo '  "proxies": {'
        echo '    "http-proxy": "http://127.0.0.1:17890",'
        echo '    "https-proxy": "http://127.0.0.1:17890",'
        echo '    "no-proxy": "localhost,127.0.0.1,.local"'
        echo '  }'
        echo '}'
        ;;
    3)
        echo "🏃‍♂️ 方案3: 使用本地 ARM 架构构建"
        echo "在 ARM Mac 上构建 ARM 镜像 (无需跨平台)..."
        if make build; then
            echo "✅ ARM 镜像构建成功!"
            echo "📝 注意: 这是 ARM 架构镜像，可以在 ARM Mac 上正常运行"
        else
            echo "❌ ARM 镜像构建失败"
        fi
        ;;
    4)
        echo "⚙️ 方案4: 手动代理配置"
        echo "请手动配置您的代理设置:"
        echo ""
        echo "如果使用 Clash 等代理工具:"
        echo "1. 确保 '允许局域网连接' 已启用"
        echo "2. 记录代理端口 (通常是 7890 或 17890)"
        echo "3. 在 Docker Desktop 中配置代理"
        echo ""
        echo "如果想完全禁用代理:"
        echo "1. 关闭代理软件"
        echo "2. 运行: make build-x86"
        echo "3. 重新启动代理软件"
        ;;
    5)
        echo "👋 退出修复工具"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac