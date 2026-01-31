# MyWeb 项目配置说明

## 配置文件概览

本项目使用以下主要配置文件：

### Docker Compose 配置
- `docker-compose.dev.yml` - 开发环境配置
- `docker-compose.prod.amd.yml` - 生产环境配置 (AMD64架构)

### Docker 镜像配置
- `Dockerfile.backend` - 后端服务Dockerfile
- `Dockerfile.frontend` - 前端服务Dockerfile

### Nginx 配置
- `nginx.conf` - 生产环境Nginx配置
- `nginx.dev.conf` - 开发环境Nginx配置

### 环境变量配置
- `.env.example` - 环境变量示例文件
- `.env` - 实际环境变量文件（需手动创建）

## Docker Compose 配置详解

### 开发环境配置 (docker-compose.dev.yml)

**特点：**
- 本地构建镜像
- 暴露所有端口用于调试
- 支持热重载
- 卷挂载便于开发

**服务配置：**
- **Backend**: 
  - 端口: 8000 (内部)
  - 卷挂载: ./backend:/app
  - 环境: development

- **Frontend**:
  - 端口: 3000 (内部)
  - 卷挂载: ./frontend:/app
  - 环境: development

- **Nginx**:
  - 外部端口: 6608
  - 配置: nginx.dev.conf
  - 代理API请求到后端

### 生产环境配置 (docker-compose.prod.amd.yml)

**特点：**
- 使用预构建镜像
- 不暴露后端端口
- 优化性能配置
- AMD64架构优化

**服务配置：**
- **Backend**:
  - 镜像: shuhao07/my_web-backend:latest-amd64
  - 端口: 8000 (仅内部)
  - 环境: production
  - 访问限制: 仅内部网络

- **Frontend**:
  - 镜像: shuhao07/my_web-frontend:latest-amd64
  - 环境: production

- **Nginx**:
  - 外部端口: 6608
  - 配置: nginx.prod.conf
  - 安全头设置

## 部署说明

### 开发环境部署
```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 停止开发环境
docker-compose -f docker-compose.dev.yml down

# 构建并启动
docker-compose -f docker-compose.dev.yml up -d --build
```

### 生产环境部署
```bash
# 启动生产环境
docker-compose -f docker-compose.prod.amd.yml up -d

# 停止生产环境
docker-compose -f docker-compose.prod.amd.yml down

# 构建并启动
docker-compose -f docker-compose.prod.amd.yml up -d --build
```

## 网络配置

### 端口分配
- **6608**: 外部访问端口（Nginx代理）
- **8000**: 内部后端端口（仅容器间通信）
- **3000**: 内部前端端口（仅容器间通信）

### 代理规则
- `/api/*` → 后端服务:8000
- `/content/*` → 后端服务:8000  
- `/*` (其他) → 前端服务:3000

## 环境变量配置

### 主要环境变量
- `BACKEND_HOST`: 后端主机地址
- `BACKEND_PORT`: 后端端口
- `FRONTEND_HOST`: 前端主机地址
- `FRONTEND_PORT`: 前端端口
- `EXTERNAL_HOST`: 外部访问主机
- `EXTERNAL_PORT`: 外部访问端口
- `ALLOWED_ORIGINS`: CORS允许的源站

### 默认值配置
- `BACKEND_HOST`: 0.0.0.0
- `BACKEND_PORT`: 8000
- `EXTERNAL_PORT`: 6608
- `ALLOWED_ORIGINS`: *

## 安全配置

### 生产环境安全措施
- 后端服务不对外暴露
- CORS策略严格控制
- Nginx安全头设置
- 访问日志记录

### 开发环境安全措施
- 宽松的CORS策略
- 详细的错误信息
- 热重载功能
- 调试模式启用

## 性能优化

### Nginx优化
- 静态文件缓存
- Gzip压缩
- 连接池管理
- 负载均衡支持

### Docker优化
- 多阶段构建
- 镜像层缓存
- 网络优化
- 资源限制设置