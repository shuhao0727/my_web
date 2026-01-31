# AMD服务器部署指南

## 部署配置文件说明

对于AMD服务器部署，请使用以下配置文件：

### 生产环境部署 (推荐)
- **配置文件**: `docker-compose.prod.local.yml`
- **用途**: 适用于本地生产环境部署
- **端口**: 6608 (外部访问端口)
- **特点**: 包含完整的Nginx反向代理配置，适合生产环境

### 开发环境部署 (可选)
- **配置文件**: `docker-compose.dev.yml`
- **用途**: 适用于开发调试环境
- **端口**: 6608 (外部访问端口)
- **特点**: 包含开发模式下的热重载功能

## 部署步骤

### 1. 环境准备
```bash
# 确保Docker和Docker Compose已安装
docker --version
docker-compose --version

# 克隆项目代码
git clone <your-repository-url>
cd my_web
```

### 2. 配置环境变量
复制示例环境配置文件：
```bash
cp .env.example .env
```

根据您的生产环境修改以下关键配置：
- `APP_ENV=production` - 设置为生产环境
- `APP_DEBUG=false` - 关闭调试模式
- 安全认证相关配置项
- 数据库路径和连接配置

### 3. 构建AMD架构镜像
```bash
# 构建AMD64架构镜像
./scripts/build-all-amd64.sh
```

或者手动构建：
```bash
# 构建后端镜像 (AMD64)
docker build -f Dockerfile.backend --platform linux/amd64 -t myweb-backend .

# 构建前端镜像 (AMD64)
docker build -f Dockerfile.frontend --platform linux/amd64 -t myweb-frontend .
```

### 4. 启动生产环境
```bash
# 使用生产环境配置启动
docker-compose -f docker-compose.prod.local.yml up -d
```

### 5. 验证部署
```bash
# 检查容器状态
docker-compose -f docker-compose.prod.local.yml ps

# 查看日志
docker-compose -f docker-compose.prod.local.yml logs -f

# 访问应用
# 通过 http://<server-ip>:6608 访问应用
```

## 部署配置详解

### docker-compose.prod.local.yml 配置
- **前端**: Next.js应用，运行在3000端口
- **后端**: FastAPI应用，运行在8000端口  
- **Nginx**: 反向代理，监听6608端口
- **文件卷**: 持久化content目录和数据库文件
- **网络**: 内部网络隔离，外部只能访问6608端口

### 环境变量说明
- `APP_ENV=production`: 生产环境标志
- `ALLOWED_ORIGINS`: CORS允许的域名列表
- `CONTENT_DIR`: 内容目录挂载路径
- `DATABASE_URL/AI_DATABASE_URL`: 数据库连接字符串

## 常见问题排查

### 1. 端口被占用
```bash
# 检查端口占用情况
netstat -tulpn | grep 6608
lsof -i :6608
```

### 2. 容器无法启动
```bash
# 查看详细日志
docker-compose -f docker-compose.prod.local.yml logs --tail=100 backend
docker-compose -f docker-compose.prod.local.yml logs --tail=100 frontend
docker-compose -f docker-compose.prod.local.yml logs --tail=100 nginx
```

### 3. 数据库连接失败
检查数据库文件权限和路径配置是否正确。

## 维护命令

### 停止服务
```bash
docker-compose -f docker-compose.prod.local.yml down
```

### 重启服务
```bash
docker-compose -f docker-compose.prod.local.yml restart
```

### 更新应用
```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose -f docker-compose.prod.local.yml down
docker-compose -f docker-compose.prod.local.yml build --no-cache
docker-compose -f docker-compose.prod.local.yml up -d
```

### 备份数据
```bash
# 备份数据库文件
cp xbk.db xbk.db.backup.$(date +%Y%m%d_%H%M%S)
cp znt.db znt.db.backup.$(date +%Y%m%d_%H%M%S)

# 备份内容目录
tar -czf content_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/content/
```

## 注意事项

1. **安全性**: 生产环境必须修改默认密码和密钥
2. **防火墙**: 确保6608端口在防火墙中开放
3. **SSL证书**: 如需HTTPS，请配置Nginx SSL证书
4. **监控**: 定期检查日志和系统资源使用情况
5. **备份**: 建立定期备份策略，保护重要数据

使用 `docker-compose.prod.local.yml` 文件进行AMD服务器的生产环境部署。