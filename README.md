# MyWeb - 信息学竞赛教学管理系统

一个基于FastAPI和Next.js的信息学竞赛教学管理系统，支持Typst文档渲染、AI智能体、课程管理等功能。

## 特性

- **前后端分离**: 使用FastAPI（后端）和Next.js（前端）
- **Typst文档支持**: 支持Typst格式文档的编写和实时渲染
- **AI智能体**: 集成AI助手功能
- **课程管理**: 支持课程安排、成绩管理等教育功能
- **容器化部署**: 支持Docker和Docker Compose部署

## 技术栈

### 后端
- **Python 3.11+**
- **FastAPI**: Web框架
- **SQLAlchemy**: ORM
- **SQLite**: 默认数据库
- **Typst**: 文档编译引擎
- **APScheduler**: 任务调度

### 前端
- **Next.js 16+**
- **React 19+**
- **TypeScript**
- **Ant Design**: UI组件库
- **Axios**: HTTP客户端

## 环境要求

- Node.js 18+
- Python 3.11+
- Docker (可选，用于容器化部署)
- Typst 0.14.0 (可选，用于文档渲染)

## 安装和运行

### 方法一：本地开发模式

#### 1. 克隆项目
```bash
git clone <repository-url>
cd my_web
```

#### 2. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 3. 安装前端依赖
```bash
cd frontend
npm install
```

#### 4. 配置环境变量
复制环境变量配置文件：
```bash
cp .env.example .env
# 根据需要编辑 .env 文件
```

#### 5. 启动后端服务
```bash
cd backend
python main.py
```

#### 6. 启动前端服务
```bash
cd frontend
npm run dev
```

### 方法二：Docker部署

#### 1. 构建并启动服务
```bash
docker-compose up -d --build
```

#### 2. 访问应用
- 前端：http://${FRONTEND_HOST:-localhost}:${FRONTEND_PORT:-3000}
- 后端API：http://${BACKEND_HOST:-localhost}:${BACKEND_PORT:-8000}
- 文档：http://${BACKEND_HOST:-localhost}:${BACKEND_PORT:-8000}/docs

## 项目结构

```
my_web/
├── backend/                    # 后端服务
│   ├── main.py                # 主应用入口
│   ├── config/                # 配置文件
│   ├── models/                # 数据模型
│   ├── routers/               # API路由
│   │   ├── ai/                # AI相关路由
│   │   ├── xbk/               # XBK相关路由
│   │   └── typst_content.py   # Typst内容路由
│   ├── services/              # 业务服务
│   ├── content/               # 内容文件
│   └── requirements.txt       # Python依赖
├── frontend/                   # 前端服务
│   ├── app/                   # 页面组件
│   ├── components/            # UI组件
│   ├── lib/                   # 工具库
│   ├── next.config.ts         # Next.js配置
│   └── package.json           # Node.js依赖
├── deploy.sh                  # 项目部署脚本
├── Dockerfile.backend         # 后端Dockerfile (X86架构优化)
├── Dockerfile.frontend        # 前端Dockerfile (X86架构优化)
├── docker-compose.dev.yml         # 开发环境Docker Compose配置
├── docker-compose.prod.amd.yml    # 生产环境Docker Compose配置 (AMD64)
├── nginx.prod.conf            # Nginx生产环境配置
├── CONFIGURATION.md           # 配置文件说明
└── .env.example              # 环境变量示例
```

## 部署方式

### 方式一：使用部署脚本（推荐）

项目提供了完整的部署脚本 `deploy.sh`：

```bash
# 查看帮助信息
./deploy.sh help

# 安装依赖
./deploy.sh deps

# 启动开发环境
./deploy.sh docker-start

# 启动X86_64架构优化环境
./deploy.sh docker-optimize

# 启动生产环境
./deploy.sh docker-prod
```

### 方式二：传统Docker Compose部署

#### 开发环境部署
```bash
docker-compose up -d --build
```

#### 生产环境部署
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## 配置文件说明

### Docker配置文件
- `docker-compose.yml`: 开发环境配置，适合本地开发调试
- `docker-compose.prod.yml`: 生产环境配置，包含Nginx反向代理和健康检查
- `Dockerfile.*`: 分别针对不同架构的Docker构建文件

### 架构支持
项目提供多架构Docker镜像支持：
- **AMD64**: 标准x86_64架构，适用于大多数PC和云服务器
- **ARM64**: 适用于Apple Silicon (M1/M2)、树莓派等ARM架构设备

### 环境变量配置

### 后端配置
- `BACKEND_HOST`: 后端服务主机，默认 `0.0.0.0`
- `BACKEND_PORT`: 后端服务端口，默认 `8000`
- `DATABASE_URL`: 数据库连接URL，默认 `sqlite:///./xbk.db`
- `AI_DATABASE_URL`: AI数据库URL，默认 `sqlite:///./znt.db`
- `CONTENT_DIR`: 内容目录，默认 `./content`
- `GITHUB_ACCESS_TOKEN`: GitHub访问令牌
- `SYNC_INTERVAL_SECONDS`: 同步间隔秒数
- `ENABLE_AUTO_SYNC`: 是否启用自动同步

### 前端配置
- `NEXT_PUBLIC_API_URL`: 后端API地址
- `NEXT_PUBLIC_API_URL_INTERNAL`: 内部API地址
- `NEXT_PUBLIC_BASE_PATH`: 基础路径

## API文档

启动服务后访问 http://localhost:8000/docs 查看API文档。

## 部署

### 生产环境部署
使用Docker Compose进行生产环境部署：

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### CI/CD
项目支持GitHub Actions自动部署，配置文件位于 `.github/workflows/`。

## 开发指南

### 添加新功能
1. 在 `backend/routers/` 下创建新的路由模块
2. 在 `frontend/app/` 下创建新的页面组件
3. 更新 `backend/main.py` 注册新的路由
4. 更新前端导航菜单

### 测试
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 维护

### 数据库迁移
使用Alembic进行数据库迁移：
```bash
cd backend
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

### 日志管理
- 后端日志: `backend/backend.log`
- 前端日志: 浏览器控制台

## 常见问题

### Typst渲染问题
确保Typst已正确安装：
```bash
typst --version
```

### 数据库连接问题
检查数据库URL配置，确保数据库文件路径存在。

### 环境变量问题
确保所有必要的环境变量都已正确设置。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 许可证

MIT License