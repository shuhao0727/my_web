# MyWeb 环境变量配置指南

本文档详细说明了MyWeb项目中所有可配置的环境变量，以及如何在不同环境中使用它们来避免硬编码。

## 全局环境变量

### 基础配置
- `APP_ENV`: 应用环境 (development|production|test)，默认值：`development`
- `APP_DEBUG`: 调试模式开关 (true|false)，默认值：`true`
- `APP_NAME`: 应用名称，默认值：`MyWeb`

### 服务端口配置
- `BACKEND_HOST`: 后端服务主机，默认值：`0.0.0.0`
- `BACKEND_PORT`: 后端服务端口，默认值：`8000`
- `FRONTEND_HOST`: 前端服务主机，默认值：`localhost`
- `FRONTEND_PORT`: 前端服务端口，默认值：`3000`
- `EXTERNAL_HOST`: 外部访问主机，默认值：`localhost`
- `EXTERNAL_PORT`: 外部访问端口，默认值：`6608`

### 数据库配置
- `DATABASE_URL`: 主数据库连接URL，默认值：`sqlite:///./xbk.db`
- `AI_DATABASE_URL`: AI模块数据库URL，默认值：`sqlite:///./znt.db`
- `XBK_DB_PATH`: XBK数据库路径，默认值：`./xbk.db`
- `ZNT_DB_PATH`: AI数据库路径，默认值：`./znt.db`
- `DB_POOL_SIZE`: 数据库连接池大小，默认值：`20`
- `DB_POOL_OVERFLOW`: 数据库连接池溢出，默认值：`10`
- `DB_ECHO`: 数据库日志开关 (true|false)，默认值：`false`

## 前端环境变量

### API配置
- `NEXT_PUBLIC_API_URL`: 后端API基础URL，默认值：`${BACKEND_URL:-http://backend:8000}`
- `NEXT_PUBLIC_API_URL_INTERNAL`: 内部API基础URL，默认值：`${BACKEND_URL:-http://backend:8000}`
- `NEXT_PUBLIC_BASE_PATH`: 应用基础路径，无默认值

### 运行时配置
- `NODE_ENV`: Node.js环境 (development|production)，默认值：`development`
- `PORT`: 前端服务端口，默认值：`3000`

## 后端环境变量

### CORS配置
- `ALLOWED_ORIGINS`: 允许的源站点，默认值：`*`

### 内容目录配置
- `CONTENT_DIR`: 内容文件目录，默认值：`./content`
- `GITHUB_REPO_NAME`: GitHub仓库名称，默认值：`2-My-notes`

### 认证配置
- `XBK_JWT_SECRET_KEY`: XBK模块JWT密钥
- `JWT_SECRET_KEY`: AI模块JWT密钥
- `ADMIN_USERNAME`: 管理员用户名，默认值：`admin`
- `WANGSHU_USERNAME`: 特定用户用户名，默认值：`wangshu0727`
- `WANGSHU_PASSWORD`: 特定用户密码

### GitHub配置
- `GITHUB_ACCESS_TOKEN`: GitHub访问令牌
- `GITHUB_OWNER`: GitHub仓库所有者

### AI服务配置
- `DIFY_API_KEY`: Dify API密钥
- `DIFY_APP_ID`: Dify应用ID
- `DEEPSEEK_API_KEY`: DeepSeek API密钥

### 同步与调度配置
- `ENABLE_AUTO_SYNC`: 启用自动同步 (true|false)，默认值：`false`
- `SYNC_INTERVAL_SECONDS`: 同步间隔秒数，默认值：`3600`

### 日志配置
- `LOG_LEVEL`: 日志级别 (DEBUG|INFO|WARNING|ERROR)，默认值：`INFO`
- `LOG_FILE`: 日志文件路径，默认值：`backend.log`

## Docker环境变量

### 镜像构建配置
- `DOCKER_REGISTRY`: Docker镜像仓库
- `IMAGE_TAG`: 镜像标签，默认值：`latest`
- `DOMAIN_NAME`: 域名配置

### 构建优化配置
- `BUILDKIT_PROXY`: BuildKit代理配置
- `BASE_IMAGE`: 基础镜像配置

## Nginx代理配置

Nginx使用服务发现机制，通过以下方式确定后端服务：

- 后端服务名称: `backend`
- 后端端口: `8000`
- 前端服务名称: `frontend`
- 前端端口: `3000`

## 环境特定配置

### 开发环境
```bash
# 开发环境推荐配置
APP_ENV=development
APP_DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:6608,*
EXTERNAL_PORT=6608
```

### 生产环境
```bash
# 生产环境推荐配置
APP_ENV=production
APP_DEBUG=false
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
EXTERNAL_HOST=your-domain.com
EXTERNAL_PORT=443
```

### 测试环境
```bash
# 测试环境推荐配置
APP_ENV=test
APP_DEBUG=false
ALLOWED_ORIGINS=*
EXTERNAL_PORT=6608
```

## 环境变量优先级

配置项的优先级从高到低：
1. Docker容器内的环境变量
2. 宿主机的环境变量
3. `.env` 文件中的配置
4. 环境变量默认值

## 最佳实践

### 1. 避免硬编码
- 不要在代码中硬编码任何主机名、端口或URL
- 使用环境变量来配置服务地址
- 使用默认值来保证向后兼容

### 2. 环境隔离
- 为不同环境使用不同的环境变量文件
- 敏感信息使用加密存储
- 使用配置管理工具来管理环境变量

### 3. 服务发现
- 使用服务名称而不是IP地址
- 依赖Docker网络来处理服务间的通信
- 使用DNS解析来获取服务地址

### 4. 安全考虑
- 不要在日志中输出敏感环境变量
- 使用只读权限保护环境变量文件
- 定期轮换敏感密钥

## 常见配置示例

### 本地开发配置
```bash
# .env.development
APP_ENV=development
EXTERNAL_HOST=localhost
EXTERNAL_PORT=6608
BACKEND_PORT=8000
FRONTEND_PORT=3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:6608,*
```

### 生产环境配置
```bash
# .env.production
APP_ENV=production
EXTERNAL_HOST=your-domain.com
EXTERNAL_PORT=443
BACKEND_PORT=8000
FRONTEND_PORT=3000
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
APP_DEBUG=false
```

### Docker Compose配置
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - BACKEND_PORT=8000
      - EXTERNAL_HOST=${EXTERNAL_HOST:-localhost}
      - EXTERNAL_PORT=${EXTERNAL_PORT:-6608}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-*}
```

通过使用环境变量，您可以轻松地在不同环境中部署应用程序，而无需修改代码或配置文件。