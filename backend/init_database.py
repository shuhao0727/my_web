"""
数据库初始化脚本
在容器启动时运行，用于创建必要的数据库表和默认数据
"""
import os
import sys
import sqlite3
import bcrypt
import hashlib
from pathlib import Path

def hash_password(password: str) -> str:
    """使用bcrypt哈希密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def init_ai_database(db_path: str):
    """初始化AI智能体数据库 (znt.db)"""
    print(f"初始化AI数据库: {db_path}")
    
    # 确保目录存在
    db_dir = os.path.dirname(db_path)
    if db_dir:
        Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建ai_users表（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            student_id TEXT UNIQUE,
            class_name TEXT
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_ai_users_username ON ai_users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_ai_users_student_id ON ai_users(student_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_ai_users_class_name ON ai_users(class_name)")
    
    # 创建ai_agents表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            api_type TEXT NOT NULL,
            api_key TEXT,
            base_url TEXT,
            model TEXT,
            app_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建ai_conversations表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            agent_id INTEGER NOT NULL,
            session_id TEXT UNIQUE,
            title TEXT,
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            total_messages INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            conversation_metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES ai_users(id),
            FOREIGN KEY (agent_id) REFERENCES ai_agents(id)
        )
    """)
    
    # 创建ai_messages表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            tokens INTEGER,
            message_metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id)
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_ai_conversations_user_agent 
        ON ai_conversations(user_id, agent_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_ai_messages_conversation_created 
        ON ai_messages(conversation_id, created_at)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_ai_agents_active 
        ON ai_agents(is_active)
    """)
    
    # 检查默认管理员用户是否存在
    cursor.execute("SELECT COUNT(*) FROM ai_users WHERE username = 'admin'")
    admin_exists = cursor.fetchone()[0] > 0
    
    if not admin_exists:
        print("创建默认管理员用户: admin / wangshu0727")
        
        # 使用学号后6位作为默认密码
        student_id = "wangshu0727"
        default_password = student_id[-6:] if len(student_id) >= 6 else student_id
        password_hash = hash_password(default_password)
        
        cursor.execute("""
            INSERT INTO ai_users (username, password_hash, student_id, class_name)
            VALUES (?, ?, ?, ?)
        """, ("admin", password_hash, student_id, "管理员"))
        
        print(f"管理员账户已创建 - 用户名: admin, 学号: {student_id}")
        print(f"默认密码: {default_password} (学号后6位)")
    else:
        print("管理员用户已存在")
    
    conn.commit()
    conn.close()
    print(f"AI数据库初始化完成: {db_path}")

def init_myweb_database(db_path: str):
    """初始化主数据库 (my_web.db)"""
    print(f"初始化主数据库: {db_path}")
    
    # 确保目录存在
    db_dir = os.path.dirname(db_path)
    if db_dir:
        Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 这里可以根据需要添加my_web.db的初始化逻辑
    # 目前该数据库可能已经有表结构，我们只确保文件存在
    
    conn.close()
    print(f"主数据库初始化完成: {db_path}")

def init_xbk_database(db_path: str):
    """初始化XBK数据库 (xbk.db)"""
    print(f"初始化XBK数据库: {db_path}")
    
    # 确保目录存在
    db_dir = os.path.dirname(db_path)
    if db_dir:
        Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建denglu表（用于管理员登录）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS denglu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT NOT NULL
        )
    """)
    
    # 检查默认管理员是否已存在
    cursor.execute("SELECT COUNT(*) FROM denglu WHERE name = 'admin' AND student_id = 'wangshu0727'")
    admin_exists = cursor.fetchone()[0] > 0
    
    if not admin_exists:
        cursor.execute("""
            INSERT INTO denglu (name, student_id)
            VALUES (?, ?)
        """, ("admin", "wangshu0727"))
        print("XBK数据库管理员记录已添加: admin / wangshu0727")
    else:
        print("XBK数据库管理员记录已存在")
    
    # 其他表由应用程序在需要时创建
    # 这里只确保文件存在和基本表结构
    
    conn.commit()
    conn.close()
    print(f"XBK数据库初始化完成: {db_path}")

def main():
    """主初始化函数"""
    print("开始初始化数据库...")
    
    # 从环境变量获取数据库路径
    data_dir = os.getenv("DATA_DIR", "/app/data")
    
    # 创建数据目录
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    # 初始化各个数据库
    ai_db_path = os.getenv("AI_DATABASE_URL", f"sqlite:///{data_dir}/znt.db").replace("sqlite:///", "")
    myweb_db_path = os.getenv("DATABASE_URL", f"sqlite:///{data_dir}/my_web.db").replace("sqlite:///", "")
    xbk_db_path = os.getenv("XBK_DATABASE_URL", f"sqlite:///{data_dir}/xbk.db").replace("sqlite:///", "")
    
    # 处理可能的sqlite://前缀
    if ai_db_path.startswith("sqlite://"):
        ai_db_path = ai_db_path.replace("sqlite://", "")
    if myweb_db_path.startswith("sqlite://"):
        myweb_db_path = myweb_db_path.replace("sqlite://", "")
    if xbk_db_path.startswith("sqlite://"):
        xbk_db_path = xbk_db_path.replace("sqlite://", "")
    
    # 初始化数据库
    init_myweb_database(myweb_db_path)
    init_ai_database(ai_db_path)
    init_xbk_database(xbk_db_path)
    
    print("所有数据库初始化完成！")

if __name__ == "__main__":
    main()