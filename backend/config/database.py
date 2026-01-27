"""
数据库配置和基类 - 针对高并发优化版本
支持多数据库：默认数据库和智能体数据库（znt）
根据环境变量选择PostgreSQL（生产环境）或SQLite（开发环境）
"""
import os
import logging
from pathlib import Path

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

def find_database_file(filename, search_paths=None):
    """
    智能查找数据库文件路径，始终返回绝对路径
    搜索顺序:
    1. 当前工作目录
    2. backend/目录
    3. 项目根目录
    4. 指定的搜索路径
    """
    if search_paths is None:
        search_paths = []
    
    # 默认搜索路径
    default_paths = [
        filename,  # 当前目录
        f"backend/{filename}",  # backend目录
        f"../backend/{filename}",  # 上级的backend目录（如果从子目录运行）
        f"../../backend/{filename}",  # 更上级的backend目录
        f"/Users/wsh/Desktop/my_web/backend/{filename}",  # 绝对路径
    ]
    
    all_paths = default_paths + search_paths
    
    for path in all_paths:
        # 尝试绝对路径
        abs_path = Path(path).absolute()
        if abs_path.exists():
            logger.info(f"🔍 找到数据库文件 {filename}: {abs_path}")
            return str(abs_path)
        
        # 尝试相对路径
        if Path(path).exists():
            abs_path = Path(path).absolute()
            logger.info(f"🔍 找到数据库文件 {filename}: {abs_path}")
            return str(abs_path)
    
    # 如果没找到，返回传入的文件名（可能是相对路径）
    logger.warning(f"⚠️  未找到数据库文件 {filename}，将使用默认路径: {filename}")
    return filename

# 根据环境变量选择使用PostgreSQL还是SQLite
USE_POSTGRESQL = os.getenv("USE_POSTGRESQL", "true").lower() == "true"
logger.info(f"📊 数据库模式配置: USE_POSTGRESQL={USE_POSTGRESQL}, 环境变量值={os.getenv('USE_POSTGRESQL')}")

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
    DATABASE_URL_ENV = os.getenv("DATABASE_URL")
    if DATABASE_URL_ENV:
        DEFAULT_DATABASE_URL = DATABASE_URL_ENV
    else:
        # 直接使用绝对路径
        db_path = str(Path(__file__).parent.parent / "xbk.db")
        DEFAULT_DATABASE_URL = f"sqlite:///{db_path}"
        logger.info(f"🔧 设置默认数据库URL: {DEFAULT_DATABASE_URL}")
    
    # 智能体数据库URL - 用于AI智能体相关数据
    AI_DATABASE_URL_ENV = os.getenv("AI_DATABASE_URL")
    if AI_DATABASE_URL_ENV:
        AI_DATABASE_URL = AI_DATABASE_URL_ENV
    else:
        # 直接使用绝对路径
        db_path = str(Path(__file__).parent.parent / "znt.db")
        AI_DATABASE_URL = f"sqlite:///{db_path}"
        logger.info(f"🔧 设置AI数据库URL: {AI_DATABASE_URL}")
    
    def configure_sqlite_engine(url, engine_name="default"):
        """创建并配置SQLite引擎，启用WAL模式和连接池"""
        from sqlalchemy import create_engine, event
        from pathlib import Path
        import os
        
        if "sqlite" not in url:
            # 非SQLite数据库，使用默认配置
            return create_engine(url)
        
        # 如果是SQLite，确保使用绝对路径
        if url.startswith("sqlite:///"):
            # 提取路径部分
            db_path = url.replace("sqlite:///", "")
            
            # 使用智能查找函数获取数据库文件的绝对路径
            abs_path = find_database_file(db_path)
            # 确保是绝对路径
            abs_path = str(Path(abs_path).absolute())
            
            # 使用三个斜杠的格式（SQLAlchemy推荐）
            url = f"sqlite:///{abs_path}"
            logger.info(f"🔧 将SQLite路径转换为绝对路径: {abs_path}")
            
            # 删除可能存在的WAL文件以避免锁定问题
            wal_path = f"{abs_path}-wal"
            shm_path = f"{abs_path}-shm"
            journal_path = f"{abs_path}-journal"
            
            for lock_file in [wal_path, shm_path, journal_path]:
                if os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                        logger.info(f"🗑️  删除锁文件: {lock_file}")
                    except Exception as e:
                        logger.warning(f"⚠️  删除锁文件 {lock_file} 失败: {e}")
        
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
            # 直接使用智能查找函数获取数据库文件的绝对路径
            db_path_abs = find_database_file(db_name)
            # 确保是绝对路径
            db_path_abs = str(Path(db_path_abs).absolute())
            
            logger.info(f"🔧 优化数据库 {db_name}，绝对路径: {db_path_abs}")
            
            if Path(db_path_abs).exists():
                try:
                    conn = sqlite3.connect(db_path_abs)
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
                logger.info(f"ℹ️  数据库文件 {db_path_abs} 不存在，将在首次使用时创建并优化")

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