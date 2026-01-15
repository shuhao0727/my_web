# 项目结构规划文档

## 项目概述
这是一个全栈Web应用，包含前端、后端、数据库和部署配置。

## 技术栈选择
基于设计构思文档，我们选择以下技术栈：

### 前端
- **框架**: Next.js 15 (React 19, App Router)
- **语言**: TypeScript
- **UI库**: Ant Design + Tailwind CSS
- **状态管理**: Zustand
- **图表**: Recharts
- **表单**: React Hook Form + Zod
- **HTTP客户端**: Axios

### 后端
- **框架**: Node.js + Express.js
- **语言**: TypeScript
- **ORM**: Prisma (连接PostgreSQL)
- **认证**: JWT + bcrypt
- **API文档**: Swagger/OpenAPI
- **日志**: Winston
- **验证**: Joi

### 数据库
- **主数据库**: PostgreSQL
- **缓存**: Redis
- **ORM**: Prisma Client

### DevOps
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **监控**: Sentry
- **部署**: Vercel (前端) + 阿里云 (后端)

## 项目目录结构

```
my_web/
├── .github/                    # GitHub配置
│   └── workflows/              # GitHub Actions工作流
├── docs/                       # 项目文档
├── frontend/                   # 前端应用
│   ├── public/                 # 静态资源
│   │   ├── images/             # 图片资源
│   │   ├── fonts/              # 字体文件
│   │   └── favicon.ico         # 网站图标
│   ├── src/
│   │   ├── app/                # Next.js App Router
│   │   │   ├── (public)/       # 公开页面组
│   │   │   │   ├── page.tsx    # 首页
│   │   │   │   ├── about/      # 关于页面
│   │   │   │   ├── blog/       # 博客页面
│   │   │   │   └── contact/    # 联系页面
│   │   │   ├── (student)/      # 学生端页面组
│   │   │   │   ├── login/      # 登录页面
│   │   │   │   ├── register/   # 注册页面
│   │   │   │   ├── ai-chat/    # AI智能体主页面（登录后直接进入）
│   │   │   │   └── resources/  # 学习资源查看（只读）
│   │   │   ├── (teacher)/      # 教师端页面组
│   │   │   │   ├── admin/      # 管理仪表板
│   │   │   │   ├── students/   # 学生管理
│   │   │   │   ├── analytics/  # 数据分析
│   │   │   │   ├── content/    # 内容管理
│   │   │   │   └── settings/   # 系统设置
│   │   │   ├── api/            # 前端API路由
│   │   │   │   ├── auth/       # 认证相关
│   │   │   │   └── webhooks/   # Webhooks
│   │   │   ├── layout.tsx      # 根布局
│   │   │   ├── loading.tsx     # 加载组件
│   │   │   └── error.tsx       # 错误页面
│   │   ├── components/         # 可复用组件
│   │   │   ├── ui/             # 基础UI组件
│   │   │   │   ├── Button/
│   │   │   │   ├── Card/
│   │   │   │   ├── Input/
│   │   │   │   └── ...
│   │   │   ├── layout/         # 布局组件
│   │   │   │   ├── Header/
│   │   │   │   ├── Footer/
│   │   │   │   ├── Sidebar/
│   │   │   │   └── ...
│   │   │   ├── features/       # 功能组件
│   │   │   │   ├── Chat/
│   │   │   │   ├── Analytics/
│   │   │   │   ├── UserProfile/
│   │   │   │   └── ...
│   │   │   └── shared/         # 共享组件
│   │   ├── lib/                # 工具函数和库
│   │   │   ├── api/            # API客户端
│   │   │   │   ├── client.ts   # Axios配置
│   │   │   │   ├── auth.ts     # 认证API
│   │   │   │   ├── dify.ts     # Dify API
│   │   │   │   └── ...
│   │   │   ├── utils/          # 工具函数
│   │   │   │   ├── format.ts
│   │   │   │   ├── validation.ts
│   │   │   │   └── ...
│   │   │   ├── constants/      # 常量定义
│   │   │   ├── types/          # TypeScript类型
│   │   │   └── hooks/          # 自定义Hooks
│   │   ├── stores/             # Zustand状态存储
│   │   │   ├── auth.store.ts
│   │   │   ├── user.store.ts
│   │   │   └── ...
│   │   ├── styles/             # 样式文件
│   │   │   ├── globals.css
│   │   │   ├── tailwind.css
│   │   │   └── antd.less
│   │   └── middleware.ts       # Next.js中间件
│   ├── next.config.js          # Next.js配置
│   ├── tailwind.config.js      # Tailwind配置
│   ├── tsconfig.json           # TypeScript配置
│   ├── package.json
│   └── .env.local              # 前端环境变量
├── backend/                    # 后端应用
│   ├── src/
│   │   ├── config/             # 配置文件
│   │   │   ├── database.ts
│   │   │   ├── redis.ts
│   │   │   ├── jwt.ts
│   │   │   └── ...
│   │   ├── controllers/        # 控制器
│   │   │   ├── auth.controller.ts
│   │   │   ├── user.controller.ts
│   │   │   ├── dify.controller.ts
│   │   │   ├── analytics.controller.ts
│   │   │   └── ...
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── auth.service.ts
│   │   │   ├── user.service.ts
│   │   │   ├── dify.service.ts
│   │   │   ├── analytics.service.ts
│   │   │   └── ...
│   │   ├── models/             # 数据模型
│   │   │   ├── user.model.ts
│   │   │   ├── conversation.model.ts
│   │   │   ├── message.model.ts
│   │   │   └── ...
│   │   ├── routes/             # 路由定义
│   │   │   ├── auth.routes.ts
│   │   │   ├── user.routes.ts
│   │   │   ├── dify.routes.ts
│   │   │   ├── analytics.routes.ts
│   │   │   └── ...
│   │   ├── middleware/         # 中间件
│   │   │   ├── auth.middleware.ts
│   │   │   ├── validation.middleware.ts
│   │   │   ├── logging.middleware.ts
│   │   │   └── ...
│   │   ├── utils/              # 工具函数
│   │   │   ├── logger.ts
│   │   │   ├── encryption.ts
│   │   │   ├── validation.ts
│   │   │   └── ...
│   │   ├── types/              # TypeScript类型
│   │   │   ├── user.types.ts
│   │   │   ├── dify.types.ts
│   │   │   └── ...
│   │   ├── prisma/             # Prisma配置
│   │   │   ├── schema.prisma   # 数据库模式
│   │   │   └── seed.ts         # 种子数据
│   │   └── app.ts              # Express应用
│   ├── tests/                  # 测试文件
│   │   ├── unit/
│   │   └── integration/
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── .env                    # 后端环境变量
├── docker-compose.yml          # Docker Compose配置
├── .gitignore
├── README.md                   # 项目说明
├── design-conception.md        # 设计构思文档
├── project-structure.md        # 项目结构文档
└── LICENSE                     # 开源许可证
```

## 关键文件说明

### 前端关键文件

1. **frontend/src/app/layout.tsx** - 应用根布局
2. **frontend/src/app/(public)/page.tsx** - 首页
3. **frontend/src/app/(student)/ai-chat/page.tsx** - AI智能体主页面（学生登录后主界面）
4. **frontend/src/components/features/Chat/** - 聊天组件
5. **frontend/src/lib/api/dify.ts** - Dify API集成
6. **frontend/src/stores/auth.store.ts** - 认证状态管理

### 后端关键文件

1. **backend/src/app.ts** - Express应用入口
2. **backend/src/prisma/schema.prisma** - 数据库模式定义
3. **backend/src/controllers/dify.controller.ts** - Dify API控制器
4. **backend/src/services/analytics.service.ts** - 数据分析服务
5. **backend/src/routes/** - 所有API路由定义

## 数据库模式（Prisma Schema）

```prisma
// backend/src/prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  username      String
  passwordHash  String
  role          Role      @default(STUDENT)
  profile       StudentProfile?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
  lastLogin     DateTime?
  
  conversations Conversation[]
  activityLogs  ActivityLog[]
  analytics     LearningAnalytics[]
  
  @@map("users")
}

model StudentProfile {
  id               String   @id @default(cuid())
  userId           String   @unique
  user             User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  grade            String?
  className        String?
  competitionLevel String?
  interests        String[]
  createdAt        DateTime @default(now())
  updatedAt        DateTime @updatedAt
  
  @@map("student_profiles")
}

model Conversation {
  id              String    @id @default(cuid())
  userId          String
  user            User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  difySessionId   String?
  title           String?
  startTime       DateTime  @default(now())
  endTime         DateTime?
  totalMessages   Int       @default(0)
  
  messages        Message[]
  
  @@map("conversations")
}

model Message {
  id             String   @id @default(cuid())
  conversationId String
  conversation   Conversation @relation(fields: [conversationId], references: [id], onDelete: Cascade)
  content        String
  senderType     SenderType
  timestamp      DateTime @default(now())
  metadata       Json?
  
  @@map("messages")
}

model ActivityLog {
  id           String     @id @default(cuid())
  userId       String
  user         User       @relation(fields: [userId], references: [id], onDelete: Cascade)
  activityType ActivityType
  resourceId   String?
  timestamp    DateTime   @default(now())
  details      Json?
  
  @@map("activity_logs")
}

model LearningAnalytics {
  id                String   @id @default(cuid())
  userId            String
  user              User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  date              DateTime @default(now())
  totalQuestions    Int      @default(0)
  avgSessionLength  Float?   @default(0)
  topicsCovered     String[]
  performanceScore  Float?
  
  @@map("learning_analytics")
}

model Article {
  id              String   @id @default(cuid())
  authorId        String
  author          User     @relation(fields: [authorId], references: [id], onDelete: Cascade)
  title           String
  slug            String   @unique
  content         String
  excerpt         String?
  coverImage      String?
  status          ArticleStatus @default(DRAFT)
  publishedAt     DateTime?
  category        String?
  tags            String[]
  viewCount       Int      @default(0)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  @@map("articles")
}

model Tutorial {
  id              String   @id @default(cuid())
  authorId        String
  author          User     @relation(fields: [authorId], references: [id], onDelete: Cascade)
  title           String
  slug            String   @unique
  content         String
  description     String?
  category        TutorialCategory
  difficulty      DifficultyLevel
  estimatedTime   Int?  // 分钟
  videoUrl        String?
  attachments     String[]  // 附件文件路径
  viewCount       Int      @default(0)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  @@map("tutorials")
}

model CompetitionProblem {
  id              String   @id @default(cuid())
  authorId        String
  author          User     @relation(fields: [authorId], references: [id], onDelete: Cascade)
  title           String
  description     String
  difficulty      ProblemDifficulty
  category        ProblemCategory
  tags            String[]
  inputFormat     String
  outputFormat    String
  sampleInput     String?
  sampleOutput    String?
  timeLimit       Int      @default(1000)  // ms
  memoryLimit     Int      @default(256)   // MB
  testData        Json?    // 测试用例
  solution        String?
  hint            String?
  viewCount       Int      @default(0)
  attemptCount    Int      @default(0)
  successCount    Int      @default(0)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  @@map("competition_problems")
}

enum Role {
  STUDENT
  TEACHER
  ADMIN
}

enum SenderType {
  USER
  ASSISTANT
}

enum ActivityType {
  LOGIN
  LOGOUT
  CHAT_START
  CHAT_END
  RESOURCE_VIEW
  QUESTION_ASK
  FILE_UPLOAD
  ARTICLE_VIEW
  TUTORIAL_VIEW
  PROBLEM_ATTEMPT
}

enum ArticleStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

enum TutorialCategory {
  PROGRAMMING
  AI_ML
  ALGORITHMS
  DATA_STRUCTURES
  WEB_DEVELOPMENT
  OTHER
}

enum DifficultyLevel {
  BEGINNER
  INTERMEDIATE
  ADVANCED
  EXPERT
}

enum ProblemDifficulty {
  EASY
  MEDIUM
  HARD
  EXPERT
}

enum ProblemCategory {
  ALGORITHMS
  DATA_STRUCTURES
  DYNAMIC_PROGRAMMING
  GRAPH_THEORY
  MATH
  STRINGS
  OTHER
}
```

## 环境变量配置

### 前端环境变量 (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NEXT_PUBLIC_DIFY_API_KEY=your_dify_api_key
NEXT_PUBLIC_DIFY_BASE_URL=https://api.dify.ai/v1
NEXT_PUBLIC_APP_NAME=AI教育平台
```

### 后端环境变量 (.env)
```env
# 数据库
DATABASE_URL="postgresql://user:password@localhost:5432/my_web_db"

# Redis
REDIS_URL="redis://localhost:6379"

# JWT
JWT_SECRET="your_jwt_secret_key"
JWT_EXPIRES_IN="7d"

# Dify配置
DIFY_API_KEY="your_dify_api_key"
DIFY_BASE_URL="https://api.dify.ai/v1"

# 应用配置
PORT=3001
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000
```

## 开发工作流

### 1. 环境设置
```bash
# 克隆项目
git clone https://github.com/yourusername/my_web.git
cd my_web

# 安装依赖
cd frontend && npm install
cd ../backend && npm install

# 启动数据库 (使用Docker)
docker-compose up -d postgres redis

# 初始化数据库
cd backend
npx prisma migrate dev
npx prisma db seed

# 启动开发服务器
# 终端1: 后端
cd backend && npm run dev

# 终端2: 前端
cd frontend && npm run dev
```

### 2. 开发命令
```bash
# 前端
npm run dev          # 开发模式
npm run build        # 生产构建
npm run start        # 生产启动
npm run lint         # 代码检查

# 后端
npm run dev          # 开发模式 (nodemon)
npm run build        # TypeScript编译
npm run start        # 生产启动
npm run test         # 运行测试
npm run prisma:gen   # 生成Prisma客户端
npm run prisma:migrate # 数据库迁移
```

## 部署配置

### Docker Compose (生产环境)
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: my_web_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/my_web_db
      REDIS_URL: redis://redis:6379
      NODE_ENV: production
    ports:
      - "3001:3001"
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 下一步行动

1. **初始化项目结构**：创建上述目录和文件
2. **设置Git仓库**：配置.gitignore和README
3. **安装依赖**：分别在前端和后端安装所需包
4. **配置数据库**：设置PostgreSQL和Redis
5. **开发核心功能**：按照里程碑逐步实现

---
*文档版本：v1.0*
*创建日期：2026年1月15日*
*最后更新：2026年1月15日*
