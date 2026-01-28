"""
预启动检查与初始化脚本
在main.py启动前执行，确保系统所需的基础设施就绪
功能：
1. 检查并初始化数据库（xbk.db, znt.db）
2. 检查并创建content目录结构
3. 检查并同步GitHub笔记仓库
"""
import os
import sys
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pre_startup.log")
    ]
)
logger = logging.getLogger(__name__)

class PreStartupInitializer:
    """预启动初始化器"""
    
    def __init__(self):
        # 获取项目根目录
        self.project_root = Path(__file__).parent.parent
        self.backend_root = Path(__file__).parent
        
        logger.info("=" * 50)
        logger.info("MyWeb预启动初始化开始")
        logger.info("=" * 50)
        logger.info(f"项目根目录: {self.project_root}")
        logger.info(f"后端根目录: {self.backend_root}")
        
        # 加载环境变量
        self.load_environment_variables()
        
        # 数据库路径（相对于项目根目录）
        self.xbk_db_path = self.project_root / "backend" / "xbk.db"
        self.znt_db_path = self.project_root / "backend" / "znt.db"
        logger.info(f"XBK数据库路径: {self.xbk_db_path}")
        logger.info(f"ZNT数据库路径: {self.znt_db_path}")
        
        # content目录路径
        self.content_dir = self.backend_root / "content"
        self.wz_dir = self.content_dir / "wz"
        self.notes_dir = self.content_dir / "2-My-notes"
        
        logger.info(f"Content目录: {self.content_dir}")
        logger.info(f"WZ文章目录: {self.wz_dir}")
        logger.info(f"笔记目录: {self.notes_dir}")
    
    def load_environment_variables(self):
        """加载环境变量"""
        # 从多个位置加载.env文件
        env_paths = [
            self.project_root / ".env",
            self.backend_root / ".env",
        ]
        
        env_loaded = False
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"✅ 环境变量已加载: {env_path}")
                env_loaded = True
                break
        
        if not env_loaded:
            logger.warning("⚠️  环境变量文件未找到，使用默认值")
    
    def check_and_init_databases(self):
        """检查并初始化数据库"""
        logger.info("=" * 30)
        logger.info("检查数据库...")
        logger.info("=" * 30)
        
        # 检查数据库文件是否存在
        xbk_exists = self.xbk_db_path.exists()
        znt_exists = self.znt_db_path.exists()
        
        logger.info(f"XBK数据库 {'已存在' if xbk_exists else '不存在'}: {self.xbk_db_path}")
        logger.info(f"ZNT数据库 {'已存在' if znt_exists else '不存在'}: {self.znt_db_path}")
        
        if xbk_exists and znt_exists:
            logger.info("✅ 数据库文件已存在，跳过初始化")
            return True
        
        # 需要初始化数据库
        logger.info("⚠️  检测到数据库文件不存在，开始初始化...")
        
        try:
            # 导入数据库初始化器
            sys.path.insert(0, str(self.backend_root))
            from init_databases import DatabaseInitializer
            
            # 创建数据库初始化器并运行
            db_initializer = DatabaseInitializer()
            success = db_initializer.run(force_reinit=False)
            
            if success:
                logger.info("✅ 数据库初始化成功完成")
            else:
                logger.error("❌ 数据库初始化失败")
            
            return success
            
        except ImportError as e:
            logger.error(f"❌ 导入数据库初始化模块失败: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 数据库初始化过程异常: {e}", exc_info=True)
            return False
    
    def check_and_create_content_directories(self):
        """检查并创建content目录结构"""
        logger.info("=" * 30)
        logger.info("检查content目录结构...")
        logger.info("=" * 30)
        
        try:
            # 1. 确保content目录存在
            self.content_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Content目录已确保: {self.content_dir}")
            
            # 2. 检查并创建wz目录
            if not self.wz_dir.exists():
                self.wz_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ WZ目录已创建: {self.wz_dir}")
                
                # 创建示例MD文档
                sample_md_path = self.wz_dir / "欢迎来到MyWeb.md"
                sample_content = """# 欢迎来到MyWeb

## 关于这个网站

这是一个个人网站项目，主要功能包括：

### 1. AI智能体实验室
- 集成Dify AI平台
- 智能对话功能
- 多AI模型支持

### 2. 信息学竞赛资源
- 算法学习笔记
- 竞赛题目解析
- 训练计划制定

### 3. 信息技术教学
- 教学博客分享
- 教学资源整理
- 课堂实践案例

### 4. 个人程序系统
- 学校课程管理系统
- 数据处理工具
- 自动化脚本

### 5. 文章博客系统
- 技术文章发布
- 学习笔记分享
- 项目经验总结

## 使用说明

1. **AI智能体**：点击首页的AI智能体卡片，体验智能对话功能
2. **竞赛资源**：查看信息学竞赛相关的学习资料和题目
3. **个人程序**：使用学校课程管理系统等实用工具
4. **文章博客**：阅读最新的技术文章和学习笔记

## 技术栈

- **前端**：Next.js + React + TypeScript + Ant Design
- **后端**：FastAPI + Python + SQLite/PostgreSQL
- **部署**：Docker + Docker Compose
- **数据库**：SQLite（开发）/ PostgreSQL（生产）

## 开发说明

这个网站是开源的，代码托管在GitHub上。如果您对项目感兴趣，欢迎贡献代码或提出建议。

---
*最后更新：2024年1月*
*作者：Shuhao Wang*
"""
                
                sample_md_path.write_text(sample_content, encoding="utf-8")
                logger.info(f"✅ 示例MD文档已创建: {sample_md_path}")
            else:
                logger.info(f"✅ WZ目录已存在: {self.wz_dir}")
            
            # 3. 检查并创建2-My-notes目录
            if not self.notes_dir.exists():
                self.notes_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ 2-My-notes目录已创建: {self.notes_dir}")
            
            # 检查2-My-notes目录是否为空
            notes_empty = True
            if self.notes_dir.exists():
                items = list(self.notes_dir.iterdir())
                # 排除隐藏文件和.git目录
                visible_items = [item for item in items if not item.name.startswith('.')]
                notes_empty = len(visible_items) == 0
                
                if not notes_empty:
                    logger.info(f"✅ 2-My-notes目录非空，包含 {len(visible_items)} 个项目")
                else:
                    logger.info(f"⚠️  2-My-notes目录为空")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建content目录结构失败: {e}", exc_info=True)
            return False
    
    def sync_github_notes(self, notes_empty):
        """同步GitHub笔记仓库"""
        logger.info("=" * 30)
        logger.info("检查GitHub笔记同步...")
        logger.info("=" * 30)
        
        # 检查是否需要同步：目录为空或者需要强制同步
        if not notes_empty:
            logger.info("✅ 2-My-notes目录非空，跳过GitHub同步")
            return True
        
        # 检查GitHub配置
        github_token = os.getenv("GITHUB_ACCESS_TOKEN")
        github_repo_owner = os.getenv("GITHUB_REPO_OWNER", "shuhao0727")
        github_repo_name = os.getenv("GITHUB_REPO_NAME", "2-My-notes")
        github_branch = os.getenv("GITHUB_REPO_BRANCH", "main")
        
        if not github_token:
            logger.warning("⚠️  未设置GITHUB_ACCESS_TOKEN，跳过GitHub同步")
            logger.info("ℹ️  请在.env文件中设置GITHUB_ACCESS_TOKEN以启用笔记同步")
            return False
        
        logger.info(f"GitHub仓库: {github_repo_owner}/{github_repo_name}@{github_branch}")
        
        # 临时设置CONTENT_DIR环境变量，确保GitHub同步服务使用正确的本地路径
        original_content_dir = os.getenv("CONTENT_DIR")
        os.environ["CONTENT_DIR"] = str(self.content_dir)
        logger.info(f"✅ 设置CONTENT_DIR环境变量为本地路径: {self.content_dir}")
        
        try:
            # 导入GitHub同步服务
            sys.path.insert(0, str(self.backend_root))
            from services.repo_sync_service import GitHubRepoSyncService
            
            # 创建同步服务实例
            sync_service = GitHubRepoSyncService()
            
            # 检查仓库状态
            repo_status = sync_service.get_repo_status()
            logger.info(f"GitHub仓库状态: {repo_status.get('status')}")
            
            # 执行同步
            if repo_status.get("exists") and repo_status.get("status") == "cloned":
                logger.info("✅ GitHub仓库已克隆，执行更新")
                result = sync_service.pull_updates()
            else:
                logger.info("⚠️  GitHub仓库未克隆或状态异常，执行克隆")
                result = sync_service.clone_repository()
            
            if result.get("success"):
                logger.info(f"✅ GitHub同步成功: {result.get('message')}")
                
                # 验证同步结果
                if self.notes_dir.exists():
                    items = list(self.notes_dir.iterdir())
                    visible_items = [item for item in items if not item.name.startswith('.')]
                    
                    if len(visible_items) > 0:
                        logger.info(f"✅ 同步完成，目录中现在有 {len(visible_items)} 个项目")
                        for item in visible_items[:5]:  # 只显示前5个项目
                            logger.info(f"   - {item.name}")
                        if len(visible_items) > 5:
                            logger.info(f"   ... 还有 {len(visible_items) - 5} 个项目")
                    else:
                        logger.warning("⚠️  同步完成但目录仍然为空")
                
                return True
            else:
                error_msg = result.get("error", "未知错误")
                logger.error(f"❌ GitHub同步失败: {error_msg}")
                
                # 检查是否是token过期
                if "Authentication failed" in error_msg or "token expired" in error_msg.lower():
                    logger.error("❌ GitHub token可能已过期，请在.env文件中更新GITHUB_ACCESS_TOKEN")
                
                return False
                
        except ImportError as e:
            logger.error(f"❌ 导入GitHub同步模块失败: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ GitHub同步过程异常: {e}", exc_info=True)
            return False
    
    def run_initialization(self):
        """运行完整的初始化流程"""
        logger.info("=" * 50)
        logger.info("开始执行预启动初始化流程")
        logger.info("=" * 50)
        
        start_time = time.time()
        results = {
            "databases": False,
            "directories": False,
            "github_sync": False,
        }
        
        try:
            # 1. 检查并初始化数据库
            results["databases"] = self.check_and_init_databases()
            
            # 2. 检查并创建目录结构
            results["directories"] = self.check_and_create_content_directories()
            
            # 3. 检查2-My-notes目录是否为空
            notes_empty = True
            if self.notes_dir.exists():
                items = list(self.notes_dir.iterdir())
                visible_items = [item for item in items if not item.name.startswith('.')]
                notes_empty = len(visible_items) == 0
            
            # 4. 如果需要，同步GitHub笔记
            if notes_empty:
                results["github_sync"] = self.sync_github_notes(notes_empty)
            else:
                results["github_sync"] = True  # 目录非空，视为同步成功
            
            # 汇总结果
            elapsed_time = time.time() - start_time
            
            logger.info("=" * 50)
            logger.info("预启动初始化完成")
            logger.info("=" * 50)
            
            for step, success in results.items():
                status = "✅ 成功" if success else "❌ 失败"
                logger.info(f"{step}: {status}")
            
            logger.info(f"总耗时: {elapsed_time:.2f}秒")
            
            # 判断整体成功
            all_success = all(results.values())
            if all_success:
                logger.info("🎉 所有预启动检查通过，系统准备就绪")
            else:
                logger.warning("⚠️  部分预启动检查失败，系统可能无法正常工作")
                # 输出失败的步骤
                failed_steps = [step for step, success in results.items() if not success]
                logger.warning(f"失败的步骤: {', '.join(failed_steps)}")
            
            return all_success
            
        except Exception as e:
            logger.error(f"❌ 预启动初始化流程异常: {e}", exc_info=True)
            return False


def main():
    """主函数，用于命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MyWeb预启动初始化工具")
    parser.add_argument("--force", action="store_true", help="强制重新初始化所有组件")
    parser.add_argument("--skip-github", action="store_true", help="跳过GitHub同步")
    parser.add_argument("--skip-db", action="store_true", help="跳过数据库初始化")
    
    args = parser.parse_args()
    
    initializer = PreStartupInitializer()
    
    if args.force:
        logger.info("⚠️  强制模式：将重新初始化所有组件")
    
    success = initializer.run_initialization()
    
    if success:
        print("✅ 预启动初始化成功完成")
        sys.exit(0)
    else:
        print("❌ 预启动初始化失败")
        sys.exit(1)


if __name__ == "__main__":
    main()