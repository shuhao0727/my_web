# ==================== 构建阶段 ====================
FROM node:20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制包管理文件
COPY package.json package-lock.json ./

# 安装依赖（包括开发依赖，用于构建）
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# ==================== 生产阶段 ====================
FROM node:20-alpine AS production

# 设置环境变量
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=6608

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 从构建阶段复制必要文件
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# 切换到非root用户
USER nextjs

# 暴露端口
EXPOSE 6608

# 启动命令（生产环境）
CMD ["node", "server.js"]

# ==================== 开发阶段 ====================
FROM node:20-alpine AS development

# 设置环境变量
ENV NODE_ENV=development \
    PORT=6608

# 设置工作目录
WORKDIR /app

# 复制包管理文件
COPY package.json package-lock.json ./

# 安装所有依赖（包括开发依赖）
RUN npm ci

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 6608

# 启动开发服务器
CMD ["npm", "run", "dev"]