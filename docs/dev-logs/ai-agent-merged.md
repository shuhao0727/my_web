# AI智能体模块 - 完整开发文档

## 一、核心功能概述

### 1.1 模块定位
- **名称**: AI智能体模块 (AI Lab)
- **定位**: 集成多AI服务的学生学习助手平台
- **用户角色**: 管理员(admin) / 学生(student)
- **核心价值**: 统一管理多个AI服务，提供个性化学习支持

### 1.2 核心功能
- ✅ **多AI服务集成**: DeepSeek API、Dify API
- ✅ **用户管理系统**: 学生信息CRUD、Excel批量导入
- ✅ **智能体管理**: 创建、配置、测试不同AI智能体
- ✅ **对话系统**: 完整对话历史、消息存储、上下文管理
- ✅ **权限控制**: 双角色权限体系、数据隔离
- ✅ **管理界面**: 学生管理、智能体管理、数据统计
- ✅ **实时监控**: 对话监控、时间戳验证、使用统计

## 二、技术架构

### 2.1 系统架构
```
┌─────────┐    ┌─────────┐    ┌──────────────┐
│ 前端    │ ←→ │ 后端API │ ←→ │ 外部AI服务   │
│ Next.js │    │ FastAPI │    │ DeepSeek/Dify│
└─────────┘    └─────────┘    └──────────────┘
                      ↓
                ┌──────────┐
                │ 数据库   │
                │ SQLite   │
                │ (znt.db) │
                └──────────┘
```

### 2.2 数据库设计 (znt.db)

#### 2.2.1 用户表 (ai_users)
```sql
CREATE TABLE ai_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL,           -- 用户名（唯一，作为姓名显示）
    password_hash VARCHAR(255) NOT NULL,      -- 密码哈希（实际应用需加密）
    student_id VARCHAR(50) UNIQUE,           -- 学号（学生专用）
    class_name VARCHAR(100),                 -- 班级名称
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.2.2 智能体表 (ai_agents)
```sql
CREATE TABLE ai_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,              -- 智能体名称
    api_type VARCHAR(20) NOT NULL CHECK (api_type IN ('deepseek', 'dify')), -- 智能体类型
    api_key VARCHAR(255),                     -- API密钥
    base_url VARCHAR(255),                    -- 基础URL
    model VARCHAR(100),                       -- 模型名称（用于DeepSeek类）
    app_id VARCHAR(100),                      -- 应用ID（用于Dify类）
    is_active BOOLEAN DEFAULT TRUE,           -- 是否启用
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.2.3 对话表 (ai_conversations)
```sql
CREATE TABLE ai_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                -- 用户ID (关联ai_users.id)
    agent_id INTEGER NOT NULL,               -- 智能体ID (关联ai_agents.id)
    session_id VARCHAR(100) UNIQUE,          -- 会话ID（唯一）
    title VARCHAR(200),                      -- 对话标题（自动生成）
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 开始时间（UTC时间）
    end_time DATETIME,                       -- 结束时间
    total_messages INTEGER DEFAULT 0,        -- 总消息数
    total_tokens BIGINT DEFAULT 0,           -- 总token数
    conversation_metadata JSON,              -- 会话元数据（JSON格式）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES ai_users (id),
    FOREIGN KEY(agent_id) REFERENCES ai_agents (id)
);
```

#### 2.2.4 消息表 (ai_messages)
```sql
CREATE TABLE ai_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,        -- 对话ID (关联ai_conversations.id)
    role VARCHAR(20) NOT NULL,               -- 角色：user/assistant
    content TEXT NOT NULL,                   -- 消息内容
    tokens INTEGER,                          -- 消息消耗的token数
    message_metadata JSON,                   -- 消息元数据（JSON格式）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 创建时间（UTC时间）
    FOREIGN KEY(conversation_id) REFERENCES ai_conversations (id)
);
```

#### 2.2.5 索引设计
```sql
-- 智能体表索引
CREATE INDEX ix_ai_agents_active ON ai_agents (is_active);

-- 对话表索引
CREATE INDEX ix_ai_conversations_user_agent ON ai_conversations (user_id, agent_id);
CREATE INDEX ix_ai_conversations_user_id ON ai_conversations (user_id);
CREATE INDEX ix_ai_conversations_agent_id ON ai_conversations (agent_id);
CREATE INDEX ix_ai_conversations_start_time ON ai_conversations (start_time);

-- 消息表索引
CREATE INDEX ix_ai_messages_conversation_id ON ai_messages (conversation_id);
CREATE INDEX ix_ai_messages_created_at ON ai_messages (created_at);
CREATE INDEX ix_ai_messages_conversation_created ON ai_messages (conversation_id, created_at);
```

### 2.3 关键配置

#### 2.3.1 DeepSeek类配置
```yaml
名称: DeepSeek助手
类型: deepseek
api_key: "sk-xxxxxxxxxxxxxxxx"
base_url: "https://api.deepseek.com"
model: "deepseek-chat"
```

#### 2.3.2 Dify类配置
```yaml
名称: 代码审查专家
类型: dify
api_key: "app-xxxxxxxxxxxxxxxx"
base_url: "http://localhost:6606/v1"
app_id: "code-review-app"
```

## 三、快速启动指南

### 3.1 环境准备
```bash
# 1. 启动后端服务
cd /Volumes/文件/4-实用代码/my_web/backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

# 2. 启动前端服务
cd /Volumes/文件/4-实用代码/my_web/frontend
nohup npm run dev > frontend.log 2>&1 &

# 3. 验证服务状态
curl -s http://localhost:8000/health  # 应返回200
curl -s http://localhost:6608  # 应返回200
```

### 3.2 初始配置
1. **数据库初始化**: znt.db已包含初始表结构
2. **默认用户**: 
   - 管理员: username="管理员", role="admin"
   - 学生: 可通过Excel批量导入
3. **AI服务配置**: 在智能体管理界面添加API密钥

### 3.3 访问地址
- 主页面: http://localhost:6608/ai-lab
- 管理界面: http://localhost:6608/ai-lab/admin (新标签页打开)
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 四、用户管理流程

### 4.1 学生导入
1. 准备Excel模板（姓名、学号、班级）
2. 在管理界面选择文件导入
3. 系统验证数据格式并导入数据库
4. 学生可立即登录使用

### 4.2 登录流程
1. **输入信息**: 姓名(必填) + 学号(可选)
2. **后端验证**: 
   - 验证用户名存在
   - 如果提供学号，验证学号匹配
   - 检查账户状态(is_active)
3. **会话建立**: 返回用户信息，建立前端会话

### 4.3 权限控制
- **管理员**: 所有管理功能 + 所有智能体访问
- **学生**: 仅限分配的智能体 + 个人对话历史

## 五、智能体管理

### 5.1 智能体类型

#### 5.1.1 DeepSeek类智能体
- **特点**: 单一API端点，标准化参数
- **必填配置**: API密钥、模型名称、基础URL
- **示例**: DeepSeek助手、OpenAI等

#### 5.1.2 Dify类智能体
- **特点**: 需要应用ID配置
- **必填配置**: API密钥、基础URL、应用ID
- **示例**: Dify应用、自定义API等

### 5.2 管理功能
- ✅ **添加智能体**: 根据类型显示不同配置表单
- ✅ **查看列表**: 表格显示名称、类型、状态
- ✅ **编辑配置**: 修改API密钥等参数
- ✅ **删除智能体**: 移除不再使用的智能体
- ✅ **启用/禁用**: 控制智能体是否可用
- ✅ **测试连接**: 一键测试API连通性

### 5.3 智能体切换优化
切换智能体时，系统会：
1. 保存当前智能体信息
2. 加载新智能体的对话历史
3. 检查当前对话是否属于新智能体
4. 仅清空不相关的对话消息，保持相关对话上下文

## 六、对话系统

### 6.1 对话流程
1. **智能体选择**: 左侧边栏选择可用智能体
2. **消息发送**: 用户输入 → 后端API → AI服务 → 响应返回
3. **历史记录**: 所有对话自动保存，支持继续对话
4. **上下文管理**: 保持对话上下文，支持长对话

### 6.2 时间显示处理

#### 6.2.1 问题描述
- **现象**: 消息时间显示为05:40，实际当前时间应为13:46左右（8小时时差）
- **原因**: 数据库存储UTC时间，前端解析时未正确处理时区转换

#### 6.2.2 解决方案
```typescript
// 将数据库UTC时间字符串转换为本地时间显示
const parseDbTimeToLocal = (dbTimeString: string): Date => {
  // 数据库时间格式可能是 "2026-01-20 05:50:48" (UTC时间)
  // 也可能是ISO格式 "2026-01-20T05:50:48"
  
  // 首先，如果字符串已经是ISO格式（包含T），直接解析
  if (dbTimeString.includes('T')) {
    return new Date(dbTimeString);
  }
  
  // 否则，假设是"YYYY-MM-DD HH:MM:SS"格式，并且是UTC时间
  // 将其转换为ISO格式的UTC时间字符串
  const isoString = dbTimeString.replace(' ', 'T') + 'Z';
  const date = new Date(isoString);
  
  // 如果解析失败，尝试直接解析
  if (isNaN(date.getTime())) {
    console.warn('时间解析失败，使用直接解析:', dbTimeString);
    return new Date(dbTimeString);
  }
  
  return date;
};

// 格式化时间显示，确保显示正确的本地时间
const formatTimeForDisplay = (dateInput: Date | string): string => {
  let date: Date;
  if (typeof dateInput === 'string') {
    date = parseDbTimeToLocal(dateInput);
  } else {
    date = dateInput;
  }
  
  // 使用亚洲/上海时区显示时间
  return date.toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit', 
    minute: '2-digit',
    timeZone: 'Asia/Shanghai'
  });
};
```

#### 6.2.3 验证方法
1. 发送新消息，时间应正确显示为当前本地时间
2. 查看历史对话消息，时间应正确转换
3. 控制台查看调试信息（开发环境）

### 6.3 Markdown支持
- 前端使用react-markdown渲染消息内容
- 后端保留原始Markdown格式
- 支持代码块、列表、链接等Markdown语法

## 七、数据管理系统（简化版）

### 7.1 设计目标
为管理员提供简单的后台界面，查看学生使用AI智能体的情况：
1. **学生使用统计**: 查看每个学生使用智能体的基本情况
2. **对话内容查看**: 查看学生提问的问题和提问时间
3. **简单筛选**: 按班级、时间范围筛选数据

### 7.2 核心功能

#### 7.2.1 学生列表页面
- 显示学生基本信息：姓名、学号、班级
- 显示使用统计：对话总数、消息总数
- 显示最后活跃时间
- 支持按班级筛选

#### 7.2.2 学生对话记录
- 点击学生进入对话记录页面
- 显示该学生的所有对话列表
- 每个对话显示：对话标题、开始时间、消息数
- 点击对话查看具体内容

#### 7.2.3 对话详情查看
- 显示完整的对话内容
- 按时间顺序显示消息（用户提问和AI回答）
- 每条消息显示：角色、内容、时间

### 7.3 API接口设计

#### 7.3.1 学生列表API
```
GET /api/ai/data/students
参数：class_name（班级筛选）、search（姓名/学号搜索）、page、page_size
```

#### 7.3.2 学生对话列表API
```
GET /api/ai/data/students/{student_id}/conversations
参数：start_date、end_date、page、page_size
```

#### 7.3.3 对话详情API
```
GET /api/ai/data/conversations/{conversation_id}
返回完整对话内容
```

## 八、监控系统

### 8.1 实时对话监控

#### 8.1.1 监控脚本
```bash
cd /Volumes/文件/4-实用代码/my_web/backend
python3 conversation_monitor_enhanced.py
```

#### 8.1.2 监控功能
1. **实时消息显示**: 👤表示用户消息，🤖表示AI回复
2. **时间戳验证**: 显示数据库原始时间、UTC时间、本地时间的完整转换
3. **对话状态跟踪**: 显示对话ID、用户、智能体、token数
4. **系统状态摘要**: 总体统计和最近1小时活动

#### 8.1.3 增强监控特性
- 每秒检查新消息
- 显示时间转换验证（UTC → UTC+8）
- 提供详细的调试信息
- 监控智能体使用排名

### 8.2 服务监控

#### 8.2.1 健康检查
```bash
# 后端健康检查
curl -s http://localhost:8000/health

# 前端状态检查
curl -s http://localhost:6608
```

#### 8.2.2 日志查看
```bash
# 后端日志
tail -f /Volumes/文件/4-实用代码/my_web/backend/backend.log

# 前端日志
tail -f /Volumes/文件/4-实用代码/my_web/frontend/frontend.log
```

## 九、关键API接口

### 9.1 用户认证
- `POST /api/ai/auth/login` - 用户登录
- `GET /api/ai/auth/me` - 获取当前用户信息

### 9.2 用户管理
- `GET /api/ai/users` - 获取用户列表
- `POST /api/ai/users` - 创建用户
- `PUT /api/ai/users/{id}` - 更新用户
- `DELETE /api/ai/users/{id}` - 删除用户
- `POST /api/ai/users/import` - Excel批量导入

### 9.3 智能体管理
- `GET /api/ai/agents` - 获取智能体列表
- `POST /api/ai/agents` - 创建智能体
- `PUT /api/ai/agents/{id}` - 更新智能体
- `DELETE /api/ai/agents/{id}` - 删除智能体
- `POST /api/ai/agents/{id}/test-connection` - 测试连接

### 9.4 对话管理
- `GET /api/ai/conversations` - 获取对话列表（支持agent_id筛选）
- `GET /api/ai/conversations/{id}` - 获取对话详情
- `POST /api/ai/chat` - 发送消息

### 9.5 数据管理
- `GET /api/ai/data/students` - 获取学生使用统计
- `GET /api/ai/data/students/{id}/conversations` - 获取学生对话列表
- `GET /api/ai/data/conversations/{id}` - 获取对话详情

## 十、前端界面说明

### 10.1 主界面布局
```
┌─────────────────────────────────────┐
│ Header: 用户信息 + 管理按钮(admin)   │
├─────────────┬───────────────────────┤
│ 左侧边栏     │ 主内容区               │
│ • 智能体列表 │ • 对话界面             │
│ • 搜索框     │ • 消息历史             │
│ • 对话历史   │ • 输入框               │
└─────────────┴───────────────────────┘
```

### 10.2 管理界面布局
```
┌─────────────────────────────────────┐
│ 左侧导航栏                           │
│ • 学生信息管理                      │
│ • 智能体管理                        │
│ • 智能体数据管理                    │
├─────────────────────────────────────┤
│ 右侧主区域                          │
│ (根据选中项显示对应内容)             │
└─────────────────────────────────────┘
```

### 10.3 智能体管理界面
```
┌─────────────────────────────────────────────────┐
│ [搜索框]                           [创建按钮]    │
├─────────────────────────────────────────────────┤
│ 名称 | API类型 | API | 状态 | 操作              │
├─────────────────────────────────────────────────┤
│ DeepSeek助手 | DeepSeek类 | https://api... | ✅ | ✏️ 🗑️ │
│ 代码审查专家 | Dify类    | http://local... | ✅ | ✏️ 🗑️ │
└─────────────────────────────────────────────────┘
```

### 10.4 数据管理界面
```
┌─────────────────────────────────────────────┐
│  📊 学生使用统计                           │
├─────────────────────────────────────────────┤
│ [班级筛选] [搜索]                           │
├─────────────────────────────────────────────┤
│ 姓名      学号      班级  对话数 消息数  最后活跃 │
├─────────────────────────────────────────────┤
│ 张三     20230001  50     5      25     01-20 13:30 │
│ 张张     20230003  11     3      18     01-19 10:15 │
└─────────────────────────────────────────────┘
```

## 十一、故障排除

### 11.1 常见问题

#### 登录失败
- **症状**: "学号不正确"或"用户不存在"
- **解决**: 
  1. 确认用户名正确（中文姓名）
  2. 学号为可选，可不填写
  3. 检查用户状态(is_active=true)

#### API调用失败
- **症状**: 智能体无响应或报错
- **解决**:
  1. 检查API密钥配置
  2. 验证网络连接
  3. 查看后端日志

#### 时间显示错误
- **症状**: 消息时间显示比实际早8小时
- **解决**:
  1. 确认前端时间解析函数正常工作
  2. 检查数据库时间是否为UTC格式
  3. 验证时区转换逻辑

#### 智能体切换问题
- **症状**: 切换智能体时消息被清空
- **解决**:
  1. 确认切换逻辑正确筛选对话
  2. 检查对话是否属于当前智能体
  3. 验证API筛选参数传递正确

### 11.2 调试技巧

#### 服务连接检查
```bash
# 检查后端进程
ps aux | grep uvicorn

# 检查前端进程
ps aux | grep next

# 检查端口占用
lsof -i :8000
lsof -i :6608
```

#### 数据库检查
```bash
# 检查数据库连接
sqlite3 /Volumes/文件/4-实用代码/my_web/backend/znt.db "SELECT COUNT(*) FROM ai_messages;"

# 检查表结构
sqlite3 /Volumes/文件/4-实用代码/my_web/backend/znt.db ".schema ai_messages"
```

#### API连通性测试
```bash
# 测试DeepSeek智能体连通性
curl -X POST "http://localhost:8000/api/ai/agents/6/test-connection" -H "Content-Type: application/json" -d '{}'

# 测试聊天API
curl -X POST "http://localhost:8000/api/ai/chat/" -H "Content-Type: application/json" -d '{"user_id": 1, "agent_id": 6, "message": "测试"}' --max-time 10
```

### 11.3 日志查看
```bash
# 后端日志
tail -50 /Volumes/文件/4-实用代码/my_web/backend/backend.log

# 前端日志 (开发模式)
# 浏览器开发者工具 → Console
```

## 十二、维护与扩展

### 12.1 数据备份
```bash
# 备份数据库
cp /Volumes/文件/4-实用代码/my_web/backend/znt.db /Volumes/文件/4-实用代码/my_web/backend/znt.db.backup_$(date +%Y%m%d)
```

### 12.2 添加新AI服务
1. 在`backend/services/`创建新的客户端类
2. 实现通用API接口
3. 更新智能体配置类型
4. 前端添加相应支持

### 12.3 性能优化建议
- **数据库索引**: 在频繁查询的字段添加索引
- **API缓存**: 对稳定数据添加缓存层
- **连接池**: 优化数据库连接管理

### 12.4 扩展功能（未来）
- 更多AI服务集成（Claude、Gemini等）
- 高级数据分析功能
- 移动端优化
- 实时通知系统
- 智能分析（问题分类、学习难点识别）

## 十三、版本历史

### v1.0 (基础版本)
- 基础用户系统和智能体框架
- Mock API支持

### v2.0 (主要版本)
- 集成真实API (DeepSeek + Dify)
- 完整用户管理系统
- Excel批量导入功能
- 管理界面重构
- 数据库优化和字段简化

### v2.1 (2026-01-20)
- Markdown格式支持：前端使用react-markdown渲染，后端保留原始格式
- 消息顺序优化：按ID升序排列确保正确顺序
- 对话窗口高度调整：从500px增加到650px
- 服务端口修正：前端运行在6608端口

### v2.2 (2026-01-20) - 时间显示和智能体切换修复
- 时间显示问题修复：数据库UTC时间正确转换为本地时间显示
- 智能体切换优化：切换智能体时保持相关对话，仅清空不相关消息
- 监控系统增强：创建conversation_monitor_enhanced.py，提供时间戳验证
- 连接测试功能：添加智能体API连接测试功能
- 界面优化：移除冗长说明文本，使界面更简洁

### v2.3 (2026-01-20) - 服务重启和文档整理
- 服务管理优化：提供完整的服务重启脚本
- 文档整合：合并所有AI-Agent相关文档，保留最新内容
- 监控完善：增强监控系统的时间验证功能

### 未来计划
- 数据管理系统完整实现
- 更多AI服务集成
- 高级用户行为分析
- 个性化学习推荐
- 移动端应用开发

## 十四、部署和维护

### 14.1 部署要求
- Python 3.8+ 环境
- Node.js 16+ 环境
- SQLite数据库
- 稳定的网络连接（用于AI API调用）

### 14.2 启动脚本
```bash
#!/bin/bash
# 启动脚本：start_services.sh

# 停止现有服务
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null

# 启动后端服务
cd /Volumes/文件/4-实用代码/my_web/backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
echo "后端服务启动中..."

# 等待后端启动
sleep 3

# 启动前端服务
cd /Volumes/文件/4-实用代码/my_web/frontend
nohup npm run dev > frontend.log 2>&1 &
echo "前端服务启动中..."

# 等待前端启动
sleep 5

# 验证服务状态
echo "验证服务状态..."
curl -s -o /dev/null -w "后端状态: %{http_code}\n" http://localhost:8000/health 2>/dev/null
curl -s -o /dev/null -w "前端状态: %{http_code}\n" http://localhost:6608 2>/dev/null

echo "服务启动完成。"
echo "后端日志: backend/backend.log"
echo "前端日志: frontend/frontend.log"
```

### 14.3 维护计划
- **每日**: 检查服务状态，备份重要数据
- **每周**: 清理旧日志，检查磁盘空间
- **每月**: 更新依赖包，检查安全更新
- **每季度**: 全面性能评估，优化系统架构

## 十五、附录

### A. Excel导入模板
```
姓名, 学号, 班级, 角色, 状态
张三, 20230001, 计算机1班, student, 是
李四, 20230002, 计算机1班, student, 是
```

### B. 默认账户
- **管理员**: 用户名="管理员", 无密码验证(开发模式)
- **学生**: 通过Excel导入或管理界面创建

### C. 文件路径
- 后端主文件: `backend/main.py`
- AI模块路由: `backend/routers/ai/`
- 前端AI页面: `frontend/app/ai-lab/`
- 数据库文件: `backend/znt.db`
- 监控脚本: `backend/conversation_monitor_enhanced.py`
- 开发日志: `docs/dev-logs/`

### D. 关键命令
```bash
# 服务管理
./start_services.sh                    # 启动所有服务
pkill -f "uvicorn main:app"           # 停止后端
pkill -f "npm run dev"                # 停止前端

# 监控和调试
python3 backend/conversation_monitor_enhanced.py  # 监控对话
tail -f backend/backend.log           # 查看后端日志
tail -f frontend/frontend.log         # 查看前端日志

# 数据库操作
sqlite3 backend/znt.db                # 连接数据库
.backup backup.db                     # 备份数据库
```

---
**文档版本**: v2.3  
**最后更新**: 2026-01-20  
**适用版本**: 当前生产环境  
**文档状态**: ✅ 已完成合并和更新  

**合并来源**:
- `ai-agent-overview.md` - 基础框架和核心功能
- `ai-agent-config-update.md` - 配置更新和监控系统
- `ai-agent-time-fix-20260120.md` - 时间显示修复方案
- `ai-agent-management-design.md` - 智能体管理设计
- `ai-agent-data-management-simple.md` - 数据管理系统简化版

**已删除冗余文档**:
- `ai-agent-data-management-design.md` (详细版，保留简化版)
- 其他过时或重复的内容

**下一步**: 将此文档设为AI智能体模块的主要文档，其他相关文档可归档或删除。
