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

# 尝试从多个位置加载.env文件
env_paths = [
    os.path.join(os.path.dirname(__file__), '.env'),  # backend/.env
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # 根目录/.env
]

env_loaded = False
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ 环境变量已加载: {env_path}")
        print(f"   CONTENT_DIR={os.getenv('CONTENT_DIR')}")
        print(f"   GITHUB_ACCESS_TOKEN exists: {bool(os.getenv('GITHUB_ACCESS_TOKEN'))}")
        env_loaded = True
        break

if not env_loaded:
    print(f"⚠️  环境变量文件未找到，尝试路径: {env_paths}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动阶段
    print("🚀 启动后端服务...")
    
    # 环境变量已经在模块级别加载，这里只打印其他配置
    print(f"   SYNC_INTERVAL_SECONDS={os.getenv('SYNC_INTERVAL_SECONDS')}")
    print(f"   ENABLE_AUTO_SYNC={os.getenv('ENABLE_AUTO_SYNC')}")
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("backend.log")
        ]
    )
    
    # 数据库优化：启用WAL模式和连接池
    try:
        from config.database import optimize_database_performance
        optimize_database_performance()
        print("✅ 数据库WAL模式优化完成")
    except Exception as e:
        print(f"⚠️  数据库优化失败: {e}")
    
    # 启动自动同步调度器（增加错误恢复机制）
    try:
        from scheduler.sync_scheduler import repo_sync_scheduler
        # 检查是否启用自动同步
        enable_auto_sync = os.getenv("ENABLE_AUTO_SYNC", "True").lower() == "true"
        if enable_auto_sync:
            # 在后台线程中启动调度器，避免阻塞主应用启动
            import threading
            def start_scheduler_safe():
                try:
                    if repo_sync_scheduler.start():
                        print("✅ 仓库自动同步调度器已启动")
                    else:
                        print("⚠️  仓库自动同步调度器未启动（可能已禁用或已在运行）")
                except Exception as e:
                    print(f"❌ 启动自动同步调度器失败: {e}")
                    # 记录错误但不影响应用启动
                    # 可以在这里添加重试逻辑或告警
            
            scheduler_thread = threading.Thread(target=start_scheduler_safe, daemon=True)
            scheduler_thread.start()
            print("✅ 仓库自动同步调度器启动线程已启动（后台运行）")
        else:
            print("ℹ️  自动同步已禁用，跳过调度器启动")
    except ImportError as e:
        print(f"❌ 导入调度器模块失败: {e}")
    except Exception as e:
        print(f"❌ 配置自动同步调度器时发生异常: {e}")
    
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

# 配置CORS - 根据环境设置合适的白名单
is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
if is_production:
    # 生产环境：只允许特定的来源
    allowed_origins = [
        "https://your-domain.com",  # 替换为实际的生产域名
        "https://www.your-domain.com",
    ]
    print(f"✅ 生产环境CORS配置：{allowed_origins}")
else:
    # 开发环境：允许常见的本地开发地址
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:6608", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:6608",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    print(f"✅ 开发环境CORS配置：{allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# 添加API速率限制中间件（仅在非开发环境启用）
enable_rate_limit = os.getenv("ENABLE_RATE_LIMIT", "false").lower() == "true"
if enable_rate_limit or is_production:
    try:
        from middleware.rate_limit import RateLimitMiddleware
        # 生产环境使用更严格的限制，开发环境宽松
        requests_per_minute = 60 if is_production else 120
        app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)
        print(f"✅ API速率限制已启用：每分钟{requests_per_minute}次请求")
    except ImportError as e:
        print(f"⚠️  导入速率限制中间件失败: {e}")
    except Exception as e:
        print(f"❌ 配置速率限制中间件失败: {e}")
else:
    print("ℹ️  API速率限制已禁用")

# 添加全局错误处理中间件
try:
    from middleware.error_handler import setup_error_handlers
    is_development = os.getenv("ENVIRONMENT", "development").lower() != "production"
    setup_error_handlers(app, is_development=is_development)
    print("✅ 全局错误处理中间件已设置")
except ImportError as e:
    print(f"⚠️  导入错误处理中间件失败: {e}")
except Exception as e:
    print(f"❌ 配置错误处理中间件失败: {e}")

# 添加静态文件缓存中间件（仅在非开发环境启用）
enable_static_cache = os.getenv("ENABLE_STATIC_CACHE", "true").lower() == "true"
if enable_static_cache or is_production:
    try:
        from middleware.static_cache import setup_static_cache
        setup_static_cache(app, static_path="/content", enable_gzip=True)
        print("✅ 静态文件缓存中间件已设置")
    except ImportError as e:
        print(f"⚠️  导入静态文件缓存中间件失败: {e}")
    except Exception as e:
        print(f"❌ 配置静态文件缓存中间件失败: {e}")
else:
    print("ℹ️  静态文件缓存已禁用")

# 注册静态文件服务
# 1. 静态PDF缓存目录
content_dir = os.getenv("CONTENT_DIR", "./content")
if os.path.exists(content_dir):
    app.mount("/content", StaticFiles(directory=content_dir), name="content")
    print(f"✅ 静态文件服务已挂载: /content -> {content_dir}")
else:
    print(f"⚠️  内容目录不存在: {content_dir}")
    # 尝试创建目录
    try:
        os.makedirs(content_dir, exist_ok=True)
        print(f"✅ 已创建内容目录: {content_dir}")
    except Exception as e:
        print(f"❌ 创建内容目录失败: {e}")

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

# 新增Typst内容路由
try:
    from routers.typst_content import router as typst_router
    app.include_router(typst_router)
    print("✅ Typst内容路由已加载")
except ImportError as e:
    print(f"⚠️  Typst内容路由导入失败: {e}")

# 新增文章板块路由
try:
    from routers.articles import articles_router
    app.include_router(articles_router)
    print("✅ 文章板块路由已加载")
except ImportError as e:
    print(f"⚠️  文章板块路由导入失败: {e}")

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
