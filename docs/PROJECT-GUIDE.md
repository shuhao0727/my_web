# MyWeb 项目综合指南

## 一、项目简介

MyWeb 是一个综合性个人网站项目，集成了多个功能模块，旨在提供一站式的学习、竞赛、教学和实用工具平台。项目采用现代化的前后端分离架构，支持容器化部署和持续集成。

### 1.1 项目特点
- **模块化设计**：各功能模块独立开发，松耦合集成
- **现代化技术栈**：Next.js 14 + FastAPI + TypeScript + SQLite
- **容器化支持**：前后端均有 Dockerfile，支持一键部署
- **完整文档体系**：详细的开发日志和设计文档
- **安全认证**：多模块支持 JWT + bcrypt 认证

### 1.2 项目目标
1. **学习平台**：为信息学竞赛学习者提供算法笔记和题解
2. **AI助手**：集成多AI服务的智能学习助手
3. **教学工具**：为教师提供课程管理和学生管理工具
4. **实用程序**：校本课处理等个人实用程序
5. **知识管理**：个人笔记和资源管理

### 1.3 快速开始

#### 环境准备
```bash
# 克隆项目
git clone https://github.com/shuhao0727/my_web.git
cd my_web

# 安装Typst编译器（macOS）
brew install typst

# 或从官网下载：https://github.com/typst/typst
```

#### 后端设置
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

#### 前端设置
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 访问应用
- 前端地址：http://localhost:6608
- 竞赛页面：http://localhost:6608/competition
- API文档：http://localhost:8000/docs

## 二、系统架构

### 2.1 技术架构概览
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     前端         │ ←→ │    后端API       │ ←→ │     数据库       │
│   Next.js 14    │    │    FastAPI       │    │    SQLite       │
│   TypeScript    │    │                  │    │                 │
│   Ant Design    │    │                  │    │ 1. my_web.db    │
│   Tailwind CSS  │    │                  │    │ 2. znt.db       │
│   (端口:6608)   │    │   (端口:8000)    │    │ 3. xbk.db       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ↑                      ↑                      ↑
         │                      │                      │
   用户界面交互           RESTful API             数据持久化
```

### 2.2 目录结构
```
/Volumes/文件/4-实用代码/my_web/
├── frontend/                    # 前端项目 (Next.js 14)
│   ├── app/                    # App Router 页面
│   │   ├── (home)/            # 首页
│   │   ├── ai-lab/            # AI智能体模块
│   │   ├── competition/       # 信息学竞赛模块
│   │   ├── personal-programs/ # 个人程序中心
│   │   ├── teaching/          # 教学模块
│   │   └── blog/              # 文章模块
│   ├── components/            # 公共组件
│   ├── lib/                   # 工具函数和API客户端
│   └── public/                # 静态资源
├── backend/                    # 后端项目 (FastAPI)
│   ├── routers/               # API路由
│   │   ├── ai/               # AI智能体相关路由
│   │   ├── xbk/              # 校本课处理路由
│   │   └── repo_sync.py      # 仓库同步路由
│   ├── services/              # 业务服务层
│   ├── models/                # 数据模型
│   ├── config/                # 配置管理
│   ├── scheduler/             # 定时任务
│   └── requirements.txt       # Python依赖
├── content/                   # 内容存储（竞赛笔记等）
├── docs/                      # 项目文档
│   └── dev-logs/             # 开发日志（各模块详细记录）
├── xbk高一/                   # 校本课桌面应用（待移植）
└── 部署文件/                  # 部署相关文件
```

## 三、功能模块详解

### 3.1 AI智能体模块 (AI Lab)
**定位**：集成多AI服务的学生学习助手平台

#### 核心功能
- ✅ **多AI服务集成**：DeepSeek API、Dify API
- ✅ **用户管理系统**：学生信息CRUD、Excel批量导入
- ✅ **智能体管理**：创建、配置、测试不同AI智能体
- ✅ **对话系统**：完整对话历史、消息存储、上下文管理
- ✅ **权限控制**：管理员/学生双角色权限体系
- ✅ **数据管理**：学生使用统计、对话内容查看

#### 技术特点
- **数据库设计**：znt.db，包含ai_users、ai_agents、ai_conversations、ai_messages等表
- **安全认证**：JWT令牌 + bcrypt密码哈希，企业级安全标准
- **时间处理**：UTC时间存储，前端正确转换为本地时区
- **模块化代码**：DataManagement组件拆分为3个文件，提升可维护性

#### 访问地址
- 主页面：http://localhost:6608/ai-lab
- 管理界面：http://localhost:6608/ai-lab/admin
- API文档：http://localhost:8000/docs

### 3.2 信息学竞赛模块 (Competition)
**定位**：为信息学竞赛学习者和教练提供算法笔记、题解和教学资源

#### 核心功能
- ✅ **GitHub仓库自动同步**：定时从GitHub仓库拉取最新的竞赛笔记和题解
- ✅ **PDF笔记浏览**：将Typst格式的算法笔记编译为PDF并提供在线浏览
- ✅ **章节分类管理**：按算法知识点（基础、数据结构、图论、动态规划等）组织内容
- ✅ **自动更新检测**：智能检测仓库更新，减少不必要的PDF重新编译

#### 技术特点
- **定时任务**：基于schedule库，支持可配置的同步间隔
- **PDF缓存**：减少重复编译，提高性能
- **环境变量配置**：同步频率、启用状态等均可通过环境变量配置
- **状态监控**：提供调度器状态监控API

#### 配置示例
```env
SYNC_INTERVAL_SECONDS=86400     # 同步间隔（秒），24小时
ENABLE_AUTO_SYNC=True           # 是否启用自动同步
GITHUB_ACCESS_TOKEN=xxx         # GitHub访问令牌（可选）
```

### 3.3 个人程序中心 (Personal Programs)
**定位**：登录保护的个性化应用集合，为学生和教师提供学习工具和实用程序

#### 核心功能
- ✅ **登录保护**：使用XBK用户认证系统（基于denglu表）
- ✅ **应用入口**：提供"校本课处理"等应用卡片
- ✅ **新窗口跳转**：点击卡片在新标签页中打开应用页面
- ✅ **用户隐私**：隐藏用户名显示，保护用户隐私

#### 技术特点
- **简单认证**：基于denglu表的用户名+学号认证
- **静态卡片**：应用卡片静态展示，无需数据库存储
- **响应式设计**：自动适配不同屏幕尺寸
- **安全跳转**：使用安全属性`rel="noopener noreferrer"`

#### 默认用户
```sql
INSERT INTO denglu (name, student_id) VALUES ('admin', 'wangshu0727');
```

### 3.4 校本课处理系统 (XBK System)
**定位**：基于Web的校本课程管理系统（从桌面应用移植）

#### 核心功能
- ✅ **多组数据支持**：通过年份和年级字段支持多组数据存储
- ✅ **数据导入**：支持Excel文件批量导入
- ✅ **数据处理**：数据清洗、合并、分析
- ✅ **数据导出**：导出选课表、分发表、教师分发表等
- ✅ **实时筛选**：前端支持按年份、年级、班级实时筛选数据

#### 数据库设计
```sql
-- 核心表结构
CREATE TABLE course_catalog (年份, 年级, 课程代码, 课程名称, ...);
CREATE TABLE student_info (年份, 年级, 班级, 学号, 姓名, ...);
CREATE TABLE course_selection (年份, 年级, 课程代码, 学号, ...);
CREATE TABLE merged_data (年份, 年级, 班级, 学号, 课程代码, ...);
CREATE TABLE system_config (key, value); -- 存储筛选条件
```

#### 技术特点
- **模块化导出**：数据导出和美化功能分离，符合单一职责原则
- **专业Excel处理**：保持原有程序的Excel处理能力，确保导出文件质量
- **实时数据展示**：合并数据表用于高效查询和实时展示
- **数据验证**：导出文件包含数据验证和工作表保护

### 3.5 首页和导航系统 (Homepage)
**定位**：提供个人网站的统一入口和导航中心

#### 核心功能
- ✅ **统一入口**：展示网站整体结构和内容概览
- ✅ **快速导航**：提供到各子模块的快速访问
- ✅ **响应式设计**：适配不同设备访问
- ✅ **简洁界面**：移除冗余功能，专注于核心导航

#### 设计特点
- **三栏布局**：Logo区域、导航菜单、右侧空白区域
- **分布式居中**：导航菜单绝对居中，忽略Logo区域
- **简洁标签**：精简导航项文字标签
- **无用户登录**：纯信息展示平台，无需用户登录功能

#### 导航项
1. AI智能体
2. 信息学竞赛
3. 信息技术
4. 个人程序
5. 文章
6. NAS导航页（外部链接）
7. Dify应用平台（外部链接）

## 四、数据库设计

### 4.1 数据库文件概览
```
backend/
├── my_web.db      # 主应用数据库（待统一）
├── znt.db         # AI智能体模块数据库
└── xbk.db         # 校本课处理系统数据库
```

### 4.2 核心表结构

#### 4.2.1 AI智能体模块 (znt.db)
```sql
-- 用户表
CREATE TABLE ai_users (id, username, password_hash, student_id, class_name, ...);

-- 智能体表
CREATE TABLE ai_agents (id, name, api_type, api_key, base_url, model, app_id, ...);

-- 对话表
CREATE TABLE ai_conversations (id, user_id, agent_id, session_id, title, ...);

-- 消息表
CREATE TABLE ai_messages (id, conversation_id, role, content, tokens, ...);
```

#### 4.2.2 校本课处理系统 (xbk.db)
```sql
-- 用户登录表
CREATE TABLE denglu (id, name, student_id);

-- 课程目录表
CREATE TABLE course_catalog (id, 年份, 年级, 课程代码, 课程名称, 课程负责人, ...);

-- 学生信息表
CREATE TABLE student_info (id, 年份, 年级, 班级, 学号, 姓名, ...);

-- 选课结果表
CREATE TABLE course_selection (id, 年份, 年级, 班级, 学号, 姓名, 课程代码, ...);

-- 合并数据表（用于高效查询）
CREATE TABLE merged_data (id, 年份, 年级, 班级, 学号, 姓名, 课程代码, 课程名称, ...);

-- 系统配置表
CREATE TABLE system_config (id, key, value, description);
```

## 五、API接口设计

### 5.1 API前缀
```
AI智能体模块: /api/ai/*
校本课处理系统: /api/xbk/*
仓库同步: /api/repo/*
通用接口: /health, /docs
```

### 5.2 核心API接口

#### AI智能体模块
- `POST /api/ai/auth/login` - 用户登录（JWT认证）
- `GET /api/ai/users` - 获取用户列表
- `POST /api/ai/agents` - 创建智能体
- `POST /api/ai/chat` - 发送消息到AI
- `GET /api/ai/data/students` - 获取学生使用统计

#### 校本课处理系统
- `POST /api/xbk/login` - 用户登录（简单认证）
- `POST /api/xbk/import/catalog` - 导入课程目录
- `POST /api/xbk/import/student-info` - 导入学生信息
- `GET /api/xbk/data/merged` - 获取合并数据
- `GET /api/xbk/export/course-selection` - 导出选课表

#### 仓库同步
- `GET /api/repo/status` - 获取仓库同步状态
- `POST /api/repo/sync` - 手动触发同步
- `GET /api/repo/sync-scheduler/status` - 获取调度器状态

## 六、部署与运维

### 6.1 本地开发环境
```bash
# 启动后端服务
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端服务
cd frontend
npm run dev
```

### 6.2 服务端口
- **前端开发服务器**: http://localhost:6608
- **后端API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 6.3 容器化部署
项目已提供Dockerfile支持容器化部署：

#### 前端Dockerfile
```dockerfile
FROM node:18-alpine AS base
# ... 多阶段构建配置
EXPOSE 3000
CMD ["node", "server.js"]
```

### 6.4 部署架构（单服务器容器化方案）
```
┌─────────────────────────────────────────────────┐
│                  云服务器                        │
│  ┌─────────────┐  ┌─────────────┐               │
│  │  前端容器   │  │  后端容器   │               │
│  │  (Next.js)  │  │  (FastAPI)  │               │
│  │  端口:3000  │  │  端口:8000  │               │
│  └─────────────┘  └─────────────┘               │
│          │               │                      │
│          └───────┬───────┘                      │
│                  │                              │
│           ┌─────────────┐                      │
│           │  Nginx反向  │                      │
│           │    代理     │                      │
│           │  端口:80/443│                      │
│           └─────────────┘                      │
└─────────────────────────────────────────────────┘
```

### 6.5 环境变量配置（.env.example）
```bash
# 后端配置
DATABASE_URL=sqlite:///app/data/my_web.db
JWT_SECRET_KEY=your-secret-key-change-in-production
XBK_JWT_SECRET_KEY=xbk-secret-key-change-in-production

# AI服务配置
DEEPSEEK_API_KEY=your-deepseek-api-key
DIFY_API_KEY=your-dify-api-key
DIFY_BASE_URL=http://localhost:6606/v1

# 仓库同步
GITHUB_ACCESS_TOKEN=your-github-token
SYNC_INTERVAL_SECONDS=86400
ENABLE_AUTO_SYNC=true

# 前端配置
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 七、项目状态与下一步计划

### 7.1 当前状态
- ✅ **核心功能**: 所有主要模块功能已实现并测试
- ✅ **文档完整**: 开发日志和技术文档齐全
- ✅ **代码质量**: 模块化设计，代码结构清晰
- ✅ **部署就绪**: 支持容器化部署，有完整部署规划
- ✅ **安全认证**: 多模块支持安全认证，符合企业级标准

### 7.2 已知问题
1. **数据库分散**: 目前有多个数据库文件（my_web.db、znt.db、xbk.db），建议统一
2. **日志管理**: 日志文件分散，缺乏统一的日志管理系统
3. **监控告警**: 缺乏生产环境监控和告警机制
4. **CI/CD**: 需要建立完整的CI/CD流水线

### 7.3 下一步计划

#### 短期计划（1-2周）
1. **代码整理**: 清理冗余文件，完善.gitignore
2. **GitHub同步**: 将最新代码推送到GitHub仓库
3. **文档完善**: 更新README和部署文档
4. **本地测试**: 确保所有功能在本地正常运行

#### 中期计划（2-4周）
1. **容器化部署**: 完善Docker配置，支持一键启动
2. **环境配置**: 支持环境变量配置，便于不同环境部署
3. **数据库迁移**: 考虑生产环境使用PostgreSQL/MySQL
4. **自动化脚本**: 创建部署和运维脚本

#### 长期计划（1-2个月）
1. **CI/CD流水线**: GitHub Actions自动化测试和部署
2. **监控告警**: 系统监控、日志收集和性能监控
3. **高可用部署**: 多实例部署和负载均衡
4. **安全加固**: HTTPS、防火墙、访问控制

## 八、开发日志文档索引

### 8.1 文档概览
```
docs/dev-logs/                    # 开发日志目录（详细记录）
├── ai-agent-merged.md          # AI智能体模块完整开发文档
├── competition-dev-log.md      # 信息学竞赛模块开发日志
├── dify-agent-design.md        # Dify类智能体集成设计
├── homepage-dev-log.md         # 首页开发日志
├── personal-programs-design.md # 个人程序中心设计文档
└── xbk-dev-log.md             # 校本课系统开发文档
```

### 8.2 文档内容摘要

#### 8.2.1 ai-agent-merged.md
- **版本**: v2.8（最新）
- **内容**: AI智能体模块的完整技术文档，包含从v1.0到v2.8的所有版本变更
- **重点**: 数据库设计、API接口、安全认证、时间处理、模块化重构

#### 8.2.2 xbk-dev-log.md
- **版本**: v2.5（最新）
- **内容**: 校本课处理系统的完整开发文档，包含移植计划、数据库设计、API设计
- **重点**: 多组数据支持、模块化导出、实时筛选、Excel美化

#### 8.2.3 competition-dev-log.md
- **内容**: 信息学竞赛模块的开发日志，记录遇到的问题和解决方案
- **重点**: GitHub自动同步、PDF缓存、环境变量配置、调度器管理

#### 8.2.4 homepage-dev-log.md
- **内容**: 首页和导航系统的开发日志，记录界面优化过程
- **重点**: 响应式设计、导航布局、标签精简、外部链接集成

#### 8.2.5 personal-programs-design.md
- **内容**: 个人程序中心的设计文档，记录登录保护和应用展示实现
- **重点**: 简单认证、静态卡片、隐私保护、新窗口跳转

#### 8.2.6 dify-agent-design.md
- **内容**: Dify类智能体的集成设计方案，记录与DeepSeek类的差异
- **重点**: API类型对比、表单验证、用户标识处理、连接测试

## 九、贡献与维护

### 9.1 开发规范
1. **代码风格**: 遵循项目现有代码风格，TypeScript使用严格模式
2. **提交信息**: 使用清晰的提交信息，关联相关文档更新
3. **文档更新**: 代码变更时同步更新相关文档
4. **测试要求**: 新功能需提供测试用例，确保向后兼容

### 9.2 文档维护
1. **版本控制**: 文档版本号与代码版本号同步
2. **变更记录**: 重要变更需记录在相关文档中
3. **定期审查**: 每月审查文档准确性，更新过时内容
4. **问题反馈**: 文档问题通过GitHub Issues反馈

### 9.3 问题处理流程
1. **问题发现**: 用户反馈或系统监控发现问题
2. **问题记录**: 在相关文档中记录问题现象和复现步骤
3. **问题分析**: 分析问题原因，制定解决方案
4. **修复实施**: 实施修复，更新相关文档
5. **验证测试**: 验证修复效果，确保问题解决

## 十、联系与支持

### 10.1 项目信息
- **项目名称**: MyWeb
- **仓库地址**: https://github.com/shuhao0727/my_web.git
- **当前分支**: main（领先origin/main 7个提交）
- **最新提交**: b2f8ec6（修改完善了一些错误）

### 10.2 技术支持
- **文档查询**: 首先查阅相关开发日志文档
- **问题排查**: 检查后端日志文件（backend/backend.log）
- **API测试**: 使用API文档（http://localhost:8000/docs）进行测试
- **社区支持**: 通过GitHub Issues获取支持

### 10.3 版本信息
- **前端**: Next.js 14 + TypeScript + Ant Design
- **后端**: FastAPI + Python 3.13 + SQLite
- **数据库**: SQLite 3.x
- **部署**: Docker + Nginx（规划中）

---
**文档版本**: v1.0  
**创建日期**: 2026年1月22日  
**最后更新**: 2026年1月22日  
**维护团队**: 项目开发团队  

**下一步行动**:
1. 团队评审此项目概述文档
2. 按照部署规划开始实施部署
3. 建立定期文档审查机制
4. 完善监控和告警系统
