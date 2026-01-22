#!/bin/bash
# 后端服务启动脚本 - 避免多进程冲突
# 使用：./start_service.sh [start|stop|restart|status]

SERVICE_NAME="my_web_backend"
PORT=8000
PID_FILE="/tmp/${SERVICE_NAME}.pid"
LOG_FILE="backend.log"
APP_DIR="/Volumes/文件/4-实用代码/my_web/backend"
PYTHON_CMD="python3"
UVICORN_CMD="$PYTHON_CMD -m uvicorn main:app --host 127.0.0.1 --port $PORT --reload"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[$SERVICE_NAME]${NC} $1"
}

print_error() {
    echo -e "${RED}[$SERVICE_NAME]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$SERVICE_NAME]${NC} $1"
}

# 检查端口是否被占用
check_port() {
    if lsof -i :$PORT > /dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 获取进程PID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE" 2>/dev/null
    else
        ps aux | grep -E "uvicorn.*main:app.*$PORT" | grep -v grep | awk '{print $2}' | head -1
    fi
}

# 停止服务
stop_service() {
    print_status "正在停止服务..."
    
    # 方法1: 使用PID文件
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if [ -n "$PID" ] && ps -p $PID > /dev/null 2>&1; then
            kill -TERM $PID 2>/dev/null
            sleep 2
            if ps -p $PID > /dev/null 2>&1; then
                kill -KILL $PID 2>/dev/null
            fi
            print_status "已停止进程 $PID"
        fi
        rm -f "$PID_FILE"
    fi
    
    # 方法2: 杀死所有相关的uvicorn进程
    PIDS=$(ps aux | grep -E "uvicorn.*main:app" | grep -v grep | awk '{print $2}')
    if [ -n "$PIDS" ]; then
        for PID in $PIDS; do
            kill -TERM $PID 2>/dev/null
            sleep 1
            if ps -p $PID > /dev/null 2>&1; then
                kill -KILL $PID 2>/dev/null
            fi
        done
        print_status "已停止所有相关进程"
    fi
    
    # 方法3: 使用pkill（更彻底）
    pkill -f "uvicorn.*main:app" 2>/dev/null
    pkill -f "python.*uvicorn.*main:app" 2>/dev/null
    
    # 等待端口释放
    COUNTER=0
    while check_port && [ $COUNTER -lt 10 ]; do
        sleep 1
        COUNTER=$((COUNTER + 1))
    done
    
    if check_port; then
        print_error "无法释放端口 $PORT，请手动检查"
        return 1
    else
        print_status "服务已完全停止"
        return 0
    fi
}

# 启动服务
start_service() {
    print_status "正在启动服务..."
    
    # 检查是否已在运行
    if check_port; then
        PID=$(get_pid)
        if [ -n "$PID" ] && ps -p $PID > /dev/null 2>&1; then
            print_warning "服务已在运行 (PID: $PID)"
            return 0
        else
            print_warning "端口 $PORT 被占用，但无法找到有效进程，尝试清理..."
            stop_service
        fi
    fi
    
    # 切换到应用目录
    cd "$APP_DIR" || {
        print_error "无法切换到目录: $APP_DIR"
        return 1
    }
    
    # 启动服务
    print_status "启动命令: $UVICORN_CMD"
    nohup $UVICORN_CMD > "$LOG_FILE" 2>&1 &
    PID=$!
    
    # 保存PID
    echo $PID > "$PID_FILE"
    print_status "服务已启动，PID: $PID"
    
    # 等待服务就绪
    print_status "等待服务启动..."
    COUNTER=0
    while [ $COUNTER -lt 30 ]; do
        if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
            print_status "服务启动成功！"
            print_status "日志文件: $APP_DIR/$LOG_FILE"
            print_status "API文档: http://localhost:$PORT/docs"
            print_status "健康检查: http://localhost:$PORT/health"
            return 0
        fi
        sleep 1
        COUNTER=$((COUNTER + 1))
    done
    
    print_error "服务启动超时，请检查日志: $APP_DIR/$LOG_FILE"
    return 1
}

# 重启服务
restart_service() {
    print_status "正在重启服务..."
    stop_service
    sleep 2
    start_service
}

# 查看状态
status_service() {
    if check_port; then
        PID=$(get_pid)
        if [ -n "$PID" ] && ps -p $PID > /dev/null 2>&1; then
            print_status "服务正在运行 (PID: $PID)"
            
            # 检查健康状态
            if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
                print_status "健康检查: 正常"
            else
                print_warning "健康检查: 异常"
            fi
            
            # 显示进程信息
            ps -p $PID -o pid,user,%cpu,%mem,etime,command
            return 0
        else
            print_warning "端口 $PORT 被占用，但无法找到有效进程"
            return 1
        fi
    else
        print_status "服务未运行"
        return 1
    fi
}

# 主逻辑
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        echo ""
        echo "命令说明:"
        echo "  start   启动后端服务"
        echo "  stop    停止后端服务"
        echo "  restart 重启后端服务"
        echo "  status  查看服务状态"
        echo ""
        echo "默认配置:"
        echo "  服务名称: $SERVICE_NAME"
        echo "  端口: $PORT"
        echo "  应用目录: $APP_DIR"
        echo "  PID文件: $PID_FILE"
        echo "  日志文件: $APP_DIR/$LOG_FILE"
        exit 1
        ;;
esac

exit $?
