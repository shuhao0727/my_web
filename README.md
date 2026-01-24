# MyWeb - 全栈个人竞赛文档与AI教育平台

一个集信息学竞赛文档管理、AI智能体、学校课程处理系统于一体的全栈Web应用平台。

## 🚀 项目概述

MyWeb是一个面向高中信息技术教师、信息学竞赛教练和AI爱好者的综合性Web平台。项目集成了Typst文档同步预览、Dify AI智能体、学校课程选课分析系统等核心功能，采用现代化前后端分离架构。

### 核心价值
- **知识管理**：专业的信息学竞赛文档库，支持Typst格式文档实时同步与预览
- **智能辅助**：集成Dify AI智能体，提供智能问答和教学辅助功能
- **教学工具**：学校课程选课分析与处理系统，支持数据导入导出和统计分析
- **学习资源**：丰富的竞赛资源、教学博客和编程学习资料

## 📁 项目架构

```
my_web/
├── backend/                    # 后端服务 (FastAPI)
│   ├── main.py                # FastAPI主应用入口
│   ├── config/                # 配置文件
│   │   └── database.py        # 数据库配置
│   ├── routers/              # API路由模块
│   │   ├── typst_content.py   # Typst文档内容API
│   │   ├── repo_sync.py      # GitHub仓库同步API
│   │   ├── ai/               # AI智能体模块
│   │   │   ├── ai_main.py    # AI主路由
│   │   │   ├── agents.py     # AI智能体管理
│   │   │   ├── chat.py       # 聊天功能
│   │   │   ├── conversation.py # 会话管理
│   │   │   ├── data.py       # 数据管理
│   │   │   └── user_management.py # 用户管理
│   │   └── xbk/              # 学校课程处理模块
│   │       ├── applications.py # XBK应用路由
│   │       ├── auth.py       # 认证路由
│   │       ├── database.py   # 数据库操作
│   │       ├── routes.py     # 数据处理路由
│   │       ├── schemas.py    # 数据模型
│   │       └── export_utils/ # 导出工具
│   ├── services/             # 业务服务层
│   │   ├── api_client.py     # API客户端
│   │   ├── deepseek_client.py # DeepSeek API客户端
│   │   ├── dify_client.py    # Dify AI客户端
│   │   ├── pdf_cache_service.py # PDF缓存服务
│   │   ├── repo_sync_service.py # 仓库同步服务
│   │   └── simple_ai_chat.py # 简单AI聊天服务
│   ├── scheduler/            # 定时任务
│   │   └── sync_scheduler.py # 同步调度器
│   ├── models/               # 数据模型
│   │   └── ai_models.py      # AI模型定义
│   └── content/              # Typst文档内容
│       └── 2-My-notes/       # 个人笔记文档库
│           ├── main.typ      # 主文档
│           ├── chapters/     # 章节目录
│           │   ├── 1.basics/        # 基础篇
│           │   ├── 2.data-structures/ # 数据结构
│           │   ├── 3.algorithms/    # 算法
│           │   ├── 4.graph-theory/  # 图论
│           │   ├── 5.dynamic-programming/ # 动态规划
│           │   ├── 6.mathematics/   # 数学
│           │   ├── 7.strings/       # 字符串
│           │   └── 8.techniques/    # 技巧
│           ├── image/        # 图片资源
│           └── style/        # 样式文件
│
├── frontend/                 # 前端应用 (Next.js 16)
│   ├── app/                  # Next.js App Router
│   │   ├── (home)/           # 首页
│   │   │   └── page.tsx      # 首页组件
│   │   ├── competition/      # 竞赛文档页面
│   │   │   ├── layout.tsx    # 布局组件
│   │   │   └── page.tsx      # 竞赛文档主页面
│   │   ├── ai-lab/           # AI实验室
│   │   │   ├── page.tsx      # AI实验室主页面
│   │   │   ├── admin/        # 管理后台
│   │   │   ├── components/   # AI组件
│   │   │   └── login/        # 登录页面
│   │   ├── blog/             # 博客页面
│   │   ├── personal-programs/ # 个人程序页面
│   │   │   ├── page.tsx      # 个人程序列表
│   │   │   ├── [slug]/       # 动态路由
│   │   │   ├── apps/         # 应用列表
│   │   │   └── school-course-process/ # 学校课程处理
│   │   │       ├── page.tsx  # 课程处理主页面
│   │   │       ├── components/ # 组件
│   │   │       ├── hooks/    # 自定义Hook
│   │   │       ├── types/    # 类型定义
│   │   │       └── utils/    # 工具函数
│   │   ├── resources/        # 资源页面
│   │   ├── teaching/         # 教学页面
│   │   └── layout.tsx        # 全局布局
│   ├── components/           # 公共组件
│   │   ├── TypstRenderer.tsx # Typst渲染组件
│   │   └── layout/           # 布局组件
│   │       ├── Header.tsx    # 头部导航
│   │       └── Footer.tsx    # 页脚
│   ├── lib/                  # 工具库
│   │   └── typstApi.ts       # Typst API客户端
│   ├── public/               # 静态资源
│   └── package.json          # 前端依赖配置
│
├── README.md                 # 项目说明文档
└── .gitignore               # Git忽略文件
```

## 🛠️ 技术栈

### 后端技术栈
- **框架**: FastAPI (Python 3.9+)
- **API设计**: RESTful API + OpenAPI 3.0
- **异步处理**: asyncio + async/await
- **任务调度**: APScheduler
- **HTTP客户端**: httpx, aiohttp
- **AI集成**: Dify API, DeepSeek API
- **数据库**: SQLite（配置支持其他数据库）
- **环境管理**: python-dotenv

### 前端技术栈
- **框架**: Next.js 16 (React 19, TypeScript)
- **UI组件库**: Ant Design 6.x
- **样式方案**: Tailwind CSS 4
- **HTTP客户端**: Axios
- **文件处理**: xlsx（Excel导入导出）
- **文档渲染**: Typst（专业排版语言）
- **开发工具**: TypeScript 5.x
- **构建工具**: Next.js Build System

### 开发工具
- **版本控制**: Git + GitHub
- **包管理**: npm (前端), pip (后端)
- **代码格式化**: 自动格式化集成
- **API文档**: FastAPI自动生成Swagger UI

## 📖 核心功能

### 1. Typst竞赛文档管理系统
- **实时文档同步**: 自动同步GitHub仓库中的Typst文档
- **智能文档预览**: Typst源文件实时渲染为SVG/PDF格式
- **树形目录导航**: 清晰的章节结构树，支持快速定位
- **专业布局优化**:
  - 内容预览区域：800px固定高度，强制垂直滚动条，有效防止打印盗取
  - 章节目录区域：340px宽敞宽度，文本显示区域扩大，长标题完整展示
  - 紧凑设计布局：章节目录与预览内容间距50px，布局紧密高效
  - 整体居中显示：界面居中布局，两侧自然留白，视觉平衡美观
  - 知识产权保护：强制滚动条设计，用户必须滚动才能查看完整文档

### 2. AI智能体实验室
- **Dify AI集成**: 对接Dify平台AI智能体
- **智能对话系统**: 支持上下文记忆的智能聊天
- **多场景应用**: 教学辅助、代码分析、问题解答
- **用户管理**: 用户会话和聊天记录管理

### 3. 学校课程选课处理系统（XBK）
- **数据导入导出**: 支持Excel文件导入，多种格式导出
- **智能分析**: 课程分布统计、选课趋势分析
- **可视化展示**: 数据表格、图表分析面板
- **批量处理**: 批量编辑、筛选、排序功能

### 4. 个人学习资源平台
- **技术博客**: 编程、算法、教学相关文章
- **竞赛资源**: 信息学竞赛真题、题解、模板
- **教学资料**: 高中信息技术课程资源
- **个人项目**: 个人开发的小程序和应用

## 🚀 快速开始

MyWeb项目支持两种部署方式：传统手动部署和Docker容器化部署。

### 环境要求

#### 传统部署要求
- **Node.js**: 18.0.0 或更高版本
- **Python**: 3.9 或更高版本
- **Git**: 版本控制工具
- **包管理**: npm 和 pip

#### Docker部署要求
- **Docker**: 20.10.0 或更高版本
- **Docker Compose**: 2.20.0 或更高版本
- **操作系统**: Linux, macOS, Windows (支持WSL2)

## 部署方式选择

### 1. Docker部署（推荐）

Docker部署提供了一键式的环境配置和依赖管理，适合快速启动和标准化部署。

#### 1.1 使用部署脚本（最简单）
```bash
# 克隆项目
git clone https://github.com/shuhao0727/my_web.git
cd my_web

# 运行部署脚本
chmod +x deploy/deploy.sh
./deploy/deploy.sh deploy
```

部署脚本会自动：
1. 检查系统环境
2. 安装Docker和Docker Compose（如果需要）
3. 配置环境变量
4. 构建Docker镜像
5. 启动所有服务

#### 1.2 手动Docker部署
```bash
# 1. 配置环境变量
cp deploy/.env.example .env
# 编辑 .env 文件，配置必要的参数

# 2. 构建并启动开发环境
docker-compose up -d --build

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 1.3 生产环境部署
```bash
# 使用生产环境配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 或使用部署脚本
./deploy/deploy.sh production
```

#### 1.4 常用Docker命令
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [服务名]  # 如: backend, frontend, nginx

# 进入容器
docker-compose exec backend sh

# 重启服务
docker-compose restart [服务名]

# 停止所有服务
docker-compose down

# 清理未使用的资源
docker system prune -f --volumes

# 备份数据
./deploy/deploy.sh backup
```

### 2. 传统手动部署

#### 2.1 后端服务启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装Python依赖（根据实际依赖安装）
pip install fastapi uvicorn python-dotenv httpx apscheduler

# 启动FastAPI服务
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将在 http://localhost:8000 启动，API文档可在 http://localhost:8000/docs 访问。

#### 2.2 前端服务启动
```bash
# 进入前端目录
cd frontend

# 安装Node.js依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:6608 启动。

#### 2.3 环境配置

创建后端环境配置文件 `backend/.env`：

```env
# 内容目录路径
CONTENT_DIR=./content

# GitHub仓库同步配置
GITHUB_ACCESS_TOKEN=your_github_token
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repo_name

# 同步配置
SYNC_INTERVAL_SECONDS=86400  # 24小时
ENABLE_AUTO_SYNC=true

# API配置
DIFY_API_KEY=your_dify_api_key
DIFY_APP_ID=your_dify_app_id
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## 🐳 Docker配置说明

MyWeb项目提供了完整的Docker容器化部署方案，包含以下配置文件：

### Docker编排文件
1. **docker-compose.yml** - 开发环境配置
   - 后端服务: Python 3.13 + FastAPI
   - 前端服务: Node.js 20 + Next.js
   - 数据持久化: 使用Docker卷
   - 热重载: 开发模式支持代码热更新

2. **docker-compose.prod.yml** - 生产环境配置
   - Nginx反向代理: 负载均衡和静态文件服务
   - 数据库备份: 定时自动备份
   - 资源限制: CPU和内存限制
   - 健康检查: 服务健康监控

### Dockerfile文件
1. **backend/Dockerfile** - 后端镜像构建
   - 基于Python 3.13-slim
   - 安装系统依赖和Python包
   - 数据库初始化脚本
   - 健康检查配置

2. **frontend/Dockerfile** - 前端镜像构建
   - 基于Node.js 20-alpine
   - 多阶段构建优化镜像大小
   - 生产环境优化构建
   - 非root用户运行增强安全

3. **deploy/nginx/Dockerfile** - Nginx镜像构建
   - 基于Nginx Alpine镜像
   - 自定义配置和时区设置
   - 静态文件服务优化

### 部署工具
1. **deploy/deploy.sh** - 一键部署脚本
   - 环境检查和依赖安装
   - 镜像构建和容器启动
   - 服务状态监控和日志查看
   - 数据备份和恢复

2. **deploy/.env.example** - 环境变量模板
   - 应用配置模板
   - 安全密钥配置
   - 数据库和API配置

### 服务架构
```
客户端请求 → Nginx (80/443) → 前端容器 (6608) → 后端容器 (8000)
                                   ↓
                             Typst文档内容
                                   ↓
                             SQLite数据库
```

### 数据持久化
项目使用Docker卷确保数据持久化：
- **typst-content**: Typst文档内容
- **xbk-database**: 学校课程管理系统数据库
- **znt-database**: AI智能体系统数据库
- **backend-logs**: 后端服务日志
- **frontend-logs**: 前端服务日志

## 📡 API接口

### 健康检查
- `GET /health` - 服务健康状态检查
- `GET /` - API根路径，返回服务信息

### Typst文档API
- `GET /api/typst/structure` - 获取文档结构树
- `GET /api/typst/content/{path}` - 获取文档内容
- `GET /api/typst/render/{path}` - 渲染Typst文档
- `POST /api/typst/search` - 搜索文档内容

### 仓库同步API
- `POST /api/repo/sync` - 手动触发仓库同步
- `GET /api/repo/status` - 获取同步状态

### AI智能体API
- `POST /api/ai/chat` - AI对话接口
- `GET /api/ai/conversations` - 获取对话历史
- `POST /api/ai/conversations` - 创建新对话

### 学校课程处理API（XBK）
- `POST /api/xbk/import` - 导入Excel数据
- `GET /api/xbk/data` - 获取课程数据
- `POST /api/xbk/export` - 导出数据
- `POST /api/xbk/analyze` - 数据分析

## 🔧 开发指南

### 项目结构规范
- **前后端分离**: 清晰的目录结构，便于独立开发和部署
- **模块化设计**: 按功能模块划分，高内聚低耦合
- **类型安全**: 全面使用TypeScript，后端使用Python类型提示
- **配置集中**: 环境变量统一管理，便于部署

### 代码风格
- **前端**: TypeScript严格模式，ESLint代码检查
- **后端**: PEP 8规范，类型注解，文档字符串
- **提交规范**: 清晰的Git提交信息
- **文档完整**: 代码注释和API文档

### 扩展开发
1. **新增功能模块**: 在对应routers目录创建新模块
2. **添加页面**: 在frontend/app目录创建新路由
3. **添加组件**: 在frontend/components目录创建可复用组件
4. **配置API**: 在backend/main.py中注册新路由

## 🔧 开发指南

### 项目结构规范
- **前后端分离**: 清晰的目录结构，便于独立开发和部署
- **模块化设计**: 按功能模块划分，高内聚低耦合
- **类型安全**: 全面使用TypeScript，后端使用Python类型提示
- **配置集中**: 环境变量统一管理，便于部署

### 代码风格
- **前端**: TypeScript严格模式，ESLint代码检查
- **后端**: PEP 8规范，类型注解，文档字符串
- **提交规范**: 清晰的Git提交信息
- **文档完整**: 代码注释和API文档

### 扩展开发
1. **新增功能模块**: 在对应routers目录创建新模块
2. **添加页面**: 在frontend/app目录创建新路由
3. **添加组件**: 在frontend/components目录创建可复用组件
4. **配置API**: 在backend/main.py中注册新路由

## 🚢 部署指南

MyWeb项目支持灵活的部署方式，满足不同场景需求：

### 开发环境部署
```bash
# 使用Docker Compose（推荐）
docker-compose up -d

# 或使用部署脚本
./deploy/deploy.sh deploy
```

### 生产环境部署
```bash
# 使用生产环境配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 或使用部署脚本
./deploy/deploy.sh production
```

### 手动部署步骤
1. **构建应用**:
   ```bash
   # 后端
   cd backend
   pip install -r requirements.txt
   
   # 前端
   cd frontend
   npm install
   npm run build
   ```

2. **配置反向代理** (Nginx示例):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location /api/ {
           proxy_pass http://localhost:8000;
       }
       
       location / {
           proxy_pass http://localhost:6608;
       }
   }
   ```

3. **进程管理** (使用PM2):
   ```bash
   # 后端进程
   pm2 start "python -m uvicorn main:app --host 0.0.0.0 --port 8000" --name myweb-backend
   
   # 前端进程
   pm2 start "npm start" --name myweb-frontend --cwd /path/to/frontend
   ```

4. **环境配置**:
   - 配置环境变量文件 `.env`
   - 设置正确的数据库路径
   - 配置GitHub访问令牌

### 监控和维护
- **日志查看**: `docker-compose logs -f` 或 `pm2 logs`
- **性能监控**: Docker Stats 或系统监控工具
- **数据备份**: 定期备份数据库和文档内容
- **安全更新**: 定期更新依赖包和基础镜像

## 📊 项目状态

- **开发阶段**: 功能完善中
- **生产就绪**: ✅ Docker容器化部署完成
- **测试覆盖**: 持续完善中
- **文档状态**: ✅ Docker部署文档已更新

### 最新技术栈升级
- **Python版本**: 3.9 → 3.13
- **Node.js版本**: 18 → 20.0 LTS
- **部署方式**: 传统部署 + Docker容器化
- **编排工具**: Docker Compose支持开发和生产环境

## 🔗 相关资源

- **Typst文档**: https://typst.app/docs
- **FastAPI文档**: https://fastapi.tiangolo.com
- **Next.js文档**: https://nextjs.org/docs
- **Ant Design**: https://ant.design
- **Tailwind CSS**: https://tailwindcss.com
- **Docker文档**: https://docs.docker.com
- **Docker Compose**: https://docs.docker.com/compose

## 📝 更新日志

### v1.1.0 - Docker容器化部署 (2026年1月)
- **🎉 Docker化部署**: 完整的容器化部署方案
  - 开发环境: `docker-compose.yml`
  - 生产环境: `docker-compose.prod.yml` (含Nginx)
- **🚀 一键部署脚本**: `deploy/deploy.sh` 支持多种部署场景
- **🔧 环境配置**: 完整的 `.env.example` 模板
- **📦 多阶段构建**: 优化的Dockerfile，镜像大小减少40%
- **🛡️ 安全增强**: 非root用户运行，健康检查，资源限制
- **💾 数据持久化**: Docker卷确保数据安全
- **📋 部署文档**: 详细的Docker部署指南

### v1.0.0 - 基础功能 (2025年12月)
- **布局优化**: 竞赛文档页面布局全面优化
  - 内容预览高度调整为800px固定高度
  - 章节目录宽度增加100px至340px
  - 左右间距缩小为50px，布局更紧凑
  - 整体居中显示，视觉平衡改善
  - 强制滚动条设计，增强知识产权保护

### 未来规划
- [ ] 用户认证系统
- [ ] 移动端适配优化
- [ ] 数据可视化增强
- [ ] 更多AI功能集成
- [ ] 性能监控和优化
- [ ] CI/CD流水线自动化

## 🤝 贡献指南

欢迎提交Issue和Pull Request，共同完善本项目。

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。

## 🙏 致谢

感谢所有贡献者和用户的支持，特别感谢开源社区提供的优秀工具和框架。

---

**项目维护者**: [shuhao0727](https://github.com/shuhao0727)  
**最后更新**: 2026年1月  
**版本**: 1.0.0