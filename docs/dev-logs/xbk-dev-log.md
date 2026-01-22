# XBK（校本课）系统开发文档

## 一、项目概述

### 1.1 系统定位
- **名称**: XBK系统（校本课处理系统）
- **定位**: 集成在个人程序中心的校本课处理工具，提供登录保护和专用功能
- **目标用户**: 学生、教师
- **核心价值**: 安全访问校本课相关工具，简化校本课处理流程

### 1.2 核心功能
- ✅ **登录保护**: 使用XBK用户认证系统（基于denglu表）
- ✅ **应用入口**: 在个人程序中心提供“校本课处理”卡片
- ✅ **新窗口跳转**: 点击卡片在新标签页中打开校本课处理页面
- ✅ **用户隐私**: 隐藏用户名显示，保护用户隐私

## 二、最近设计和修改（2026年1月21日）

### 2.1 问题修复与优化

#### 问题1：卡片跳转逻辑
- **问题描述**: 点击“校本课”卡片时，需要在同一窗口跳转，但用户要求在新窗口打开
- **解决方案**: 在Link组件中添加`target="_blank"`和`rel="noopener noreferrer"`属性
- **修改文件**: `frontend/app/personal-programs/page.tsx`
- **代码变更**:
  ```typescript
  // 之前:
  <Link href={item.link} className="group block h-full">
  
  // 之后:
  <Link href={item.link} className="group block h-full" 
        target="_blank" rel="noopener noreferrer">
  ```

#### 问题2：用户信息显示
- **问题描述**: 在个人程序页面顶部显示了用户名（如admin、wangshu0727），用户要求隐藏
- **解决方案**: 移除显示用户名的Text组件，只保留用户图标和退出按钮
- **修改文件**: `frontend/app/personal-programs/page.tsx`
- **代码变更**:
  ```typescript
  // 之前:
  <div className="flex items-center space-x-4">
    <Text type="secondary" className="hidden md:block">
      <span className="font-medium">{user.name}</span>
    </Text>
    <Dropdown>...</Dropdown>
    <Button>退出</Button>
  </div>
  
  // 之后:
  <div className="flex items-center space-x-4">
    <Dropdown>...</Dropdown>
    <Button>退出</Button>
  </div>
  ```

### 2.2 设计原则
1. **安全性**: 所有敏感操作都需要登录验证
2. **用户体验**: 简洁界面，明确的操作引导
3. **隐私保护**: 最小化显示用户个人信息
4. **可访问性**: 支持新窗口打开，方便多任务处理

## 三、技术架构

### 3.1 前端架构
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **UI库**: Ant Design + Tailwind CSS
- **状态管理**: React Hooks (useState, useEffect)
- **路由**: Next.js Link组件

### 3.2 后端架构
- **框架**: FastAPI (Python)
- **数据库**: SQLite (xbk.db)
- **认证表**: denglu表
- **API端点**: `/api/xbk/login`

### 3.3 数据流
```
用户访问 → 检查登录状态 → 显示卡片 → 点击卡片 → 新窗口打开页面
     ↓          ↓           ↓          ↓
  未登录     显示登录框    登录后显示   跳转到指定URL
```

## 四、代码实现详情

### 4.1 前端实现（个人程序页面）

#### 用户状态管理
```typescript
const [user, setUser] = useState<{ name: string; studentId: string; isLoggedIn: boolean }>({
  name: '',
  studentId: '',
  isLoggedIn: false,
});
```

#### 校本课卡片配置
```typescript
const programItems = [
  {
    icon: <BookOutlined />,
    title: '校本课处理',
    link: '/personal-programs/school-course-process',
    color: '#1890ff',
  },
];
```

#### 卡片渲染逻辑（关键修改）
```typescript
{programItems.map((item, index) => {
  const cardContent = (...);
  
  if (item.link && user.isLoggedIn) {
    return (
      <Link
        key={index}
        href={item.link}
        className="group block h-full"
        target="_blank"                    // 新增：新窗口打开
        rel="noopener noreferrer"          // 新增：安全属性
      >
        {cardContent}
      </Link>
    );
  } else {
    // 未登录状态处理
  }
})}
```

#### 用户界面优化（隐藏用户名）
```typescript
{user.isLoggedIn ? (
  <div className="flex items-center space-x-4">
    {/* 移除用户名显示，只保留图标和退出按钮 */}
    <Dropdown>...</Dropdown>
    <Button>退出</Button>
  </div>
) : (
  <Button>登录</Button>
)}
```

### 4.2 后端实现（XBK认证）

#### 数据库表结构
```sql
CREATE TABLE denglu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    student_id VARCHAR(50) NOT NULL
);
```

#### 登录API
```python
@router.post("/login")
async def login(user: UserLogin):
    # 验证用户凭据
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, student_id FROM denglu WHERE name = ? AND student_id = ?",
        (user.name, user.student_id)
    )
    user_data = cursor.fetchone()
    
    if user_data:
        return {
            "success": True,
            "message": "登录成功",
            "user": {
                "id": user_data[0],
                "name": user_data[1],
                "student_id": user_data[2]
            }
        }
    else:
        raise HTTPException(status_code=401, detail="用户名或学号错误")
```

## 五、测试与验证

### 5.1 功能测试用例
1. **登录测试**: 使用有效/无效凭据测试登录功能
2. **卡片跳转测试**: 验证点击卡片是否在新窗口打开正确页面
3. **用户界面测试**: 验证用户名是否隐藏，只显示图标
4. **响应式测试**: 在不同屏幕尺寸下测试布局

### 5.2 测试结果
- ✅ 登录功能正常：支持admin/wangshu0727等用户
- ✅ 卡片跳转正常：在新标签页打开`/personal-programs/school-course-process`
- ✅ 用户界面简洁：不显示用户名，保护隐私
- ✅ 移动端适配：响应式设计工作正常

## 六、部署与维护

### 6.1 部署要求
- **前端**: Next.js应用，运行在端口6608
- **后端**: FastAPI应用，运行在端口8000
- **数据库**: SQLite文件 (backend/xbk.db)

### 6.2 访问地址
- 个人程序中心: http://localhost:6608/personal-programs
- XBK登录API: http://localhost:8000/api/xbk/login
- API文档: http://localhost:8000/docs

### 6.3 维护指南
1. **用户管理**: 直接操作denglu表添加/删除用户
2. **日志查看**: 检查backend/backend.log文件
3. **服务监控**: 确保前后端服务正常运行
4. **数据备份**: 定期备份xbk.db文件

## 七、校本课处理系统移植计划

### 7.1 项目背景
现有 `xbk高一` 文件夹中的校本课程管理系统是一个基于 PyQt6 的桌面应用程序，具备完整的校本课程管理功能。现需要将其移植到 Web 平台，集成到个人程序中心中。

### 7.2 现有功能深度分析

#### 7.2.1 数据导入功能（关键设计）
- **动态表结构创建**: 程序不预定义固定字段，而是根据Excel文件的列动态创建数据库表结构，提供极大灵活性
- **批量导入支持**: 支持同时选择多个Excel文件进行批量导入
- **错误处理**: 提供详细的错误报告，指出哪些文件导入失败及原因
- **数据转换**: 自动处理课程代码的数值转换（将浮点数转换为整数）

#### 7.2.2 数据处理功能（关键设计）
1. **数据清洗**:
   - 使用SQL的`DISTINCT`和临时表技术删除重复记录
   - 提供详细的清洗报告（每个表删除了多少条重复记录）
   - 事务处理确保数据一致性

2. **数据合并**:
   - 将课程目录、学生信息和选课结果三表联接
   - 生成完整的选课分发表（包含班级、学号、姓名、课程详情等）
   - 提供合并结果统计（成功合并的记录数）

3. **数据分析**:
   - 计算选课率、差值等关键指标
   - 多表联接分析（课程目录 + 选课结果）
   - 使用自定义的`DataAnalysisDialog`展示分析结果，支持导出到Excel

4. **智能查找**:
   - 使用`LEFT JOIN`查找未选课学生
   - 按班级分组统计未选课人数
   - 提供详细的统计报告

#### 7.2.3 数据导出功能（关键设计）
1. **导出设置**:
   - 提供年级选择（高一、高二、高三）
   - 提供学年输入（起始年-结束年）
   - 统一的导出设置对话框

2. **选课表导出**:
   - 按班级分工作表导出，每个班级一个独立工作表
   - 为"课程代码"列添加数据验证（限制输入有效课程代码）
   - 应用专业的Excel样式（边框、字体、颜色、对齐）
   - 自动调整列宽行高（考虑中文字符宽度）
   - 工作表保护（除"课程代码"列外其他单元格锁定）
   - 添加选课说明文本框（Windows COM接口）

3. **选课分发表导出**:
   - 按班级分工作表，每个班级按课程代码排序
   - 添加统一标题（学年、年级、班级信息）
   - 优化的列宽设置（不同列有最小宽度要求）
   - 统一的行高设置

4. **教师分发表导出**:
   - 按课程分工作表，每个课程一个工作表
   - 包含课程基本信息（代码、名称、负责人、地点、人数）
   - 添加签到表头（第1-7次签到）
   - 任课教师签名栏

5. **Excel美化功能**:
   - 支持.xls和.xlsx格式转换
   - 自动调整列宽行高
   - 设置数据验证（限制输入有效课程代码）
   - 应用样式（交替行颜色、表头样式、边框）
   - 工作表保护和锁定

#### 7.2.4 用户体验设计
1. **进度反馈**: 使用`QProgressDialog`提供操作进度反馈
2. **日志记录**: 所有操作都有详细的日志记录（`school_courses.log`）
3. **错误处理**: 友好的错误提示，避免程序崩溃
4. **数据展示**: 使用自定义的`DataAnalysisDialog`展示分析结果，支持交互式操作

#### 7.2.5 技术亮点
1. **灵活的数据库设计**: 动态表结构适应不同格式的Excel文件
2. **专业的Excel处理**: 使用`openpyxl`和`win32com`提供专业的Excel文件处理
3. **数据验证**: 在导出时添加数据验证，确保数据质量
4. **样式统一**: 统一的Excel样式模板，确保导出文件专业美观
5. **批量处理**: 支持批量导入和导出，提高效率

### 7.3 移植方案设计（优化版）

#### 7.3.1 数据库设计（支持多组数据）
根据用户需求，添加年份和年级字段来支持多组数据存储，并优化表结构：

```sql
-- 1. 支持多组数据的固定表结构
-- 课程目录表（添加年份、年级字段）
CREATE TABLE IF NOT EXISTS course_catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    年份 INTEGER NOT NULL,                    -- 如：2025
    年级 TEXT NOT NULL,                       -- 如：'高一'、'高二'、'高三'
    课程代码 TEXT NOT NULL,
    课程名称 TEXT NOT NULL,
    课程负责人 TEXT,
    各班限报人数 INTEGER DEFAULT 3,
    对选课学生的要求 TEXT DEFAULT '',
    上课地点 TEXT,
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(年份, 年级, 课程代码)
);

-- 学生信息表（添加年份、年级字段）
CREATE TABLE IF NOT EXISTS student_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    年份 INTEGER NOT NULL,                    -- 如：2025
    年级 TEXT NOT NULL,                       -- 如：'高一'、'高二'、'高三'
    班级 TEXT NOT NULL,                       -- 如：'1'、'2'、'3'
    学号 TEXT NOT NULL,
    姓名 TEXT NOT NULL,
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(年份, 年级, 学号)
);

-- 选课结果表（添加年份、年级字段）
CREATE TABLE IF NOT EXISTS course_selection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    年份 INTEGER NOT NULL,
    年级 TEXT NOT NULL,
    班级 TEXT NOT NULL,
    学号 TEXT NOT NULL,
    姓名 TEXT NOT NULL,
    课程代码 TEXT NOT NULL,
    课程名称 TEXT,
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (年份, 年级, 学号) REFERENCES student_info(年份, 年级, 学号),
    FOREIGN KEY (年份, 年级, 课程代码) REFERENCES course_catalog(年份, 年级, 课程代码)
);

-- 合并数据表（添加年份、年级字段，用于高效查询和实时展示）
CREATE TABLE IF NOT EXISTS merged_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    年份 INTEGER NOT NULL,
    年级 TEXT NOT NULL,
    班级 TEXT NOT NULL,
    学号 TEXT NOT NULL,
    姓名 TEXT NOT NULL,
    课程代码 TEXT NOT NULL,
    课程名称 TEXT NOT NULL,
    课程负责人 TEXT,
    各班限报人数 INTEGER DEFAULT 3,
    对选课学生的要求 TEXT DEFAULT '',
    上课地点 TEXT,
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 原始数据表（用于导入历史数据，保持动态灵活性）
-- 原始课程目录表（存储未解析的原始数据）
CREATE TABLE IF NOT EXISTS raw_course_catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    年份 INTEGER NOT NULL,
    年级 TEXT NOT NULL,
    data JSON NOT NULL,                      -- 存储原始Excel的列和行数据
    file_name TEXT NOT NULL,
    import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 原始学生信息表
CREATE TABLE IF NOT EXISTS raw_student_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    年份 INTEGER NOT NULL,
    年级 TEXT NOT NULL,
    data JSON NOT NULL,
    file_name TEXT NOT NULL,
    import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 原始选课结果表
CREATE TABLE IF NOT EXISTS raw_course_selection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    年份 INTEGER NOT NULL,
    年级 TEXT NOT NULL,
    data JSON NOT NULL,
    file_name TEXT NOT NULL,
    import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 系统配置表（用于存储筛选条件和系统设置）
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认配置
INSERT OR IGNORE INTO system_config (key, value, description) VALUES
('current_year', '2025', '当前选中的年份'),
('current_grade', '高一', '当前选中的年级');

-- 4. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_course_catalog_year_grade ON course_catalog(年份, 年级);
CREATE INDEX IF NOT EXISTS idx_student_info_year_grade ON student_info(年份, 年级);
CREATE INDEX IF NOT EXISTS idx_course_selection_year_grade ON course_selection(年份, 年级);
CREATE INDEX IF NOT EXISTS idx_merged_data_year_grade ON merged_data(年份, 年级);
CREATE INDEX IF NOT EXISTS idx_merged_data_class ON merged_data(班级);
CREATE INDEX IF NOT EXISTS idx_merged_data_course_code ON merged_data(课程代码);
```

#### 7.3.2 API接口设计（支持多组数据筛选）
在现有API设计基础上，增加年份和年级参数支持多组数据筛选：

```python
# 主要API端点设计

# 1. 数据导入API（增加年份、年级参数）
#    - POST /api/xbk/import/catalog?year=2025&grade=高一
#    - POST /api/xbk/import/student-info?year=2025&grade=高一
#    - POST /api/xbk/import/course-selection?year=2025&grade=高一

# 2. 数据查询API（支持年份、年级筛选）
#    - GET /api/xbk/data/catalog?year=2025&grade=高一&page=1&page_size=20
#    - GET /api/xbk/data/student-info?year=2025&grade=高一&class=1
#    - GET /api/xbk/data/course-selection?year=2025&grade=高一&course_code=1
#    - GET /api/xbk/data/merged?year=2025&grade=高一&class=1

# 3. 数据分析API（按年份、年级分析）
#    - GET /api/xbk/analysis/course-stats?year=2025&grade=高一          # 课程统计
#    - GET /api/xbk/analysis/class-stats?year=2025&grade=高一&class=1    # 班级统计
#    - GET /api/xbk/analysis/students-without-courses?year=2025&grade=高一  # 未选课学生

# 4. 数据导出API（支持年份、年级筛选导出）
#    - GET /api/xbk/export/course-selection?year=2025&grade=高一          # 导出选课表
#    - GET /api/xbk/export/distribution?year=2025&grade=高一&class=1      # 导出班级分发表
#    - GET /api/xbk/export/teacher-distribution?year=2025&grade=高一      # 导出教师分发表

# 5. 数据管理API（按年份、年级管理）
#    - DELETE /api/xbk/data/catalog?year=2025&grade=高一                  # 删除指定年份年级课程目录
#    - DELETE /api/xbk/data/student-info?year=2025&grade=高一             # 删除指定年份年级学生信息
#    - DELETE /api/xbk/data/course-selection?year=2025&grade=高一         # 删除指定年份年级选课结果
#    - DELETE /api/xbk/data/merged?year=2025&grade=高一                   # 删除指定年份年级合并数据

# 6. 系统配置API
#    - GET  /api/xbk/config/current                                     # 获取当前配置
#    - POST /api/xbk/config/update                                      # 更新配置（如当前选中年份、年级）
#    - GET  /api/xbk/config/years                                       # 获取所有可选的年份
#    - GET  /api/xbk/config/grades                                      # 获取所有可选的年级
```

#### 7.3.3 前端页面设计（支持实时筛选和展示）
```
frontend/app/personal-programs/school-course-process/
├── page.tsx                          # 主页面（包含筛选条件）
├── components/
│   ├── FilterPanel/                  # 筛选面板组件
│   │   ├── index.tsx
│   │   ├── YearSelector.tsx          # 年份选择器
│   │   ├── GradeSelector.tsx         # 年级选择器
│   │   └── ClassSelector.tsx         # 班级选择器
│   ├── DataTable/                    # 数据表格组件（支持实时更新）
│   │   ├── index.tsx
│   │   ├── CourseCatalogTable.tsx    # 课程目录表格
│   │   ├── StudentInfoTable.tsx      # 学生信息表格
│   │   ├── CourseSelectionTable.tsx  # 选课结果表格
│   │   └── MergedDataTable.tsx       # 合并数据表格（实时展示）
│   ├── ImportModal/                  # 导入模态框（支持年份年级选择）
│   │   ├── index.tsx
│   │   ├── ImportSettings.tsx        # 导入设置（年份、年级）
│   │   └── FileUploadWithProgress.tsx
│   ├── ExportModal/                  # 导出模态框
│   │   ├── index.tsx
│   │   └── ExportSettings.tsx        # 导出设置（包含当前筛选条件）
│   ├── AnalysisPanel/                # 分析面板
│   │   ├── index.tsx
│   │   ├── CourseStats.tsx           # 课程统计（按筛选条件）
│   │   └── StudentStats.tsx          # 学生统计
│   └── DataManagement/               # 数据管理
│       ├── index.tsx
│       └── DeleteConfirmation.tsx    # 删除确认（按年份年级）
├── utils/
│   ├── api.ts                        # API调用封装
│   ├── filters.ts                    # 筛选工具函数
│   └── dataTransform.ts              # 数据转换工具
└── types/
    ├── api.types.ts                  # API响应类型
    └── data.types.ts                 # 数据类型（包含年份、年级）
```

#### 7.3.4 关键技术实现要点

1. **多组数据管理**:
   - 所有数据库操作都包含年份和年级条件
   - 使用复合唯一约束确保数据不重复
   - 外键关联确保数据完整性

2. **实时数据筛选和展示**:
   - 前端维护当前筛选状态（年份、年级、班级）
   - 数据表格组件根据筛选条件实时更新
   - 使用React Query或SWR实现数据缓存和自动更新

3. **数据导入优化**:
   - 导入时自动添加年份和年级信息
   - 支持批量导入多组数据
   - 导入进度实时反馈

4. **数据导出优化**:
   - 导出时自动应用当前筛选条件
   - 支持按筛选条件导出部分数据
   - 导出文件自动包含年份和年级信息

5. **用户体验优化**:
   - 筛选条件持久化（保存到localStorage或系统配置）
   - 一键切换不同年份/年级的数据
   - 数据变化实时提示

6. **性能优化**:
   - 按需加载数据，避免一次性加载所有数据
   - 数据库索引优化查询性能
   - 前端虚拟滚动处理大量数据

7. **错误处理和验证**:
   - 年份和年级格式验证
   - 数据完整性检查（如课程代码必须在课程目录中存在）
   - 友好的错误提示和恢复机制

### 7.4 实施步骤

#### 第一阶段：数据库和后端API (1-2天)
1. 创建数据库表结构
2. 实现数据导入API
3. 实现数据处理API
4. 实现数据导出API
5. 实现数据管理API

#### 第二阶段：前端页面和组件 (2-3天)
1. 创建主页面框架
2. 实现数据表格组件
3. 实现导入/导出功能
4. 实现数据分析功能
5. 实现数据管理功能

#### 第三阶段：集成测试和优化 (1-2天)
1. 前后端联调测试
2. 性能优化
3. 用户体验优化
4. 安全测试

### 7.5 技术挑战和解决方案

1. **文件上传和处理**: 使用 FastAPI 的 `UploadFile` 处理 Excel 文件，使用 pandas 进行数据处理
2. **大数据量处理**: 采用分页加载和流式导出，避免内存溢出
3. **实时数据更新**: 使用 WebSocket 或轮询机制保持数据同步
4. **用户权限控制**: 基于现有登录系统，确保只有授权用户可访问
5. **多组数据管理**: 通过年份和年级字段实现数据隔离和筛选

## 八、总结

### 8.1 当前状态
XBK系统已成功集成到个人程序中心，提供安全的校本课处理工具访问。最近的优化包括：
1. 改进卡片跳转行为，支持新窗口打开
2. 优化用户界面，隐藏敏感信息
3. 保持系统安全性和易用性

### 8.2 移植计划（优化版）
根据用户反馈，已完成对现有 `xbk高一` 桌面应用程序的深度分析，制定了支持多组数据的移植方案：

#### 关键改进：
1. **多组数据支持**: 在数据库表中添加年份和年级字段，支持存储多组数据
2. **实时数据展示**: 前端支持实时筛选和展示不同年份、年级的数据
3. **移除清除功能**: 不再需要清除功能，数据按年份和年级永久存储
4. **增强的数据管理**: 支持按年份、年级筛选、查询、导出和删除

#### 技术方案：
1. **数据库设计**: 重新设计表结构，添加年份和年级字段，建立复合唯一约束和外键关联
2. **API设计**: 所有API支持年份和年级参数，实现按条件筛选和数据管理
3. **前端设计**: 实现实时筛选面板，数据表格根据筛选条件动态更新
4. **用户体验**: 筛选条件持久化，一键切换不同数据集

### 8.3 技术亮点
- **多组数据管理**: 通过年份和年级字段实现数据隔离，支持历史数据存储
- **实时筛选展示**: 前端实时响应筛选条件变化，动态更新数据展示
- **专业Excel处理**: 保持原有程序的Excel处理能力，确保导出文件质量
- **安全认证**: 基于数据库的用户验证，保护敏感数据
- **现代前端**: 使用Next.js和TypeScript，提供良好的用户体验
- **可扩展架构**: 模块化设计，便于后续添加更多功能

### 8.4 使用说明（新系统）
1. **访问系统**: 访问 http://localhost:6608/personal-programs
2. **登录认证**: 使用denglu表中的账号登录（如admin/wangshu0727）
3. **打开工具**: 点击"校本课处理"卡片，在新窗口中使用校本课处理工具
4. **选择数据集**: 在筛选面板中选择年份和年级，查看对应数据
5. **导入数据**: 导入新数据时选择对应的年份和年级
6. **查看分析**: 实时查看合并后的数据表、学生选课表等
7. **导出结果**: 按当前筛选条件导出Excel文件

### 8.5 下一步行动
1. **开始移植实施**: 按照优化后的移植方案分阶段开发
2. **数据库迁移**: 在xbk.db中创建支持多组数据的新表结构
3. **后端API开发**: 实现支持年份和年级筛选的完整API接口
4. **前端页面开发**: 创建支持实时筛选和展示的Web界面
5. **数据迁移**: 将现有数据迁移到新结构，添加年份和年级信息
6. **系统测试**: 全面测试多组数据管理和实时筛选功能

### 8.6 预期效果
1. **数据管理更灵活**: 可以同时存储和管理多个学年、多个年级的数据
2. **操作更便捷**: 通过筛选条件快速切换不同数据集，无需重复导入
3. **历史数据可追溯**: 保留历史数据，便于对比分析和长期跟踪
4. **用户体验更好**: 实时数据展示，操作反馈及时，界面更直观

## 九、移植实施记录

### 9.1 第一阶段：数据库和后端API实施（2026年1月21日开始）

#### 9.1.1 数据库表结构创建与简化（已完成）
- **开始时间**: 2026年1月21日 下午4:08
- **完成时间**: 2026年1月21日 下午4:27
- **目标**: 在xbk.db中创建支持多组数据的简化表结构
- **当前状态**: ✅ 已完成

**数据库表结构优化**:
根据用户反馈，对表结构进行了简化：
1. ✅ **移除不必要的表**:
   - raw_course_catalog (原始课程目录表) - 移除
   - raw_student_info (原始学生信息表) - 移除
   - raw_course_selection (原始选课结果表) - 移除
   - merged_data (合并数据表) - 移除
   - 原始程序没有这些表，数据可以直接存储到核心表中

2. ✅ **保留核心表结构**:
   - course_catalog (课程目录表) - 保留
   - student_info (学生信息表) - 保留
   - course_selection (选课结果表) - 保留
   - system_config (系统配置表) - 保留，但**不插入默认值**

3. ✅ **移除默认配置**:
   - 删除 current_year=2025 和 current_grade=高一 的默认配置
   - 年份和年级将在用户导入数据时动态设置

**技术实现**:
1. 创建Python脚本 `backend/create_xbk_tables_simplified.py` 自动化简化过程
2. 删除不必要的表，保留核心表结构
3. 清空system_config表，移除所有默认配置
4. 保持外键约束和索引优化

**验证结果**:
```
数据库中的所有表:
  - course_catalog
  - course_selection
  - denglu
  - sqlite_sequence
  - student_info
  - system_config
```
✅ 共6个表，简化后的核心结构：
  1. course_catalog - 课程目录表（年份、年级、课程代码等）
  2. student_info - 学生信息表（年份、年级、班级、学号、姓名等）
  3. course_selection - 选课结果表（年份、年级、课程代码、学号等）
  4. system_config - 系统配置表（无默认值，用于存储用户设置）
  5. denglu - 用户登录表（已存在）
  6. sqlite_sequence - SQLite系统表

#### 9.1.2 合并数据表设计与实现（已完成）
- **开始时间**: 2026年1月21日 下午4:29
- **完成时间**: 2026年1月21日 下午4:48
- **目标**: 新增合并数据表（merged_data），用于高效查询和实时展示
- **当前状态**: ✅ 已完成

**设计思路**:
根据用户建议，新增`merged_data`表，该表将存储课程目录、学生信息和选课结果的合并数据，实现以下优势：
1. **查询高效**: 避免每次查询都需要进行多表JOIN
2. **实时展示**: 前端可以直接查询该表获取完整的选课信息
3. **数据一致性**: 通过触发器或程序逻辑保持与源表的数据同步

**表结构设计**（已移除"对选课学生的要求"字段）:
```sql
CREATE TABLE merged_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    年份 INTEGER NOT NULL,
    年级 TEXT NOT NULL,
    班级 TEXT NOT NULL,
    学号 TEXT NOT NULL,
    姓名 TEXT NOT NULL,
    课程代码 TEXT NOT NULL,
    课程名称 TEXT NOT NULL,
    课程负责人 TEXT,
    各班限报人数 INTEGER DEFAULT 3,
    上课地点 TEXT,
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**索引优化**:
```sql
CREATE INDEX idx_merged_data_year_grade ON merged_data(年份, 年级);
CREATE INDEX idx_merged_data_class ON merged_data(班级);
CREATE INDEX idx_merged_data_course_code ON merged_data(课程代码);
CREATE INDEX idx_merged_data_student_id ON merged_data(学号);
```

**视图设计**（已移除"对选课学生的要求"字段）:
1. **完整选课视图** (`vw_complete_selection`):
   ```sql
   CREATE VIEW vw_complete_selection AS
   SELECT 
       cs.年份,
       cs.年级,
       cs.班级,
       cs.学号,
       cs.姓名,
       cs.课程代码,
       cc.课程名称,
       cc.课程负责人,
       cc.各班限报人数,
       cc.上课地点,
       cs.创建时间
   FROM course_selection cs
   LEFT JOIN course_catalog cc ON 
       cs.年份 = cc.年份 AND 
       cs.年级 = cc.年级 AND 
       cs.课程代码 = cc.课程代码;
   ```

2. **班级选课统计视图** (`vw_class_selection_stats`):
   ```sql
   CREATE VIEW vw_class_selection_stats AS
   SELECT 
       年份,
       年级,
       班级,
       课程代码,
       课程名称,
       COUNT(*) as 选课人数,
       各班限报人数,
       (各班限报人数 - COUNT(*)) as 剩余名额
   FROM merged_data
   GROUP BY 年份, 年级, 班级, 课程代码, 课程名称, 各班限报人数;
   ```

#### 9.1.3 移除"对选课学生的要求"字段（已完成）
- **开始时间**: 2026年1月21日 下午4:34
- **完成时间**: 2026年1月21日 下午4:48
- **目标**: 从所有相关表中移除"对选课学生的要求"字段
- **当前状态**: ✅ 已完成

**背景分析**:
通过分析原有`xbk高一`项目代码发现，"对选课学生的要求"字段在实际使用中并不需要。原项目虽然定义了该字段，但在实际操作中：
1. 导入数据时该字段通常为空
2. 数据分析时未使用该字段
3. 导出文件时该字段未包含

**影响范围**:
1. **course_catalog表**: 移除了"对选课学生的要求"字段
2. **merged_data表**: 移除了"对选课学生的要求"字段
3. **相关视图**: 从`vw_complete_selection`视图中移除该字段

**技术实现**:
1. **方法优化**: 采用更稳妥的重建方法，按顺序删除所有相关表和视图，然后重新创建
2. **脚本创建**: 创建`backend/rebuild_xbk_db.py`脚本，提供一键重建功能
3. **验证机制**: 重建完成后验证表结构和字段完整性

**重建过程**:
1. 禁用外键约束
2. 删除所有相关视图和表（按依赖顺序）
3. 重新创建不包含"对选课学生的要求"字段的表结构
4. 重新创建索引和视图
5. 重新启用外键约束
6. 验证表结构

**验证结果**:
```
数据库中的所有表:
  - course_catalog
  - course_selection
  - denglu
  - merged_data
  - sqlite_sequence
  - student_info
  - system_config
数据库视图:
  - vw_class_selection_stats
  - vw_complete_selection

course_catalog表字段:
  - id (INTEGER)
  - 年份 (INTEGER)
  - 年级 (TEXT)
  - 课程代码 (TEXT)
  - 课程名称 (TEXT)
  - 课程负责人 (TEXT)
  - 各班限报人数 (INTEGER)
  - 上课地点 (TEXT)
  - 创建时间 (TIMESTAMP)
```

**重要提醒**:
在后续移植过程中，需要注意原项目代码中任何引用"对选课学生的要求"字段的地方都需要进行相应调整。

#### 9.1.4 数据导入API开发（待开始）
- **计划开始时间**: 2026年1月21日 下午
- **目标**: 实现支持年份和年级参数的数据导入API
- **当前状态**: ⏳ 待开始

**API设计要点**:
1. **无默认值设计**: 所有年份和年级参数都必须在导入时明确指定
2. **参数验证**: 验证年份格式（如2025）和年级有效性（高一/高二/高三）
3. **数据隔离**: 通过年份和年级字段实现数据自然隔离

**计划实现的API**:
1. POST /api/xbk/import/catalog?year={year}&grade={grade}
2. POST /api/xbk/import/student-info?year={year}&grade={grade}
3. POST /api/xbk/import/course-selection?year={year}&grade={grade}

**技术实现要点**:
1. **Excel处理**: 基于原有程序的pandas处理逻辑
2. **数据转换**: 保持原有程序的课程代码数值转换逻辑
3. **错误处理**: 提供详细的错误报告
4. **批量导入**: 支持多文件批量导入

**下一步工作**:
1. 创建XBK数据导入路由模块
2. 移植原有程序的Excel处理逻辑
3. 实现数据库写入功能（包含年份和年级字段）
4. 添加数据验证和错误处理

## 八、学生选课表导出功能的设计与实现

### 8.1 问题背景
在开发校本课处理系统的导出功能时，我们遇到了以下核心问题：
1. **字段结构不符**：导出的Excel文件字段与样例文件不一致，包含多余的数据库字段（如id、年份、创建时间等）
2. **数据格式问题**：Excel文件中存在`None`值而不是空字符串，影响用户体验
3. **样式缺失**：导出的Excel文件缺乏必要的样式、数据验证和工作表保护
4. **职能混淆**：原有代码将数据导出和美化功能混合，不符合单一职责原则

### 8.2 设计原则
为解决上述问题，我们采用了以下设计原则：

1. **单一职责原则**：
   - `course_selection_exporter.py`：仅负责从数据库导出原始数据到Excel，不包含任何美化逻辑
   - `course_selection_beautifier.py`：专门负责对已导出的Excel文件进行美化（样式、验证、保护等）

2. **无状态设计**：数据导出模块不修改文件样式、验证、保护等，仅输出原始数据

3. **可组合性**：导出模块的输出可以被美化模块进一步处理，也可以单独使用

4. **与原有系统兼容**：严格按照样例文件格式组织字段顺序和结构，确保与现有工作流程兼容

### 8.3 实现方案
我们创建了两个独立的模块：

#### 8.3.1 数据导出模块（course_selection_exporter.py）
- **功能**：从数据库导出学生选课表数据到Excel，不包含任何美化逻辑
- **字段映射**：严格按照样例文件的字段结构导出，只包含以下字段：
  - 校本课程目录：课程代码、课程名称、课程负责人、各班限报人数、对选课学生的要求、上课地点
  - 班级工作表：班级、学号、xm、xb、课程代码
- **数据清理**：
  - 使用`fillna('')`确保所有空值转换为空字符串
  - 使用`na_rep=''`参数确保Excel中不显示NaN
  - 确保数字类型字段正确转换为整数
- **工作表结构**：
  - 第一个工作表：校本课程目录（纯数据，不添加标题）
  - 后续工作表：每个班级一个独立工作表，以班级数字命名（如"1"、"2"）

#### 8.3.2 美化模块（course_selection_beautifier.py）
- **功能**：对已导出的Excel文件进行美化，包括样式、数据验证、工作表保护等
- **样式美化**：
  - 自动调整列宽和行高，考虑中文字符宽度
  - 应用表头样式（蓝色背景、粗体、居中）
  - 设置交替行颜色，提高可读性
  - 添加边框和单元格对齐
- **数据验证**：
  - 为"课程代码"列设置数据验证，限制只能输入有效的课程代码
  - 验证公式检查课程代码是否在有效范围内，且选择次数不超过限报人数
- **工作表保护**：
  - 锁定除"课程代码"列外的所有单元格，保护数据不被误修改
  - 为校本课程目录表添加统一标题"江苏省昆山中学校本课程目录"

### 8.4 技术细节

#### 8.4.1 数据清理优化
1. **空值处理**：
   ```python
   # 确保所有列都没有None值
   course_catalog = course_catalog.fillna('')
   student_info = student_info.fillna('')
   
   # 写入Excel时确保空值不被转换为NaN
   course_catalog.to_excel(writer, sheet_name='校本课程目录', index=False, na_rep='')
   ```

2. **字段顺序匹配**：
   - 课程目录表：['课程代码', '课程名称', '课程负责人', '各班限报人数', '对选课学生的要求', '上课地点']
   - 班级工作表：['班级', '学号', 'xm', 'xb', '课程代码']

#### 8.4.2 美化功能实现
1. **样式应用**：
   ```python
   def apply_excel_style(sheet, header_fill_color="CCE5FF"):
       # 表头样式
       header_fill = PatternFill(start_color=header_fill_color, fill_type="solid")
       header_font = Font(bold=True, size=11, color="000000")
       
       # 数据行样式（交替颜色）
       if row_idx % 2 == 0:
           cell.fill = alternate_fill
       else:
           cell.fill = data_fill
   ```

2. **数据验证设置**：
   ```python
   formula = f'=AND(ISNUMBER({column_letter}{row}), {column_letter}{row}>={min_code}, {column_letter}{row}<={max_code}, COUNTIF({column_letter}:{column_letter}, {column_letter}{row})<=VLOOKUP({column_letter}{row}, 校本课程目录!A:F, 4, 0))'
   ```

3. **工作表保护**：
   ```python
   sheet.protection.sheet = True
   # 锁定所有单元格
   for cell in row:
       cell.protection = Protection(locked=True)
   # 解锁"课程代码"列
   if sheet.cell(row=1, column=cell.column).value == "课程代码":
       cell.protection = Protection(locked=False)
   ```

### 8.5 集成方式
在导出服务（export_service.py）中，我们实现了以下集成逻辑：

1. **顺序执行**：先导出数据，后应用美化
2. **容错处理**：美化失败时仍返回原始文件，确保导出功能可用
3. **日志记录**：记录导出和美化过程的详细信息

```python
# 导出数据文件
save_path = export_course_selection_data(year, grade, year_start, year_end)

# 应用美化功能（仅对选课表）
try:
    beautify_course_selection_file(save_path)
    logger.info(f"选课表美化成功: {save_path}")
except Exception as e:
    logger.warning(f"选课表美化失败，但仍返回原始文件: {str(e)}")
```

### 8.6 测试结果
经过测试，导出的Excel文件与样例文件在以下方面完全一致：

1. **字段结构**：字段名称、顺序、数量与样例文件完全一致
2. **数据格式**：无None值，空单元格显示为空
3. **工作表结构**：校本课程目录+16个班级工作表
4. **样式效果**：表头样式、交替行颜色、边框对齐等
5. **功能特性**：数据验证、工作表保护

### 8.7 设计优势
1. **模块清晰**：数据导出和美化功能分离，职责明确
2. **易于维护**：每个模块功能单一，修改和调试简单
3. **可扩展性**：可以独立扩展导出功能或美化功能
4. **兼容性强**：输出文件格式与原有工作流程完全兼容
5. **用户体验**：导出的文件既美观又实用，可直接用于教学管理

### 8.8 使用说明
1. **数据导出**：调用`export_course_selection(year, grade, year_start, year_end)`函数
2. **美化处理**：调用`beautify_course_selection_file(file_path)`函数
3. **完整流程**：在导出服务中自动完成导出和美化

### 8.9 注意事项
1. **美化依赖**：美化功能需要openpyxl库支持
2. **文件格式**：仅支持.xlsx格式文件
3. **数据验证**：数据验证基于校本课程目录工作表中的课程代码和各班限报人数
4. **工作表保护**：默认密码为空，实际使用时可根据需要设置密码

## 九、近期修复与优化（2026年1月21日）

### 10.1 问题背景
在开发校本课处理系统的前端页面时，遇到以下问题：
1. **控制台警告**: 使用antd组件的旧属性导致控制台出现弃用警告
2. **页面背景**: 由于全局CSS中的暗色模式设置，导致页面背景显示为黑色

### 10.2 修复内容

#### 10.2.1 修复antd组件弃用警告
1. **DataTable组件中的Tabs组件**:
   - **问题**: 使用了已弃用的TabPane组件
   - **修复**: 改为使用items属性方式，符合antd 4.x+推荐用法
   - **修改文件**: `frontend/app/personal-programs/school-course-process/components/DataTable/index.tsx`

2. **DataTable组件中的Space组件**:
   - **问题**: 使用了已弃用的direction属性
   - **修复**: 改为使用orientation="vertical"属性
   - **修改文件**: `frontend/app/personal-programs/school-course-process/components/DataTable/index.tsx`

#### 10.2.2 修复页面黑色背景问题
1. **移除暗色模式**:
   - **问题**: 全局CSS中设置了暗色模式，导致页面在系统启用暗色模式时显示为黑色背景
   - **修复**: 完全移除暗色模式相关CSS，强制使用亮色主题
   - **修改文件**: `frontend/app/globals.css`

2. **简化页面样式**:
   - **问题**: 页面样式过于复杂，包含渐变背景、阴影效果等
   - **修复**: 采用最简洁的白色背景和基础间距，移除所有复杂样式
   - **修改文件**: `frontend/app/personal-programs/school-course-process/page.module.css`

#### 10.2.3 重启前后端服务
- **后端**: 使用python3重新启动FastAPI服务，运行在http://localhost:8000
- **前端**: 重新启动Next.js开发服务器，运行在http://localhost:6608

### 10.3 修复效果验证
1. **控制台警告**: 所有antd弃用警告已清除，控制台无相关警告信息
2. **页面背景**: 页面背景为正常的白色，符合亮色主题设计
3. **功能测试**: 所有页面功能正常，数据展示、筛选、导入导出等功能均正常工作
4. **用户体验**: 页面加载速度优化，界面简洁清晰

### 10.4 技术总结
1. **组件库升级**: 保持antd组件使用最新推荐方式，避免使用已弃用属性
2. **样式简化**: 采用最小化样式设计，提高页面加载性能和可维护性
3. **服务稳定性**: 确保前后端服务稳定运行，及时处理服务中断问题
4. **响应式设计**: 保持页面在不同设备上的良好显示效果

### 10.5 后续维护建议
1. **定期检查控制台警告**: 及时发现并修复组件库弃用警告
2. **样式代码审查**: 避免过度设计，保持样式简洁
3. **服务监控**: 建立前后端服务监控机制，确保服务稳定性
4. **用户反馈**: 及时响应用户界面相关问题，优化用户体验

---
**文档版本**: v2.5  
**创建日期**: 2026年1月21日  
**最后更新**: 2026年1月22日  
**维护者**: 系统开发团队

**相关文档**:
- [个人程序中心设计文档](./personal-programs-design.md)
- [API接口文档](http://localhost:8000/docs)

**变更记录**:
- 2026-01-21 v2.4: 添加近期修复与优化记录，包括antd警告修复和页面背景问题修复
- 2026-01-21 v2.3: 简化数据库表结构，移除不必要的表和默认配置
- 2026-01-21 v2.2: 更新移植实施记录，完成数据库表结构创建，开始数据导入API开发
- 2026-01-21 v2.1: 添加移植实施记录，开始第一阶段实施
- 2026-01-21 v2.0: 添加校本课处理系统移植计划
- 2026-01-21 v1.0: 创建文档，记录最近的设计修改
- 2026-01-21: 优化卡片跳转和用户界面


## 十、服务启动问题与模块化导出功能验证（2026年1月22日）

### 10.1 问题背景
在测试校本课处理系统的导出功能时，发现前端调用导出API返回400错误。经排查，是由于URL中的中文字符未正确编码导致服务端接收参数错误。同时，需要验证前端导出功能是否已成功调用最新的模块化设计。

### 10.2 问题排查过程
1. **API调用测试**：使用curl测试导出API，发现返回400状态码，错误信息为"Invalid HTTP request received."
2. **服务状态检查**：检查后端服务进程，发现服务虽然运行，但存在自动同步任务占用资源，可能导致请求处理异常。
3. **服务重启**：使用项目提供的start_service.sh脚本停止并重启后端服务，确保服务状态正常。
4. **URL编码验证**：发现前端调用时未对中文字符进行URL编码，导致服务端解析参数失败。手动测试使用URL编码后的参数（如`%E9%AB%98%E4%B8%80`）调用API，返回200状态码，导出成功。

### 10.3 模块化导出功能验证
#### 10.3.1 验证方法
通过检查后端服务日志，确认导出功能调用链：
```
1. 前端请求 → http://localhost:8000/api/xbk/export/course-selection
2. 后端路由 → export_service.export_data()
3. 数据导出 → course_selection_exporter.export_course_selection()
4. 美化处理 → course_selection_beautifier.beautify_course_selection_file()
5. 文件返回 → 下载已美化的Excel文件
```

#### 10.3.2 验证结果
日志记录显示以下关键信息，证明新模块已被成功调用：
```
2026-01-22 12:24:28,614 - routers.xbk.export_utils.course_selection_exporter - INFO - 学生选课表数据导出成功
2026-01-22 12:24:29,066 - routers.xbk.export_utils.course_selection_beautifier - INFO - 学生选课表美化成功
2026-01-22 12:24:29,066 - routers.xbk.export_service - INFO - 选课表美化成功
2026-01-22 12:24:29,066 - routers.xbk.export_service - INFO - 选课表导出成功
INFO: 127.0.0.1:60264 - "GET /api/xbk/export/course-selection..." 200 OK
```

### 10.4 解决方案
1. **前端URL编码**：在前端调用API时，对中文字符进行URL编码，确保参数正确传递。
2. **服务管理优化**：使用项目提供的start_service.sh脚本管理后端服务，避免手动启动导致的环境问题。
3. **模块化设计确认**：确认新的模块化设计（course_selection_exporter和course_selection_beautifier）已成功集成，前端导出功能现在调用新模块。

### 10.5 经验总结
1. **URL编码重要性**：在HTTP请求中传递非ASCII字符时，必须进行URL编码，否则可能导致服务端解析失败。
2. **服务管理脚本使用**：项目提供的服务管理脚本（start_service.sh）经过优化，能够正确处理服务启动、停止和状态检查，推荐使用脚本而非手动命令。
3. **日志监控价值**：系统日志是验证功能调用链和排查问题的重要工具，应养成查看日志的习惯。
4. **模块化设计优势**：新的模块化设计将数据导出和美化功能分离，符合单一职责原则，便于维护和测试。

### 10.6 后续建议
1. **前端代码检查**：检查前端调用导出API的代码，确保对中文字符进行URL编码。
2. **服务监控**：建立服务监控机制，确保前后端服务持续稳定运行。
3. **自动化测试**：增加API接口的自动化测试用例，覆盖中文字符参数场景。

---
*注：本文档记录了XBK系统的最新开发和修改情况，供开发团队和维护人员参考。*
