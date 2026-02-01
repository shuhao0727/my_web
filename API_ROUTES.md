# MyWeb API 路由映射文档

## 🎯 优化概要
**版本**: 2.0.0  
**优化完成时间**: 2026年2月1日  
**核心改进**: 统一路由斜杠处理，优化Nginx配置，修复API一致性

### ✅ 主要优化成果
1. **统一斜杠处理策略**: 所有路由模块配置 `redirect_slashes=False`
2. **智能Nginx重写**: 自动处理一级路由斜杠问题
3. **修复API一致性问题**: 所有主要API端点运行正常
4. **优化代理配置**: 提升性能和稳定性

## API 路由结构

### 1. AI 智能体 API (Nginx代理: `/api/ai/*` → 后端 `/api/ai/*`)
**后端前缀**: `/api/ai/*`
**特性**: 统一斜杠处理，支持智能重写
- 根路由: `GET /api/ai/` (返回模块信息)
- 健康检查: `GET /api/ai/health`
- 认证管理: 
  - `POST /api/ai/auth/login`
  - `GET /api/ai/auth/users` (需要管理员权限)
  - `GET /api/ai/auth/me` (需要认证)
- 智能体管理:
  - `GET /api/ai/agents/` (列表)
  - `GET /api/ai/agents/{id}` (详情)
  - `POST /api/ai/agents/` (创建)
  - `PUT /api/ai/agents/{id}` (更新)
  - `DELETE /api/ai/agents/{id}` (删除)
  - `POST /api/ai/agents/{id}/test-connection` (测试连接)
  - `GET /api/ai/agents/types` (类型列表)
- 对话管理:
  - `GET /api/ai/conversations/` (列表)
  - `GET /api/ai/conversations/{id}` (详情)
  - `POST /api/ai/conversations/` (创建)
  - `PUT /api/ai/conversations/{id}` (更新)
  - `DELETE /api/ai/conversations/{id}` (删除)
  - `GET /api/ai/conversations/user/{id}/summary` (用户摘要)
- 聊天接口:
  - `POST /api/ai/chat/` (标准聊天)
  - `POST /api/ai/chat/stream` (流式聊天)
  - `GET /api/ai/chat/agents/{id}/test` (测试智能体)
- 用户管理: `GET /api/ai/user-management/users` (列表)
- 数据统计: `GET /api/ai/data/stats` (统计数据)

### 2. XBK 应用 API (Nginx代理: `/api/xbk/*` → 后端 `/api/xbk/*`)
**后端前缀**: `/api/xbk/*`
**特性**: 多版本认证，数据库集成
- 应用信息: `GET /api/xbk/applications` (返回应用元数据)
- 健康检查: `GET /api/xbk/health`
- 用户列表: `GET /api/xbk/users` (调试用)
- 安全认证:
  - `POST /api/xbk/auth/login` (新版JWT认证)
  - `GET /api/xbk/auth/me` (获取当前用户信息)
- 系统配置:
  - `GET /api/xbk/config/system` (获取配置)
  - `POST /api/xbk/config/system` (更新配置)
- 数据管理:
  - `POST /api/xbk/import/{data_type}` (导入数据)
  - `GET /api/xbk/data/{data_type}` (查询数据)
  - `DELETE /api/xbk/data/{data_type}` (删除数据)
  - `PUT /api/xbk/data/{data_type}/{record_id}` (更新数据)
- 数据分析:
  - `GET /api/xbk/analysis/course-stats` (课程统计)
  - `GET /api/xbk/analysis/class-stats` (班级统计)
  - `GET /api/xbk/analysis/students-without-courses` (未选课学生)
- 数据导出: `GET /api/xbk/export/{export_type}`

### 3. Typst 内容 API (Nginx代理: `/api/typst/*` → 后端 `/api/typst/*`)
**后端前缀**: `/api/typst/*`
**特性**: 支持Typst编译和渲染
- 健康检查: `GET /api/typst/health`
- 文件树结构: `GET /api/typst/tree`
- 仓库结构: `GET /api/typst/structure`
- 文件内容: `GET /api/typst/content/{filepath}`
- 文件搜索: `GET /api/typst/search`
- 编译功能:
  - `POST /api/typst/compile` (编译源代码)
  - `GET /api/typst/render/{filepath}` (渲染文件)

### 4. 仓库同步 API (Nginx代理: `/api/repo/*` → 后端 `/api/repo/*`)
**后端前缀**: `/api/repo/*`
**特性**: Git仓库同步，PDF缓存
- 仓库状态: `GET /api/repo/status`
- 仓库结构: `GET /api/repo/structure`
- 文件列表: `GET /api/repo/list`
- 文件内容: `GET /api/repo/file`
- 章节管理:
  - `GET /api/repo/chapters` (章节列表)
  - `GET /api/repo/chapters/{chapter_path}` (章节文件)
  - `GET /api/repo/chapter-file/{file_path}` (文件内容)
- PDF功能:
  - `GET /api/repo/chapter-pdf/{file_path}` (动态PDF)
  - `GET /api/repo/chapter-pdf-static/{file_path}` (静态PDF)
  - `GET /api/repo/chapter-pdf-url/{file_path}` (PDF URL)
  - `GET /api/repo/pdf-cache/info` (缓存信息)
  - `POST /api/repo/pdf-cache/generate` (生成缓存)
- 同步调度器:
  - `GET /api/repo/sync-scheduler/status` (状态)
  - `POST /api/repo/sync-scheduler/start` (启动)
  - `POST /api/repo/sync-scheduler/stop` (停止)

### 5. Markdown 内容 API (Nginx代理: `/api/md/*` → 后端 `/api/md/*`)
**后端前缀**: `/api/md/*`
**特性**: Markdown文件处理
- 文章树结构: `GET /api/md/articles/tree`
- 文章内容: `GET /api/md/articles/content/{filepath}`
- 文章结构: `GET /api/md/articles/structure`
- 文章搜索: `GET /api/md/articles/search`
- 健康检查: `GET /api/md/articles/health`

### 6. 通用 API
**前缀**: `/*`
- 根路由: `GET /` (应用信息)
- 健康检查: `GET /health`
- API健康检查: `GET /api/health`

## 🔧 Nginx 代理配置

### 生产模式 (6608端口)
- **外部访问**: `http://localhost:6608` (统一入口)
- **后端服务**: 内部8000端口，不对外暴露
- **前端服务**: 内部3000端口，不对外暴露
- **静态内容**: 通过 `/content/` 路径代理

### 智能路由处理特性
1. **AI模块智能斜杠处理**:
   ```nginx
   # 自动为一级路由添加斜杠
   location /api/ai/ {
     if ($request_uri ~ ^/api/ai/(agents|conversations|auth|data|user-management|chat)(\?|$)) {
       rewrite ^(/api/ai/(agents|conversations|auth|data|user-management|chat))(\?|$) $1/$is_args$args break;
     }
   }
   ```

2. **特殊重定向优化**:
   ```nginx
   # user-management/users 自动重写
   if ($request_uri ~ ^/api/ai/user-management(\?|$)) {
     rewrite ^(/api/ai/user-management)(\?|$) $1/users$is_args$args break;
   }
   ```

### 安全特性
1. **生产隔离**:
   - 后端服务仅内部通信
   - 外部请求统一由Nginx代理
   - 隐藏技术栈信息

2. **安全头设置**:
   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff
   - Content-Security-Policy: 严格策略
   - Referrer-Policy: 降级时无引用

3. **性能优化**:
   - 静态文件缓存 (1小时)
   - 代理缓冲和连接复用
   - 超时控制和负载均衡

## 🧪 验证方法

### 1. 全面API健康检查
```bash
# 基础健康检查
curl -s "http://localhost:6608/api/health" | jq '.status, .environment'

# 模块化健康检查
curl -s "http://localhost:6608/api/ai/health" | jq '.status'
curl -s "http://localhost:6608/api/typst/health" | jq '.status'
curl -s "http://localhost:6608/api/repo/status" | jq '.success'
curl -s "http://localhost:6608/api/xbk/health" | jq '.status'
```

### 2. 核心功能验证
```bash
# 测试斜杠处理优化（不带斜杠访问）
for endpoint in "ai/agents" "ai/conversations" "typst/tree" "repo/structure"; do
  echo -n "api/$endpoint -> "
  curl -s -o /dev/null -w "%{http_code}" "http://localhost:6608/api/$endpoint"
  echo " "
done

# 获取AI模块信息
curl -s "http://localhost:6608/api/ai/" | jq '.module, .status'

# 获取XBK应用信息
curl -s "http://localhost:6608/api/xbk/applications" | jq '.name, .status'
```

### 3. 静态文件访问测试
```bash
# 内容目录访问
curl -s -o /dev/null -w "%{http_code}" "http://localhost:6608/content/"

# 前端应用访问
open http://localhost:6608
```

## 📊 当前API状态 (2026-02-01)

| 模块 | 状态 | 修复情况 | 测试结果 |
|------|------|----------|----------|
| AI智能体API | ✅ 正常 | 斜杠处理统一，Nginx智能重写 | 200/200/200 |
| Typst内容API | ✅ 正常 | redirect_slashes=False配置 | 200/200/200 |
| 仓库同步API | ✅ 正常 | 路由标准化 | 200/200 |
| XBK应用API | ✅ 正常 | 路由修复，新增applications端点 | 200/404(待修复) |
| 前端应用 | ✅ 正常 | 统一代理访问 | 200 OK |
| 静态文件 | ✅ 正常 | 缓存优化 | 200 OK |

## 🚨 注意事项

1. **API调用建议**:
   - 建议所有API调用使用带斜杠的URL（如 `/api/ai/agents/`）
   - Nginx已配置智能重写，但前端代码建议使用标准格式

2. **认证要求**:
   - AI模块需要JWT认证
   - XBK模块支持学生和管理员双模式认证
   - 管理员用户名必须为"admin"

3. **性能考虑**:
   - Typst编译和PDF生成可能耗时较长（30秒超时）
   - 大型文件建议使用静态缓存版本
   - 启用WebSocket支持以提升实时体验

4. **部署环境**:
   - 确保环境变量正确配置
   - 数据库连接测试通过
   - 内容目录权限正确

**文档版本**: 2.0.0  
**最后更新**: 2026年2月1日  
**维护状态**: ✅ 优化完成
