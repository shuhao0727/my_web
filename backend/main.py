"""
FastAPI主应用入口 - 集成自动同步功能
核心功能：静态文件服务、仓库同步API、自动同步调度器
"""
import sys
import os
# 将backend目录添加到Python路径，以便导入routers等模块
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# 在导入其他模块之前加载环境变量
from dotenv import load_dotenv
import logging
from config.database import test_connections

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
    print(f"✅ 环境变量已加载: {env_path}")
else:
    print(f"⚠️  环境变量文件不存在: {env_path}，使用默认配置")
    # 设置默认环境变量
    os.environ.setdefault('CONTENT_DIR', './content')
    os.environ.setdefault('BACKEND_HOST', '0.0.0.0')
    os.environ.setdefault('BACKEND_PORT', '8000')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动阶段
    print("🚀 启动后端服务...")
    
    # 检查环境变量
    content_dir = os.getenv("CONTENT_DIR", "./content")
    sync_interval = os.getenv("SYNC_INTERVAL_SECONDS")
    enable_auto_sync = os.getenv("ENABLE_AUTO_SYNC")
    
    print(f"   CONTENT_DIR={content_dir}")
    print(f"   SYNC_INTERVAL_SECONDS={sync_interval}")
    print(f"   ENABLE_AUTO_SYNC={enable_auto_sync}")
    print(f"   GITHUB_ACCESS_TOKEN exists: {bool(os.getenv('GITHUB_ACCESS_TOKEN'))}")
    
    # 配置日志
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "backend.log")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )
    
    # 测试数据库连接
    try:
        test_connections()
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        raise
    
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
    
    # 检查内容目录
    os.makedirs(content_dir, exist_ok=True)
    print(f"✅ 内容目录已准备: {content_dir}")
    
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
    debug=os.getenv("APP_DEBUG", "false").lower() == "true",
)

# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# 配置CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:6608,*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # 暴露头部信息
    expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"],
)

# 注册静态文件服务
# 1. 静态内容目录
content_dir = os.getenv("CONTENT_DIR", "./content")
os.makedirs(content_dir, exist_ok=True)

app.mount("/content", StaticFiles(directory=content_dir), name="content")
print(f"✅ 静态文件服务已挂载: /content -> {content_dir}")

# 新增仓库同步路由
try:
    from routers.repo_sync import router as repo_sync_router
    app.include_router(repo_sync_router)
    print("✅ 仓库同步路由已加载")
except ImportError as e:
    print(f"⚠️  仓库同步路由导入失败: {e}")

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

# 新增Typst内容路由
try:
    from routers.typst_content import router as typst_router
    app.include_router(typst_router)
    print("✅ Typst内容路由已加载")
except ImportError as e:
    print(f"⚠️  Typst内容路由导入失败: {e}")

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
        "environment": os.getenv("APP_ENV", "development"),
        "content_dir": os.getenv("CONTENT_DIR", "./content"),
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "environment": os.getenv("APP_ENV", "development"),
        "database_status": "connected" if test_connections() is None else "disconnected"
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    reload = os.getenv("APP_DEBUG", "false").lower() == "true"
    
    print(f"🚀 启动服务: {host}:{port} (debug={reload})")
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
