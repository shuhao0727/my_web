#!/bin/bash
# 服务监控脚本 - 定期检查后端服务状态，崩溃时自动重启
# 建议将此脚本加入crontab：*/5 * * * * /path/to/monitor_service.sh

SERVICE_NAME="my_web_backend"
PORT=8000
PID_FILE="/tmp/${SERVICE_NAME}.pid"
APP_DIR="/Volumes/文件/4-实用代码/my_web/backend"
START_SCRIPT="${APP_DIR}/start_service.sh"
LOG_FILE="${APP_DIR}/monitor.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo -e "${GREEN}[$SERVICE_NAME监控]${NC} $1"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$LOG_FILE"
    echo -e "${RED}[$SERVICE_NAME监控]${NC} $1"
}

log_warning() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1" >> "$LOG_FILE"
    echo -e "${YELLOW}[$SERVICE_NAME监控]${NC} $1"
}

# 检查服务状态
check_service() {
    # 检查端口是否被占用
    if lsof -i :$PORT > /dev/null 2>&1; then
        # 检查健康端点
        if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
            return 0  # 服务正常
        else
            return 1  # 端口被占用但服务不健康
        fi
    else
        return 2  # 服务未运行
    fi
}

# 重启服务
restart_service() {
    log "尝试重启服务..."
    if [ -x "$START_SCRIPT" ]; then
        cd "$APP_DIR"
        "$START_SCRIPT" stop >> "$LOG_FILE" 2>&1
        sleep 3
        "$START_SCRIPT" start >> "$LOG_FILE" 2>&1
        sleep 5
        
        # 检查重启是否成功
        if check_service; then
            log "服务重启成功"
            return 0
        else
            log_error "服务重启失败"
            return 1
        fi
    else
        log_error "启动脚本不存在或不可执行: $START_SCRIPT"
        return 1
    fi
}

# 主监控循环
main() {
    log "开始监控服务..."
    
    # 检查启动脚本
    if [ ! -x "$START_SCRIPT" ]; then
        log_error "启动脚本不存在或不可执行，请检查: $START_SCRIPT"
        exit 1
    fi
    
    # 检查服务状态
    check_service
    STATUS=$?
    
    case $STATUS in
        0)
            PID=$(cat "$PID_FILE" 2>/dev/null || ps aux | grep -E "uvicorn.*main:app.*$PORT" | grep -v grep | awk '{print $2}' | head -1)
            log "服务运行正常 (PID: $PID)"
            ;;
        1)
            log_warning "端口 $PORT 被占用，但服务不健康，尝试重启..."
            restart_service
            ;;
        2)
            log_warning "服务未运行，尝试启动..."
            restart_service
            ;;
    esac
    
    log "监控检查完成"
}

# 执行主函数
main

exit 0
