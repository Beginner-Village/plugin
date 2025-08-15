# HiAgent Plugin Runtime Complete Image
# 基于 Python 3.11 官方镜像构建完整的插件运行时环境
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    SERVICE_TYPE=api

# 清除可能存在的代理配置并安装系统依赖
RUN unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY && \
    rm -f /etc/apt/apt.conf.d/*proxy* && \
    apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt pyproject.toml ./

# 升级 pip 并安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制并安装 SDK
COPY hiagent-plugin-sdk/ ./hiagent-plugin-sdk/
RUN cd hiagent-plugin-sdk && \
    pip install -e . && \
    cd ..

# 复制应用代码
COPY app/ ./app/
COPY main.py worker.py ./

# 复制部署脚本
COPY deploy/ ./deploy/

# 复制配置文件
COPY config.yaml docker-config.yaml ./
COPY config-example.yaml ./

# 创建必要的目录
RUN mkdir -p /app/extensions /tmp/hiagent_storage /app/logs

# 设置执行权限
RUN chmod +x deploy/entrypoint.sh deploy/deploy.sh deploy/install.sh

# 验证 SDK 和应用安装
RUN python -c "import hiagent_plugin_sdk; print('SDK 验证成功')" && \
    python -c "from app.config import load; print('应用配置加载成功')"

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD if [ "$SERVICE_TYPE" = "api" ]; then \
            curl -f http://localhost:8000/ping || exit 1; \
        else \
            python -c "import redis; redis.Redis(host='redis', port=6379).ping()" || exit 1; \
        fi

# 设置容器启动命令
ENTRYPOINT ["deploy/entrypoint.sh"]