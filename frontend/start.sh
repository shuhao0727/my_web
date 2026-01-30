#!/bin/sh
# Next.js Docker启动脚本
# 解决Next.js在容器中绑定到容器ID而不是0.0.0.0的问题
# 设置HOSTNAME环境变量为0.0.0.0，确保Next.js监听所有网络接口

# 设置HOSTNAME环境变量为0.0.0.0
# 这样server.js中的hostname = process.env.HOSTNAME || '0.0.0.0'会优先使用我们设置的值
export HOSTNAME=0.0.0.0

# 清理代理环境变量，避免影响内部网络通信
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# 获取端口配置
PORT="${PORT:-6608}"

echo "Starting Next.js server..."
echo "  - Port: ${PORT}"
echo "  - Hostname: ${HOSTNAME}"
echo "  - Node environment: ${NODE_ENV:-production}"

# 启动Next.js服务器
exec node server.js