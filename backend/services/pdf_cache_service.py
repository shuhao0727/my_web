"""
PDF缓存服务 - 处理Typst文件编译为PDF的缓存功能
"""
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class PdfCacheService:
    """PDF缓存服务"""
    
    def __init__(self, repo_dir: Path):
        """
        初始化PDF缓存服务
        
        Args:
            repo_dir: 仓库目录的Path对象
        """
        self.repo_dir = repo_dir
        self.cache_dir = repo_dir / ".pdf_cache"
    
    def ensure_cache_directory(self):
        """确保缓存目录存在"""
        self.cache_dir.mkdir(exist_ok=True)
        return self.cache_dir
    
    def get_typst_files(self):
        """获取所有Typst文件"""
        try:
            if not self.repo_dir.exists():
                return []
            
            typst_files = []
            chapters_dir = self.repo_dir / "chapters"
            
            if chapters_dir.exists():
                for typ_file in chapters_dir.glob("**/*.typ"):
                    # 计算相对于仓库目录的路径
                    rel_path = typ_file.relative_to(self.repo_dir)
                    typst_files.append(str(rel_path))
            
            return typst_files
            
        except Exception as e:
            logger.error(f"获取Typst文件列表失败: {e}")
            return []
    
    def compile_to_pdf(self, relative_path: str):
        """将Typst文件编译为PDF"""
        try:
            source_path = self.repo_dir / relative_path
            
            if not source_path.exists():
                return {
                    "success": False,
                    "error": f"文件不存在: {relative_path}",
                }
            
            if source_path.suffix != ".typ":
                return {
                    "success": False,
                    "error": f"不是Typst文件: {relative_path}",
                }
            
            # 创建输出目录（如果不存在）
            self.ensure_cache_directory()
            
            # 生成输出文件名（使用相对路径的哈希或直接命名）
            path_hash = hashlib.md5(str(relative_path).encode()).hexdigest()[:8]
            output_filename = f"{source_path.stem}_{path_hash}.pdf"
            output_path = self.cache_dir / output_filename
            
            # 检查是否需要重新编译（如果PDF已存在且比源文件新，则跳过编译）
            if output_path.exists() and output_path.stat().st_mtime >= source_path.stat().st_mtime:
                logger.info(f"PDF已是最新，跳过编译: {relative_path}")
            else:
                # 编译Typst到PDF，添加--root参数以允许访问项目根目录
                logger.info(f"编译Typst到PDF: {relative_path}")
                cmd = [
                    "typst", "compile",
                    "--root", str(self.repo_dir),  # 设置项目根目录
                    str(source_path),
                    str(output_path)
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False,  # 不抛出异常，我们自己处理
                )
                
                if result.returncode != 0:
                    error_msg = f"编译失败: {result.stderr}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "details": result.stdout,
                    }
            
            # 读取PDF文件
            pdf_content = output_path.read_bytes()
            
            return {
                "success": True,
                "path": relative_path,
                "pdf_path": str(output_path),
                "pdf_filename": output_filename,
                "size": len(pdf_content),
                "content": pdf_content,  # 二进制内容
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = f"编译过程出错: {e.stderr}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "details": e.stdout,
            }
        except Exception as e:
            error_msg = f"编译PDF失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
            }
    
    def generate_all_pdf_cache(self):
        """为所有Typst文件生成PDF缓存"""
        try:
            if not self.repo_dir.exists():
                return {
                    "success": False,
                    "error": "仓库目录不存在",
                }
            
            # 获取所有Typst文件
            typst_files = self.get_typst_files()
            logger.info(f"找到 {len(typst_files)} 个Typst文件需要编译")
            
            # 创建PDF缓存目录
            self.ensure_cache_directory()
            
            results = {
                "total": len(typst_files),
                "success": 0,
                "failed": 0,
                "skipped": 0,
                "details": []
            }
            
            # 编译每个文件
            for rel_path in typst_files:
                try:
                    source_path = self.repo_dir / rel_path
                    path_hash = hashlib.md5(str(rel_path).encode()).hexdigest()[:8]
                    output_filename = f"{source_path.stem}_{path_hash}.pdf"
                    output_path = self.cache_dir / output_filename
                    
                    # 检查是否需要重新编译
                    if output_path.exists() and output_path.stat().st_mtime >= source_path.stat().st_mtime:
                        logger.info(f"PDF已是最新，跳过: {rel_path}")
                        results["skipped"] += 1
                        results["details"].append({
                            "file": rel_path,
                            "status": "skipped",
                            "reason": "PDF已是最新"
                        })
                        continue
                    
                    # 编译文件
                    logger.info(f"编译Typst到PDF: {rel_path}")
                    cmd = [
                        "typst", "compile",
                        "--root", str(self.repo_dir),
                        str(source_path),
                        str(output_path)
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    
                    if result.returncode == 0:
                        results["success"] += 1
                        results["details"].append({
                            "file": rel_path,
                            "status": "success",
                            "output_path": str(output_path.relative_to(self.repo_dir))
                        })
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "file": rel_path,
                            "status": "failed",
                            "error": result.stderr[:200] if result.stderr else "未知错误"
                        })
                        logger.error(f"编译失败 {rel_path}: {result.stderr}")
                        
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append({
                        "file": rel_path,
                        "status": "failed",
                        "error": str(e)[:200]
                    })
                    logger.error(f"处理文件 {rel_path} 时发生错误: {e}")
            
            logger.info(f"PDF缓存生成完成: 成功{results['success']}, 失败{results['failed']}, 跳过{results['skipped']}")
            
            return {
                "success": True,
                "message": f"PDF缓存生成完成: 成功{results['success']}, 失败{results['failed']}, 跳过{results['skipped']}",
                "results": results
            }
            
        except Exception as e:
            error_msg = f"生成PDF缓存失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
            }
    
    def get_pdf_cache_info(self):
        """获取PDF缓存信息"""
        try:
            if not self.repo_dir.exists():
                return {
                    "success": False,
                    "error": "仓库目录不存在",
                }
            
            if not self.cache_dir.exists():
                return {
                    "success": True,
                    "exists": False,
                    "count": 0,
                    "files": []
                }
            
            pdf_files = []
            total_size = 0
            
            for pdf_file in self.cache_dir.glob("*.pdf"):
                pdf_files.append({
                    "name": pdf_file.name,
                    "size": pdf_file.stat().st_size,
                    "modified": datetime.fromtimestamp(pdf_file.stat().st_mtime).isoformat()
                })
                total_size += pdf_file.stat().st_size
            
            return {
                "success": True,
                "exists": True,
                "count": len(pdf_files),
                "total_size": total_size,
                "files": pdf_files
            }
            
        except Exception as e:
            error_msg = f"获取PDF缓存信息失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
            }
    
    def get_static_pdf_url(self, relative_path: str):
        """获取静态PDF文件的URL路径"""
        try:
            source_path = self.repo_dir / relative_path
            
            if not source_path.exists() or source_path.suffix != ".typ":
                return None
            
            path_hash = hashlib.md5(str(relative_path).encode()).hexdigest()[:8]
            pdf_filename = f"{source_path.stem}_{path_hash}.pdf"
            
            # 返回相对于content目录的路径，便于前端直接访问
            return f"/content/{self.repo_dir.name}/.pdf_cache/{pdf_filename}"
            
        except Exception:
            return None
    
    def get_static_pdf_path(self, relative_path: str):
        """获取静态PDF文件的本地路径"""
        try:
            source_path = self.repo_dir / relative_path
            
            if not source_path.exists() or source_path.suffix != ".typ":
                return None
            
            path_hash = hashlib.md5(str(relative_path).encode()).hexdigest()[:8]
            pdf_filename = f"{source_path.stem}_{path_hash}.pdf"
            pdf_path = self.cache_dir / pdf_filename
            
            if pdf_path.exists():
                return str(pdf_path)
            else:
                return None
            
        except Exception:
            return None
