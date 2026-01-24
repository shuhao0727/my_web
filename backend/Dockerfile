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

# 安装 Typst - 使用更稳定的安装方式
RUN ARCH=$(uname -m) && \
    # 设置默认变量
    TYPST_URL="" && \
    if [ "$ARCH" = "x86_64" ]; then \
        TYPST_URL="https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-gnu.tar.xz"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        TYPST_URL="https://github.com/typst/typst/releases/latest/download/typst-aarch64-unknown-linux-gnu.tar.xz"; \
    else \
        echo "Unsupported architecture: $ARCH. Installing via cargo instead." && \
        apt-get update && apt-get install -y cargo && \
        cargo install typst --locked && \
        exit 0; \
    fi && \
    echo "Downloading Typst from: $TYPST_URL" && \
    wget -q "$TYPST_URL" -O typst.tar.xz && \
    mkdir -p typst-extract && \
    tar -xf typst.tar.xz -C typst-extract --strip-components=1 && \
    mv typst-extract/typst /usr/local/bin/ && \
    chmod +x /usr/local/bin/typst && \
    rm -rf typst.tar.xz typst-extract && \
    echo "Typst installed successfully" && \
    typst --version

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
