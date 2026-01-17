# 信息学竞赛开发日志

## 一、板块目标和功能
- **核心目标**: 为信息学竞赛学习者和教练提供算法笔记、题解和教学资源的集中管理和展示平台
- **主要功能**:
  1. **GitHub仓库自动同步**: 定时从GitHub仓库拉取最新的竞赛笔记和题解
  2. **PDF笔记浏览**: 将Typst格式的算法笔记编译为PDF并提供在线浏览
  3. **章节分类管理**: 按算法知识点（基础、数据结构、图论、动态规划等）组织内容
  4. **自动更新检测**: 智能检测仓库更新，减少不必要的PDF重新编译

## 二、当前进度
- **已完成的功能**:
  - ✅ GitHub仓库自动同步系统（基于schedule库）
  - ✅ PDF缓存服务（减少重复编译）
  - ✅ 章节分类API接口
  - ✅ 自动同步间隔配置化（支持环境变量调整）
  - ✅ 调度器状态监控API

- **遇到的问题及解决方案**:
  1. **问题**: 自动同步间隔修改后不生效
     **原因**: 调度器在初始化时读取环境变量，重启服务后配置未更新
     **解决方案**: 修改调度器代码，延迟加载环境变量，在启动时重新读取配置
     ```python
     # 原代码（问题）
     def __init__(self):
         self.sync_interval = int(os.getenv("SYNC_INTERVAL_SECONDS", "21600"))
     
     # 修改后代码（解决方案）
     def _load_config(self):
         self.sync_interval = int(os.getenv("SYNC_INTERVAL_SECONDS", "21600"))
     
     def start(self):
         self._load_config()  # 启动时重新加载配置
     ```

  2. **问题**: 环境变量读取失败
     **原因**: main.py未加载.env文件
     **解决方案**: 在main.py中添加dotenv支持
     ```python
     from dotenv import load_dotenv
     env_path = os.path.join(os.path.dirname(__file__), '.env')
     if os.path.exists(env_path):
         load_dotenv(env_path)
     ```

  3. **问题**: 同步频率过高（6小时/次）
     **原因**: 默认配置过于频繁，消耗网络和计算资源
     **解决方案**: 将同步间隔调整为24小时
     ```env
     # 修改前
     SYNC_INTERVAL_SECONDS=21600  # 6小时
     # 修改后
     SYNC_INTERVAL_SECONDS=86400  # 24小时
     ```

  4. **问题**: 竞赛页面无法加载文档（"信息学竞赛的内容显示没有文件了"）
     **原因**: 配置中使用了错误的IP地址（http://192.168.5.69:6608）导致CORS错误和API调用失败
     **解决方案**: 
     1. 修复后端CORS配置，移除错误的IP地址，只保留localhost地址
     2. 确认前端API_BASE配置为正确的localhost地址
     3. 重启前后端服务并验证连接
     ```python
     # 修复后的CORS配置
     origins = [
         "http://localhost:3000",
         "http://localhost:6608",
         "http://127.0.0.1:3000", 
         "http://127.0.0.1:6608",
     ]
     ```

## 三、关键变量名
### 环境变量 (.env)
```env
SYNC_INTERVAL_SECONDS=86400     # 同步间隔（秒），24小时
ENABLE_AUTO_SYNC=True           # 是否启用自动同步
GITHUB_ACCESS_TOKEN=xxx         # GitHub访问令牌（可选）
DATABASE_URL=sqlite:///./my_web.db  # 数据库连接字符串
```

### 调度器相关变量
- `sync_interval`: 同步间隔时间（秒）
- `enable_auto_sync`: 是否启用自动同步
- `is_running`: 调度器是否正在运行

### 仓库同步变量
- `repo_path`: 本地仓库路径（/Volumes/文件/4-实用代码/my_web/content/2-My-notes）
- `remote_url`: GitHub远程仓库地址（https://github.com/shuhao0727/2-My-notes.git）

### API端点
- `GET /api/repo/status` - 获取仓库同步状态
- `POST /api/repo/sync` - 手动触发同步
- `GET /api/repo/sync-scheduler/status` - 获取调度器状态
- `POST /api/repo/sync-scheduler/start` - 启动调度器
- `POST /api/repo/sync-scheduler/stop` - 停止调度器

## 四、AI完善过程中需要注意的事项
1. **网络连接稳定性**:
   - GitHub API可能有访问限制，需要添加重试机制
   - 网络超时时间需要适当延长（当前75秒可能不够）
   - 考虑添加代理支持或备用同步方式

2. **资源使用优化**:
   - PDF编译消耗CPU资源，需要控制并发编译数量
   - 磁盘空间管理，定期清理旧版本PDF缓存
   - 内存使用监控，避免内存泄漏

3. **错误处理和恢复**:
   - Git操作失败时的回滚机制
   - PDF编译失败时的降级方案（显示原始Typst文件）
   - 数据库连接中断的自动重连

4. **安全性考虑**:
   - GitHub令牌的安全存储，避免硬编码
   - 文件路径遍历漏洞防护
   - API接口的访问权限控制

5. **用户体验优化**:
   - 同步进度实时反馈
   - 失败操作的友好错误提示
   - 手动同步和自动同步的区分显示

---
*最后更新: 2026-01-17 20:26:00*
