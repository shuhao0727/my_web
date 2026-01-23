"""
FastAPI主应用入口 - 集成自动同步功能
核心功能：静态文件服务、仓库同步API、自动同步调度器
"""
import sys
import os
# 将backend目录添加到Python路径，以便导入routers等模块
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动阶段
    print("🚀 启动后端服务...")
    
    # 加载环境变量
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ 环境变量已加载: {env_path}")
        print(f"   SYNC_INTERVAL_SECONDS={os.getenv('SYNC_INTERVAL_SECONDS')}")
        print(f"   ENABLE_AUTO_SYNC={os.getenv('ENABLE_AUTO_SYNC')}")
    else:
        print(f"⚠️  环境变量文件不存在: {env_path}")
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("backend.log")
        ]
    )
    
    # 启动自动同步调度器（临时禁用以避免启动阻塞）
    # try:
    #     from scheduler.sync_scheduler import repo_sync_scheduler
    #     if repo_sync_scheduler.start():
    #         print("✅ 仓库自动同步调度器已启动")
    #     else:
    #         print("⚠️  仓库自动同步调度器未启动（可能已禁用或已在运行）")
    # except Exception as e:
    #     print(f"❌ 启动自动同步调度器失败: {e}")
    print("⚠️  仓库自动同步调度器已临时禁用（避免网络连接阻塞）")
    
    yield
    
    # 关闭阶段
    print("🛑 关闭后端服务...")
    
    # 停止自动同步调度器
    try:
        from scheduler.sync_scheduler import repo_sync_scheduler
        repo_sync_scheduler.stop()
        print("✅ 仓库自动同步调度器已停止")
    except Exception as e:
        print(f"❌ 停止自动同步调度器失败: {e}")

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
    "*",  # 临时允许所有来源用于调试
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 临时允许所有来源
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

# 新增AI智能体路由（模块化版本）
try:
    from routers.ai.ai_main import router as ai_agent_router
    app.include_router(ai_agent_router, prefix="/api/ai")  # 添加前缀
    print("✅ AI智能体路由已加载（模块化版本）")
except ImportError as e:
    print(f"⚠️  AI智能体路由导入失败: {e}")

# 新增XBK应用路由
try:
    from routers.xbk.applications import xbk_router
    app.include_router(xbk_router, prefix="/api/xbk")  # 添加前缀
    print("✅ XBK应用路由已加载")
except ImportError as e:
    print(f"⚠️  XBK应用路由导入失败: {e}")

# 新增XBK数据处理路由
try:
    from routers.xbk.routes import data_router
    app.include_router(data_router, prefix="/api/xbk")  # 添加前缀
    print("✅ XBK数据处理路由已加载")
except ImportError as e:
    print(f"⚠️  XBK数据处理路由导入失败: {e}")

# 新增XBK安全认证路由
try:
    from routers.xbk.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/xbk")  # 添加前缀
    print("✅ XBK安全认证路由已加载")
except ImportError as e:
    print(f"⚠️  XBK安全认证路由导入失败: {e}")

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
        reload=False,
    )
