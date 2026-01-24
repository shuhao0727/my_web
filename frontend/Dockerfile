# 使用 Node.js 20 LTS 官方镜像
FROM node:20-alpine AS base

# 安装依赖阶段 - 安装所有依赖（包括devDependencies）
FROM base AS deps
RUN apk add --no-cache libc6-compat git
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# 构建阶段
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# 设置构建环境变量
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# 运行阶段 - 最小化镜像
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=6608
ENV HOSTNAME="0.0.0.0"
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 创建必要的目录并设置权限
RUN mkdir -p /app/.next && \
    chown -R nextjs:nodejs /app

# 复制构建产物
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 6608

CMD ["node", "server.js"]
