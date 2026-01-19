# AI智能体模块 - 简明开发文档

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
                └──────────┘
```

### 2.2 数据库设计 (znt.db)
```sql
-- 核心表结构
ai_users           # 用户表 (id, username, student_id, class_name, role, is_active, ...)
ai_agents          # 智能体表 (id, name, api_type, api_config, is_active, ...)
ai_conversations   # 对话表 (id, user_id, agent_id, title, created_at, ...)
ai_messages        # 消息表 (id, conversation_id, role, content, timestamp, ...)
```

### 2.3 关键配置
```python
# DeepSeek配置
{
  "api_type": "deepseek",
  "api_key": "sk-...",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}

# Dify配置
{
  "api_type": "dify", 
  "api_key": "app-...",
  "base_url": "http://wangsh.cn:6606/v1",
  "app_id": "..."
}
```

## 三、快速启动指南

### 3.1 环境准备
```bash
# 1. 启动后端服务
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 2. 启动前端服务
cd frontend
npm run dev  # 端口6608
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

## 四、用户管理流程

### 4.1 学生导入
```mermaid
graph LR
    A[准备Excel模板] --> B[管理界面导入]
    B --> C[数据验证]
    C --> D[数据库写入]
    D --> E[学生可登录]
```

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

## 五、智能体使用流程

### 5.1 智能体选择
1. 左侧边栏显示可用智能体列表
2. 支持搜索过滤
3. 点击智能体开始对话

### 5.2 对话交互
1. **消息发送**: 用户输入 → 后端API → AI服务 → 响应返回
2. **历史记录**: 所有对话自动保存，支持继续对话
3. **上下文管理**: 保持对话上下文，支持长对话

### 5.3 管理功能
- **智能体配置**: API类型、密钥、参数设置
- **使用统计**: 对话次数、消息数量、API调用统计
- **状态监控**: API健康检查、错误日志

## 六、关键API接口

### 6.1 用户认证
- `POST /api/ai/auth/login` - 用户登录
- `GET /api/ai/auth/me` - 获取当前用户信息

### 6.2 用户管理
- `GET /api/ai/users` - 获取用户列表
- `POST /api/ai/users` - 创建用户
- `PUT /api/ai/users/{id}` - 更新用户
- `DELETE /api/ai/users/{id}` - 删除用户
- `POST /api/ai/users/import` - Excel批量导入

### 6.3 智能体管理
- `GET /api/ai/agents` - 获取智能体列表
- `POST /api/ai/agents` - 创建智能体
- `PUT /api/ai/agents/{id}` - 更新智能体
- `DELETE /api/ai/agents/{id}` - 删除智能体

### 6.4 对话管理
- `GET /api/ai/conversations` - 获取对话列表
- `POST /api/ai/conversations` - 创建对话
- `POST /api/ai/conversations/{id}/messages` - 发送消息

## 七、前端界面说明

### 7.1 主界面布局
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

### 7.2 管理界面布局
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

## 八、故障排除

### 8.1 常见问题

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

#### 前端界面异常
- **症状**: 页面空白或功能异常
- **解决**:
  1. 检查浏览器控制台错误
  2. 确认前后端服务运行正常
  3. 清理浏览器缓存

#### 编辑学生信息时"Failed to fetch"错误
- **症状**: 在管理界面编辑学生信息时，控制台出现"Failed to fetch"错误，请求失败
- **原因分析**:
  1. **后端服务中断**: 编辑操作期间后端服务可能意外重启或崩溃
  2. **数据库表缺失**: `ai_users`表缺少`created_at`字段导致查询失败（已修复）
  3. **API响应格式**: 后端返回的响应格式与前端期望的不一致
  4. **网络连接**: 前端与后端之间的网络连接问题
- **解决方案**:
  1. **重启后端服务**: 确保后端服务稳定运行
  2. **验证数据库表**: 确认`ai_users`表结构完整
  3. **修复排序字段**: 将`AiUser.created_at`改为`AiUser.id`进行排序
  4. **增强错误处理**: 在前端添加更详细的错误日志和重试机制
- **已实施的修复**:
  ```python
  # 原代码（问题）
  users = query.order_by(AiUser.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
  
  # 修复后代码
  users = query.order_by(AiUser.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
  ```
- **验证方法**:
  ```bash
  # 测试API连通性
  curl -X PUT "http://localhost:8000/api/ai/user-management/users/8" \
    -H "Content-Type: application/json" \
    -d '{"class_name": "14"}'
  
  # 检查后端日志
  tail -f backend/backend.log
  ```

#### Excel导入成功后前端未立即刷新
- **症状**: Excel文件导入成功，数据库已写入新记录，但前端表格未立即显示新数据
- **原因分析**:
  1. **状态更新延迟**: React状态更新可能异步，导致数据重新获取时机不当
  2. **搜索过滤干扰**: 如果当前有搜索文本，新导入的数据可能被过滤掉
  3. **数据获取时机**: 后端数据提交与前端重新获取之间存在微小延迟
- **解决方案**:
  1. **立即刷新数据**: 在导入成功后立即调用`onRefresh()`重新获取数据
  2. **清空搜索文本**: 重置搜索框，确保新数据不会被过滤
  3. **双重刷新机制**: 添加短暂延迟后再次刷新，确保数据同步
- **已实施的修复**:
  ```typescript
  // 修复后的handleImport函数
  const handleImport = async (file: File) => {
    setImportLoading(true);
    
    try {
      const result = await aiApi.userManagement.importUsers(file);
      if (result.success) {
        message.success(`导入成功 ${result.imported_count} 条记录`);
        // 触发重新加载数据
        if (onRefresh) onRefresh();
        // 清空搜索文本，确保显示所有数据（包括新导入的）
        setSearchText('');
        // 添加短暂延迟确保数据加载
        setTimeout(() => {
          if (onRefresh) onRefresh();
        }, 300);
      } else {
        message.error(`导入失败: ${result.errors?.join(', ') || '未知错误'}`);
      }
    } catch (error: any) {
      console.error('导入请求失败:', error);
      message.error(`导入失败: ${error.message || '网络请求失败'}`);
    } finally {
      setImportLoading(false);
    }
    
    return false; // 阻止默认上传行为
  };
  ```
- **验证方法**:
  1. 在前端管理界面导入Excel文件
  2. 观察是否立即显示新导入的学生记录
  3. 检查控制台是否有错误
  4. 验证数据库记录是否已更新

### 8.2 日志查看
```bash
# 后端日志
tail -f backend/backend.log

# 前端日志 (开发模式)
# 浏览器开发者工具 → Console
```

## 九、维护与扩展

### 9.1 数据备份
```bash
# 备份数据库
cp backend/znt.db backend/znt.db.backup_$(date +%Y%m%d)
```

### 9.2 添加新AI服务
1. 在`backend/services/`创建新的客户端类
2. 实现通用API接口
3. 更新智能体配置类型
4. 前端添加相应支持

### 9.3 性能优化建议
- **数据库索引**: 在频繁查询的字段添加索引
- **API缓存**: 对稳定数据添加缓存层
- **连接池**: 优化数据库连接管理

## 十、版本历史

### v1.0 (基础版本)
- 基础用户系统和智能体框架
- Mock API支持

### v2.0 (当前版本)
- 集成真实API (DeepSeek + Dify)
- 完整用户管理系统
- Excel批量导入功能
- 管理界面重构
- 数据库优化和字段简化

### 未来计划
- 更多AI服务集成
- 高级数据分析功能
- 移动端优化
- 实时通知系统

---

## 附录

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

---
**文档版本**: v2.0  
**最后更新**: 2026-01-19  
**适用版本**: 当前生产环境
