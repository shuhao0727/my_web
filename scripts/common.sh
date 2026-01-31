#!/bin/bash

# 构建脚本公共函数库

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
    
    # 检查Python3
    if [ "$1" = "backend" ] && ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装（后端构建需要）"
        exit 1
    fi
    
    # 检查npm
    if [ "$1" = "frontend" ] && ! command -v npm &> /dev/null; then
        log_error "npm 未安装（前端构建需要）"
        exit 1
    fi
    
    log_success "工具检查完成"
}

# 清理临时文件
cleanup_temp_files() {
    log_info "清理临时构建文件..."
    
    # 删除依赖ID文件
    rm -f backend-dependency-id.txt frontend-dependency-id.txt
    
    # 删除typst缓存配置文件（保留二进制文件）
    rm -f .typst-cache.env
    
    # 删除构建过程中的临时文件
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -type f -delete 2>/dev/null || true
    
    log_success "临时文件清理完成"
}

# 显示帮助信息模板
show_help_template() {
    local script_name="$1"
    local description="$2"
    
    echo "$description"
    echo ""
    echo "用法: $script_name [选项]"
    echo ""
    echo "选项:"
    echo "  build        构建镜像（包含依赖检查和缓存）"
    echo "  push         推送镜像到仓库"
    echo "  list         列出镜像"
    echo "  cleanup      清理旧镜像"
    echo "  deps         显示依赖信息"
    echo "  cache-clean  清理构建缓存"
    echo "  all          执行完整构建流程（检查缓存 -> 生成ID -> 构建 -> 推送）"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $script_name build     # 构建镜像"
    echo "  $script_name all       # 完整构建流程"
}

# 检查依赖ID文件
check_dependency_id_file() {
    local type="$1"  # backend or frontend
    
    if [ "$type" = "backend" ] && [ -f "backend-dependency-id.txt" ]; then
        cat backend-dependency-id.txt | head -c 12
        return 0
    elif [ "$type" = "frontend" ] && [ -f "frontend-dependency-id.txt" ]; then
        cat frontend-dependency-id.txt | head -c 12
        return 0
    else
        echo "latest"
        return 1
    fi
}