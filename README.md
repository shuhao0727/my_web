# MyWeb - 个人竞赛文档平台

一个专注于信息学竞赛文档浏览的个人网站，集成Typst文档同步和预览功能。

## 📁 项目结构

```
my_web/
├── README.md                    # 项目说明
├── backend/                     # 后端服务
│   ├── main.py                  # FastAPI主应用
│   ├── requirements.txt         # Python依赖
│   ├── routers/                 # API路由
│   │   ├── typst_content.py     # Typst内容API
│   │   └── repo_sync.py         # 仓库同步API
│   ├── services/                # 服务层
│   │   └── repo_sync_service.py # 仓库同步服务
│   └── content/                 # Typst文档内容
├── frontend/                    # 前端应用
│   ├── app/                     # Next.js应用
│   │   ├── (home)/              # 首页
│   │   ├── competition/         # 竞赛文档页面
│   │   ├── ai-lab/              # AI实验室
│   │   ├── blog/                # 博客
│   │   ├── teaching/            # 教学页面
│   │   └── resources/           # 资源页面
│   ├── components/              # 组件库
│   │   └── TypstRenderer.tsx    # Typst渲染组件
│   ├── lib/                     # 工具库
│   │   └── typstApi.ts          # Typst API客户端
│   └── package.json             # Node.js依赖
```

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI (Python)
- **API**: RESTful API设计
- **文档同步**: GitHub仓库自动同步
- **Typst处理**: 文件结构解析和内容服务

### 前端
- **框架**: Next.js 16 (React 19, TypeScript)
- **UI库**: Ant Design
- **样式**: Tailwind CSS
- **状态管理**: React Hooks

## 🚀 快速开始

### 1. 启动后端服务
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

### 3. 访问应用
- 前端地址：http://localhost:6608
- 竞赛文档页面：http://localhost:6608/competition
- API文档：http://localhost:8000/docs

## 📖 核心功能

### Typst文档浏览
- 实时同步GitHub仓库中的Typst文档
- 文档树形导航结构
- Typst源代码预览和格式化显示
- 支持搜索功能

### 自动同步
- 24小时自动同步检查
- 手动同步支持
- 同步状态实时显示

## 🔧 开发说明

本项目为个人学习项目，专注于信息学竞赛文档管理和展示。

**代码结构清晰，便于扩展和维护。**

---
**项目状态**：开发中
