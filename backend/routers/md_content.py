"""
Markdown内容API路由
提供Markdown文件内容、文件树结构等API
"""
import os
from pathlib import Path
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import markdown

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/md")

def get_content_dir() -> Path:
    """获取内容目录路径"""
    content_dir = os.getenv("CONTENT_DIR", "./content")
    return Path(content_dir)

def get_articles_dir() -> Path:
    """获取文章目录路径"""
    return get_content_dir() / "wz"

@router.get("/articles/tree")
async def get_articles_tree(path: str = Query("")):
    """获取文章文件树结构
    
    Args:
        path: 相对路径，默认为根目录
    """
    try:
        articles_dir = get_articles_dir()
        target_dir = articles_dir / path if path else articles_dir
        
        if not target_dir.exists():
            raise HTTPException(status_code=404, detail=f"路径不存在: {path}")
        
        if not target_dir.is_dir():
            raise HTTPException(status_code=400, detail=f"路径不是目录: {path}")
        
        # 排除的目录和文件
        exclude_names = {".git", "__pycache__", ".DS_Store", "node_modules"}
        
        files = []
        for item in target_dir.iterdir():
            if item.name in exclude_names:
                continue
                
            is_dir = item.is_dir()
            
            # 如果是目录，直接添加
            if is_dir:
                # 计算相对于articles_dir的完整路径
                full_relative_path = item.relative_to(articles_dir)
                path_str = str(full_relative_path).replace("\\", "/")  # 统一路径分隔符
                
                file_info = {
                    "name": item.name,
                    "path": path_str,
                    "type": "directory",
                    "size": 0,  # 目录大小通常为0
                    "extension": "",
                    "is_markdown": False,
                }
                files.append(file_info)
            # 如果是文件，检查是否为允许的类型
            elif item.name.endswith(".md") or item.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".txt", ".doc", ".docx"}:
                # 计算文件相对于articles_dir的完整路径
                full_relative_path = item.relative_to(articles_dir)
                file_path_str = str(full_relative_path).replace("\\", "/")
                
                file_info = {
                    "name": item.name,
                    "path": file_path_str,
                    "type": "file",
                    "size": item.stat().st_size,
                    "extension": item.suffix,
                    "is_markdown": item.suffix.lower() == ".md",
                }
                files.append(file_info)
        
        # 排序：目录在前，文件在后，按名称排序
        files.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        return {
            "success": True,
            "path": path,  # 这里应该返回用户传入的path参数
            "files": files,
            "count": len(files),
            "articles_path": str(articles_dir),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章文件树失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文章文件树失败: {str(e)}")

@router.get("/articles/content/{filepath:path}")
async def get_article_content(filepath: str):
    """获取Markdown文件内容
    
    Args:
        filepath: 文件相对路径，如 "article1.md"
    """
    try:
        articles_dir = get_articles_dir()
        file_path = articles_dir / filepath
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在: {filepath}")
        
        if file_path.is_dir():
            raise HTTPException(status_code=400, detail=f"路径是目录，不是文件: {filepath}")
        
        # 检查文件扩展名
        if file_path.suffix.lower() != ".md":
            # 如果是图片文件，返回二进制信息
            if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"}:
                return {
                    "success": True,
                    "path": filepath,
                    "type": "binary",
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix,
                }
            # 其他文件类型
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_path.suffix}")
        
        # 读取Markdown文件内容
        content = file_path.read_text(encoding="utf-8")
        
        # 转换为HTML（可选，如果前端需要预渲染的HTML）
        try:
            html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        except:
            html_content = content
        
        return {
            "success": True,
            "path": filepath,
            "content": content,
            "html_content": html_content,
            "size": len(content),
            "encoding": "utf-8",
        }
        
    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="文件编码不是UTF-8")
    except Exception as e:
        logger.error(f"读取文章内容失败: {e}")
        raise HTTPException(status_code=500, detail=f"读取文章内容失败: {str(e)}")

@router.get("/articles/structure")
async def get_articles_structure():
    """获取文章仓库的整体结构"""
    try:
        articles_dir = get_articles_dir()
        
        if not articles_dir.exists():
            raise HTTPException(status_code=404, detail="文章目录不存在")
        
        # 计算总的Markdown文件数量
        total_md_files = len(list(articles_dir.glob("**/*.md")))
        
        structure = {
            "categories": {
                "exists": articles_dir.is_dir(),
                "count": total_md_files,
                "subdirectories": [d.name for d in articles_dir.iterdir() if d.is_dir()],
            },
            "markdown_files": {
                "total": total_md_files,
                "files": [str(f.relative_to(articles_dir)) for f in articles_dir.glob("*.md")] + 
                        [str(f.relative_to(articles_dir)) for f in articles_dir.glob("**/*.md") if f.parent != articles_dir],
            },
        }
        
        # 获取所有子目录和文件分类
        categories = []
        for item in articles_dir.iterdir():
            if item.is_dir():
                dir_md_files = list(item.glob("**/*.md"))  # 包括子目录中的文件
                category_info = {
                    "name": item.name,
                    "file_count": len(dir_md_files),
                    "files": [str(f.relative_to(item)) for f in dir_md_files],
                }
                categories.append(category_info)
        
        structure["categories"]["category_list"] = categories
        
        return {
            "success": True,
            "structure": structure,
            "articles_path": str(articles_dir),
        }
        
    except Exception as e:
        logger.error(f"获取文章结构失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文章结构失败: {str(e)}")

@router.get("/articles/search")
async def search_articles(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    file_ext: Optional[str] = Query(".md", description="文件扩展名过滤")
):
    """搜索文章文件
    
    Args:
        query: 搜索关键词
        file_ext: 文件扩展名，默认为.md
    """
    try:
        articles_dir = get_articles_dir()
        
        if not articles_dir.exists():
            raise HTTPException(status_code=404, detail="文章目录不存在")
        
        results = []
        search_pattern = f"**/*{file_ext}"
        
        for file_path in articles_dir.glob(search_pattern):
            # 跳过不需要的目录
            if any(exclude in str(file_path) for exclude in [".git", "__pycache__", "node_modules"]):
                continue
                
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if query.lower() in content.lower():
                    results.append({
                        "path": str(file_path.relative_to(articles_dir)),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "match_count": content.lower().count(query.lower()),
                    })
            except:
                continue
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
        }
        
    except Exception as e:
        logger.error(f"搜索文章失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索文章失败: {str(e)}")

@router.get("/articles/health")
async def articles_health_check():
    """文章API健康检查"""
    try:
        articles_dir = get_articles_dir()
        exists = articles_dir.exists()
        
        return {
            "status": "healthy" if exists else "warning",
            "articles_exist": exists,
            "articles_path": str(articles_dir),
            "message": "文章API服务正常" if exists else "文章目录不存在",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }

if __name__ == "__main__":
    # 测试代码
    import asyncio
    
    async def test():
        print("测试文章API路由...")
        
        # 测试获取结构
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        
        client = TestClient(app)
        
        response = client.get("/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
        
        response = client.get("/tree")
        print(f"文件树: {response.status_code} - {response.json()}")
    
    asyncio.run(test())