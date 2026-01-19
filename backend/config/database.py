"""
数据库配置和基类
支持多数据库：默认数据库和智能体数据库（znt）
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 默认数据库URL - 用于用户、文档等
DEFAULT_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./my_web.db")

# 智能体数据库URL - 用于AI智能体相关数据
AI_DATABASE_URL = os.getenv("AI_DATABASE_URL", "sqlite:///./znt.db")

# 创建默认数据库引擎
default_engine = create_engine(
    DEFAULT_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DEFAULT_DATABASE_URL else {}
)

# 创建智能体数据库引擎
ai_engine = create_engine(
    AI_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in AI_DATABASE_URL else {}
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
