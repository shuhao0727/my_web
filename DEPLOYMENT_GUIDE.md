# AI教育平台 - 部署指南

## 项目状态
✅ 本地开发已完成
✅ 生产构建已验证
⚠️  GitHub推送遇到SSL/TLS连接问题

## 文件结构
```
my_web/
├── design-conception.md        # 设计构思文档
├── project-structure.md       # 项目结构文档
├── frontend/                  # 前端项目
│   ├── app/                   # Next.js应用
│   ├── components/            # 组件库
│   ├── public/                # 静态资源
│   ├── package.json          # 依赖配置
│   └── ...                   # 其他配置文件
└── DEPLOYMENT_GUIDE.md       # 本部署指南
```

## 推送GitHub的解决方案

### 方案1：使用GitHub Desktop（推荐）
1. 下载并安装 [GitHub Desktop](https://desktop.github.com/)
2. 打开GitHub Desktop
3. 选择 "File" → "Add Local Repository"
4. 选择 `f:\my_web` 目录
5. 在左下角输入提交信息："完成AI教育平台开发"
6. 点击 "Commit to main"
7. 点击 "Push origin"

### 方案2：使用Personal Access Token
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token"
3. 选择权限：`repo` (所有仓库权限)
4. 生成Token并复制
5. 在命令行执行：
```bash
cd f:\my_web
git remote set-url origin https://[YOUR_TOKEN]@github.com/shuhao0727/my_web.git
git push origin main
```

### 方案3：使用SSH密钥
1. 生成SSH密钥（如果还没有）：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
2. 将公钥添加到GitHub：
   - 复制 `C:\Users\Administrator\.ssh\id_ed25519.pub` 内容
   - 访问 https://github.com/settings/keys
   - 点击 "New SSH key"
3. 更新远程仓库URL：
```bash
cd f:\my_web
git remote set-url origin git@github.com:shuhao0727/my_web.git
git push origin main
```

### 方案4：手动上传ZIP文件
1. 访问 https://github.com/shuhao0727/my_web
2. 点击 "Add file" → "Upload files"
3. 将整个 `my_web` 文件夹拖放到上传区域
4. 输入提交信息："完成AI教育平台开发"
5. 点击 "Commit changes"

## 项目特点

### 已完成功能
- ✅ 完整的前端架构（Next.js 15 + TypeScript + Ant Design + Tailwind CSS）
- ✅ 响应式设计（桌面端 + 移动端）
- ✅ 核心页面：首页、关于、博客、登录、注册
- ✅ 生产构建验证通过
- ✅ Docker容器化配置

### 技术栈
- **框架**: Next.js 15 (App Router)
- **语言**: TypeScript
- **UI库**: Ant Design 5.0
- **样式**: Tailwind CSS
- **部署**: Docker, Vercel, GitHub Pages

### 页面列表
1. **首页** (`/`) - 平台介绍和核心功能展示
2. **关于页面** (`/about`) - 教师团队介绍和成就展示
3. **博客页面** (`/blog`) - 技术文章和教程
4. **登录页面** (`/login`) - 学生/教师登录
5. **注册页面** (`/register`) - 学生注册功能

## 运行项目

### 本地开发
```bash
cd frontend
npm install
npm run dev
```
访问：http://localhost:3000

### 生产构建
```bash
cd frontend
npm run build
npm start
```

### Docker部署
```bash
cd frontend
docker build -t ai-education-platform .
docker run -p 3000:3000 ai-education-platform
```

## 后续开发计划

### 第一阶段：用户系统（2-3周）
- JWT认证实现
- 用户个人中心
- 密码重置功能

### 第二阶段：AI功能集成（3-4周）
- Dify AI智能体API集成
- AI聊天界面
- 代码编辑器集成

### 第三阶段：学习资源管理（2-3周）
- 资源上传系统
- 视频课程播放器
- 在线编程练习

### 第四阶段：教师后台（4-5周）
- 学生管理系统
- 学习数据分析仪表板
- 内容管理系统

## 故障排除

### SSL/TLS连接问题
如果遇到SSL/TLS连接失败，可以尝试：
1. 更新Git：`git update-git-for-windows`
2. 重置SSL证书：`git config --global http.sslBackend schannel`
3. 使用代理（如果需要）

### 构建问题
如果Next.js构建失败：
1. 清除缓存：`cd frontend && rm -rf .next node_modules`
2. 重新安装依赖：`npm install`
3. 重新构建：`npm run build`

## 联系方式
如有问题，请联系项目维护者。

---
**项目最后更新时间**: 2026年1月15日
**项目状态**: ✅ 开发完成，等待部署
