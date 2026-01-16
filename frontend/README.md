# AI教育平台 - 前端

这是一个面向高中信息技术老师、信息学竞赛教练和AI爱好者的智能教育平台前端应用。

## 功能特性

- **用户系统**：学生注册/登录，教师后台管理
- **AI智能体集成**：集成Dify AI智能体，提供24小时学习辅导
- **学习资源管理**：编程教程、竞赛题目、视频课程等丰富资源
- **学习数据分析**：可视化分析学生学习行为，提供个性化推荐
- **教师内容发布**：教师可发布文章、教程、竞赛题目等教学资源

## 技术栈

- **框架**：Next.js 15 (React 19, App Router)
- **语言**：TypeScript
- **UI组件库**：Ant Design
- **样式**：Tailwind CSS
- **状态管理**：React Hooks
- **HTTP客户端**：Axios

## 项目结构

```
frontend/
├── app/                          # Next.js App Router
│   ├── (public)/                # 公开页面组
│   │   ├── page.tsx             # 首页
│   │   ├── about/              # 关于页面
│   │   └── blog/               # 博客页面
│   ├── (student)/              # 学生端页面组
│   │   ├── login/              # 登录页面
│   │   ├── register/           # 注册页面
│   │   ├── ai-chat/            # AI智能体主页面
│   │   └── resources/          # 学习资源查看
│   ├── (teacher)/              # 教师端页面组
│   │   ├── admin/              # 管理仪表板
│   │   ├── students/           # 学生管理
│   │   ├── analytics/          # 数据分析
│   │   ├── content/            # 内容管理
│   │   └── settings/           # 系统设置
│   ├── layout.tsx              # 根布局
│   └── globals.css             # 全局样式
├── components/                  # 可复用组件
│   ├── layout/                 # 布局组件
│   │   ├── Header/            # 网站头部
│   │   └── Footer/            # 网站底部
│   ├── features/               # 功能组件
│   └── shared/                 # 共享组件
├── lib/                        # 工具函数和库
│   ├── api/                    # API客户端
│   ├── utils/                  # 工具函数
│   ├── constants/              # 常量定义
│   └── types/                  # TypeScript类型
├── stores/                     # 状态管理
├── public/                     # 静态资源
└── styles/                     # 样式文件
```

## 快速开始

### 环境要求

- Node.js 18+ 
- npm 或 yarn

### 安装依赖

```bash
cd frontend
npm install
```

### 开发环境运行

```bash
npm run dev
```

访问 http://localhost:6608

### 构建生产版本

```bash
npm run build
npm run start
```

### 代码检查

```bash
npm run lint
```

## 环境变量配置

创建 `.env.local` 文件：

```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NEXT_PUBLIC_APP_NAME=AI教育平台
```

## 部署

### Docker 部署

1. 构建 Docker 镜像：
```bash
docker build -t ai-education-frontend .
```

2. 运行容器：
```bash
docker run -p 6608:6608 ai-education-frontend
```

### Vercel 部署

1. 将代码推送到 GitHub 仓库
2. 在 Vercel 中导入项目
3. 配置环境变量
4. 自动部署

## 开发指南

### 添加新页面

1. 在 `app` 目录下创建新的文件夹（路由组）
2. 创建 `page.tsx` 文件作为页面组件
3. 如果需要，创建布局文件 `layout.tsx`

### 添加新组件

1. 在 `components` 目录下创建组件文件夹
2. 创建组件文件（例如：`MyComponent.tsx`）
3. 在需要的地方导入使用

### API 调用

1. 在 `lib/api` 目录下创建 API 客户端
2. 使用 Axios 进行 HTTP 请求
3. 在组件中使用 React Query 或直接调用

## 设计规范

### 颜色方案

- 主色：蓝色 (#1d4ed8)
- 辅助色：绿色 (#10b981)、紫色 (#8b5cf6)、橙色 (#f59e0b)
- 文本色：灰色 (#6b7280)

### 字体

- 主要字体：Inter (通过 Next.js 自动加载)

### 响应式设计

- 移动端优先
- 使用 Tailwind CSS 断点系统

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

MIT

## 联系方式

- 邮箱：contact@ai-education.com
- 网站：https://ai-education.com

## 更新日志

### v1.0.0 (2026-01-15)
- 初始版本发布
- 基础页面结构
- 用户登录/注册界面
- AI教育平台首页
- 关于页面
