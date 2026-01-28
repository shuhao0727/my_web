# 使用本地Python 3.11 Alpine镜像（避免网络访问）
FROM python@sha256:71ab7a182d44e2bef6e3fb3513c301b2f4b6c7bcf358a7c878a237b256804df5

# 设置构建参数，用于传递代理设置
ARG HTTP_PROXY
ARG HTTPS_PROXY

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# 设置代理环境变量（如果有的话）
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

# 安装系统依赖（Alpine Linux使用apk）
RUN apk update && apk add --no-cache \
    build-base \
    curl \
    musl-dev \
    libffi-dev \
    openssl-dev \
    fontconfig \
    freetype \
    ttf-dejavu \
    font-noto \
    font-noto-cjk \
    font-noto-extra \
    && rm -rf /var/cache/apk/*

# 安装Typst编译器（使用本地文件，请先下载Typst 0.14.2二进制包到backend目录）
# 1. 从以下链接下载Typst 0.14.2二进制包：
#    https://github.com/typst/typst/releases/download/v0.14.2/typst-x86_64-unknown-linux-musl.tar.xz
# 2. 将文件重命名为 typst.tar.xz 并放在 backend/ 目录下
COPY typst.tar.xz /tmp/typst.tar.xz
RUN echo "安装xz工具用于解压..." && \
    apk add --no-cache xz && \
    echo "检查Typst文件大小..." && \
    filesize=$(stat -c%s /tmp/typst.tar.xz) && \
    if [ $filesize -lt 12000000 ]; then \
        echo "错误：Typst文件太小（仅${filesize}字节），请确保下载了正确的Typst二进制包"; \
        echo "请从 https://github.com/typst/typst/releases/download/v0.14.2/typst-x86_64-unknown-linux-musl.tar.xz 下载"; \
        exit 1; \
    fi && \
    echo "Typst文件大小: ${filesize} 字节" && \
    echo "解压安装Typst..." && \
    tar -xJf /tmp/typst.tar.xz -C /tmp && \
    # 查找解压后的typst二进制文件（目录名可能因版本而异）
    find /tmp -name "typst" -type f -exec mv {} /usr/local/bin/typst \; && \
    chmod +x /usr/local/bin/typst && \
    rm -rf /tmp/typst.tar.xz /tmp/typst-* && \
    echo "验证Typst安装..." && \
    typst --version && \
    echo "✅ Typst安装成功"

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖（使用pip缓存加速）
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs backups

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令（先初始化数据库，再启动服务器）
CMD sh -c "python init_databases.py && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
