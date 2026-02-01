# MyWeb 部署指南

## 概述

本文档提供了MyWeb项目的完整部署指南，包括生产模式和开发模式的各种部署选项，特别针对AMD64架构进行了优化。

## 部署模式

### 1. 生产模式部署

#### 1.1 默认生产模式 (跨平台)
```bash
# 使用预构建的镜像
docker-compose -f docker-compose.prod.local.yml up -d
```

#### 1.2 AMD64 生产模式
```bash
# 构建并运行AMD64架构优化的镜像
docker-compose -f docker-compose.prod.amd64.yml up -d
```

#### 1.3 本地构建生产模式
```bash
# 从本地代码构建并运行（适用于ARM64等非AMD64架构）
docker-compose -f docker-compose.prod.local.yml up -d --build
```

### 2. 开发模式部署

#### 2.1 默认开发模式 (跨平台)
```bash
# 使用预构建镜像的开发模式
docker-compose -f docker-compose.dev.yml up -d
```

#### 2.2 AMD64 开发模式
```bash
# AMD64架构优化的开发模式
docker-compose -f docker-compose.dev.amd64.yml up -d
```

## 镜像构建

### 构建AMD64架构后端镜像
```bash
# 构建AMD64架构的后端镜像
./scripts/build-backend-image.sh build amd64

# 构建AMD64架构的前端镜像
./scripts/build-frontend-image.sh build amd64

# 构建所有架构的镜像
./scripts/build-all-amd64.sh
```

## 配置文件说明

### Docker Compose 文件对比

| 文件 | 用途 | 架构 | 特点 |
|------|------|------|------|
| `docker-compose.prod.local.yml` | 生产模式 | 跨平台 | 使用预构建镜像，适合快速部署 |
| `docker-compose.prod.amd64.yml` | 生产模式 | AMD64 | AMD64优化，性能更好 |
| `docker-compose.dev.yml` | 开发模式 | 跨平台 | 热重载，便于开发调试 |
| `docker-compose.dev.amd64.yml` | 开发模式 | AMD64 | AMD64优化的开发环境 |

### Nginx 配置

- **生产模式**: `nginx.prod.conf`
- **开发模式**: `nginx.dev.conf`

## API 端点验证

部署完成后，可以通过以下端点验证服务：

### 核心 API 端点
```bash
# 系统健康检查
curl http://localhost:6608/health
# 返回: {"status":"healthy","environment":"production","database_status":"connected"}

# XBK 应用信息
curl http://localhost:6608/api/xbk/applications
# 返回: 应用详细信息

# XBK 健康检查
curl http://localhost:6608/api/xbk/health
# 返回: {"status":"healthy"}

# AI 智能体列表
curl http://localhost:6608/api/ai/agents
# 返回: 智能体配置信息

# AI 对话列表
curl http://localhost:6608/api/ai/conversations
# 返回: 对话记录

# Typst 文件树
curl http://localhost:6608/api/typst/tree
# 返回: 文档结构

# 仓库结构
curl http://localhost:6608/api/repo/structure
# 返回: 内容仓库结构
```

### 所有可用 API 端点
- `/api/xbk/applications` - XBK应用信息
- `/api/xbk/health` - XBK健康检查
- `/api/xbk/users` - 用户管理
- `/api/xbk/data/catalog` - 数据目录
- `/api/xbk/login` - 用户登录
- `/api/ai/agents` - AI智能体管理
- `/api/ai/conversations` - AI对话管理
- `/api/ai/data/stats` - AI数据分析
- `/api/ai/auth/users` - AI认证用户
- `/api/typst/tree` - Typst文档树
- `/api/repo/structure` - 仓库结构
- `/api/health` - API健康检查
- `/health` - 系统健康检查

## 环境变量配置

### 生产环境配置 (.env.production)
```bash
APP_ENV=production
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=6608
DATABASE_URL=sqlite:///xbk.db
AI_DATABASE_URL=sqlite:///znt.db
ALLOWED_ORIGINS=http://nginx:6608
```

### 开发环境配置 (.env.development)
```bash
APP_ENV=development
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=6608
DATABASE_URL=sqlite:///xbk.db
AI_DATABASE_URL=sqlite:///znt.db
ALLOWED_ORIGINS=http://localhost:6608,http://nginx:6608
```

## 部署验证步骤

### 1. 启动服务
```bash
docker-compose -f docker-compose.prod.amd64.yml up -d
```

### 2. 等待服务启动
```bash
# 等待至少60秒让所有服务完全启动
sleep 60
```

### 3. 验证所有端点
```bash
# 验证系统健康
curl -s "http://localhost:6608/health"

# 验证XBK服务
curl -s "http://localhost:6608/api/xbk/applications"
curl -s "http://localhost:6608/api/xbk/health"
curl -s "http://localhost:6608/api/xbk/data/catalog"

# 验证AI服务
curl -s "http://localhost:6608/api/ai/agents"
curl -s "http://localhost:6608/api/ai/conversations"

# 验证Typst服务
curl -s "http://localhost:6608/api/typst/tree"
curl -s "http://localhost:6608/api/repo/structure"
```

### 4. 验证前端访问
```bash
# 检查前端页面是否正常加载
curl -s "http://localhost:6608" | head -10
```

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 查看容器日志
   docker logs myweb_backend_prod_amd64
   docker logs myweb_frontend_prod_amd64
   docker logs myweb_nginx_prod_amd64
   ```

2. **API访问失败**
   ```bash
   # 检查容器状态
   docker ps
   docker-compose -f docker-compose.prod.amd64.yml ps
   ```

3. **数据库连接问题**
   ```bash
   # 使用sqlite3检查数据库
   sqlite3 xbk.db .tables
   sqlite3 znt.db .tables
   ```

### 性能监控
```bash
# 查看容器资源使用情况
docker stats myweb_backend_prod_amd64 myweb_frontend_prod_amd64 myweb_nginx_prod_amd64
```

## 维护命令

### 停止服务
```bash
docker-compose -f docker-compose.prod.amd64.yml down
```

### 重启服务
```bash
docker-compose -f docker-compose.prod.amd64.yml down
docker-compose -f docker-compose.prod.amd64.yml up -d
```

### 更新服务
```bash
# 拉取最新镜像并重启
docker-compose -f docker-compose.prod.amd64.yml pull
docker-compose -f docker-compose.prod.amd64.yml up -d
```

### 清理资源
```bash
# 清理未使用的镜像
docker image prune -f

# 清理构建缓存
./scripts/build-backend-image.sh cache-clean
```

## 生产环境最佳实践

1. **使用AMD64架构部署**以获得最佳性能
2. **定期备份数据库** (`xbk.db`, `znt.db`)
3. **监控服务健康状态**
4. **配置SSL证书**用于HTTPS访问
5. **设置日志轮转**防止磁盘空间不足

## 技术栈

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js (React)
- **Database**: SQLite (for simplicity), PostgreSQL (production ready)
- **Proxy**: Nginx
- **Containerization**: Docker + Docker Compose
- **Architecture**: AMD64 optimized