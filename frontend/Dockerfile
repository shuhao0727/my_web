# 使用本地Node.js镜像（避免网络访问）
FROM node@sha256:09e2b3d9726018aecf269bd35325f46bf75046a643a66d28360ec71132750ec8

# 设置工作目录
WORKDIR /app

# 复制standalone构建产物
COPY ./.next/standalone/ ./
COPY ./.next/static ./.next/static
COPY ./public ./public

# 创建非root用户
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 更改文件所有者
RUN chown -R nextjs:nodejs /app

# 切换到非root用户
USER nextjs

# 暴露端口
EXPOSE 6608

# 设置环境变量（可以在运行时覆盖）
ENV PORT=6608
ENV HOST=0.0.0.0
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL_INTERNAL=http://backend:8000

# 启动Next.js服务器
CMD ["node", "server.js"]