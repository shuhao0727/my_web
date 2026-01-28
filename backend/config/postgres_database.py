"""
PostgreSQL数据库配置和基类 - 针对高并发优化版本
支持多数据库：默认数据库和智能体数据库（znt）
优化特性：连接池、连接复用、性能调优
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# PostgreSQL数据库URL - 优先使用环境变量
DEFAULT_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myweb_user:myweb_password@localhost:5432/myweb")
AI_DATABASE_URL = os.getenv("AI_DATABASE_URL", "postgresql://myweb_user:myweb_password@localhost:5432/ai_db")

def create_postgres_engine(url: str, engine_name: str = "PostgreSQL", pool_size: int = 25, max_overflow: int = 50):
    """
    创建并配置PostgreSQL引擎，针对100并发优化
    
    Args:
        url: 数据库连接URL
        engine_name: 引擎名称（用于日志）
        pool_size: 连接池大小（建议值：CPU核心数 * 2 + 1）
        max_overflow: 最大溢出连接数
    
    Returns:
        配置好的SQLAlchemy引擎
    """
    # 解析连接参数
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    
    logger.info(f"🔄 创建{engine_name}引擎: {parsed.hostname}:{parsed.port}/{parsed.path[1:]}")
    
    # 创建带优化连接池的引擎
    engine = create_engine(
        url,
        # 连接池配置
        poolclass=QueuePool,
        pool_size=pool_size,           # 连接池大小
        max_overflow=max_overflow,      # 最大溢出连接数
        pool_pre_ping=True,             # 连接前ping检查
        pool_recycle=1800,              # 连接回收时间（30分钟）
        pool_timeout=30,                # 连接超时时间
        pool_use_lifo=True,             # LIFO队列，提高缓存命中率
        
        # 性能优化
        echo=False,                     # 生产环境关闭SQL日志
        echo_pool=False,                # 关闭连接池日志
        future=True,                    # 使用SQLAlchemy 2.0风格
        
        # 连接参数
        connect_args={
            "connect_timeout": 10,      # 连接超时
            "application_name": f"myweb_{engine_name.lower()}",  # 应用名称
            "options": "-c statement_timeout=30000"  # 语句超时30秒
        },
        
        # 执行选项
        executemany_mode="values_plus_batch",  # 批量插入优化
        hide_parameters=False,          # 生产环境可设为True提高安全性
    )
    
    # 测试连接
    try:
        with engine.connect() as conn:
            # 获取PostgreSQL版本
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"✅ {engine_name}连接成功: {version}")
            
            # 设置连接优化参数
            conn.execute(text("SET statement_timeout = 30000"))  # 30秒超时
            conn.execute(text("SET lock_timeout = 10000"))       # 10秒锁超时
            conn.execute(text("SET idle_in_transaction_session_timeout = 60000"))  # 60秒空闲超时
            
    except Exception as e:
        logger.error(f"❌ {engine_name}连接测试失败: {e}")
        raise
    
    logger.info(f"✅ {engine_name}引擎已创建，连接池配置：size={pool_size}, overflow={max_overflow}")
    return engine

def create_fallback_engine(url: str, engine_name: str = "SQLite"):
    """创建SQLite回退引擎（用于开发或测试）"""
    from sqlalchemy import event
    
    logger.warning(f"⚠️  使用SQLite回退引擎: {engine_name}")
    
    # 如果是SQLite URL，转换为绝对路径
    if url.startswith("sqlite:///"):
        db_path = url.replace("sqlite:///", "")
        # 使用统一的绝对路径函数
        try:
            from config.database import get_absolute_db_path
            abs_path = get_absolute_db_path(db_path)
        except ImportError:
            # 回退方案：从当前工作目录计算
            from pathlib import Path
            project_root = Path.cwd()
            abs_path = str(project_root / db_path)
        
        # 确保目录存在
        from pathlib import Path
        Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
        
        url = f"sqlite:///{abs_path}"
        logger.info(f"🔧 SQLite数据库路径: {abs_path}")
    
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    
    # SQLite性能优化
    @event.listens_for(engine, "connect")
    def set_sqlite_pragmas(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-10000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA busy_timeout=10000")
            cursor.close()
            logger.info(f"✅ {engine_name}数据库WAL模式和性能优化已启用")
        except Exception as e:
            logger.warning(f"⚠️  配置{engine_name}数据库PRAGMA失败: {e}")
    
    return engine

# 根据环境变量选择数据库引擎
USE_POSTGRESQL = os.getenv("USE_POSTGRESQL", "true").lower() == "true"

if USE_POSTGRESQL:
    try:
        # 尝试连接PostgreSQL
        default_engine = create_postgres_engine(DEFAULT_DATABASE_URL, "默认PostgreSQL")
        ai_engine = create_postgres_engine(AI_DATABASE_URL, "AI智能体PostgreSQL")
        logger.info("✅ 使用PostgreSQL作为主数据库")
    except Exception as e:
        logger.error(f"❌ PostgreSQL连接失败，回退到SQLite: {e}")
        # 回退到SQLite，使用统一的路径配置
        try:
            from config.database import XBK_DB_PATH, ZNT_DB_PATH
            DEFAULT_DATABASE_URL = f"sqlite:///{XBK_DB_PATH}"
            AI_DATABASE_URL = f"sqlite:///{ZNT_DB_PATH}"
        except ImportError:
            # 回退方案
            DEFAULT_DATABASE_URL = "sqlite:///backend/xbk.db"
            AI_DATABASE_URL = "sqlite:///backend/znt.db"
        
        default_engine = create_fallback_engine(DEFAULT_DATABASE_URL, "默认SQLite")
        ai_engine = create_fallback_engine(AI_DATABASE_URL, "AI智能体SQLite")
else:
    # 直接使用SQLite，使用统一的路径配置
    try:
        from config.database import XBK_DB_PATH, ZNT_DB_PATH
        DEFAULT_DATABASE_URL = f"sqlite:///{XBK_DB_PATH}"
        AI_DATABASE_URL = f"sqlite:///{ZNT_DB_PATH}"
    except ImportError:
        # 回退方案
        DEFAULT_DATABASE_URL = "sqlite:///backend/xbk.db"
        AI_DATABASE_URL = "sqlite:///backend/znt.db"
    
    default_engine = create_fallback_engine(DEFAULT_DATABASE_URL, "默认SQLite")
    ai_engine = create_fallback_engine(AI_DATABASE_URL, "AI智能体SQLite")

# 创建SessionLocal类
DefaultSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=default_engine)
AiSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ai_engine)

# 创建基类
DefaultBase = declarative_base()
AiBase = declarative_base()

def get_default_db():
    """
    获取默认数据库会话的依赖函数
    针对高并发优化：使用连接池，自动管理会话生命周期
    """
    db = DefaultSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_ai_db():
    """
    获取智能体数据库会话的依赖函数
    针对高并发优化：使用连接池，自动管理会话生命周期
    """
    db = AiSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_connection_pool_stats():
    """
    获取连接池统计信息
    用于监控和性能分析
    """
    # 尝试获取动态统计，如果失败则返回默认值
    def try_get_pool_stats(engine):
        try:
            # 使用类型忽略来避免Pylance错误
            pool = engine.pool
            size = pool.size() if hasattr(pool, 'size') else 0
            checked_out = getattr(pool, 'checkedout', lambda: 0)()
            overflow = getattr(pool, 'overflow', lambda: 0)()
            return size, checked_out, overflow
        except Exception:
            # 如果获取失败，返回默认值
            return 0, 0, 0

    default_size, default_checked_out, default_overflow = try_get_pool_stats(default_engine)
    ai_size, ai_checked_out, ai_overflow = try_get_pool_stats(ai_engine)

    stats = {
        "default": {
            "pool_size": default_size,
            "checked_out": default_checked_out,
            "overflow": default_overflow,
            "engine_type": str(type(default_engine)),
        },
        "ai": {
            "pool_size": ai_size,
            "checked_out": ai_checked_out,
            "overflow": ai_overflow,
            "engine_type": str(type(ai_engine)),
        }
    }
    return stats

def optimize_database_performance():
    """
    执行数据库性能优化
    包括索引创建、统计信息更新等
    """
    # 仅在PostgreSQL模式下执行性能优化
    if not USE_POSTGRESQL:
        logger.info("ℹ️  SQLite模式，跳过数据库性能优化")
        return
    try:
        with default_engine.connect() as conn:
            # 创建常用索引（根据实际表结构调整）
            indexes = [
                # 用户表索引
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
                
                # 文章表索引
                "CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_articles_author_id ON articles(author_id)",
                "CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status)",
                
                # 评论表索引
                "CREATE INDEX IF NOT EXISTS idx_comments_article_id ON comments(article_id)",
                "CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at)",
                
                # 会话表索引
                "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)",
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    logger.debug(f"✅ 创建索引: {index_sql}")
                except Exception as e:
                    logger.debug(f"⚠️  创建索引失败（可能表不存在）{index_sql}: {e}")
            
            # 更新统计信息（PostgreSQL）
            if USE_POSTGRESQL:
                conn.execute(text("ANALYZE"))
                logger.info("✅ PostgreSQL统计信息已更新")
            
            conn.commit()
            logger.info("✅ 数据库性能优化完成")
            
    except Exception as e:
        logger.error(f"❌ 数据库性能优化失败: {e}")

# 应用启动时自动优化（仅在PostgreSQL模式下执行）
if __name__ != "__main__" and USE_POSTGRESQL:
    # 在应用启动时执行一次性能优化
    import threading
    threading.Thread(target=optimize_database_performance, daemon=True).start()

__all__ = [
    "default_engine",
    "ai_engine",
    "DefaultSessionLocal",
    "AiSessionLocal",
    "DefaultBase",
    "AiBase",
    "get_default_db",
    "get_ai_db",
    "get_connection_pool_stats",
    "optimize_database_performance",
    "USE_POSTGRESQL",
]