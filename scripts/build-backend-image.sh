#!/bin/bash

# 后端镜像打包脚本
# 支持依赖ID管理和本地镜像缓存

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要工具
check_tools() {
    log_info "检查必要工具..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    log_success "工具检查完成"
}

# 生成依赖ID
generate_dependency_id() {
    log_info "生成后端依赖ID..."
    
    # 使用绝对路径或回到项目根目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    
    if [ -f "$PROJECT_ROOT/backend/requirements.txt" ]; then
        # 基于requirements.txt生成依赖ID
        DEPENDENCY_ID=$(sha256sum "$PROJECT_ROOT/backend/requirements.txt" | cut -d' ' -f1)
        echo $DEPENDENCY_ID > "$PROJECT_ROOT/backend-dependency-id.txt"
        log_info "依赖ID: $DEPENDENCY_ID"
    else
        log_error "找不到 $PROJECT_ROOT/backend/requirements.txt"
        exit 1
    fi
}

# 检查本地Typst镜像或二进制
check_local_typst() {
    log_info "检查本地Typst资源..."
    
    # 方法1：使用预先提取的二进制文件
    if [ -f ".typst-cache/typst" ] && [ -x ".typst-cache/typst" ]; then
        log_info "找到预先提取的Typst二进制文件"
        echo "TYPST_SOURCE=cache" > .typst-cache.env
        log_info "将使用缓存中的Typst二进制文件"
        return 0
    fi
    
    # 方法2：尝试运行提取脚本
    log_info "尝试从本地镜像提取Typst二进制文件..."
    if [ -f "scripts/extract-typst-from-image.sh" ]; then
        chmod +x scripts/extract-typst-from-image.sh
        if ./scripts/extract-typst-from-image.sh; then
            log_info "成功从镜像提取Typst二进制文件"
            echo "TYPST_SOURCE=cache" > .typst-cache.env
            return 0
        else
            log_warning "从镜像提取失败"
        fi
    fi
    
    # 方法3：使用本地已有的二进制文件
    TYPST_BINARY=""
    for path in /opt/homebrew/bin/typst /usr/local/bin/typst /usr/bin/typst "$HOME/.local/bin/typst" "$(which typst 2>/dev/null)"; do
        if [ -f "$path" ] && [ -x "$path" ]; then
            TYPST_BINARY="$path"
            log_info "找到本地Typst二进制文件: $TYPST_BINARY"
            # 复制Typst二进制文件到构建上下文
            mkdir -p .typst-cache
            cp "$TYPST_BINARY" .typst-cache/typst
            chmod +x .typst-cache/typst
            echo "TYPST_BINARY=$TYPST_BINARY" > .typst-cache.env
            echo "TYPST_COPIED=true" >> .typst-cache.env
            log_info "已将Typst二进制文件复制到构建上下文"
            return 0
        fi
    done
    
    # 方法4：检查Docker镜像
    if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "typst"; then
        log_info "找到本地Typst Docker镜像"
        TYPST_IMAGE=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "typst" | head -1)
        echo "TYPST_IMAGE=$TYPST_IMAGE" > .typst-cache.env
        return 0
    fi
    
    log_warning "未找到本地Typst资源，将从网络下载"
    echo "TYPST_SOURCE=network" > .typst-cache.env
}

# 构建后端镜像
build_backend_image() {
    log_info "构建后端镜像..."
    
    # 获取依赖ID用于标签
    if [ -f "backend-dependency-id.txt" ]; then
        TAG=$(cat backend-dependency-id.txt | head -c 12)
    else
        TAG="latest"
    fi
    
    # 检查是否有架构参数
    ARCH=""
    if [ "$2" = "amd64" ]; then
        ARCH="--platform linux/amd64"
        log_info "构建 AMD64 架构镜像"
    elif [ "$2" = "arm64" ]; then
        ARCH="--platform linux/arm64"
        log_info "构建 ARM64 架构镜像"
    else
        log_info "构建当前平台架构镜像"
    fi
    
    # 构建参数
    BUILD_ARGS=""
    
    # 如果有本地Typst镜像，作为构建参数传递
    if [ -f ".typst-cache.env" ]; then
        source .typst-cache.env
        if [ -n "$TYPST_IMAGE" ]; then
            BUILD_ARGS="$BUILD_ARGS --build-arg TYPST_IMAGE=$TYPST_IMAGE"
        fi
    fi
    
    # 构建镜像
    docker build $ARCH -f Dockerfile.backend \
        -t myweb-backend:${TAG} \
        -t myweb-backend:latest \
        --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
        --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown") \
        $BUILD_ARGS \
        .
    
    log_success "后端镜像构建完成"
    echo "镜像标签: myweb-backend:${TAG}"
    echo "镜像标签: myweb-backend:latest"
}

# 推送镜像到仓库
push_image() {
    log_info "推送镜像到仓库..."
    
    if [ -f "backend-dependency-id.txt" ]; then
        TAG=$(cat backend-dependency-id.txt | head -c 12)
    else
        TAG="latest"
    fi
    
    docker push myweb-backend:${TAG}
    docker push myweb-backend:latest
    
    log_success "镜像推送完成"
}

# 列出可用镜像
list_images() {
    log_info "后端镜像列表:"
    docker images myweb-backend --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

# 清理旧镜像
cleanup_images() {
    log_info "清理旧镜像..."
    
    # 删除悬空镜像
    docker image prune -f
    
    # 删除旧版本镜像（保留最新的3个）
    OLD_IMAGES=$(docker images myweb-backend --format "{{.ID}}" | tail -n +4)
    if [ ! -z "$OLD_IMAGES" ]; then
        echo $OLD_IMAGES | xargs -r docker rmi
    fi
    
    log_success "镜像清理完成"
}

# 显示依赖信息
show_dependencies() {
    log_info "后端依赖信息:"
    if [ -f "backend/requirements.txt" ]; then
        echo "=== Python Dependencies ==="
        cat backend/requirements.txt
        echo ""
    fi
    
    if [ -f "backend-dependency-id.txt" ]; then
        echo "=== Dependency ID ==="
        echo "ID: $(cat backend-dependency-id.txt)"
    fi
}

# 显示Typst缓存信息
show_typst_cache() {
    log_info "Typst缓存信息:"
    if [ -f ".typst-cache.env" ]; then
        cat .typst-cache.env
    else
        echo "无缓存信息"
    fi
}

# 清理缓存
cleanup_cache() {
    log_info "清理构建缓存..."
    rm -f backend-dependency-id.txt .typst-cache.env
    docker builder prune -f
    log_success "缓存清理完成"
}

# 显示帮助信息
show_help() {
    echo "后端镜像打包脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  build        构建后端镜像（包含依赖检查和缓存）"
    echo "  push         推送镜像到仓库"
    echo "  list         列出后端镜像"
    echo "  cleanup      清理旧镜像"
    echo "  deps         显示依赖信息"
    echo "  typst        显示Typst缓存信息"
    echo "  cache-clean  清理构建缓存"
    echo "  all          执行完整构建流程（检查缓存 -> 生成ID -> 构建 -> 推送）"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build     # 构建后端镜像"
    echo "  $0 all       # 完整构建流程"
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi

    case $1 in
        build)
            check_tools
            check_local_typst
            generate_dependency_id
            build_backend_image $@
            ;;
        push)
            check_tools
            push_image
            ;;
        list)
            list_images
            ;;
        cleanup)
            cleanup_images
            ;;
        deps)
            show_dependencies
            ;;
        typst)
            show_typst_cache
            ;;
        cache-clean)
            cleanup_cache
            ;;
        all)
            check_tools
            check_local_typst
            generate_dependency_id
            build_backend_image
            push_image
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"