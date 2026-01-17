# 更新日志

## 2026-01-16

### GitHub令牌过期弹窗功能
- **后端检测机制优化**：在 `backend/services/repo_sync_service.py` 中实现令牌过期缓存机制，避免频繁调用GitHub API。
  - 添加 `token_expired` 实例变量缓存令牌状态，仅在同步操作失败时检查令牌有效性
  - 修改 `get_repo_status()` 方法返回缓存状态，不再每次调用 `git ls-remote` 检查远程仓库
  - 在 `clone_repository()` 和 `pull_updates()` 中检测认证错误并更新令牌状态
  - 同步成功时自动重置令牌过期状态为 `False`

- **前端弹窗实现**：在 `frontend/app/competition/page.tsx` 中添加GitHub令牌过期弹窗：
  - 页面加载时调用 `checkTokenStatus()` 检查令牌状态
  - 检测到 `token_expired: true` 时自动显示弹窗提示
  - 弹窗包含详细的解决方案指导：获取新令牌、更新配置文件、重启服务
  - 移除定期检查机制，避免频繁请求，仅在页面加载时检查一次

- **API接口更新**：更新 `frontend/lib/repoApi.ts` 中 `RepoStatus` 接口，添加 `token_expired` 字段。

- **代码清理**：清理 `frontend/lib/repoApi.ts` 中不必要的Typst到HTML转换代码（约100行）。

### 技术要点
1. **零频繁检查**：页面加载不再触发GitHub API调用，仅在同步失败时检测令牌过期
2. **智能检测**：令牌过期状态在内存中缓存，快速响应页面请求
3. **用户友好**：清晰的弹窗指导用户如何更新令牌，最小化用户困惑
4. **自动恢复**：令牌更新后同步成功自动清除过期状态

### 后端清理
- **删除不必要的目录**：删除了 `backend/models/`, `backend/schemas/`, `backend/database/`, `backend/scheduler/` 目录，因为这些目录中的代码目前未被使用，且项目已转向使用静态文件服务和GitHub同步API。
- **简化主应用**：清理了 `backend/main.py` 中无用的导入和代码，仅保留静态文件服务和仓库同步API。

### 前端简化
- **删除未使用页面**：删除了 `frontend/app/admin/` 和 `frontend/app/(student)/` 目录，这些页面目前未被使用，且功能尚未实现。
- **简化竞赛页面**：将 `frontend/app/competition/page.tsx` 简化为仅保留目录树和PDF预览功能，移除了仓库状态、同步按钮等冗余UI。
- **删除日志文件**：删除了 `frontend/frontend.log` 和 `backend/backend.log` 等日志文件。

### 配置优化
- **开启自动同步**：将 `backend/.env` 中的 `ENABLE_AUTO_SYNC` 设置为 `True`，并设置同步间隔为6小时（21600秒）。
- **修复导入问题**：在 `backend/main.py` 中移除了对已删除模块的导入，确保应用能够正常启动。

### 功能说明
- **当前核心功能**：竞赛文档浏览（通过GitHub仓库同步Typst文档并编译为PDF）。
- **服务状态**：
  - 后端API运行在 `http://localhost:8000`
  - 前端Next.js运行在 `http://localhost:6608`
  - 竞赛页面地址：`http://localhost:6608/competition`

## 设计注意事项

### 前端结构
1. **页面组织**：所有页面位于 `frontend/app/` 目录下，按照功能划分。
2. **组件复用**：通用组件应放在 `frontend/components/` 目录中。
3. **API调用**：所有后端API调用应通过 `frontend/lib/` 目录下的模块进行封装。

### 后端结构
1. **简洁为主**：后端仅提供静态文件服务和必要的API，不包含复杂的业务逻辑。
2. **数据存储**：目前使用SQLite数据库，但主要数据来源于GitHub仓库同步。
3. **自动同步**：通过环境变量控制自动同步，默认每6小时同步一次。

### 开发规范
1. **代码提交**：每次功能更新后，应更新本日志。
2. **依赖管理**：Python依赖使用 `requirements.txt`，Node.js依赖使用 `package.json`。
3. **日志记录**：避免将日志文件提交到版本控制系统，应在 `.gitignore` 中忽略。

### 未来规划
1. **用户系统**：如需添加用户登录功能，可重新设计 `app/(student)/` 目录。
2. **后台管理**：如需后台管理，可重新设计 `app/admin/` 目录。
3. **扩展功能**：可根据需要添加AI实验室、博客、资源下载等模块。

## 已知问题
1. **PDF缓存**：部分PDF文件可能因编译错误而无法生成，需要检查Typst文件语法。
2. **GitHub同步**：网络问题可能导致同步失败，需确保网络连接正常。
3. **跨域访问**：已配置CORS，但若前端端口变更需同步更新。

## 部署说明
1. **后端部署**：使用 `uvicorn backend.main:app` 启动。
2. **前端部署**：使用 `npm run build` 构建，然后 `npm start` 启动生产服务器。
3. **环境变量**：需配置 `backend/.env` 文件，尤其是GitHub访问令牌。

---
*最后更新：2026-01-16*
