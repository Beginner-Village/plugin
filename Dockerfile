# 使用Python 3.11官方镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt ./
COPY hiagent-plugin-sdk ./hiagent-plugin-sdk

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e ./hiagent-plugin-sdk

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/extensions /tmp/hiagent_storage

# 设置权限
RUN chmod +x deploy/entrypoint.sh

# 暴露端口
EXPOSE 8000

# 使用entrypoint脚本启动
ENTRYPOINT ["deploy/entrypoint.sh"]