"""
FastAPI主应用入口 - 简化版本
仅保留核心功能：静态文件服务和仓库同步API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 启动后端服务...")
    yield
    print("🛑 关闭后端服务...")

# 创建FastAPI应用
app = FastAPI(
    title="MyWeb后端API",
    description="个人网站后端API服务",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置CORS
origins = [
    "http://localhost:3000",
    "http://localhost:6608",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:6608",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册静态文件服务
# 1. 静态PDF缓存目录
content_dir = "/Volumes/文件/4-实用代码/my_web/content"
if os.path.exists(content_dir):
    app.mount("/content", StaticFiles(directory=content_dir), name="content")
    print(f"✅ 静态文件服务已挂载: /content -> {content_dir}")
else:
    print(f"⚠️  内容目录不存在: {content_dir}")

# 新增仓库同步路由
try:
    from routers.repo_sync import router as repo_sync_router
    app.include_router(repo_sync_router)
except ImportError:
    print("⚠️  仓库同步路由导入失败，请检查repo_sync.py文件")

# 健康检查
@app.get("/")
async def root():
    """根路由，返回API状态"""
    return {
        "app": "MyWeb后端API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "static_files": "/content",
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."],
    )
