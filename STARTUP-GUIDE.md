# MyWeb 容器化部署启动指南

## 🚀 快速开始

### 1. 环境准备
确保已安装：
- Docker 20.10+
- Docker Compose 2.0+
- Git

### 2. 项目结构确认
```
my_web/
├── docker-compose.yml          # 多服务编排配置
├── backend/                    # 后端服务
│   ├── Dockerfile             # Python 3.11 + 数据库初始化
│   ├── init_database.py       # 数据库初始化脚本
│   ├── .env.production        # 生产环境变量
│   └── requirements.txt       # Python依赖
├── frontend/                  # 前端服务
│   ├── Dockerfile             # Node.js 20 + Next.js
│   ├── .env.production        # 生产环境变量
│   ├── next.config.ts         # Next.js配置
│   └── package.json           # Node.js依赖
└── data/                      # 数据持久化目录
    ├── databases/             # SQLite数据库文件
    ├── content/               # 静态内容文件
    └── logs/                  # 应用日志
```

### 3. 配置文件设置

#### 后端环境变量
```bash
# 复制后端环境变量模板
cp backend/.env.production backend/.env

# 编辑后端环境变量（重要！）
vim backend/.env

# 需要设置的变量：
# - GITHUB_ACCESS_TOKEN: GitHub个人访问令牌
# - DEEPSEEK_API_KEY: DeepSeek API密钥（可选）
# - DIFY_API_KEY: Dify API密钥（可选）
# - JWT_SECRET_KEY: JWT密钥（生产环境必须更改）
# - XBK_JWT_SECRET_KEY: XBK JWT密钥（生产环境必须更改）
```

#### 前端环境变量
```bash
# 前端环境变量已预配置，如需自定义可编辑
vim frontend/.env.production
```

### 4. 启动所有服务
```bash
# 构建并启动所有容器
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 访问服务
- **前端应用**: http://localhost:6608
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🔧 服务配置详解

### 后端服务 (backend)
- **端口**: 8000
- **数据库**: 
  - `my_web.db` - 主数据库
  - `znt.db` - AI智能体数据库
  - `xbk.db` - XBK应用数据库
- **数据持久化**: `./data/databases/` → `/app/data/`
- **内容目录**: `./data/content/` → `/app/content/`
- **日志目录**: `./data/logs/backend/` → `/app/logs/`

### 前端服务 (frontend)
- **端口**: 6608
- **构建工具**: Node.js 20 + Next.js 16
- **API代理**: 自动代理到后端服务（`http://backend:8000`）
- **数据持久化**: `./data/logs/frontend/` → `/app/logs/`

### 管理员账户
系统会自动创建默认管理员账户：
- **用户名**: `admin`
- **学号**: `wangshu0727`
- **登录方式**: 使用用户名 `admin` 和学号 `wangshu0727` 登录AI实验室
- **默认密码**: 学号后6位（`hu0727`），用于密码验证（如需）

**首次登录后请立即修改密码！**

## 📊 数据库管理

### 数据库初始化
容器启动时自动执行 `init_database.py`，创建：
1. **AI数据库 (znt.db)**
   - `ai_users` - 用户表（含默认管理员）
   - `ai_agents` - 智能体表
   - `ai_conversations` - 对话表
   - `ai_messages` - 消息表

2. **XBK数据库 (xbk.db)**
   - `denglu` - 登录表（含默认管理员）

3. **主数据库 (my_web.db)**
   - 保留现有表结构

### 数据库备份
```bash
# 备份所有数据库
cp -r data/databases/ data/databases_backup_$(date +%Y%m%d_%H%M%S)

# 恢复数据库
cp -r data/databases_backup/* data/databases/
```

## 🛠️ 运维命令

### 常用Docker命令
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 更新服务（代码变更后）
docker-compose build --no-cache
docker-compose up -d
```

### 健康检查
```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查前端健康状态
curl http://localhost:6608

# 检查容器健康状态
docker-compose ps
```

## 🔄 更新部署

### 代码更新
```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker-compose build --no-cache

# 3. 重启服务
docker-compose up -d

# 4. 清理旧镜像
docker image prune -f
```

### 环境变量更新
```bash
# 1. 更新环境变量文件
vim backend/.env
vim frontend/.env.production

# 2. 重启服务
docker-compose restart
```

## 🚀 开发到生产同步流程

### 1. 开发环境修改
在本地开发环境进行网页修改：
```bash
# 启动本地开发服务器
cd frontend
npm run dev  # 前端在 http://localhost:6608
# 或者
cd backend
python3 -m uvicorn main:app --reload --port 8000  # 后端在 http://localhost:8000
```

### 2. 测试修改
确保修改在本地运行正常：
- 前端功能测试
- 后端API测试
- 数据库迁移测试（如有）

### 3. 提交代码到Git
```bash
# 添加修改
git add .

# 提交修改
git commit -m "描述修改内容"

# 推送到远程仓库（如GitHub）
git push origin main
```

### 4. 服务器部署
在服务器上执行：
```bash
# 进入项目目录
cd /path/to/my_web

# 拉取最新代码
git pull origin main

# 重新构建Docker镜像
docker-compose build --no-cache

# 重启服务
docker-compose up -d

# 验证服务状态
docker-compose ps
docker-compose logs --tail=50
```

### 5. 验证部署
访问服务验证修改：
- 前端：http://服务器IP:6608
- 后端API：http://服务器IP:8000/docs
- 健康检查：http://服务器IP:8000/health

### 快速部署脚本
创建 `deploy.sh` 脚本：
```bash
#!/bin/bash
set -e

echo "开始部署 MyWeb..."

# 拉取最新代码
git pull origin main

# 构建镜像
docker-compose build --no-cache

# 重启服务
docker-compose up -d

# 清理旧镜像
docker image prune -f

echo "部署完成！"
```

赋予执行权限并运行：
```bash
chmod +x deploy.sh
./deploy.sh
```

### 注意事项
1. **数据库迁移**：如果修改涉及数据库结构变化，需要手动备份和迁移。
2. **环境变量**：确保服务器上的环境变量文件（如backend/.env）已正确配置。
3. **端口开放**：确保服务器防火墙开放6608和8000端口。
4. **备份**：部署前建议备份数据库：
   ```bash
   cp -r data/databases data/databases_backup_$(date +%Y%m%d_%H%M%S)
   ```

## 📈 监控与日志

### 日志文件位置
- **后端日志**: `data/logs/backend/`
- **前端日志**: `data/logs/frontend/`
- **Nginx日志**: `data/logs/nginx/`（如果启用）

### 实时日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看容器内部日志
docker-compose exec backend tail -f /app/logs/backend.log
```

## 🔍 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
sudo lsof -i :6608
sudo lsof -i :8000

# 修改docker-compose.yml中的端口映射
# 例如将6608:6608改为6609:6608
```

#### 2. 数据库权限问题
```bash
# 确保数据目录有正确权限
chmod -R 755 data/
chown -R $USER:$USER data/
```

#### 3. 依赖安装失败
```bash
# 清理Docker缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

#### 4. 容器启动失败
```bash
# 查看详细错误信息
docker-compose logs --tail=100 backend

# 检查环境变量
docker-compose exec backend env

# 手动测试数据库初始化
docker-compose exec backend python init_database.py
```

### 调试模式
```bash
# 以前台模式运行查看输出
docker-compose up

# 进入容器调试
docker-compose exec backend bash
cd /app
python init_database.py
```

## 🚢 生产部署建议

### 安全配置
1. **更改默认密钥**
   - 修改 `JWT_SECRET_KEY` 和 `XBK_JWT_SECRET_KEY`
   - 使用强密码生成器生成

2. **启用HTTPS**
   - 配置Nginx SSL证书
   - 更新前端`NEXT_PUBLIC_API_URL`为HTTPS

3. **防火墙配置**
   - 只开放必要端口（80, 443, 22）
   - 限制API访问来源

### 性能优化
1. **数据库优化**
   - 定期清理日志表
   - 建立合适索引

2. **容器资源限制**
```yaml
# 在docker-compose.yml中添加
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

3. **启用缓存**
   - 配置Redis缓存
   - 启用CDN静态资源缓存

### 备份策略
1. **定期备份**
```bash
# 每日备份脚本
0 2 * * * /usr/bin/bash /opt/myweb/backup.sh
```

2. **监控告警**
   - 配置容器健康检查告警
   - 监控磁盘空间和内存使用

## 📞 支持与维护

### 获取帮助
1. **查看文档**
   - `README.md` - 项目概述
   - `CHANGELOG.md` - 更新日志
   - `DEPLOYMENT-PLAN.md` - 部署计划

2. **问题反馈**
   - GitHub Issues: https://github.com/shuhao0727/my_web/issues
   - 查看日志文件定位问题

### 版本信息
- **当前版本**: v2.0（容器化版本）
- **前端**: Node.js 20 + Next.js 16 + React 19
- **后端**: Python 3.11 + FastAPI + SQLite
- **部署方式**: Docker Compose多容器

---

**最后更新**: 2026-01-24  
**维护者**: 系统管理员  
**状态**: ✅ 生产就绪