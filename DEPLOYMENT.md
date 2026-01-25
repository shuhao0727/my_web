# MyWeb 项目部署指南

## 项目概述

MyWeb是一个完整的Web应用，包含：
- **后端**: FastAPI Python应用，提供API和Typst文档渲染
- **前端**: Next.js React应用，提供用户界面
- **数据库**: PostgreSQL（生产） / SQLite（开发）
- **缓存**: Redis
- **文档渲染**: Typst

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM（推荐8GB）
- 10GB可用磁盘空间

## 快速部署

### 1. 克隆项目
```bash
git clone https://github.com/shuhao0727/my_web.git
cd my_web
```

### 2. 环境配置
```bash
# 复制环境变量模板
cp .env.example .env  # 如果没有模板，创建基础.env文件
```

编辑`.env`文件，设置必要的环境变量：
```env
# 数据库配置
POSTGRES_PASSWORD=your_secure_password

# 安全配置
SECRET_KEY=your-secret-key-change-in-production

# GitHub同步（可选）
GITHUB_ACCESS_TOKEN=your_github_token
```

### 3. 架构适配

根据目标服务器架构调整Typst安装包：

| 架构 | Typst安装包 | 说明 |
|------|-------------|------|
| x86_64 (AMD/Intel) | `typst-x86_64-unknown-linux-musl.tar.xz` | 大多数服务器 |
| ARM64 (Apple M系列) | `typst-aarch64-unknown-linux-musl.tar.xz` | M1/M2/M3 Mac |
| ARMv7 | `typst-armv7-unknown-linux-musleabi.tar.xz` | Raspberry Pi等 |

**重要**: 确保`backend/`目录下有正确的Typst安装包。默认已包含x86_64版本。

### 4. 构建和启动

#### 开发环境（快速测试）
```bash
# 使用简化的测试配置
docker-compose -f docker-compose.test.yml up --build
```

#### 生产环境
```bash
# 完整生产部署
docker-compose -f docker-compose.prod.yml up --build -d
```

### 5. 验证部署
```bash
# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 测试API健康检查
curl http://localhost:8000/health

# 测试Typst渲染
curl "http://localhost:8000/api/typst/render/chapters/1.basics/1.1-c%2B%2B.typ?output_format=svg"
```

## 配置文件说明

### 1. Docker Compose 配置

- **docker-compose.yml**: 开发环境配置
- **docker-compose.prod.yml**: 生产环境配置（推荐）
- **docker-compose.test.yml**: 测试环境配置

### 2. 环境变量

关键环境变量：

| 变量 | 说明 | 必需 |
|------|------|------|
| `POSTGRES_PASSWORD` | PostgreSQL数据库密码 | 是 |
| `SECRET_KEY` | JWT加密密钥 | 是 |
| `GITHUB_ACCESS_TOKEN` | GitHub API令牌（用于笔记同步） | 可选 |
| `DEEPSEEK_API_KEY` | DeepSeek AI API密钥 | 可选 |
| `ADMIN_PASSWORD` | 管理员密码 | 是 |

### 3. 网络端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端API | 8000 | FastAPI应用 |
| 前端Web | 6608 | Next.js应用 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |

## 架构适配指南

### 在M1/M2/M3 Mac上构建x86_64镜像

```bash
# 方法1：使用Buildx构建多架构镜像
docker buildx create --name multiarch --use
docker buildx build --platform linux/amd64 -t myweb-backend-amd64 -f backend/Dockerfile backend/

# 方法2：直接构建（使用QEMU模拟）
docker build --platform linux/amd64 -t myweb-backend-amd64 -f backend/Dockerfile backend/
```

### 在x86_64服务器上直接构建
```bash
# 最简单的方式，无需特殊配置
docker-compose -f docker-compose.prod.yml build
```

## 常见问题解决

### 1. Typst安装失败
**症状**: API返回"Typst不可用，无法渲染文档"
**解决方案**:
1. 检查Typst安装包架构是否正确
2. 确保backend目录有正确的`.tar.xz`文件
3. 检查Docker构建日志中的Typst安装步骤

### 2. 数据库连接失败
**症状**: 应用启动时报数据库连接错误
**解决方案**:
1. 检查PostgreSQL容器是否正常运行
2. 验证`.env`文件中的`POSTGRES_PASSWORD`
3. 检查网络配置

### 3. 内存不足
**症状**: 容器频繁重启或被OOM杀死
**解决方案**:
1. 在`docker-compose.prod.yml`中调整资源限制
2. 增加服务器内存
3. 禁用不需要的服务

## 生产优化建议

### 1. 安全性
- 修改所有默认密码
- 使用HTTPS（配置反向代理如Nginx）
- 定期更新依赖包
- 限制API访问速率

### 2. 性能
- 调整Docker资源限制
- 配置Redis持久化
- 启用PostgreSQL连接池
- 使用CDN加速静态资源

### 3. 监控
- 配置日志收集（ELK栈）
- 设置健康检查告警
- 监控容器资源使用率

## 备份与恢复

### 数据库备份
```bash
# 备份PostgreSQL
docker exec myweb-postgres pg_dump -U myweb_user myweb > backup_$(date +%Y%m%d).sql

# 备份SQLite数据库
cp backend/xbk.db backup/xbk_$(date +%Y%m%d).db
```

### 数据卷备份
```bash
# 备份Docker数据卷
docker run --rm -v myweb_postgres-data:/data -v $(pwd)/backup:/backup alpine tar czf /backup/postgres-data_$(date +%Y%m%d).tar.gz -C /data .
```

## 更新部署

### 1. 滚动更新
```bash
# 拉取最新代码
git pull origin main

# 重建并重启服务
docker-compose -f docker-compose.prod.yml up --build -d
```

### 2. 零停机更新
```bash
# 使用Docker Swarm或Kubernetes进行蓝绿部署
# 或配置Nginx流量切换
```

## 故障排除命令

```bash
# 查看容器日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 进入容器调试
docker exec -it myweb-backend-prod /bin/bash

# 检查Typst版本
docker exec myweb-backend-prod /usr/local/bin/typst --version

# 健康检查
curl http://localhost:8000/health
```

## 支持与联系

- GitHub: [https://github.com/shuhao0727/my_web](https://github.com/shuhao0727/my_web)
- 问题反馈: GitHub Issues

---
*最后更新: 2026年1月*