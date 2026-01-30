"""
简化版数据库配置
明确指定数据库文件位置：backend/xbk.db 和 backend/znt.db
不再使用复杂的路径查找逻辑
"""
import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 配置日志格式
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 如果logger没有处理器，则添加一个控制台处理器
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# 固定数据库路径（相对于项目根目录）

XBK_DB_PATH = "backend/xbk.db"
ZNT_DB_PATH = "backend/znt.db"

def get_absolute_db_path(relative_path):
    """将相对路径转换为绝对路径（基于项目根目录）"""
    # 获取项目根目录（/Users/wsh/Desktop/my_web）
    # database.py 在 backend/config/ 目录下，所以 parent.parent 是项目根目录
    project_root = Path(__file__).parent.parent.parent
    abs_path = str(project_root / relative_path)
    logger.info(f"数据库绝对路径: {abs_path}")
    return abs_path

def create_sqlite_engine(db_path, engine_name="SQLite"):
    """创建SQLite数据库引擎"""
    abs_path = get_absolute_db_path(db_path)
    
    # 确保目录存在
    Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"创建{engine_name}引擎: {abs_path}")
    
    # SQLite连接参数
    connect_args = {"check_same_thread": False}
    
    # 创建带连接池的引擎
    engine = create_engine(
        f"sqlite:///{abs_path}",
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
            # 设置页面大小
            cursor.execute("PRAGMA page_size=4096")
            # 设置忙超时时间（毫秒）
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()
            logger.info(f"✅ {engine_name}数据库WAL模式和性能优化已启用")
        except Exception as e:
            logger.warning(f"⚠️  配置{engine_name}数据库PRAGMA失败: {e}")
    
    return engine

# 根据环境变量选择使用PostgreSQL还是SQLite
USE_POSTGRESQL = os.getenv("USE_POSTGRESQL", "false").lower() == "true"
logger.info(f"数据库模式配置: USE_POSTGRESQL={USE_POSTGRESQL}")

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
    except Exception as e:
        logger.error(f"❌ PostgreSQL连接失败，回退到SQLite: {e}")
        USE_POSTGRESQL = False

if not USE_POSTGRESQL:
    # 使用SQLite（开发环境）
    logger.warning("⚠️  使用SQLite数据库（仅限开发环境）")
    
    # 创建SQLite引擎
    default_engine = create_sqlite_engine(XBK_DB_PATH, "XBK数据库")
    ai_engine = create_sqlite_engine(ZNT_DB_PATH, "ZNT数据库")
    
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
        
        databases = [
            (XBK_DB_PATH, "XBK数据库"),
            (ZNT_DB_PATH, "ZNT数据库"),
        ]
        
        for db_path, db_name in databases:
            abs_path = get_absolute_db_path(db_path)
            
            if Path(abs_path).exists():
                try:
                    conn = sqlite3.connect(abs_path)
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
                logger.info(f"ℹ️  数据库文件 {abs_path} 不存在，将在首次使用时创建并优化")

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
    "XBK_DB_PATH",
    "ZNT_DB_PATH",
]