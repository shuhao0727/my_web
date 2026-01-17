"""
GitHub仓库自动同步调度器
"""
import os
import logging
import threading
import time
import schedule
from datetime import datetime

from services.repo_sync_service import repo_sync_service

logger = logging.getLogger(__name__)

class RepoSyncScheduler:
    """仓库同步调度器"""
    
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        # 不在初始化时读取环境变量，在start方法中读取以确保最新配置
        
    def _load_config(self):
        """加载配置（从环境变量）"""
        self.enable_auto_sync = os.getenv("ENABLE_AUTO_SYNC", "True").lower() == "true"
        self.sync_interval = int(os.getenv("SYNC_INTERVAL_SECONDS", "21600"))  # 默认6小时
        logger.info(f"自动同步配置: enable={self.enable_auto_sync}, interval={self.sync_interval}s")
    
    def sync_job(self):
        """同步任务"""
        try:
            logger.info(f"开始定时同步任务: {datetime.now().isoformat()}")
            result = repo_sync_service.sync_repository()
            
            if result.get("success"):
                logger.info(f"定时同步成功: {result.get('message', '')}")
                
                if result.get("updated", False):
                    logger.info(f"检测到更新: {result.get('before', {}).get('commit')} -> {result.get('after', {}).get('commit')}")
                else:
                    logger.info("没有新内容需要更新")
            else:
                logger.error(f"定时同步失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"定时同步任务执行异常: {e}")
    
    def start(self):
        """启动调度器"""
        # 启动时加载最新配置
        self._load_config()
        
        if not self.enable_auto_sync:
            logger.info("自动同步已禁用，跳过调度器启动")
            return False
        
        if self.is_running:
            logger.warning("调度器已经在运行中")
            return True
        
        try:
            # 清除所有现有的定时任务
            schedule.clear()
            
            # 设置新的定时任务（使用当前配置的间隔）
            schedule.every(self.sync_interval).seconds.do(self.sync_job)
            
            # 立即执行一次
            logger.info("启动时立即执行一次同步")
            self.sync_job()
            
            # 启动调度器线程
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            self.is_running = True
            logger.info(f"仓库同步调度器已启动，每{self.sync_interval}秒执行一次")
            return True
            
        except Exception as e:
            logger.error(f"启动调度器失败: {e}")
            return False
    
    def _run_scheduler(self):
        """运行调度器的主循环"""
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except Exception as e:
            logger.error(f"调度器运行异常: {e}")
            self.is_running = False
    
    def stop(self):
        """停止调度器"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("仓库同步调度器已停止")
    
    def get_status(self):
        """获取调度器状态"""
        # 确保配置已加载
        if not hasattr(self, 'enable_auto_sync') or not hasattr(self, 'sync_interval'):
            self._load_config()
            
        return {
            "enabled": self.enable_auto_sync,
            "running": self.is_running,
            "interval_seconds": self.sync_interval,
            "interval_hours": round(self.sync_interval / 3600, 2),
            "next_jobs": len(schedule.jobs),
            "description": f"每{self.sync_interval}秒执行一次同步",
        }

# 创建全局调度器实例
repo_sync_scheduler = RepoSyncScheduler()

if __name__ == "__main__":
    # 测试代码
    import sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    scheduler = RepoSyncScheduler()
    print("调度器状态:", scheduler.get_status())
    
    if scheduler.enable_auto_sync:
        print("启动调度器...")
        scheduler.start()
        print("调度器已启动，等待10秒...")
        time.sleep(10)
        print("当前状态:", scheduler.get_status())
        print("停止调度器...")
        scheduler.stop()
    else:
        print("自动同步已禁用")
