#!/bin/bash

# 构建所有服务的AMD64镜像
# 包括前端和后端服务

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
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    log_success "工具检查完成"
}

# 构建前端AMD64镜像
build_frontend_amd64() {
    log_info "开始构建前端AMD64镜像..."
    
    cd ..  # 回到项目根目录
    ./scripts/build-frontend-image.sh build amd64
    cd scripts
    
    log_success "前端AMD64镜像构建完成"
}

# 构建后端AMD64镜像
build_backend_amd64() {
    log_info "开始构建后端AMD64镜像..."
    
    cd ..  # 回到项目根目录
    ./scripts/build-backend-image.sh build amd64
    cd scripts
    
    log_success "后端AMD64镜像构建完成"
}

# 验证镜像架构
verify_architecture() {
    log_info "验证镜像架构..."
    
    echo "前端镜像架构:"
    if [ "$(docker images myweb-frontend:latest --format '{{.Architecture}}')" = "amd64" ]; then
        echo "✓ myweb-frontend:latest 是 AMD64 架构"
    else
        echo "✗ myweb-frontend:latest 是 $(docker images myweb-frontend:latest --format '{{.Architecture}}') 架构"
    fi
    
    echo "后端镜像架构:"
    if [ "$(docker images myweb-backend:latest --format '{{.Architecture}}')" = "amd64" ]; then
        echo "✓ myweb-backend:latest 是 AMD64 架构"
    else
        echo "✗ myweb-backend:latest 是 $(docker images myweb-backend:latest --format '{{.Architecture}}') 架构"
    fi
}

# 显示帮助信息
show_help() {
    echo "AMD64镜像构建脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  all          构建前端和后端AMD64镜像"
    echo "  frontend     仅构建前端AMD64镜像"
    echo "  backend      仅构建后端AMD64镜像"
    echo "  verify       验证已构建镜像的架构"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 all       # 构建所有AMD64镜像"
    echo "  $0 frontend  # 仅构建前端AMD64镜像"
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi

    case $1 in
        all)
            check_tools
            build_frontend_amd64
            build_backend_amd64
            verify_architecture
            log_success "所有AMD64镜像构建完成"
            ;;
        frontend)
            check_tools
            build_frontend_amd64
            verify_architecture
            log_success "前端AMD64镜像构建完成"
            ;;
        backend)
            check_tools
            build_backend_amd64
            verify_architecture
            log_success "后端AMD64镜像构建完成"
            ;;
        verify)
            verify_architecture
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