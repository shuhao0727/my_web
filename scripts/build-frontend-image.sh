#!/bin/bash

# 前端镜像打包脚本
# 支持直接依赖管理和ID引用

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
    
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    
    log_success "工具检查完成"
}

# 生成依赖ID
generate_dependency_id() {
    log_info "生成前端依赖ID..."
    
    cd frontend
    if [ -f "package-lock.json" ]; then
        # 基于package-lock.json生成依赖ID
        DEPENDENCY_ID=$(sha256sum package-lock.json | cut -d' ' -f1)
        echo $DEPENDENCY_ID > ../frontend-dependency-id.txt
        log_info "依赖ID: $DEPENDENCY_ID"
    elif [ -f "yarn.lock" ]; then
        # 如果使用yarn
        DEPENDENCY_ID=$(sha256sum yarn.lock | cut -d' ' -f1)
        echo $DEPENDENCY_ID > ../frontend-dependency-id.txt
        log_info "依赖ID: $DEPENDENCY_ID"
    else
        # 如果只有package.json
        DEPENDENCY_ID=$(sha256sum package.json | cut -d' ' -f1 | head -c 12)
        echo $DEPENDENCY_ID > ../frontend-dependency-id.txt
        log_info "依赖ID: $DEPENDENCY_ID"
    fi
    cd ..
}

# 构建前端镜像
build_frontend_image() {
    log_info "构建前端镜像..."
    
    # 获取依赖ID用于标签
    if [ -f "frontend-dependency-id.txt" ]; then
        TAG=$(cat frontend-dependency-id.txt | head -c 12)
    else
        TAG="latest"
    fi
    
    # 构建镜像
    docker build -f Dockerfile.frontend \
        -t myweb-frontend:${TAG} \
        -t myweb-frontend:latest \
        --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
        --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown") \
        .
    
    log_success "前端镜像构建完成"
    echo "镜像标签: myweb-frontend:${TAG}"
    echo "镜像标签: myweb-frontend:latest"
}

# 推送镜像到仓库
push_image() {
    log_info "推送镜像到仓库..."
    
    if [ -f "frontend-dependency-id.txt" ]; then
        TAG=$(cat frontend-dependency-id.txt | head -c 12)
    else
        TAG="latest"
    fi
    
    docker push myweb-frontend:${TAG}
    docker push myweb-frontend:latest
    
    log_success "镜像推送完成"
}

# 列出可用镜像
list_images() {
    log_info "前端镜像列表:"
    docker images myweb-frontend --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

# 清理旧镜像
cleanup_images() {
    log_info "清理旧镜像..."
    
    # 删除悬空镜像
    docker image prune -f
    
    # 删除旧版本镜像（保留最新的3个）
    OLD_IMAGES=$(docker images myweb-frontend --format "{{.ID}}" | tail -n +4)
    if [ ! -z "$OLD_IMAGES" ]; then
        echo $OLD_IMAGES | xargs -r docker rmi
    fi
    
    log_success "镜像清理完成"
}

# 显示依赖信息
show_dependencies() {
    log_info "前端依赖信息:"
    if [ -f "frontend/package.json" ]; then
        echo "=== Package Dependencies ==="
        grep -A 20 '"dependencies":' frontend/package.json
        echo ""
        echo "=== Dev Dependencies ==="
        grep -A 20 '"devDependencies":' frontend/package.json
    fi
    
    if [ -f "frontend-dependency-id.txt" ]; then
        echo "=== Dependency ID ==="
        echo "ID: $(cat frontend-dependency-id.txt)"
    fi
}

# 显示帮助信息
show_help() {
    echo "前端镜像打包脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  build        构建前端镜像"
    echo "  push         推送镜像到仓库"
    echo "  list         列出前端镜像"
    echo "  cleanup      清理旧镜像"
    echo "  deps         显示依赖信息"
    echo "  all          执行完整构建流程（生成ID -> 构建 -> 推送）"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build     # 构建前端镜像"
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
            generate_dependency_id
            build_frontend_image
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
        all)
            check_tools
            generate_dependency_id
            build_frontend_image
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