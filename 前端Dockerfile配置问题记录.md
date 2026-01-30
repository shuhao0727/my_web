# 前端Dockerfile配置问题记录

## 问题发现时间
2026年1月30日 08:24

## 问题描述

### 发现的问题
在配置检查过程中，发现前端Dockerfile存在配置冲突问题，可能影响生产模式下API代理的正常工作。

### 具体问题点
```dockerfile
# frontend/Dockerfile 第13-14行
ENV NEXT_PUBLIC_API_URL=http://localhost:8000           # 构建时设置的默认值
ENV NEXT_PUBLIC_API_URL_INTERNAL=http://backend:8000   # 多余的配置
```

### 问题分析
1. **构建时与运行时配置冲突**：
   - Dockerfile中的环境变量在镜像构建时被设置
   - `standalone`构建产物（`frontend/.next/standalone/`）是在本地构建时生成的
   - 如果构建时使用了`localhost:8000`，运行时通过docker-compose覆盖可能无效

2. **多环境变量配置混乱**：
   - `NEXT_PUBLIC_API_URL_INTERNAL`变量在Next.js配置中未使用
   - 存在多个类似的API地址配置，容易混淆

3. **潜在风险**：
   - 生产模式下前端可能尝试连接`localhost:8000`而非`backend:8000`
   - 可能导致API代理失败，前端无法访问后端服务

## 相关配置文件

### 1. docker-compose.yml（当前生产模式配置）
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
    args:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://backend:8000}
  environment:
    NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://backend:8000}
    NODE_ENV=${NODE_ENV:-production}
    FRONTEND_MODE=${FRONTEND_MODE:-production}
```

### 2. .env文件（当前生产模式）
```bash
NEXT_PUBLIC_API_URL=
ENVIRONMENT=production
NODE_ENV=production
FRONTEND_MODE=production
```

### 3. frontend/next.config.ts
```typescript
async rewrites() {
  const isProduction = process.env.NODE_ENV === 'production';
  const apiUrl = isProduction 
    ? 'http://backend:8000' 
    : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  console.log('API Proxy URL:', apiUrl, '(Environment:', process.env.NODE_ENV, ')');
  
  return [...];
}
```

## 影响范围
- 生产模式下的前端容器
- API代理功能
- 前后端通信

## 解决方案建议

### 方案A：修复前端Dockerfile（推荐）
```dockerfile
# 修改frontend/Dockerfile
# 移除硬编码的API地址，改为运行时设置
# FROM node:20-alpine
# ... 其他配置不变 ...
# 移除这两行：
# ENV NEXT_PUBLIC_API_URL=http://localhost:8000
# ENV NEXT_PUBLIC_API_URL_INTERNAL=http://backend:8000
# 添加运行时环境变量占位符
# ENV NEXT_PUBLIC_API_URL=""
```

### 方案B：确保正确构建standalone产物
1. 在构建前端镜像前，确保本地构建时设置了正确的环境变量：
   ```bash
   NEXT_PUBLIC_API_URL=http://backend:8000 npm run build
   ```

2. 验证构建产物中的API地址配置

### 方案C：使用多阶段构建分离构建和运行时
```dockerfile
# 阶段1：构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL} npm run build

# 阶段2：运行阶段
FROM node:20-alpine AS runner
WORKDIR /app
# 复制构建产物
COPY --from=builder /app/.next/standalone/ ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
# ... 其他配置 ...
```

## 测试计划

### 测试步骤
1. **启动当前配置的服务**
   ```bash
   docker-compose up -d
   ```

2. **验证API代理功能**
   - 访问前端页面
   - 检查浏览器控制台错误
   - 查看前端容器日志

3. **如果发现问题，执行修复**
   - 修改前端Dockerfile
   - 重新构建前端镜像
   - 重启服务验证

### 验证方法
1. **日志检查**：
   ```bash
   docker-compose logs -f frontend | grep -E "(API Proxy|ECONNREFUSED|Error)"
   ```

2. **健康检查**：
   ```bash
   curl -f http://localhost/health
   curl -f http://localhost:6608/favicon.ico
   ```

3. **API测试**：
   ```bash
   curl -f http://localhost/api/health
   ```

## 相关依赖

### 需要检查的文件
- `frontend/.next/standalone/` - standalone构建产物目录是否存在
- `frontend/.next/standalone/server.js` - 运行时服务器文件
- `frontend/.next/standalone/.next/routes-manifest.json` - 路由配置

### 环境依赖
- Node.js环境变量处理机制
- Next.js standalone模式的运行时行为
- Docker环境变量覆盖优先级

## 风险评估
- **高风险**：如果问题存在，生产环境前端无法访问后端API
- **中风险**：需要重新构建前端镜像
- **低风险**：配置修改可能影响开发模式

## 后续操作
1. 记录当前问题状态
2. 进行镜像测试验证问题是否存在
3. 根据测试结果决定修复方案
4. 更新相关文档

## 更新记录
- 2026-01-30 08:24：首次发现问题并记录

---

*文档生成时间：2026年1月30日 08:26*
*检查人员：Cline AI助手*
*当前状态：待测试验证*