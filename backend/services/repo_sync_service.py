"""
GitHub仓库同步服务 - 直接将整个仓库克隆/更新到本地目录
"""
import os
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import requests
import hashlib
import glob

logger = logging.getLogger(__name__)

class GitHubRepoSyncService:
    """GitHub仓库同步服务"""
    
    def __init__(self):
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "shuhao0727")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "2-My-notes")
        self.branch = os.getenv("GITHUB_REPO_BRANCH", "main")
        self.repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}.git"
        
        # 本地存储路径 - 从环境变量获取，默认为./content
        content_dir = os.getenv("CONTENT_DIR", "./content")
        self.base_dir = Path(content_dir)
        self.repo_dir = self.base_dir / self.repo_name
        
        # GitHub token
        self.token = os.getenv("GITHUB_ACCESS_TOKEN")
        
        # 设置带token的URL
        if self.token:
            self.auth_repo_url = f"https://{self.token}@github.com/{self.repo_owner}/{self.repo_name}.git"
        else:
            self.auth_repo_url = self.repo_url
            logger.warning("未设置GITHUB_ACCESS_TOKEN，使用公开方式访问仓库")
        
        # 令牌过期状态（默认为False，通过同步操作更新）
        self.token_expired = False
    
    def ensure_base_directory(self):
        """确保基础目录存在"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        return str(self.base_dir)
    
    def get_repo_status(self):
        """获取仓库状态（不检查远程仓库，只返回本地状态和缓存的令牌状态）"""
        try:
            if not self.repo_dir.exists():
                return {
                    "exists": False,
                    "status": "not_cloned",
                    "last_updated": None,
                    "branch": None,
                    "commit": None,
                    "token_expired": self.token_expired,
                }
            
            # 检查是否为git仓库
            if not (self.repo_dir / ".git").exists():
                return {
                    "exists": True,
                    "status": "not_git_repo",
                    "last_updated": datetime.fromtimestamp(self.repo_dir.stat().st_mtime).isoformat(),
                    "branch": None,
                    "commit": None,
                    "token_expired": self.token_expired,
                }
            
            # 获取git信息
            git_info = self.get_git_info()
            
            status_info = {
                "exists": True,
                "status": "cloned",
                "last_updated": datetime.fromtimestamp(self.repo_dir.stat().st_mtime).isoformat(),
                "branch": git_info.get("branch"),
                "commit": git_info.get("commit"),
                "commit_message": git_info.get("commit_message"),
                "commit_date": git_info.get("commit_date"),
                "token_expired": self.token_expired,
            }
            
            return status_info
            
        except Exception as e:
            logger.error(f"获取仓库状态失败: {e}")
            return {
                "exists": False,
                "status": "error",
                "error": str(e),
                "token_expired": self.token_expired,
            }
    
    def get_git_info(self):
        """获取git仓库信息"""
        try:
            # 获取当前分支
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            branch = result.stdout.strip()
            
            # 获取最新提交
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%s|%cd", "--date=iso"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            
            commit_info = result.stdout.strip().split("|")
            if len(commit_info) >= 3:
                commit_hash = commit_info[0][:8]  # 取前8位
                commit_message = commit_info[1]
                commit_date = commit_info[2]
            else:
                commit_hash = commit_info[0][:8] if commit_info else "unknown"
                commit_message = "unknown"
                commit_date = "unknown"
            
            return {
                "branch": branch,
                "commit": commit_hash,
                "commit_message": commit_message,
                "commit_date": commit_date,
            }
            
        except Exception as e:
            logger.error(f"获取git信息失败: {e}")
            return {"branch": "unknown", "commit": "unknown"}
    
    def clone_repository(self):
        """克隆仓库到本地"""
        try:
            # 确保目录存在
            self.ensure_base_directory()
            
            # 如果目录已存在，先删除
            if self.repo_dir.exists():
                logger.info(f"删除现有目录: {self.repo_dir}")
                shutil.rmtree(self.repo_dir)
            
            logger.info(f"开始克隆仓库: {self.repo_url}")
            
            # 使用token进行克隆
            clone_url = self.auth_repo_url
            
            # 执行git clone
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", self.branch, clone_url, str(self.repo_dir)],
                capture_output=True,
                text=True,
                check=True,
            )
            
            logger.info(f"仓库克隆成功: {self.repo_dir}")
            
            # 克隆成功，重置令牌过期状态
            self.token_expired = False
            
            return {
                "success": True,
                "message": "仓库克隆成功",
                "path": str(self.repo_dir),
                "branch": self.branch,
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = f"克隆仓库失败: {e.stderr}"
            logger.error(error_msg)
            
            # 检查是否认证失败
            if "Authentication failed" in e.stderr or "could not read Username" in e.stderr:
                self.token_expired = True
                error_msg = "GitHub token expired or invalid. Please update your access token."
            
            return {
                "success": False,
                "error": error_msg,
                "details": f"返回码: {e.returncode}",
            }
        except Exception as e:
            error_msg = f"克隆仓库时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
            }
    
    def pull_updates(self):
        """拉取最新更新"""
        try:
            if not self.repo_dir.exists():
                return {
                    "success": False,
                    "error": "仓库目录不存在，请先克隆仓库",
                }
            
            logger.info(f"开始拉取更新: {self.repo_dir}")
            
            # 获取当前状态
            before_info = self.get_git_info()
            
            # 执行git pull
            result = subprocess.run(
                ["git", "pull", "origin", self.branch],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            
            # 获取更新后状态
            after_info = self.get_git_info()
            
            logger.info(f"更新拉取成功: {result.stdout}")
            
            # 拉取成功，重置令牌过期状态
            self.token_expired = False
            
            return {
                "success": True,
                "message": "更新拉取成功",
                "output": result.stdout,
                "before": before_info,
                "after": after_info,
                "updated": before_info["commit"] != after_info["commit"],
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = f"拉取更新失败: {e.stderr}"
            logger.error(error_msg)
            
            # 检查是否认证失败
            if "Authentication failed" in e.stderr or "could not read Username" in e.stderr:
                self.token_expired = True
                error_msg = "GitHub token expired or invalid. Please update your access token."
            
            return {
                "success": False,
                "error": error_msg,
                "details": f"返回码: {e.returncode}",
            }
        except Exception as e:
            error_msg = f"拉取更新时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
            }
    
    def sync_repository(self, force_clone=False):
        """同步仓库（自动判断是否需要克隆或拉取）"""
        try:
            status = self.get_repo_status()
            
            if not status["exists"] or status["status"] != "cloned" or force_clone:
                # 需要克隆
                logger.info("仓库不存在或状态异常，执行克隆操作")
                result = self.clone_repository()
            else:
                # 尝试拉取更新
                logger.info("仓库已存在，执行拉取更新")
                result = self.pull_updates()
            
            return result
                
        except Exception as e:
            error_msg = f"同步仓库失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
            }
    
    def list_files(self, relative_path=""):
        """列出指定路径下的文件和目录"""
        try:
            if not self.repo_dir.exists():
                return {
                    "success": False,
                    "error": "仓库目录不存在",
                    "files": [],
                }
            
            target_dir = self.repo_dir / relative_path
            
            if not target_dir.exists():
                return {
                    "success": False,
                    "error": f"路径不存在: {relative_path}",
                    "files": [],
                }
            
            files = []
            for item in target_dir.iterdir():
                # 跳过.git目录
                if item.name == ".git":
                    continue
                
                is_dir = item.is_dir()
                files.append({
                    "name": item.name,
                    "type": "directory" if is_dir else "file",
                    "path": str(item.relative_to(self.repo_dir)),
                    "size": item.stat().st_size if not is_dir else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    "extension": item.suffix if not is_dir else "",
                })
            
            # 按类型和名称排序
            files.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
            
            return {
                "success": True,
                "path": relative_path,
                "files": files,
                "count": len(files),
            }
            
        except Exception as e:
            error_msg = f"列出文件失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "files": [],
            }
    
    def get_file_content(self, relative_path):
        """获取文件内容"""
        # 在外部定义file_path，以便在except块中访问
        file_path = None
        try:
            if not self.repo_dir.exists():
                return {
                    "success": False,
                    "error": "仓库目录不存在",
                }
            
            file_path = self.repo_dir / relative_path
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"文件不存在: {relative_path}",
                }
            
            if file_path.is_dir():
                return {
                    "success": False,
                    "error": f"指定路径是目录，不是文件: {relative_path}",
                }
            
            # 读取文件内容
            content = file_path.read_text(encoding="utf-8")
            
            return {
                "success": True,
                "path": relative_path,
                "content": content,
                "size": len(content),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            }
            
        except UnicodeDecodeError:
            # 可能是二进制文件
            if file_path is None:
                return {
                    "success": False,
                    "error": "文件路径无效",
                }
            try:
                content = file_path.read_bytes()
                return {
                    "success": True,
                    "path": relative_path,
                    "content": "",  # 二进制文件不返回内容
                    "size": len(content),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "is_binary": True,
                    "binary_size": len(content),
                }
            except Exception as e:
                error_msg = f"读取二进制文件失败: {str(e)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                }
        except Exception as e:
            error_msg = f"读取文件失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
            }
    
    def get_repo_structure(self):
        """获取仓库结构概览"""
        try:
            if not self.repo_dir.exists():
                return {
                    "success": False,
                    "error": "仓库目录不存在",
                    "structure": {},
                }
            
            structure = {
                "chapters": {
                    "exists": (self.repo_dir / "chapters").exists(),
                    "count": len(list((self.repo_dir / "chapters").glob("**/*.typ"))) if (self.repo_dir / "chapters").exists() else 0,
                },
                "style": {
                    "exists": (self.repo_dir / "style").exists(),
                    "files": [f.name for f in (self.repo_dir / "style").iterdir()] if (self.repo_dir / "style").exists() else [],
                },
                "image": {
                    "exists": (self.repo_dir / "image").exists(),
                    "count": len(list((self.repo_dir / "image").iterdir())) if (self.repo_dir / "image").exists() else 0,
                },
                "main_typ": {
                    "exists": (self.repo_dir / "main.typ").exists(),
                    "size": (self.repo_dir / "main.typ").stat().st_size if (self.repo_dir / "main.typ").exists() else 0,
                },
            }
            
            return {
                "success": True,
                "structure": structure,
                "repo_path": str(self.repo_dir),
            }
            
        except Exception as e:
            error_msg = f"获取仓库结构失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "structure": {},
            }

# 创建全局服务实例
repo_sync_service = GitHubRepoSyncService()

if __name__ == "__main__":
    # 测试代码
    service = GitHubRepoSyncService()
    
    print("仓库状态:", service.get_repo_status())
    
    # 同步仓库
    result = service.sync_repository()
    print("同步结果:", result)
    
    if result.get("success"):
        print("仓库结构:", service.get_repo_structure())
        print("文件列表:", service.list_files(""))
