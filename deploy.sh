#!/bin/bash

# MyWeb 项目部署脚本
# 支持开发模式和生产模式部署

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

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."

    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi

    # 检查 npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi

    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip 未安装"
        exit 1
    fi

    # 检查 Typst (可选)
    if ! command -v typst &> /dev/null; then
        log_warning "Typst 未安装 (可选，用于文档渲染)"
    else
        log_info "Typst 已安装: $(typst --version)"
    fi

    # 检查 Docker (可选)
    if command -v docker &> /dev/null; then
        log_info "Docker 已安装: $(docker --version)"
    else
        log_warning "Docker 未安装 (可选，用于容器化部署)"
    fi

    log_success "依赖检查完成"
}

# 安装 Python 依赖
install_python_deps() {
    log_info "安装 Python 依赖..."
    
    cd backend
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        log_success "Python 依赖安装完成"
    else
        log_error "backend/requirements.txt 不存在"
        exit 1
    fi
    cd ..
}

# 安装 Node.js 依赖
install_node_deps() {
    log_info "安装 Node.js 依赖..."
    
    cd frontend
    if [ -f "package.json" ]; then
        npm install
        log_success "Node.js 依赖安装完成"
    else
        log_error "frontend/package.json 不存在"
        exit 1
    fi
    cd ..
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info "已从 .env.example 创建 .env 文件"
            log_warning "请根据需要编辑 .env 文件"
        else
            log_warning ".env 和 .env.example 都不存在"
        fi
    fi
}

# 启动开发模式
start_dev() {
    log_info "启动开发模式..."

    # 启动后端
    echo "启动后端服务..."
    cd backend
    python3 main.py &
    BACKEND_PID=$!
    cd ..

    # 等待后端启动
    sleep 3

    # 启动前端
    echo "启动前端服务..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    log_success "开发模式启动完成"
    echo "前端: http://localhost:6608"
    echo "后端: http://localhost:8000"

    # 等待进程
    wait $BACKEND_PID $FRONTEND_PID
}

# 构建生产版本
build_production() {
    log_info "构建生产版本..."

    # 构建前端
    cd frontend
    npm run build
    log_success "前端构建完成"
    cd ..

    log_success "生产版本构建完成"
}

# 构建前端镜像
build_frontend_image() {
    log_info "构建前端镜像..."

    # 生成依赖ID
    if [ -f "frontend/package-lock.json" ]; then
        DEPENDENCY_ID=$(sha256sum frontend/package-lock.json | cut -d' ' -f1 | head -c 12)
    else
        DEPENDENCY_ID=$(sha256sum frontend/package.json | cut -d' ' -f1 | head -c 12)
    fi

    # 检查本地是否存在所需的node镜像
    if ! docker images | grep -q "node.*20-alpine"; then
        log_error "本地未找到node:20-alpine镜像，请先拉取或使用已存在的镜像"
        log_info "本地node镜像列表:"
        docker images node
        exit 1
    fi

    # 设置Docker构建时的代理环境变量
    export DOCKER_BUILDKIT=1
    export BUILDKIT_PROXY=http://192.168.5.81:7897

    # 构建镜像并打标签，使用本地镜像
    docker build -f Dockerfile.frontend \
        -t myweb-frontend:${DEPENDENCY_ID} \
        -t myweb-frontend:latest \
        --build-arg BASE_IMAGE=node:20-alpine \
        --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
        --build-arg DEPENDENCY_ID=${DEPENDENCY_ID} \
        --network=host \
        --progress=plain \
        .

    log_success "前端镜像构建完成"
    echo "镜像标签: myweb-frontend:${DEPENDENCY_ID}"
    echo "镜像标签: myweb-frontend:latest"
    echo "依赖ID: ${DEPENDENCY_ID}"
    echo "使用本地镜像: node:20-alpine"
}

# 构建后端镜像
build_backend_image() {
    log_info "构建后端镜像..."

    # 生成依赖ID
    if [ -f "backend/requirements.txt" ]; then
        DEPENDENCY_ID=$(sha256sum backend/requirements.txt | cut -d' ' -f1 | head -c 12)
    else
        DEPENDENCY_ID=$(date +%s)
    fi

    # 构建镜像并打标签，使用本地镜像
    docker build -f Dockerfile.backend \
        -t myweb-backend:${DEPENDENCY_ID} \
        -t myweb-backend:latest \
        --build-arg BASE_IMAGE=python:3.11-slim \
        --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
        --build-arg DEPENDENCY_ID=${DEPENDENCY_ID} \
        .

    log_success "后端镜像构建完成"
    echo "镜像标签: myweb-backend:${DEPENDENCY_ID}"
    echo "镜像标签: myweb-backend:latest"
    echo "依赖ID: ${DEPENDENCY_ID}"
}

# 构建所有镜像
build_all_images() {
    build_backend_image
    build_frontend_image
}

# 启动 Docker 容器
start_docker() {
    log_info "启动 Docker 容器..."

    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose 未安装"
        exit 1
    fi

    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d --build
        log_success "Docker 容器启动完成"
        echo "前端: http://localhost:6608"
        echo "后端: http://localhost:8000"
    else
        log_error "docker-compose.yml 不存在"
        exit 1
    fi
}

# 启动 Docker 容器 (X86_64架构优化)
start_docker_optimized() {
    log_info "启动 Docker 容器 (X86_64架构优化)..."

    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose 未安装"
        exit 1
    fi

    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d --build --force-recreate
        log_success "Docker 容器 (X86_64优化) 启动完成"
        echo "前端: http://localhost:6608"
        echo "后端: http://localhost:8000"
    else
        log_error "docker-compose.yml 不存在"
        exit 1
    fi
}

# 启动生产环境 Docker 容器
start_docker_prod() {
    log_info "启动生产环境 Docker 容器..."

    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose 未安装"
        exit 1
    fi

    if [ -f "docker-compose.prod.yml" ]; then
        docker-compose -f docker-compose.prod.yml up -d --build
        log_success "生产环境 Docker 容器启动完成"
        echo "前端: http://localhost:6608"
        echo "后端: http://localhost:8000"
    else
        log_error "docker-compose.prod.yml 不存在"
        exit 1
    fi
}

# 停止 Docker 容器
stop_docker() {
    log_info "停止 Docker 容器..."

    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        log_success "Docker 容器已停止"
    else
        log_error "docker-compose.yml 不存在"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "MyWeb 项目部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  deps            安装依赖"
    echo "  setup           配置环境"
    echo "  dev             启动开发模式"
    echo "  build           构建生产版本"
    echo "  build-frontend  构建前端镜像"
    echo "  build-backend   构建后端镜像"
    echo "  build-all       构建所有镜像"
    echo "  docker-start    启动 Docker 容器"
    echo "  docker-optimize 启动 Docker 容器 (X86_64架构优化)"
    echo "  docker-prod     启动生产环境 Docker 容器"
    echo "  docker-stop     停止 Docker 容器"
    echo "  docker-restart  重启 Docker 容器"
    echo "  clean           清理构建文件"
    echo "  help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deps          # 安装所有依赖"
    echo "  $0 dev           # 启动开发模式"
    echo "  $0 build-frontend # 构建前端镜像（带依赖ID）"
    echo "  $0 build-all     # 构建所有镜像"
    echo "  $0 docker-start  # 启动 Docker 容器"
    echo "  $0 docker-optimize  # 启动 X86_64架构优化的 Docker 容器"
    echo "  $0 docker-prod   # 启动生产环境 Docker 容器"
}

# 清理构建文件
clean_build() {
    log_info "清理构建文件..."

    # 清理前端构建文件
    if [ -d "frontend/.next" ]; then
        rm -rf frontend/.next
        log_info "清理前端构建文件"
    fi

    # 清理 Python 缓存
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    log_success "清理完成"
}

# 重启 Docker 容器
restart_docker() {
    log_info "重启 Docker 容器..."
    
    stop_docker
    sleep 2
    start_docker
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi

    case $1 in
        deps)
            check_dependencies
            install_python_deps
            install_node_deps
            ;;
        setup)
            setup_env
            ;;
        dev)
            check_dependencies
            setup_env
            start_dev
            ;;
        build)
            check_dependencies
            setup_env
            install_python_deps
            install_node_deps
            build_production
            ;;
        build-frontend)
            check_dependencies
            build_frontend_image
            ;;
        build-backend)
            check_dependencies
            build_backend_image
            ;;
        build-all)
            check_dependencies
            build_all_images
            ;;
        docker-start)
            check_dependencies
            setup_env
            start_docker
            ;;
        docker-optimize)
            check_dependencies
            setup_env
            start_docker_optimized
            ;;
        docker-prod)
            check_dependencies
            setup_env
            start_docker_prod
            ;;
        docker-stop)
            stop_docker
            ;;
        docker-restart)
            restart_docker
            ;;
        clean)
            clean_build
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