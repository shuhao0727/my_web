# 使用 Python 3.11 官方镜像（更稳定，可能已有缓存）
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    sqlite3 \
    libsqlite3-dev \
    gcc \
    g++ \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Typst安装暂时跳过，因为网络问题可能导致构建失败
RUN echo "跳过Typst安装，Typst功能将不可用。如需使用，请在构建后手动安装。"

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/content /app/logs

# 设置权限
RUN chmod +x /app/init_databases.py

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["sh", "-c", "python init_databases.py && python -m uvicorn main:app --host 0.0.0.0 --port 8000"]