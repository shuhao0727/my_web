"""
静态文件缓存中间件
为静态文件添加适当的缓存头，支持文件版本控制和缓存策略
"""
import os
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)

class StaticCacheMiddleware(BaseHTTPMiddleware):
    """静态文件缓存中间件
    
    为静态文件添加缓存头，支持不同类型的缓存策略：
    1. 长期缓存：CSS、JS、图片等静态资源（内容变化时通过版本控制失效）
    2. 短期缓存：HTML、API响应等动态内容
    3. 禁止缓存：敏感数据、实时数据
    """
    
    def __init__(
        self,
        app: ASGIApp,
        static_path: str = "/content",
        enable_gzip: bool = True,
        enable_brotli: bool = False,
        cache_control_enabled: bool = True,
    ):
        super().__init__(app)
        self.static_path = static_path
        self.enable_gzip = enable_gzip
        self.enable_brotli = enable_brotli
        self.cache_control_enabled = cache_control_enabled
        
        # 文件扩展名对应的缓存策略
        self.cache_strategies = {
            # 长期缓存（1年）：内容变化时通过版本控制失效
            "long_term": {
                "extensions": ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', 
                               '.woff', '.woff2', '.ttf', '.eot', '.ico', '.webp', '.avif'],
                "max_age": 31536000,  # 1年
                "stale_while_revalidate": 86400,  # 24小时
                "cache_control": "public, immutable, max-age=31536000, stale-while-revalidate=86400",
            },
            # 中期缓存（1小时）：可能变化的静态内容
            "medium_term": {
                "extensions": ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
                "max_age": 3600,  # 1小时
                "cache_control": "public, max-age=3600",
            },
            # 短期缓存（5分钟）：动态生成的内容
            "short_term": {
                "extensions": ['.html', '.htm', '.json', '.xml'],
                "max_age": 300,  # 5分钟
                "cache_control": "public, max-age=300",
            },
            # 不缓存：API响应、敏感数据
            "no_cache": {
                "extensions": [],
                "cache_control": "no-cache, no-store, must-revalidate",
            }
        }
        
        # 构建扩展名到策略的快速查找表
        self.extension_to_strategy: Dict[str, str] = {}
        for strategy_name, strategy in self.cache_strategies.items():
            for ext in strategy["extensions"]:
                self.extension_to_strategy[ext] = strategy_name
    
    async def dispatch(self, request: Request, call_next):
        # 获取响应
        response = await call_next(request)
        
        # 只处理静态文件路径
        if not request.url.path.startswith(self.static_path):
            return response
        
        # 获取文件扩展名
        file_path = request.url.path
        file_ext = Path(file_path).suffix.lower()
        
        # 确定缓存策略
        strategy_name = self.extension_to_strategy.get(file_ext, "short_term")
        strategy = self.cache_strategies[strategy_name]
        
        # 如果是长期缓存策略，尝试添加ETag
        if strategy_name == "long_term" and self._is_static_file(file_path):
            etag = await self._generate_etag(file_path, request)
            if etag:
                response.headers["ETag"] = etag
        
        # 添加缓存控制头
        if self.cache_control_enabled and "cache_control" in strategy:
            response.headers["Cache-Control"] = strategy["cache_control"]
        
        # 添加过期头
        if "max_age" in strategy:
            from datetime import datetime, timedelta
            expires = datetime.utcnow() + timedelta(seconds=strategy["max_age"])
            response.headers["Expires"] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # 添加Vary头以支持内容协商
        vary_headers = []
        if self.enable_gzip:
            vary_headers.append("Accept-Encoding")
        if vary_headers:
            response.headers["Vary"] = ", ".join(vary_headers)
        
        # 添加X-Static-Cache头用于调试
        response.headers["X-Static-Cache-Strategy"] = strategy_name
        
        logger.debug(f"静态文件缓存: {file_path} -> {strategy_name}")
        return response
    
    def _is_static_file(self, file_path: str) -> bool:
        """检查是否是真实的静态文件（不是目录）"""
        # 这里简化处理，实际应该检查文件系统
        # 在实际应用中，应该检查文件是否存在且不是目录
        return True
    
    async def _generate_etag(self, file_path: str, request: Request) -> Optional[str]:
        """为静态文件生成ETag
        
        ETag基于文件内容和路径生成，支持弱验证和强验证
        """
        try:
            # 在实际应用中，这里应该读取文件内容生成哈希
            # 这里简化处理，使用路径和虚拟内容
            content_path = file_path.replace(self.static_path, "", 1).lstrip("/")
            
            # 尝试从环境变量获取内容目录
            content_dir = os.getenv("CONTENT_DIR", "./content")
            full_path = os.path.join(content_dir, content_path)
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                # 获取文件修改时间和大小
                stat = os.stat(full_path)
                file_info = f"{full_path}:{stat.st_mtime}:{stat.st_size}"
                # 生成弱ETag（以W/开头）
                weak_etag = hashlib.md5(file_info.encode()).hexdigest()
                return f'W/"{weak_etag}"'
            
            # 如果文件不存在，返回基于路径的ETag
            path_hash = hashlib.md5(file_path.encode()).hexdigest()
            return f'W/"{path_hash}"'
            
        except Exception as e:
            logger.debug(f"生成ETag失败: {e}")
            return None


def setup_static_cache(app, **kwargs):
    """设置静态文件缓存中间件"""
    app.add_middleware(StaticCacheMiddleware, **kwargs)
    logger.info("✅ 静态文件缓存中间件已设置")


# 文件版本控制工具
class FileVersioning:
    """文件版本控制工具类
    
    为静态资源添加版本哈希，支持缓存失效
    """
    
    @staticmethod
    def add_version_to_filename(filename: str, content_hash: Optional[str] = None) -> str:
        """为文件名添加版本哈希
        
        Args:
            filename: 原始文件名，如 "style.css"
            content_hash: 内容哈希，如果为None则自动生成
            
        Returns:
            带版本的文件名，如 "style.abc123.css"
        """
        path = Path(filename)
        
        # 如果没有提供哈希，生成一个简单的哈希
        if content_hash is None:
            import random
            import string
            content_hash = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        # 插入哈希到文件名中
        stem = path.stem
        suffix = path.suffix
        
        if stem and suffix:
            return f"{stem}.{content_hash}{suffix}"
        elif suffix:
            return f"{content_hash}{suffix}"
        else:
            return f"{content_hash}"
    
    @staticmethod
    def generate_content_hash(content: bytes) -> str:
        """生成内容哈希"""
        return hashlib.md5(content).hexdigest()[:8]
    
    @staticmethod
    def strip_version_from_filename(filename: str) -> str:
        """从文件名中移除版本哈希
        
        Args:
            filename: 带版本的文件名，如 "style.abc123.css"
            
        Returns:
            原始文件名，如 "style.css"
        """
        path = Path(filename)
        stem = path.stem
        suffix = path.suffix
        
        # 查找最后一个点作为哈希分隔符
        if '.' in stem:
            # 移除哈希部分（最后一个点之前的所有内容？实际上我们需要保留第一个点之前的内容）
            # 例如: "style.abc123" -> 我们想要 "style"
            parts = stem.split('.')
            if len(parts) > 1:
                # 假设格式是 "name.hash"
                original_stem = parts[0]
                return f"{original_stem}{suffix}"
        
        return filename


# 图片优化相关工具（占位符，实际实现需要Pillow等库）
class ImageOptimizer:
    """图片优化工具类（概念性实现）"""
    
    @staticmethod
    def optimize_image(input_path: str, output_path: Optional[str] = None, **kwargs) -> bool:
        """优化图片
        
        实际实现需要Pillow库支持
        """
        logger.info(f"图片优化功能需要Pillow库: {input_path}")
        # 这里只是占位符，实际实现需要安装Pillow
        return False
    
    @staticmethod
    def convert_to_webp(input_path: str, output_path: Optional[str] = None, quality: int = 80) -> bool:
        """转换为WebP格式
        
        实际实现需要Pillow库支持
        """
        logger.info(f"WebP转换功能需要Pillow库: {input_path}")
        return False


# 压缩工具
class CompressionUtils:
    """压缩工具类"""
    
    @staticmethod
    def should_compress_file(filepath: str) -> bool:
        """检查文件是否应该压缩"""
        compressible_extensions = {'.css', '.js', '.html', '.htm', '.txt', '.json', '.xml', '.svg'}
        return Path(filepath).suffix.lower() in compressible_extensions
    
    @staticmethod
    def get_compression_headers(enable_gzip: bool = True, enable_brotli: bool = False) -> Dict[str, str]:
        """获取压缩相关的HTTP头"""
        headers = {}
        
        if enable_gzip:
            headers["Content-Encoding"] = "gzip"
        elif enable_brotli:
            headers["Content-Encoding"] = "br"
        
        return headers