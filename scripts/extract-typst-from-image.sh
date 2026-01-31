#!/bin/bash

# 从 typst 镜像中提取 typst 二进制文件

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否已安装 Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker 未安装"
    exit 1
fi

# 检查 typst 镜像是否存在
TYPST_IMAGE="ghcr.io/typst/typst:latest"
if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^$TYPST_IMAGE$"; then
    log_error "找不到 typst 镜像: $TYPST_IMAGE"
    echo "请先拉取镜像: docker pull $TYPST_IMAGE"
    exit 1
fi

# 创建缓存目录
CACHE_DIR=".typst-cache"
mkdir -p "$CACHE_DIR"

# 创建临时容器并提取二进制文件
CONTAINER_ID=$(docker create "$TYPST_IMAGE" /bin/true)

if [ -z "$CONTAINER_ID" ]; then
    log_error "创建临时容器失败"
    exit 1
fi

log_info "从镜像 $TYPST_IMAGE 中提取 typst 二进制文件..."

# 尝试多个可能的路径
BINARY_PATHS=(
    "/usr/local/bin/typst"
    "/usr/bin/typst"
    "/bin/typst"
    "/typst"
)

FOUND=false
for path in "${BINARY_PATHS[@]}"; do
    if docker cp "${CONTAINER_ID}:${path}" "${CACHE_DIR}/typst.tmp" 2>/dev/null; then
        log_info "找到 typst 二进制文件: $path"
        mv "${CACHE_DIR}/typst.tmp" "${CACHE_DIR}/typst"
        chmod +x "${CACHE_DIR}/typst"
        FOUND=true
        break
    fi
done

# 清理临时容器
docker rm "$CONTAINER_ID" >/dev/null 2>&1

if [ "$FOUND" = false ]; then
    log_error "在镜像中找不到 typst 二进制文件"
    log_info "尝试列出镜像内容..."
    
    # 运行镜像查看文件系统
    docker run --rm "$TYPST_IMAGE" /bin/sh -c "find / -name typst -type f 2>/dev/null" | head -20
    exit 1
fi

# 验证提取的二进制文件
if [ -f "${CACHE_DIR}/typst" ] && [ -x "${CACHE_DIR}/typst" ]; then
    log_info "成功提取 typst 二进制文件"
    log_info "文件大小: $(ls -lh "${CACHE_DIR}/typst" | awk '{print $5}')"
    log_info "文件位置: $(pwd)/${CACHE_DIR}/typst"
else
    log_error "提取的二进制文件无效"
    exit 1
fi