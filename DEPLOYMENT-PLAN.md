# MyWeb 项目部署规划

## 一、项目概述

MyWeb 是一个集成了多个功能的个人网站项目，包括：

### 核心模块
1. **前端**：Next.js + TypeScript + Ant Design
2. **后端**：FastAPI + SQLite + Python
3. **功能模块**：
   - AI智能体（DeepSeek/Dify集成）
   - 个人程序（XBK数据处理）
   - 笔记系统（Typst文档）
   - 仓库同步（自动Git同步）

### 当前状态
- 本地开发环境运行正常
- 代码已版本控制（Git）
- 依赖管理完整（requirements.txt, package.json）
- 容器化支持（Dockerfile）

## 二、部署目标

### 2.1 短期目标（1-2周）
1. **代码整理**：清理冗余文件，完善.gitignore
2. **文档完善**：更新README和部署文档
3. **本地测试**：确保所有功能在本地正常运行
4. **GitHub同步**：将最新代码推送到GitHub仓库

### 2.2 中期目标（2-4周）
1. **容器化部署**：完善Docker配置，支持一键启动
2. **环境配置**：支持环境变量配置，便于不同环境部署
3. **数据库迁移**：考虑生产环境使用PostgreSQL/MySQL
4. **自动化脚本**：创建部署和运维脚本

### 2.3 长期目标（1-2个月）
1. **CI/CD流水线**：GitHub Actions自动化测试和部署
2. **监控告警**：系统监控、日志收集和性能监控
3. **高可用部署**：多实例部署和负载均衡
4. **安全加固**：HTTPS、防火墙、访问控制

## 三、部署架构

### 3.1 单服务器部署（推荐初始方案）
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

### 3.2 容器化方案
```yaml
# docker-compose.yml 示例
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///app/data/my_web.db
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./backend/data:/app/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
```

## 四、实施步骤

### 第一阶段：代码整理和文档完善（本周）

#### 任务清单
- [x] 1. 清理冗余文件（.DS_Store, __pycache__, 旧日志）
- [x] 2. 完善.gitignore文件
- [x] 3. 整理项目文档
- [ ] 4. 创建部署文档（本文档）
- [ ] 5. 更新README.md
- [ ] 6. 创建环境变量模板（.env.example）

#### 交付物
1. 干净的项目代码库
2. 完整的项目文档
3. 部署规划文档

### 第二阶段：本地部署测试（下周）

#### 任务清单
- [ ] 1. 创建docker-compose.yml
- [ ] 2. 编写启动脚本（start.sh, stop.sh）
- [ ] 3. 测试容器化部署
- [ ] 4. 配置Nginx反向代理
- [ ] 5. 测试所有功能模块
- [ ] 6. 创建备份和恢复脚本

#### 交付物
1. 可运行的docker-compose配置
2. 一键启动脚本
3. 本地部署测试报告

### 第三阶段：GitHub仓库同步（下周）

#### 任务清单
- [ ] 1. 检查并提交所有代码更改
- [ ] 2. 推送到GitHub仓库
- [ ] 3. 创建版本标签（v1.0.0）
- [ ] 4. 设置GitHub Actions基础配置
- [ ] 5. 创建issue和PR模板

#### 交付物
1. 同步的GitHub仓库
2. 版本标签
3. CI/CD基础配置

### 第四阶段：生产环境部署（下下周）

#### 任务清单
- [ ] 1. 准备云服务器（Ubuntu 22.04）
- [ ] 2. 安装Docker和Docker Compose
- [ ] 3. 配置防火墙和安全组
- [ ] 4. 部署应用容器
- [ ] 5. 配置域名和SSL证书
- [ ] 6. 设置监控和日志

#### 交付物
1. 可访问的生产环境
2. SSL证书配置
3. 基础监控配置

## 五、技术要求

### 5.1 服务器要求
- **CPU**：2核以上
- **内存**：4GB以上
- **存储**：20GB以上
- **系统**：Ubuntu 22.04 LTS 或 CentOS 8

### 5.2 软件依赖
- **Docker**：24.0+
- **Docker Compose**：2.20+
- **Git**：2.40+
- **Nginx**：1.18+

### 5.3 网络要求
- **端口**：80, 443, 22
- **域名**：建议配置自定义域名
- **SSL**：Let's Encrypt免费证书

## 六、配置文件示例

### 6.1 环境变量配置（.env.example）
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

### 6.2 Nginx配置（nginx.conf）
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /content/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 七、风险与应对

### 7.1 技术风险
| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 数据库性能瓶颈 | 中 | 高 | 使用PostgreSQL替代SQLite |
| 容器资源不足 | 低 | 中 | 监控资源使用，及时扩容 |
| 安全漏洞 | 中 | 高 | 定期更新依赖，安全扫描 |

### 7.2 操作风险
| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 部署失败 | 中 | 高 | 保留回滚方案，分阶段部署 |
| 数据丢失 | 低 | 极高 | 定期备份，测试恢复流程 |
| 配置错误 | 高 | 中 | 使用配置管理，文档详细 |

## 八、时间计划

### 第1周：准备阶段
- 代码整理和文档完善
- 本地测试环境验证
- 团队内部培训

### 第2周：开发阶段
- 容器化配置开发
- 部署脚本编写
- 本地集成测试

### 第3周：测试阶段
- 生产环境模拟测试
- 性能和安全测试
- 用户验收测试

### 第4周：上线阶段
- 生产环境部署
- 监控和告警配置
- 上线后支持

## 九、成功标准

### 技术标准
1. ✅ 所有功能模块正常运行
2. ✅ 响应时间 < 2秒
3. ✅ 系统可用性 > 99.5%
4. ✅ 数据备份恢复测试通过

### 业务标准
1. ✅ 用户可正常访问所有功能
2. ✅ 管理员可管理所有模块
3. ✅ 系统支持日常使用需求
4. ✅ 部署过程文档完整

## 十、后续优化

### 10.1 性能优化
1. 数据库查询优化
2. 前端资源压缩
3. CDN静态资源加速
4. 缓存策略优化

### 10.2 功能扩展
1. 用户认证系统增强
2. 多语言支持
3. 移动端适配
4. 第三方集成（微信、钉钉）

### 10.3 运维增强
1. 自动化监控告警
2. 日志分析系统
3. 自动化备份
4. 灾备方案

---

**文档版本**: v1.0  
**创建日期**: 2026-01-22  
**最后更新**: 2026-01-22  
**负责人**: 项目团队  

**下一步行动**：
1. 团队评审此部署规划
2. 开始第一阶段任务
3. 每周例会跟踪进度
