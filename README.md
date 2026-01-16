# MyWeb - 个人竞赛文档平台

一个专注于信息学竞赛文档浏览的个人网站，集成GitHub仓库同步和Typst文档编译功能。

## 🚀 核心功能

### 📚 竞赛文档浏览
- 从GitHub私有仓库 `shuhao0727/2-My-notes` 同步Typst文档
- 自动编译Typst文件为PDF格式
- 在线PDF预览（内联显示，防止下载）
- 文档目录树形导航（自然排序）

### 🔄 自动同步
- 定时从GitHub同步最新文档
- 支持手动触发同步
- 增量PDF缓存生成
- 6小时自动同步间隔

### 🎨 简洁界面
- 左侧文档目录树（支持折叠）
- 右侧PDF预览区域
- 响应式设计，适配不同屏幕尺寸
- 无冗余UI元素，专注文档浏览

## 📁 项目结构

```
my_web/
├── README.md                    # 项目说明
├── CHANGELOG.md                 # 更新日志
├── .env.example                 # 环境变量示例
├── backend/                     # 后端服务
│   ├── main.py                  # FastAPI主应用
│   ├── .env                     # 环境变量
│   ├── requirements.txt         # Python依赖
│   └── routers/                 # API路由
│       └── repo_sync.py         # 仓库同步API
├── frontend/                    # 前端应用
│   ├── app/                     # Next.js应用
│   │   ├── (home)/              # 首页
│   │   ├── competition/         # 竞赛文档页面
│   │   ├── about/               # 关于页面
│   │   ├── ai-lab/              # AI实验室
│   │   ├── blog/                # 博客
│   │   ├── teaching/            # 教学页面
│   │   └── resources/           # 资源页面
│   ├── components/              # 组件库
│   ├── lib/repoApi.ts           # API客户端
│   └── package.json             # Node.js依赖
└── content/                     # 静态内容
    └── 2-My-notes/              # GitHub同步的文档
        └── .pdf_cache/          # PDF缓存目录
```

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI (Python)
- **数据库**: SQLite（轻量级数据存储）
- **任务调度**: 自定义定时任务
- **Typst编译**: 集成Typst CLI编译器
- **GitHub API**: 私有仓库访问

### 前端
- **框架**: Next.js 16 (React 19, TypeScript)
- **UI库**: Ant Design
- **样式**: Tailwind CSS
- **状态管理**: React Hooks
- **构建工具**: Turbopack

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/shuhao0727/my_web.git
cd my_web

# 安装Typst编译器（macOS）
brew install typst

# 或从官网下载：https://github.com/typst/typst
```

### 2. 后端设置
```bash
cd backend

# 复制环境变量
cp .env.example .env
# 编辑.env文件，添加GitHub访问令牌

# 安装Python依赖
pip install -r requirements.txt

# 启动后端服务
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 前端设置
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用
- 前端地址：http://localhost:6608
- 竞赛页面：http://localhost:6608/competition
- API文档：http://localhost:8000/docs

## 🔧 配置说明

### GitHub访问令牌
由于项目需要访问私有仓库，需要配置GitHub Personal Access Token：

1. 访问 https://github.com/settings/tokens
2. 创建新令牌，选择 `repo` 权限
3. 将令牌添加到 `backend/.env` 文件：
   ```env
   GITHUB_ACCESS_TOKEN=your_token_here
   ```

### 同步配置
在 `backend/.env` 中配置同步参数：
```env
# 开启自动同步（默认开启）
ENABLE_AUTO_SYNC=True

# 同步间隔（秒），默认6小时
SYNC_INTERVAL_SECONDS=21600

# GitHub仓库配置
GITHUB_REPO_OWNER=shuhao0727
GITHUB_REPO_NAME=2-My-notes
GITHUB_REPO_BRANCH=main
```

## 📖 使用指南

### 文档管理
1. **添加文档**：在GitHub仓库中创建或更新Typst文件
2. **自动同步**：系统每6小时自动同步最新内容
3. **PDF编译**：Typst文件自动编译为PDF并缓存
4. **在线预览**：通过竞赛页面浏览所有文档

### 手动操作
```bash
# 手动触发同步
curl -X POST http://localhost:8000/api/repo/sync

# 检查同步状态
curl http://localhost:8000/api/repo/status

# 查看PDF缓存信息
curl http://localhost:8000/api/repo/pdf-cache/info
```

### 清理缓存
```bash
# 清理PDF缓存
rm -rf content/2-My-notes/.pdf_cache/*

# 重新生成缓存
curl -X POST http://localhost:8000/api/repo/pdf-cache/generate
```

## 🔍 API接口

### 仓库同步
- `GET /api/repo/status` - 仓库状态
- `POST /api/repo/sync` - 触发同步
- `GET /api/repo/chapters` - 获取章节树
- `GET /api/repo/chapter-pdf-static/{path}` - 获取PDF文件

### PDF缓存
- `GET /api/repo/pdf-cache/info` - 缓存信息
- `POST /api/repo/pdf-cache/generate` - 生成缓存

### 健康检查
- `GET /health` - 服务健康状态
- `GET /` - API基本信息

## 🐛 故障排除

### 常见问题

#### 1. Typst编译失败
**症状**：PDF生成失败，返回编译错误
**解决**：
- 检查Typst文件语法
- 确认Typst编译器已安装
- 查看后端日志获取详细错误信息

#### 2. GitHub同步失败
**症状**：同步任务失败，仓库不可访问
**解决**：
- 检查GitHub访问令牌权限
- 确认网络连接正常
- 验证仓库是否存在且为私有

#### 3. PDF无法预览
**症状**：PDF显示空白或错误
**解决**：
- 清理PDF缓存并重新生成
- 检查文件权限
- 确认Typst编译成功

#### 4. 服务启动失败
**症状**：后端或前端无法启动
**解决**：
- 检查端口占用（8000, 6608）
- 确认依赖已安装
- 查看日志文件获取错误信息

### 日志查看
```bash
# 查看后端日志
tail -f backend/backend.log

# 查看前端日志（开发模式）
cd frontend && npm run dev
```

## 📈 性能优化

### PDF缓存
- 自动缓存已编译的PDF文件
- 缓存有效期1小时
- 支持增量缓存更新

### 静态文件服务
- 使用FastAPI静态文件服务
- 支持缓存头和内容协商
- 防止PDF文件下载

### 内存管理
- 数据库连接池管理
- 定时清理旧缓存文件
- 渐进式PDF生成

## 🔮 未来计划

### 短期改进
- [ ] 添加搜索功能
- [ ] 支持文档书签
- [ ] 添加阅读进度跟踪
- [ ] 优化移动端体验

### 长期规划
- [ ] 用户系统（学生/教师）
- [ ] 在线代码编辑器
- [ ] 竞赛题目练习系统
- [ ] AI学习助手集成

## 📄 许可证

本项目仅供个人学习使用。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

## 📞 联系方式

如有问题或建议，请通过GitHub Issues联系。

---

**最后更新**：2026-01-16  
**当前版本**：v1.0  
**项目状态**：✅ 生产就绪
