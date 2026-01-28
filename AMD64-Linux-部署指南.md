# AMD64 Linux 系统部署指南

## 概述

本文档详细说明如何将 my_web 项目从 ARM64 (Mac M1/M2) 环境部署到 AMD64 (x86_64) Linux 系统的完整流程。采用 **Docker Registry + Git 配置分离** 的策略，实现一次构建、多地部署。

## 部署架构

```
ARM64 Mac (开发环境)                AMD64 Linux (生产环境)
├── 构建多平台镜像                  ├── 从Docker仓库拉取镜像
├── 推送镜像到Docker Hub            ├── 从GitHub获取部署配置
├── 更新部署配置文件                └── docker-compose up
└── 推送配置到GitHub
```

## 完整部署流程

### 第一阶段：本地准备（在 ARM64 Mac 上执行）

#### 步骤 1：构建 AMD64 兼容镜像并打版本标签

```bash
# 进入项目目录
cd /Users/wsh/Desktop/my_web

# 登录 Docker Hub（如果没有账号需要先注册）
docker login

# 构建后端 AMD64 镜像
echo "构建后端镜像（AMD64）..."
docker build --platform linux/amd64 --pull=false -t my_web-backend:latest -f backend/Dockerfile ./backend

# 为后端镜像打版本标签并推送到 Docker Hub
docker tag my_web-backend:latest yourusername/my_web-backend:1.0.0
docker tag my_web-backend:latest yourusername/my_web-backend:latest
docker push yourusername/my_web-backend:1.0.0
docker push yourusername/my_web-backend:latest

# 构建前端 AMD64 镜像（如果之前已构建可跳过）
echo "构建前端镜像（AMD64）..."
docker build --platform linux/amd64 --pull=false -t my_web-frontend:latest -f frontend/Dockerfile ./frontend

# 为前端镜像打版本标签并推送到 Docker Hub
docker tag my_web-frontend:latest yourusername/my_web-frontend:1.0.0
docker tag my_web-frontend:latest yourusername/my_web-frontend:latest
docker push yourusername/my_web-frontend:1.0.0
docker push yourusername/my_web-frontend:latest
```

**说明**：
- `yourusername`：您的 Docker Hub 用户名
- `1.0.0`：具体版本标签，用于生产环境部署
- `latest`：最新版本标签，用于开发环境
- `--platform linux/amd64`：确保 AMD64 架构兼容性
- 双标签策略：同时推送 `1.0.0` 和 `latest` 标签，生产环境使用具体版本，开发环境使用最新版本

#### 步骤 2：更新部署配置文件

我已经为您更新了以下文件：

1. **`docker-compose.prod.yml`**：生产环境配置，使用 Docker Hub 镜像
2. **`.env.example`**：环境变量模板
3. **`deploy/` 目录**：Nginx 配置和 SSL 支持

关键更改：
- 将 `build:` 替换为 `image: yourusername/my_web-backend:1.0.0` 和 `image: yourusername/my_web-frontend:1.0.0`
- 使用版本化标签（1.0.0）而非latest，确保生产环境稳定性
- 优化网络配置和健康检查
- 添加数据卷持久化配置

#### 步骤 3：准备 GitHub 仓库

```bash
# 确保所有文件已提交
git add .
git commit -m "feat: 添加AMD64部署配置和多平台镜像支持"

# 推送到GitHub
git push origin main
```

### 第二阶段：服务器部署（在 AMD64 Linux 上执行）

#### 步骤 1：服务器环境准备

```bash
# 1. 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get update
sudo apt-get install docker-compose-plugin

# 2. 验证安装
docker --version
docker compose version

# 3. 登录 Docker Hub（用于拉取私有镜像）
docker login
```

#### 步骤 2：获取部署配置

```bash
# 1. 克隆项目配置（仅部署相关文件）
mkdir -p /opt/my_web
cd /opt/my_web

# 克隆项目（或仅下载部署文件）
git clone https://github.com/shuhao0727/my_web.git .

# 或者使用最小化配置（推荐）
curl -L https://github.com/shuhao0727/my_web/raw/main/docker-compose.prod.yml -o docker-compose.prod.yml
curl -L https://github.com/shuhao0727/my_web/raw/main/.env.example -o .env.example
```

#### 步骤 3：配置环境变量

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑环境变量（根据实际情况修改）
nano .env

# 关键环境变量示例
GITHUB_ACCESS_TOKEN=your_github_token
SECRET_KEY=your_secret_key_for_jwt
NEXT_PUBLIC_API_URL=http://your-domain.com/api
```

#### 步骤 4：启动服务

```bash
# 1. 使用生产环境配置启动（使用版本化标签1.0.0）
docker compose -f docker-compose.prod.yml up -d

# 2. 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 3. 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 4. 验证服务健康
curl http://localhost:8000/health
curl http://localhost:6608/api/xbk/health
```

### 第三阶段：验证和优化

#### 服务验证

```bash
# 1. 检查所有容器状态
docker ps

# 2. 测试关键功能
# XBK登录测试
curl -X POST "http://localhost:8000/api/xbk/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"name": "admin", "student_id": "wangshu0727"}'

# 健康检查
curl -f http://localhost:8000/health && echo "✅ 后端服务正常"
curl -f http://localhost:6608/api/xbk/health && echo "✅ 前端代理正常"
```

#### 生产优化

1. **Nginx 配置**：`deploy/nginx/nginx.conf` 已包含优化配置
2. **SSL 证书**：在 `deploy/nginx/ssl/` 目录放置证书文件
3. **数据备份**：数据库文件通过 Docker 卷持久化

## 配置文件说明

### 1. docker-compose.prod.yml（核心部署文件）

```yaml
services:
  backend:
    image: yourusername/my_web-backend:1.0.0  # 从Docker Hub拉取特定版本
    environment:
      - ENVIRONMENT=production
    volumes:
      - xbk-database:/app/xbk.db  # 数据持久化
  
  frontend:
    image: yourusername/my_web-frontend:1.0.0  # 从Docker Hub拉取特定版本
    environment:
      - NEXT_PUBLIC_API_URL=http://nginx/api  # 通过Nginx代理
```

**版本管理说明**：
- 生产环境使用具体版本标签（如 `1.0.0`），确保部署一致性
- 开发环境可使用 `latest` 标签获取最新构建
- 更新版本时只需修改镜像标签，如 `1.0.0` → `1.0.1`

### 2. 环境变量模板 (.env.example)

```bash
# Docker镜像配置
DOCKER_HUB_USERNAME=yourusername
# 镜像版本标签（建议使用具体版本如1.0.0，而不是latest）
BACKEND_IMAGE_TAG=1.0.0
FRONTEND_IMAGE_TAG=1.0.0

# 后端配置
SECRET_KEY=change_this_to_a_secure_random_string
GITHUB_ACCESS_TOKEN=your_personal_access_token

# 前端配置
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=production
```

### 3. Nginx配置 (deploy/nginx/nginx.conf)

- 反向代理配置
- 负载均衡支持
- Gzip压缩优化
- SSL终端支持

## 故障排除

### 常见问题 1：镜像拉取失败

```bash
# 检查网络连接
ping hub.docker.com

# 重新登录 Docker Hub
docker logout
docker login

# 手动拉取镜像测试
docker pull yourusername/my_web-backend:latest
```

### 常见问题 2：端口冲突

```bash
# 检查端口占用
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# 修改 docker-compose.prod.yml 中的端口映射
ports:
  - "8080:80"    # 修改外部端口
  - "8443:443"
```

### 常见问题 3：数据库权限问题

```bash
# 检查数据卷权限
docker volume ls
docker volume inspect myweb-xbk-database

# 修复权限
sudo chown -R 1001:1001 /var/lib/docker/volumes/myweb-*/
```

### 常见问题 4：服务启动失败

```bash
# 查看详细日志
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend

# 重启服务
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

## 更新和升级

### 镜像更新流程

```bash
# 1. 本地构建新版本镜像（如1.0.1）
docker build --platform linux/amd64 --pull=false -t my_web-backend:latest -f backend/Dockerfile ./backend

# 2. 为新版本打标签并推送
docker tag my_web-backend:latest yourusername/my_web-backend:1.0.1
docker tag my_web-backend:latest yourusername/my_web-backend:latest
docker push yourusername/my_web-backend:1.0.1
docker push yourusername/my_web-backend:latest

# 3. 更新服务器上的部署配置文件
# 修改 docker-compose.prod.yml 中的镜像标签：
# image: yourusername/my_web-backend:1.0.0 → image: yourusername/my_web-backend:1.0.1

# 4. 在服务器上更新配置并重启
cd /opt/my_web
# 拉取新版本镜像
docker pull yourusername/my_web-backend:1.0.1
docker pull yourusername/my_web-frontend:1.0.1
# 重启服务
docker compose -f docker-compose.prod.yml up -d
```

**版本更新策略**：
- 小版本更新（1.0.0 → 1.0.1）：功能改进和 bug 修复
- 中版本更新（1.0.x → 1.1.0）：新增功能，向下兼容
- 大版本更新（1.x.x → 2.0.0）：重大变更，可能不兼容

### 配置更新流程

```bash
# 1. 更新 GitHub 上的配置文件
# 2. 在服务器上拉取更新
cd /opt/my_web
git pull origin main
# 或手动下载更新文件

# 3. 重启服务
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

## 监控和维护

### 日常监控命令

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看实时日志
docker compose -f docker-compose.prod.yml logs -f --tail=50

# 查看资源使用
docker stats

# 查看网络连接
docker network inspect myweb_myweb-network
```

### 备份和恢复

```bash
# 备份数据库
docker run --rm -v myweb-xbk-database:/data -v $(pwd):/backup alpine \
  tar czf /backup/xbk-database-backup-$(date +%Y%m%d).tar.gz /data

# 恢复数据库
docker run --rm -v myweb-xbk-database:/data -v $(pwd):/backup alpine \
  tar xzf /backup/xbk-database-backup-20250128.tar.gz -C /
```

## 安全建议

1. **定期更新镜像**：每月至少更新一次基础镜像
2. **监控安全公告**：关注 Docker、Python、Node.js 安全更新
3. **限制访问**：使用防火墙限制不必要的端口访问
4. **日志审计**：定期检查应用日志和安全日志
5. **备份策略**：实施 3-2-1 备份策略（3份备份，2种介质，1份异地）

## 总结

您的理解完全正确！部署流程如下：

1. ✅ **本地构建多平台镜像**并推送到 Docker Hub
2. ✅ **更新部署配置文件**（我已完成）
3. ✅ **推送配置到 GitHub**
4. ✅ **服务器拉取配置和镜像**
5. ✅ **运行 docker-compose** 启动服务

通过这种架构，您获得了：
- **架构兼容性**：一次构建，支持 ARM64 和 AMD64
- **部署简化**：服务器只需拉取镜像和配置
- **维护便利**：配置与代码分离，易于更新
- **扩展性强**：支持多环境部署

现在您可以按照本文档开始部署流程。如有任何问题，请参考故障排除部分或检查日志信息。