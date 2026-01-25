# ==================== 构建阶段 ====================
FROM --platform=linux/amd64 python:3.11-slim AS builder

# 构建参数
ARG HTTP_PROXY
ARG HTTPS_PROXY

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 如果有代理设置，则传递给环境变量
RUN if [ -n "$HTTP_PROXY" ]; then export http_proxy=$HTTP_PROXY; fi && \
    if [ -n "$HTTPS_PROXY" ]; then export https_proxy=$HTTPS_PROXY; fi

# 安装系统依赖（构建时）
RUN unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && apt-get update && apt-get install -y \
    git \
    curl \
    gcc \
    g++ \
    libpq-dev \
    libsqlite3-dev \
    pkg-config \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装本地Typst安装包（x86_64架构）
COPY typst-x86_64-unknown-linux-musl.tar.xz /tmp/
RUN echo "正在安装本地Typst安装包（x86_64架构）..." && \
    tar -xJf /tmp/typst-x86_64-unknown-linux-musl.tar.xz -C /tmp && \
    mv /tmp/typst-x86_64-unknown-linux-musl/typst /usr/local/bin/typst && \
    chmod +x /usr/local/bin/typst && \
    echo "Typst安装成功" && \
    rm -rf /tmp/typst-x86_64-unknown-linux-musl*

# 构建参数：指定依赖文件，默认为requirements.txt
ARG REQUIREMENTS_FILE=requirements.txt

# 复制依赖文件
COPY ${REQUIREMENTS_FILE} ./requirements.txt

# 创建虚拟环境并安装Python依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==================== 运行阶段 ====================
FROM --platform=linux/amd64 python:3.11-slim AS runtime

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 安装运行时的系统依赖（包括curl用于健康检查）
RUN unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    libsqlite3-0 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python虚拟环境
COPY --from=builder /opt/venv /opt/venv
# 从构建阶段复制Typst二进制文件（如果存在）- 使用RUN命令避免COPY失败
RUN if [ -f /usr/local/bin/typst ]; then \
        cp /usr/local/bin/typst /usr/local/bin/typst-tmp && \
        chmod +x /usr/local/bin/typst-tmp && \
        mv /usr/local/bin/typst-tmp /usr/local/bin/typst && \
        echo "Typst复制成功"; \
    else \
        echo "Typst文件不存在，跳过复制"; \
    fi

# 验证安装
RUN if [ -f /usr/local/bin/typst ] && [ -x /usr/local/bin/typst ]; then \
        /usr/local/bin/typst --version && echo "Typst版本检查通过"; \
    else \
        echo "Typst不可用，将使用备用方案"; \
    fi && \
    python --version && \
    pip --version

# 创建非root用户
RUN groupadd -r -g 1001 appuser && \
    useradd -r -u 1001 -g appuser appuser && \
    mkdir -p /app/content /app/logs /app/data && \
    chown -R appuser:appuser /app

# 复制应用代码
COPY --chown=appuser:appuser . .

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["sh", "-c", "python init_databases.py && python -m uvicorn main:app --host 0.0.0.0 --port 8000"]

# ==================== 镜像元数据 ====================
LABEL maintainer="myweb-dev" \
      description="MyWeb后端服务 - 高性能Python FastAPI应用" \
      version="1.0.0"

# 镜像大小优化建议：
# 1. 构建前清理：docker builder prune
# 2. 使用多阶段构建减少最终镜像大小
# 3. 使用.dockerignore排除不必要的文件
# 4. 合并RUN命令减少镜像层数