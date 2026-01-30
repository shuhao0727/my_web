# 使用Node.js镜像（AMD64架构）
FROM node:20-alpine

# 设置构建参数（代理配置）
ARG HTTP_PROXY
ARG HTTPS_PROXY

WORKDIR /app

# 环境变量配置
ENV PORT=6608
ENV HOST=0.0.0.0
ENV NODE_ENV=production

# 代理设置 - 移除以避免影响健康检查和内部网络通信
# ENV http_proxy=${HTTP_PROXY}
# ENV https_proxy=${HTTPS_PROXY}
# ENV HTTP_PROXY=${HTTP_PROXY}
# ENV HTTPS_PROXY=${HTTPS_PROXY}

# 创建非root用户
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 配置Alpine国内镜像源
RUN mkdir -p /etc/apk/conf.d/ && \
    echo "https://mirrors.ustc.edu.cn/alpine/v3.19/main" > /etc/apk/repositories && \
    echo "https://mirrors.ustc.edu.cn/alpine/v3.19/community" >> /etc/apk/repositories && \
    rm -rf /etc/apk/conf.d/proxy.conf 2>/dev/null || true && \
    echo 'http_proxy=' > /etc/apk/conf.d/no-proxy.conf && \
    echo 'https_proxy=' >> /etc/apk/conf.d/no-proxy.conf && \
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# 配置npm国内镜像源
RUN unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && \
    npm config set registry https://registry.npmmirror.com

# 安装健康检查工具
RUN unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && \
    apk add --no-cache curl

# 复制standalone构建产物
COPY ./.next/standalone/ ./
COPY ./.next/static ./.next/static
COPY ./public ./public

# 复制启动脚本并设置权限
COPY ./start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 更改文件所有者
RUN chown -R nextjs:nodejs /app

# 切换到非root用户
USER nextjs

# 暴露端口
EXPOSE 6608

# 使用自定义启动脚本启动Next.js服务器
CMD ["/app/start.sh"]
