# 使用 Python 3.11 官方镜像
FROM python:3.11-slim AS base

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖（包括bcrypt）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 额外安装bcrypt（如果requirements.txt中没有）
RUN pip install --no-cache-dir bcrypt

# 复制应用代码
COPY . .

# 创建数据目录和日志目录
RUN mkdir -p /app/data /app/logs /app/content

# 创建非root用户运行应用
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 在启动应用前运行数据库初始化脚本
CMD python init_database.py && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
