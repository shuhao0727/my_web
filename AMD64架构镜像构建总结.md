# AMD64架构Docker镜像构建总结报告

## 项目概述
本项目旨在为MyWeb应用（包含前端Next.js和后端FastAPI）构建适用于AMD CPU服务器的Docker镜像。原始代码在ARM64架构（Apple Silicon）开发机上开发，需要适配AMD64服务器架构。

## 成功构建的镜像
- **前端镜像**: `myweb-frontend:amd64` (467MB)
- **后端镜像**: `myweb-backend:amd64` (362MB)

## 构建环境
- **开发机**: macOS (ARM64/Apple Silicon)
- **目标平台**: Linux AMD64
- **Docker版本**: 支持多平台构建
- **代理配置**: HTTP_PROXY=http://192.168.0.148:7897

## 主要问题与解决方案

### 问题1：Python Alpine镜像架构不匹配

**问题描述**:
```
Error relocating /usr/local/bin/../lib/libpython3.11.so.1.0: pwritev2: symbol not found
Error relocating /usr/local/bin/../lib/libpython3.11.so.1.0: preadv2: symbol not found
```

**根本原因**:
- 本地缓存的`python:3.11-alpine`镜像是ARM64架构
- 使用`--platform linux/amd64`构建时，Docker尝试在ARM64镜像上运行AMD64代码
- `pwritev2`和`preadv2`是较新的系统调用，在不同架构的musl libc中实现不同

**解决方案**:
1. 删除本地ARM64架构的Python镜像
2. 重新拉取AMD64架构的基础镜像
3. 验证镜像架构：`docker inspect python:3.11-alpine --format='{{.Architecture}}'`
4. 测试基础功能：`docker run --platform linux/amd64 python:3.11-alpine python -c "import sys; print(sys.version)"`

### 问题2：Alpine镜像代理配置路径错误

**问题描述**:
```
/bin/sh: can't create /etc/apk/conf.d/no-proxy.conf: nonexistent directory
```

**根本原因**:
- Alpine镜像中`/etc/apk/conf.d/`目录可能不存在
- 原始Dockerfile中未创建该目录就尝试写入文件

**解决方案**:
```dockerfile
RUN mkdir -p /etc/apk/conf.d/ && \
    echo "https://mirrors.ustc.edu.cn/alpine/v3.19/main" > /etc/apk/repositories && \
    # ... 其他配置
```

### 问题3：不必要的Typst依赖

**问题描述**:
- 原始后端Dockerfile包含Typst构建阶段
- `ghcr.io/typst/typst:latest`镜像是ARM64架构
- 实际上后端服务不需要Typst编译功能

**解决方案**:
1. 检查requirements.txt确认后端确实不需要Typst
2. 移除Typst相关构建阶段
3. 简化Dockerfile为单阶段构建

### 问题4：复杂多阶段构建的兼容性问题

**问题描述**:
- 原始Dockerfile使用多阶段构建（builder + runner）
- 不同阶段的镜像架构需要一致
- 构建工具链在AMD64和ARM64间可能存在差异

**解决方案**:
1. 采用简化的单阶段构建
2. 统一使用`python:3.11-alpine`作为基础镜像
3. 直接安装所有依赖，不进行复杂的依赖分离

## 最终有效的Dockerfile配置

### 后端Dockerfile (简化版)
```dockerfile
# ========================================
# MyWeb后端 - AMD64兼容Docker镜像
# 简化构建过程，解决pwritev2/preadv2符号问题
# 使用python:3.11-alpine单阶段构建
# ========================================

FROM python:3.11-alpine

# 设置构建参数（代理配置）
ARG HTTP_PROXY
ARG HTTPS_PROXY

WORKDIR /app

# 环境变量配置
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# 代理设置
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

# 创建非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 配置Alpine国内镜像源
RUN mkdir -p /etc/apk/conf.d/ && \
    echo "https://mirrors.ustc.edu.cn/alpine/v3.19/main" > /etc/apk/repositories && \
    echo "https://mirrors.ustc.edu.cn/alpine/v3.19/community" >> /etc/apk/repositories && \
    rm -rf /etc/apk/conf.d/proxy.conf 2>/dev/null || true && \
    echo 'http_proxy=' > /etc/apk/conf.d/no-proxy.conf && \
    echo 'https_proxy=' >> /etc/apk/conf.d/no-proxy.conf && \
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# 安装系统依赖
RUN unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && \
    apk update && apk add --no-cache \
    curl \
    fontconfig \
    freetype \
    ttf-dejavu \
    font-noto \
    font-noto-cjk \
    font-noto-extra \
    && rm -rf /var/cache/apk/*

# 配置pip国内镜像源
RUN python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    python -m pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    python -m pip config unset global.proxy 2>/dev/null || true

# 安装Python依赖
COPY --chown=appuser:appgroup requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY --chown=appuser:appgroup . .

# 目录权限设置
RUN mkdir -p logs backups && \
    chown -R appuser:appgroup logs backups && \
    mkdir -p /backend && \
    chown -R appuser:appgroup /backend && \
    chown -R appuser:appgroup /app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "python init_databases.py && python -m uvicorn main:app --host 0.0.0.0 --port 8000"]
```

### 前端Dockerfile (保持原样)
前端Dockerfile已经优化支持多平台构建，无需修改：
- 使用node:20作为基础镜像
- 配置国内apt和npm镜像源
- 已包含AMD64架构支持

## 构建命令

### 后端镜像构建
```bash
cd /Users/wsh/Desktop/my_web/backend
docker build --progress=plain \
  --build-arg HTTP_PROXY=http://192.168.0.148:7897 \
  --build-arg HTTPS_PROXY=http://192.168.0.148:7897 \
  --platform linux/amd64 \
  -t myweb-backend:amd64 .
```

### 前端镜像构建
```bash
cd /Users/wsh/Desktop/my_web/frontend
docker build --progress=plain \
  --build-arg HTTP_PROXY=http://192.168.0.148:7897 \
  --build-arg HTTPS_PROXY=http://192.168.0.148:7897 \
  --platform linux/amd64 \
  -t myweb-frontend:amd64 .
```

## 验证步骤

1. **检查镜像架构**:
   ```bash
   docker inspect myweb-backend:amd64 --format='{{.Architecture}} {{.Os}}'
   docker inspect myweb-frontend:amd64 --format='{{.Architecture}} {{.Os}}'
   ```
   输出应为：`amd64 linux`

2. **测试镜像运行**:
   ```bash
   docker run --rm --platform linux/amd64 myweb-backend:amd64 python --version
   ```

3. **查看构建的镜像**:
   ```bash
   docker images --filter "reference=myweb*" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
   ```

## 经验总结与最佳实践

### 跨平台构建的关键要点

1. **基础镜像选择**:
   - 确保基础镜像支持多平台（如`python:3.11-alpine`）
   - 避免使用特定架构的镜像摘要（如`@sha256:...`）

2. **代理配置处理**:
   - 在构建参数中传递代理设置
   - 在RUN命令中清除代理环境变量，避免影响包管理器
   - 为不同包管理器（apk、apt、pip）分别配置镜像源

3. **简化构建过程**:
   - 单阶段构建比多阶段构建在跨平台时更可靠
   - 移除不必要的依赖和构建阶段
   - 优先使用alpine镜像以减小体积

4. **测试验证**:
   - 始终验证构建出的镜像架构
   - 测试镜像的基本功能
   - 使用`--platform`参数确保运行在正确架构

### 常见陷阱与避免方法

1. **符号未找到错误**:
   - 通常表示架构不匹配
   - 解决方案：重新拉取正确架构的基础镜像

2. **目录不存在错误**:
   - Alpine镜像的目录结构可能不同
   - 解决方案：使用`mkdir -p`确保目录存在

3. **网络超时问题**:
   - 国内环境需要配置镜像源
   - 解决方案：为每个包管理器配置国内镜像

### 推荐的构建流程

1. 清理旧镜像：`docker image prune -f`
2. 拉取正确架构的基础镜像：`docker pull --platform linux/amd64 <image>`
3. 验证基础镜像：`docker inspect <image> --format='{{.Architecture}}'`
4. 构建应用镜像：使用`--platform linux/amd64`参数
5. 验证构建结果：检查架构和基本功能

## 后续建议

1. **自动化构建脚本**:
   ```bash
   #!/bin/bash
   # build-amd64.sh
   set -e
   docker build --platform linux/amd64 -t myweb-backend:amd64 ./backend
   docker build --platform linux/amd64 -t myweb-frontend:amd64 ./frontend
   ```

2. **多架构镜像支持**:
   - 考虑使用`docker buildx`构建多架构镜像
   - 创建manifest list支持自动选择合适架构

3. **CI/CD集成**:
   - 在CI中明确指定构建平台
   - 添加架构验证步骤到流水线

## 结论
通过本次构建过程，我们成功解决了AMD64架构下的Docker镜像构建问题。关键成功因素包括：选择正确架构的基础镜像、简化构建过程、合理配置代理和镜像源。这些经验对于未来在不同架构服务器上部署应用具有重要参考价值。

---
*文档生成时间：2026年1月30日*
*构建环境：macOS ARM64 → Linux AMD64*