# MyWeb API 路由映射文档

## API 路由结构

### 1. AI 智能体 API (Nginx代理: `/api/ai/*` → 后端 `/api/ai/*`)
**后端前缀**: `/api/ai/*`
- 健康检查: `GET /api/ai/health`
- 认证: `POST /api/ai/auth/*`
- 智能体管理: `GET/POST/PUT/DELETE /api/ai/agents/*`
- 对话管理: `GET/POST/PUT/DELETE /api/ai/conversations/*`
- 聊天: `POST /api/ai/chat/*`
- 用户管理: `GET/POST/PUT/DELETE /api/ai/user-management/*`
- 数据管理: `GET/POST/PUT/DELETE /api/ai/data/*`

### 2. XBK 应用 API (Nginx代理: `/api/xbk/*` → 后端 `/api/xbk/*`)
**后端前缀**: `/api/xbk/*`
- 登录认证: `POST /api/xbk/login`
- 健康检查: `GET /api/xbk/health`
- 系统配置: `GET/POST /api/xbk/config/system`
- 数据导入: `POST /api/xbk/import/{data_type}`
- 数据查询: `GET /api/xbk/data/{data_type}`
- 数据删除: `DELETE /api/xbk/data/{data_type}`
- 数据更新: `PUT /api/xbk/data/{data_type}/{record_id}`
- 课程分析: `GET /api/xbk/analysis/course-stats`
- 班级分析: `GET /api/xbk/analysis/class-stats`
- 未选课分析: `GET /api/xbk/analysis/students-without-courses`
- 数据导出: `GET /api/xbk/export/{export_type}`
- 用户列表: `GET /api/xbk/users`

### 3. Typst 内容 API (Nginx代理: `/api/typst/*` → 后端 `/api/typst/*`)
**后端前缀**: `/api/typst/*`
- 文件树: `GET /api/typst/tree`
- 文件内容: `GET /api/typst/content/{filepath}`
- 仓库结构: `GET /api/typst/structure`
- 搜索: `GET /api/typst/search`
- 健康检查: `GET /api/typst/health`
- 编译: `POST /api/typst/compile`
- 渲染: `GET /api/typst/render/{filepath}`

### 4. 仓库同步 API (Nginx代理: `/api/repo/*` → 后端 `/api/repo/*`)
**后端前缀**: `/api/repo/*`
- 仓库状态: `GET /api/repo/status`
- 同步仓库: `POST /api/repo/sync`
- 仓库结构: `GET /api/repo/structure`
- 文件列表: `GET /api/repo/list`
- 文件内容: `GET /api/repo/file`
- 主文件: `GET /api/repo/main-typ`
- 章节列表: `GET /api/repo/chapters`
- 章节文件: `GET /api/repo/chapters/{chapter_path}`
- 章节文件内容: `GET /api/repo/chapter-file/{file_path}`
- 章节PDF: `GET /api/repo/chapter-pdf/{file_path}`
- 静态PDF: `GET /api/repo/chapter-pdf-static/{file_path}`
- PDF URL: `GET /api/repo/chapter-pdf-url/{file_path}`
- PDF缓存信息: `GET /api/repo/pdf-cache/info`
- 生成PDF缓存: `POST /api/repo/pdf-cache/generate`
- 样式文件: `GET /api/repo/style`
- 图片文件: `GET /api/repo/image`
- 同步调度器状态: `GET /api/repo/sync-scheduler/status`
- 启动调度器: `POST /api/repo/sync-scheduler/start`
- 停止调度器: `POST /api/repo/sync-scheduler/stop`

### 5. 通用 API
**前缀**: `/*`
- 根路由: `GET /`
- 健康检查: `GET /health`
- API健康检查: `GET /api/health`

## Nginx 代理配置

### 开发模式 (6608端口)
- 外部访问: `http://${EXTERNAL_HOST:-localhost}:${EXTERNAL_PORT:-6608}`
- 所有 `/api/*` 请求 → 后端容器:8000
- 所有 `/content/*` 请求 → 后端容器:8000
- 其他请求 → 前端容器:3000

### 生产模式 (6608端口)
- 外部访问: `http://${EXTERNAL_HOST:-localhost}:${EXTERNAL_PORT:-6608}`
- 所有 `/api/*` 请求 → 后端容器:8000 (内部通信)
- 所有 `/content/*` 请求 → 后端容器:8000 (内部通信)
- 其他请求 → 前端容器:3000 (内部通信)
- 后端端口不对外暴露

## 验证方法

### 1. API 可用性测试
```bash
# 测试健康检查
curl http://localhost:6608/api/health
curl http://localhost:6608/health

# 测试AI模块
curl http://localhost:6608/api/ai/

# 测试XBK模块
curl http://localhost:6608/api/xbk/health

# 测试Typst模块
curl http://localhost:6608/api/typst/health
```

### 2. 静态文件测试
```bash
# 测试内容访问
curl http://localhost:6608/content/
```

### 3. 前端访问测试
```bash
# 访问前端应用
open http://localhost:6608
```

## 安全特性

1. **生产模式安全**:
   - 后端容器仅内部通信
   - 外部无法直接访问后端API
   - 安全头设置 (CSP, XSS防护等)

2. **代理安全**:
   - 隐藏后端技术栈信息
   - 请求头过滤和标准化
   - 连接池管理和超时控制

3. **性能优化**:
   - 静态文件缓存
   - 连接复用和缓冲
   - 负载均衡支持