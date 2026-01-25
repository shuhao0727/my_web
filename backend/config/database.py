"""
数据库配置和基类 - 针对高并发优化版本
支持多数据库：默认数据库和智能体数据库（znt）
根据环境变量选择PostgreSQL（生产环境）或SQLite（开发环境）
"""
import os
import logging

logger = logging.getLogger(__name__)

# 根据环境变量选择使用PostgreSQL还是SQLite
USE_POSTGRESQL = os.getenv("USE_POSTGRESQL", "true").lower() == "true"

if USE_POSTGRESQL:
    try:
        # 导入PostgreSQL配置
        from .postgres_database import (
            default_engine,
            ai_engine,
            DefaultSessionLocal,
            AiSessionLocal,
            DefaultBase,
            AiBase,
            get_default_db,
            get_ai_db,
            get_connection_pool_stats,
            optimize_database_performance,
            USE_POSTGRESQL as USE_PG
        )
        logger.info("✅ 使用PostgreSQL作为主数据库")
    except ImportError as e:
        logger.error(f"❌ 导入PostgreSQL配置失败: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ PostgreSQL配置出错: {e}")
        # 回退到SQLite
        USE_POSTGRESQL = False
else:
    # 使用SQLite（开发环境）
    USE_POSTGRESQL = False

if not USE_POSTGRESQL:
    logger.warning("⚠️  使用SQLite数据库（仅限开发环境）")
    from sqlalchemy import create_engine, event
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    
    # 默认数据库URL - 用于用户、文档等（优先使用环境变量）
    DEFAULT_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./xbk.db")
    # 智能体数据库URL - 用于AI智能体相关数据
    AI_DATABASE_URL = os.getenv("AI_DATABASE_URL", "sqlite:///./znt.db")
    
    def configure_sqlite_engine(url, engine_name="default"):
        """创建并配置SQLite引擎，启用WAL模式和连接池"""
        if "sqlite" not in url:
            # 非SQLite数据库，使用默认配置
            return create_engine(url)
        
        # SQLite连接参数
        connect_args = {"check_same_thread": False}
        
        # 创建带连接池的引擎
        engine = create_engine(
            url,
            connect_args=connect_args,
            pool_size=10,           # 连接池大小
            max_overflow=20,        # 最大溢出连接数
            pool_pre_ping=True,     # 连接前ping检查
            pool_recycle=3600,      # 连接回收时间（秒）
        )
        
        # 添加WAL模式和性能优化
        @event.listens_for(engine, "connect")
        def set_sqlite_pragmas(dbapi_connection, connection_record):
            try:
                cursor = dbapi_connection.cursor()
                # 启用WAL模式（Write-Ahead Logging）提高并发
                cursor.execute("PRAGMA journal_mode=WAL")
                # 设置同步模式为NORMAL（平衡性能与安全）
                cursor.execute("PRAGMA synchronous=NORMAL")
                # 设置缓存大小（约2MB）
                cursor.execute("PRAGMA cache_size=-2000")
                # 启用外键约束
                cursor.execute("PRAGMA foreign_keys=ON")
                # 设置临时存储为内存
                cursor.execute("PRAGMA temp_store=MEMORY")
                # 设置页面大小（可选，默认通常是4096）
                cursor.execute("PRAGMA page_size=4096")
                # 设置忙超时时间（毫秒）
                cursor.execute("PRAGMA busy_timeout=5000")
                cursor.close()
                logger.info(f"✅ {engine_name}数据库WAL模式和性能优化已启用")
            except Exception as e:
                logger.warning(f"⚠️  配置{engine_name}数据库PRAGMA失败: {e}")
        
        return engine
    
    # 创建优化后的数据库引擎
    default_engine = configure_sqlite_engine(DEFAULT_DATABASE_URL, "默认")
    ai_engine = configure_sqlite_engine(AI_DATABASE_URL, "AI智能体")
    
    # 创建SessionLocal类
    DefaultSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=default_engine)
    AiSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ai_engine)
    
    # 创建基类
    DefaultBase = declarative_base()
    AiBase = declarative_base()
    
    def get_default_db():
        """获取默认数据库会话的依赖函数"""
        db = DefaultSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def get_ai_db():
        """获取智能体数据库会话的依赖函数"""
        db = AiSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def get_connection_pool_stats():
        """获取连接池统计信息（SQLite版本）"""
        return {
            "default": {
                "pool_size": 10,
                "checked_out": 0,
                "overflow": 0,
                "engine_type": "SQLite",
            },
            "ai": {
                "pool_size": 10,
                "checked_out": 0,
                "overflow": 0,
                "engine_type": "SQLite",
            }
        }
    
    def optimize_database_performance():
        """优化数据库性能（SQLite版本）"""
        import sqlite3
        from pathlib import Path
        
        databases = [
            ("xbk.db", DEFAULT_DATABASE_URL),
            ("znt.db", AI_DATABASE_URL),
        ]
        
        for db_name, db_url in databases:
            if "sqlite" in db_url:
                # 从URL提取路径
                db_path = db_url.replace("sqlite:///", "")
                if db_path.startswith("./"):
                    db_path = db_path[2:]
                
                if Path(db_path).exists():
                    try:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("PRAGMA journal_mode=WAL")
                        cursor.execute("PRAGMA synchronous=NORMAL")
                        cursor.execute("PRAGMA cache_size=-2000")
                        cursor.execute("PRAGMA foreign_keys=ON")
                        cursor.close()
                        conn.close()
                        logger.info(f"✅ 现有数据库 {db_name} 已优化为WAL模式")
                    except Exception as e:
                        logger.warning(f"⚠️  优化现有数据库 {db_name} 失败: {e}")
                else:
                    logger.info(f"ℹ️  数据库文件 {db_path} 不存在，将在首次使用时创建并优化")

# 导出统一的接口
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