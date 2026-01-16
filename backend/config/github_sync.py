"""
GitHub同步配置和工具
"""
import os
import requests
import base64
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """同步状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class GitHubSyncConfig:
    """GitHub同步配置"""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_ACCESS_TOKEN")
        self.owner = os.getenv("GITHUB_REPO_OWNER", "shuhao0727")
        self.repo = os.getenv("GITHUB_REPO_NAME", "2-My-notes")
        self.branch = os.getenv("GITHUB_REPO_BRANCH", "main")
        self.base_path = os.getenv("GITHUB_REPO_PATH", "")
        
        # 验证配置
        if not self.token:
            logger.warning("GITHUB_ACCESS_TOKEN未设置，GitHub同步功能将不可用")
        
        # GitHub API基础URL
        self.api_base = "https://api.github.com"
        
    def get_headers(self) -> Dict[str, str]:
        """获取GitHub API请求头"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    def is_configured(self) -> bool:
        """检查配置是否完整"""
        return bool(self.token)


class GitHubClient:
    """GitHub API客户端"""
    
    def __init__(self, config: GitHubSyncConfig):
        self.config = config
        self.headers = config.get_headers()
        
    def get_repository_info(self) -> Optional[Dict]:
        """获取仓库信息"""
        url = f"{self.config.api_base}/repos/{self.config.owner}/{self.config.repo}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"获取仓库信息失败: {e}")
            return None
    
    def get_file_tree(self, path: str = "") -> List[Dict[str, Any]]:
        """获取指定路径下的文件树"""
        url = f"{self.config.api_base}/repos/{self.config.owner}/{self.config.repo}/contents/{path}"
        params = {"ref": self.config.branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            items = response.json()
            
            # 如果是文件，返回空列表（应该递归处理目录）
            if isinstance(items, dict) and items.get("type") == "file":
                return []
                
            # 确保返回的是列表
            if isinstance(items, list):
                return items
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"获取文件树失败 ({path}): {e}")
            return []
    
    def get_typst_files(self, path: str = "") -> List[Dict]:
        """递归获取所有Typst文件"""
        typst_files = []
        items = self.get_file_tree(path)
        
        for item in items:
            if item["type"] == "dir":
                # 递归处理子目录
                sub_files = self.get_typst_files(item["path"])
                typst_files.extend(sub_files)
            elif item["type"] == "file" and item["name"].endswith(".typ"):
                # 添加Typst文件
                typst_files.append(item)
        
        return typst_files
    
    def get_file_content(self, path: str) -> Optional[Tuple[str, str]]:
        """获取文件内容，返回(content, sha)"""
        url = f"{self.config.api_base}/repos/{self.config.owner}/{self.config.repo}/contents/{path}"
        params = {"ref": self.config.branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            file_data = response.json()
            
            if file_data.get("encoding") == "base64":
                content = base64.b64decode(file_data["content"]).decode("utf-8")
                sha = file_data.get("sha", "")
                return content, sha
            else:
                logger.warning(f"未知的编码格式: {file_data.get('encoding')}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"获取文件内容失败 ({path}): {e}")
            return None
    
    def get_last_commit(self, path: str = "") -> Optional[Dict]:
        """获取指定路径的最后提交信息"""
        url = f"{self.config.api_base}/repos/{self.config.owner}/{self.config.repo}/commits"
        params = {
            "path": path,
            "sha": self.config.branch,
            "per_page": 1
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            commits = response.json()
            return commits[0] if commits else None
        except requests.exceptions.RequestException as e:
            logger.error(f"获取提交信息失败 ({path}): {e}")
            return None


class TypstParser:
    """Typst文件解析器"""
    
    @staticmethod
    def parse_title(content: str) -> str:
        """从Typst内容中提取标题"""
        # 查找第一个#开头的行作为标题
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line.startswith('='):
                # 可能是Typst的标题语法
                import re
                match = re.match(r'^=+\s+(.+)$', line)
                if match:
                    return match.group(1).strip()
        return "未命名文档"
    
    @staticmethod
    def parse_chapters(content: str) -> List[Dict]:
        """解析章节结构"""
        chapters = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            # 检测章节标题（支持#、##、###等）
            if line.startswith('## '):
                level = 2
                title = line[3:].strip()
            elif line.startswith('### '):
                level = 3
                title = line[4:].strip()
            elif line.startswith('#### '):
                level = 4
                title = line[5:].strip()
            else:
                continue
                
            if title:
                chapters.append({
                    "title": title,
                    "level": level,
                    "order_index": len(chapters),
                    "line_number": i
                })
        
        return chapters
    
    @staticmethod
    def extract_description(content: str) -> str:
        """提取文档描述（第一段非标题文本）"""
        lines = content.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # 找到第一个非空非标题行
            description_lines.append(line)
            if len(description_lines) >= 3:  # 取前三行作为描述
                break
        
        return ' '.join(description_lines)[:200]  # 限制长度


def create_sync_summary(files: List[Dict]) -> Dict:
    """创建同步摘要"""
    categories = {
        "算法": ["算法", "动态规划", "贪心", "搜索"],
        "数据结构": ["数据结构", "树", "图", "队列", "栈"],
        "图论": ["图论", "图", "网络流", "最短路径"],
        "数学": ["数学", "数论", "组合", "概率"],
        "基础": ["基础", "入门", "教程"],
    }
    
    summary = {
        "total_files": len(files),
        "categories": {},
        "difficulty_stats": {
            "简单": 0,
            "中等": 0,
            "困难": 0
        }
    }
    
    for file in files:
        # 根据路径和名称判断分类
        path = file.get("path", "").lower()
        name = file.get("name", "").lower()
        
        # 检测难度
        if any(word in path or word in name for word in ["基础", "入门", "简单", "easy"]):
            difficulty = "简单"
        elif any(word in path or word in name for word in ["中等", "中级", "medium", "进阶"]):
            difficulty = "中等"
        elif any(word in path or word in name for word in ["困难", "高级", "hard", "竞赛"]):
            difficulty = "困难"
        else:
            difficulty = "中等"  # 默认
        
        summary["difficulty_stats"][difficulty] += 1
        
        # 检测分类
        assigned = False
        for category, keywords in categories.items():
            if any(keyword in path or keyword in name for keyword in keywords):
                summary["categories"][category] = summary["categories"].get(category, 0) + 1
                assigned = True
                break
        
        if not assigned:
            summary["categories"]["其他"] = summary["categories"].get("其他", 0) + 1
    
    return summary


# 全局配置实例
github_config = GitHubSyncConfig()
github_client = GitHubClient(github_config)
