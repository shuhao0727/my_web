"""
数据库配置和基类
支持多数据库：默认数据库和智能体数据库（znt）
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from typing import Optional
import logging

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.default_database_url = os.getenv("DATABASE_URL", "sqlite:///./xbk.db")
        self.ai_database_url = os.getenv("AI_DATABASE_URL", "sqlite:///./znt.db")
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        self.pool_overflow = int(os.getenv("DB_POOL_OVERFLOW", "10"))
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"
        
    def get_engine_kwargs(self, database_url: str) -> dict:
        """获取数据库引擎配置参数"""
        kwargs = {
            "pool_pre_ping": True,  # 连接池预检查
            "pool_recycle": 3600,   # 连接回收时间
            "echo": self.echo,
        }
        
        if "sqlite" in database_url:
            kwargs.update({
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": 30,
                }
            })
        else:
            # 其他数据库的连接池配置
            kwargs.update({
                "pool_size": self.pool_size,
                "max_overflow": self.pool_overflow,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            })
        
        return kwargs

# 初始化配置
db_config = DatabaseConfig()

# 创建默认数据库引擎
default_engine = create_engine(
    db_config.default_database_url,
    **db_config.get_engine_kwargs(db_config.default_database_url)
)

# 创建智能体数据库引擎
ai_engine = create_engine(
    db_config.ai_database_url,
    **db_config.get_engine_kwargs(db_config.ai_database_url)
)

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

def test_connections():
    """测试数据库连接"""
    try:
        # 测试默认数据库连接
        with default_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logging.info("✅ 默认数据库连接正常")
    except Exception as e:
        logging.error(f"❌ 默认数据库连接失败: {e}")
        raise
    
    try:
        # 测试AI数据库连接
        with ai_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logging.info("✅ AI数据库连接正常")
    except Exception as e:
        logging.error(f"❌ AI数据库连接失败: {e}")
        raise

if __name__ == "__main__":
    test_connections()
