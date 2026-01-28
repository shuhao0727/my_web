"""
简化版数据库初始化脚本
明确在backend根目录下创建两个数据库：backend/xbk.db 和 backend/znt.db
"""
import os
import sqlite3
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import AiBase, ai_engine, XBK_DB_PATH, ZNT_DB_PATH, get_absolute_db_path
from models.ai_models import AiUser, AiAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        # 固定数据库路径（从config.database导入）
        self.xbk_db_path = XBK_DB_PATH
        self.znt_db_path = ZNT_DB_PATH
        
        # 管理员账户配置
        self.admin_config = {
            "admin_username": os.getenv("ADMIN_USERNAME", "admin"),
            "admin_password": os.getenv("ADMIN_PASSWORD", "admin123"),
            "wangshu_username": os.getenv("WANGSHU_USERNAME", "wangshu0727"),
            "wangshu_password": os.getenv("WANGSHU_PASSWORD", "wangshu123")
        }
        
        logger.info("数据库初始化器已创建")
        logger.info(f"XBK数据库路径: {self.xbk_db_path}")
        logger.info(f"ZNT数据库路径: {self.znt_db_path}")
    
    def init_xbk_database(self):
        """初始化XBK数据库（学校课程管理系统）"""
        # 使用绝对路径
        xbk_abs_path = get_absolute_db_path(self.xbk_db_path)
        logger.info(f"开始初始化XBK数据库: {xbk_abs_path}")
        
        # 确保目录存在
        Path(xbk_abs_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(xbk_abs_path)
        cursor = conn.cursor()
        
        try:
            # 1. 课程目录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS course_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    年份 INTEGER NOT NULL,
                    年级 TEXT NOT NULL,
                    课程代码 TEXT NOT NULL,
                    课程名称 TEXT NOT NULL,
                    课程负责人 TEXT,
                    各班限报人数 INTEGER,
                    上课地点 TEXT,
                    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    学年 TEXT DEFAULT '',
                    UNIQUE (年份, 年级, 课程代码)
                )
            ''')
            
            # 2. 学生信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    年份 INTEGER NOT NULL,
                    年级 TEXT NOT NULL,
                    班级 TEXT,
                    学号 TEXT NOT NULL,
                    姓名 TEXT NOT NULL,
                    性别 TEXT,
                    学年 TEXT DEFAULT '',
                    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (年份, 年级, 学号)
                )
            ''')
            
            # 3. 选课表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS course_selection (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    年份 INTEGER NOT NULL,
                    年级 TEXT NOT NULL,
                    班级 TEXT,
                    学号 TEXT NOT NULL,
                    姓名 TEXT,
                    课程代码 TEXT NOT NULL,
                    课程名称 TEXT,
                    学年 TEXT DEFAULT '',
                    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (年份, 年级, 学号, 课程代码),
                    FOREIGN KEY (年份, 年级, 学号) REFERENCES student_info(年份, 年级, 学号),
                    FOREIGN KEY (年份, 年级, 课程代码) REFERENCES course_catalog(年份, 年级, 课程代码)
                )
            ''')
            
            # 4. 合并数据表（用于查询和分析）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS merged_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    年份 INTEGER NOT NULL,
                    年级 TEXT NOT NULL,
                    班级 TEXT,
                    学号 TEXT NOT NULL,
                    姓名 TEXT,
                    课程代码 TEXT NOT NULL,
                    课程名称 TEXT,
                    课程负责人 TEXT,
                    各班限报人数 INTEGER,
                    上课地点 TEXT,
                    学年 TEXT DEFAULT '',
                    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (年份, 年级, 学号, 课程代码)
                )
            ''')
            
            # 5. 管理员表（XBK系统管理员）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # 6. 系统配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    config_key TEXT PRIMARY KEY,
                    config_value TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 7. 操作日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    action TEXT NOT NULL,
                    target TEXT,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 8. 登录表 (denglu) - 用于管理员登录验证
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS denglu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, student_id)
                )
            ''')
            
            # 插入登录表默认管理员账户 (name: admin, student_id: wangshu0727)
            cursor.execute(
                "INSERT OR IGNORE INTO denglu (name, student_id) VALUES (?, ?)",
                ("admin", "wangshu0727")
            )
            
            # 插入默认管理员账户（注意：移除了email字段）
            cursor.execute(
                "INSERT OR IGNORE INTO admins (username, password_hash, role) VALUES (?, ?, ?)",
                (self.admin_config["admin_username"], 
                 self.admin_config["admin_password"], 
                 "super_admin")
            )
            
            cursor.execute(
                "INSERT OR IGNORE INTO admins (username, password_hash, role) VALUES (?, ?, ?)",
                (self.admin_config["wangshu_username"], 
                 self.admin_config["wangshu_password"], 
                 "admin")
            )
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_course_catalog_year_grade ON course_catalog(年份, 年级)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_info_year_grade_class ON student_info(年份, 年级, 班级)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_course_selection_student ON course_selection(年份, 年级, 学号)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_merged_data_all ON merged_data(年份, 年级, 班级, 学号)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_operation_logs_created ON operation_logs(created_at)')
            
            # 插入默认系统配置
            default_configs = [
                ("current_year", "2024", "当前年份"),
                ("current_grade", "高一", "当前年级"),
                ("auto_sync_interval", "86400", "自动同步间隔（秒）"),
                ("max_upload_size", "10485760", "最大上传文件大小（10MB）"),
                ("backup_enabled", "true", "是否启用自动备份"),
                ("backup_interval", "86400", "备份间隔（秒）"),
                ("site_name", "MyWeb学习平台", "网站名称"),
                ("site_description", "个人学习与知识管理平台", "网站描述"),
                ("contact_email", "admin@myweb.com", "联系邮箱"),
                ("default_timezone", "Asia/Shanghai", "默认时区"),
            ]
            
            for key, value, description in default_configs:
                cursor.execute(
                    "INSERT OR REPLACE INTO system_config (config_key, config_value, description) VALUES (?, ?, ?)",
                    (key, value, description)
                )
            
            conn.commit()
            logger.info("✅ XBK数据库初始化完成")
            
            # 验证表创建
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            logger.info(f"XBK数据库表 ({len(tables)}个): {[table[0] for table in tables]}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ XBK数据库初始化失败: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def init_znt_database(self):
        """初始化ZNT数据库（AI智能体系统）"""
        # 使用绝对路径
        znt_abs_path = get_absolute_db_path(self.znt_db_path)
        logger.info(f"开始初始化ZNT数据库: {znt_abs_path}")
        
        try:
            # 确保目录存在
            Path(znt_abs_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 创建数据库引擎
            engine = create_engine(
                f"sqlite:///{znt_abs_path}",
                connect_args={"check_same_thread": False}
            )
            
            # 创建所有表（基于SQLAlchemy模型）
            AiBase.metadata.create_all(bind=engine)
            logger.info("✅ ZNT数据库表结构创建完成")
            
            # 插入默认数据
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            try:
                # 插入默认AI用户（管理员账户）
                admin_user = db.query(AiUser).filter_by(username="admin").first()
                if not admin_user:
                    admin_user = AiUser(
                        username="admin",
                        password_hash=self.admin_config["admin_password"],
                        student_id="wangshu0727",
                        class_name="管理员"
                    )
                    db.add(admin_user)
                    logger.info("✅ 创建默认AI用户: admin")
                
                wangshu_user = db.query(AiUser).filter_by(username="wangshu0727").first()
                if not wangshu_user:
                    wangshu_user = AiUser(
                        username="wangshu0727",
                        password_hash=self.admin_config["wangshu_password"],
                        student_id="000001",
                        class_name="管理员"
                    )
                    db.add(wangshu_user)
                    logger.info("✅ 创建默认AI用户: wangshu0727")
                
                # 插入默认AI智能体
                default_agent = db.query(AiAgent).filter_by(name="默认智能体").first()
                if not default_agent:
                    default_agent = AiAgent(
                        name="默认智能体",
                        api_type="dify",
                        is_active=True
                    )
                    db.add(default_agent)
                    logger.info("✅ 创建默认AI智能体")
                
                # 插入Dify智能体（如果配置了API密钥）
                dify_api_key = os.getenv("DIFY_API_KEY")
                dify_app_id = os.getenv("DIFY_APP_ID")
                if dify_api_key and dify_app_id:
                    dify_agent = db.query(AiAgent).filter_by(name="Dify智能体").first()
                    if not dify_agent:
                        dify_agent = AiAgent(
                            name="Dify智能体",
                            api_type="dify",
                            api_key=dify_api_key,
                            app_id=dify_app_id,
                            is_active=True
                        )
                        db.add(dify_agent)
                        logger.info("✅ 创建Dify智能体")
                
                # 插入DeepSeek智能体（如果配置了API密钥）
                deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
                if deepseek_api_key:
                    deepseek_agent = db.query(AiAgent).filter_by(name="DeepSeek智能体").first()
                    if not deepseek_agent:
                        deepseek_agent = AiAgent(
                            name="DeepSeek智能体",
                            api_type="deepseek",
                            api_key=deepseek_api_key,
                            model="deepseek-chat",
                            is_active=True
                        )
                        db.add(deepseek_agent)
                        logger.info("✅ 创建DeepSeek智能体")
                
                db.commit()
                logger.info("✅ ZNT数据库默认数据插入完成")
                
                # 验证表创建
                from sqlalchemy import inspect
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                logger.info(f"ZNT数据库表 ({len(tables)}个): {tables}")
                
            except Exception as e:
                db.rollback()
                logger.error(f"❌ ZNT数据库数据插入失败: {e}", exc_info=True)
                raise
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ ZNT数据库初始化失败: {e}", exc_info=True)
            raise
    
    def verify_databases(self):
        """验证数据库完整性"""
        logger.info("开始验证数据库完整性...")
        
        results = {
            "xbk": {"success": False, "tables": [], "error": None},
            "znt": {"success": False, "tables": [], "error": None}
        }
        
        try:
            # 验证XBK数据库
            xbk_abs_path = get_absolute_db_path(self.xbk_db_path)
            if Path(xbk_abs_path).exists():
                conn_xbk = sqlite3.connect(xbk_abs_path)
                cursor_xbk = conn_xbk.cursor()
                cursor_xbk.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                xbk_tables = [table[0] for table in cursor_xbk.fetchall()]
                conn_xbk.close()
                
                required_xbk_tables = {
                    "course_catalog", "student_info", "course_selection", 
                    "merged_data", "admins", "system_config", "operation_logs", "denglu"
                }
                
                missing_xbk_tables = required_xbk_tables - set(xbk_tables)
                
                results["xbk"]["tables"] = xbk_tables
                results["xbk"]["success"] = len(missing_xbk_tables) == 0
                results["xbk"]["missing"] = list(missing_xbk_tables)
                
                logger.info(f"XBK数据库表: {xbk_tables}")
                if missing_xbk_tables:
                    logger.warning(f"XBK数据库缺少表: {missing_xbk_tables}")
                else:
                    logger.info("✅ XBK数据库完整性验证通过")
            else:
                results["xbk"]["error"] = "数据库文件不存在"
                logger.warning("⚠️ XBK数据库文件不存在")
        
        except Exception as e:
            results["xbk"]["error"] = str(e)
            logger.error(f"❌ XBK数据库验证失败: {e}")
        
        try:
            # 验证ZNT数据库
            znt_abs_path = get_absolute_db_path(self.znt_db_path)
            if Path(znt_abs_path).exists():
                from sqlalchemy import create_engine, inspect
                engine = create_engine(f"sqlite:///{znt_abs_path}")
                inspector = inspect(engine)
                znt_tables = inspector.get_table_names()
                engine.dispose()
                
                required_znt_tables = {"ai_users", "ai_agents", "ai_conversations", "ai_messages"}
                missing_znt_tables = required_znt_tables - set(znt_tables)
                
                results["znt"]["tables"] = znt_tables
                results["znt"]["success"] = len(missing_znt_tables) == 0
                results["znt"]["missing"] = list(missing_znt_tables)
                
                logger.info(f"ZNT数据库表: {znt_tables}")
                if missing_znt_tables:
                    logger.warning(f"ZNT数据库缺少表: {missing_znt_tables}")
                else:
                    logger.info("✅ ZNT数据库完整性验证通过")
            else:
                results["znt"]["error"] = "数据库文件不存在"
                logger.warning("⚠️ ZNT数据库文件不存在")
                
        except Exception as e:
            results["znt"]["error"] = str(e)
            logger.error(f"❌ ZNT数据库验证失败: {e}")
        
        # 总体验证结果
        overall_success = results["xbk"]["success"] and results["znt"]["success"]
        
        if overall_success:
            logger.info("🎉 数据库完整性验证全部通过")
        else:
            logger.warning("⚠️ 数据库完整性验证未通过")
        
        return overall_success, results
    
    def backup_databases(self, backup_dir="./backups"):
        """备份数据库"""
        logger.info(f"开始备份数据库到: {backup_dir}")
        
        import shutil
        from datetime import datetime
        
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 备份XBK数据库
            xbk_abs_path = get_absolute_db_path(self.xbk_db_path)
            if Path(xbk_abs_path).exists():
                xbk_backup_path = Path(backup_dir) / f"xbk_db_backup_{timestamp}.db"
                shutil.copy2(xbk_abs_path, xbk_backup_path)
                logger.info(f"✅ XBK数据库备份完成: {xbk_backup_path}")
            else:
                logger.warning("⚠️ XBK数据库文件不存在，跳过备份")
            
            # 备份ZNT数据库
            znt_abs_path = get_absolute_db_path(self.znt_db_path)
            if Path(znt_abs_path).exists():
                znt_backup_path = Path(backup_dir) / f"znt_db_backup_{timestamp}.db"
                shutil.copy2(znt_abs_path, znt_backup_path)
                logger.info(f"✅ ZNT数据库备份完成: {znt_backup_path}")
            else:
                logger.warning("⚠️ ZNT数据库文件不存在，跳过备份")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库备份失败: {e}", exc_info=True)
            return False
    
    def run(self, force_reinit=False):
        """运行数据库初始化"""
        logger.info("=" * 50)
        logger.info("开始数据库初始化流程")
        logger.info("=" * 50)
        
        # 检查是否需要重新初始化
        need_init = force_reinit
        
        if not force_reinit:
            # 检查数据库文件是否存在
            xbk_exists = Path(self.xbk_db_path).exists()
            znt_exists = Path(self.znt_db_path).exists()
            
            if not xbk_exists or not znt_exists:
                need_init = True
                logger.info("检测到数据库文件不存在，需要初始化")
            else:
                # 验证现有数据库
                success, _ = self.verify_databases()
                if not success:
                    need_init = True
                    logger.info("数据库完整性验证失败，需要重新初始化")
        
        if need_init:
            # 备份现有数据库（如果存在）
            if Path(self.xbk_db_path).exists() or Path(self.znt_db_path).exists():
                logger.info("备份现有数据库...")
                self.backup_databases()
            
            # 初始化数据库
            try:
                self.init_xbk_database()
                self.init_znt_database()
                
                # 验证初始化结果
                success, results = self.verify_databases()
                if success:
                    logger.info("=" * 50)
                    logger.info("🎉 数据库初始化成功完成")
                    logger.info("=" * 50)
                    return True
                else:
                    logger.error("❌ 数据库初始化后验证失败")
                    logger.error(f"详细结果: {results}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ 数据库初始化过程失败: {e}", exc_info=True)
                return False
        else:
            logger.info("✅ 数据库已存在且完整，跳过初始化")
            return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MyWeb项目数据库初始化工具")
    parser.add_argument("--force", action="store_true", help="强制重新初始化数据库")
    parser.add_argument("--backup", action="store_true", help="备份数据库")
    parser.add_argument("--verify", action="store_true", help="仅验证数据库")
    parser.add_argument("--backup-dir", default="./backups", help="备份目录路径")
    
    args = parser.parse_args()
    
    initializer = DatabaseInitializer()
    
    if args.backup:
        # 仅备份
        success = initializer.backup_databases(args.backup_dir)
        exit(0 if success else 1)
    elif args.verify:
        # 仅验证
        success, results = initializer.verify_databases()
        if success:
            print("✅ 数据库完整性验证通过")
        else:
            print("❌ 数据库完整性验证失败")
            print(f"详细结果: {results}")
        exit(0 if success else 1)
    else:
        # 初始化（可选择强制）
        success = initializer.run(force_reinit=args.force)
        exit(0 if success else 1)


if __name__ == "__main__":
    main()