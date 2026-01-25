"""
文章板块API路由
提供文章列表、文章内容、文章目录等接口
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import markdown
from markdown.extensions.toc import TocExtension
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
articles_router = APIRouter(prefix="/api/articles", tags=["articles"])

# 文章目录路径
ARTICLES_DIR = Path(__file__).parent.parent / "content" / "wz"

# 确保文章目录存在
ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

def get_article_files() -> List[Path]:
    """获取所有markdown文章文件"""
    if not ARTICLES_DIR.exists():
        return []
    
    # 支持.md和.markdown扩展名
    md_files = list(ARTICLES_DIR.glob("*.md")) + list(ARTICLES_DIR.glob("*.markdown"))
    # 按修改时间倒序排序（最新的在前面）
    md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return md_files

def extract_metadata(content: str) -> Dict[str, str]:
    """从markdown内容中提取元数据（如标题、日期等）"""
    metadata = {}
    
    # 尝试解析YAML front matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = parts[1]
            # 简单的键值对解析（支持title, date, tags等）
            for line in front_matter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    if key and value:
                        metadata[key] = value
    
    # 如果没有front matter，尝试从内容中提取标题
    if 'title' not in metadata:
        # 查找第一个一级标题
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            metadata['title'] = match.group(1).strip()
        else:
            # 使用文件名作为标题
            metadata['title'] = ""
    
    return metadata

def extract_toc(content: str) -> List[Dict[str, str]]:
    """从markdown内容中提取目录（标题结构）"""
    toc = []
    
    # 正则匹配所有标题（从##到######，避免匹配#开头的其他内容）
    # 只匹配行首的标题
    pattern = r'^(#{2,6})\s+(.+)$'
    
    lines = content.split('\n')
    for line in lines:
        match = re.match(pattern, line)
        if match:
            level = len(match.group(1))  # 标题级别（2-6）
            title = match.group(2).strip()
            
            # 生成锚点ID（移除特殊字符，用-连接）
            anchor = re.sub(r'[^\w\s-]', '', title.lower())
            anchor = re.sub(r'[-\s]+', '-', anchor).strip('-')
            
            toc.append({
                "level": level,
                "title": title,
                "anchor": anchor
            })
    
    return toc

@articles_router.get("/list")
async def get_article_list() -> List[Dict[str, str]]:
    """获取文章列表"""
    try:
        articles = []
        md_files = get_article_files()
        
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                metadata = extract_metadata(content)
                
                # 使用文件名作为slug（不带扩展名）
                slug = file_path.stem
                
                # 如果没有提取到标题，使用文件名
                title = metadata.get('title') or slug
                
                # 获取文件修改时间作为日期
                stat = file_path.stat()
                import datetime
                date = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
                
                # 生成简短描述（取前100个字符）
                description = ""
                # 移除front matter和代码块
                content_without_frontmatter = content
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        content_without_frontmatter = parts[2]
                
                # 取纯文本的前100个字符
                plain_text = re.sub(r'```.*?```', '', content_without_frontmatter, flags=re.DOTALL)
                plain_text = re.sub(r'`.*?`', '', plain_text)
                plain_text = re.sub(r'[#*\-_\[\]!]', '', plain_text)
                description = plain_text.strip()[:100] + "..." if len(plain_text) > 100 else plain_text.strip()
                
                articles.append({
                    "slug": slug,
                    "title": title,
                    "date": date,
                    "description": description,
                    "file_name": file_path.name
                })
                
            except Exception as e:
                logger.error(f"处理文章文件 {file_path} 时出错: {e}")
                continue
        
        return articles
    
    except Exception as e:
        logger.error(f"获取文章列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文章列表失败: {str(e)}")

@articles_router.get("/search")
async def search_articles(query: str) -> List[Dict[str, str]]:
    """搜索文章"""
    try:
        results = []
        md_files = get_article_files()
        
        if not query or query.strip() == "":
            # 如果查询为空，返回所有文章
            return await get_article_list()
        
        query = query.lower().strip()
        
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                content_lower = content.lower()
                
                # 如果内容中包含查询关键词
                if query in content_lower:
                    metadata = extract_metadata(content)
                    slug = file_path.stem
                    title = metadata.get('title') or slug
                    
                    # 获取文件修改时间
                    stat = file_path.stat()
                    import datetime
                    date = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
                    
                    # 计算相关度（简单的关键词出现次数）
                    relevance = content_lower.count(query)
                    
                    # 提取包含关键词的片段
                    snippet = ""
                    lines = content.split('\n')
                    for line in lines:
                        if query in line.lower():
                            snippet = line.strip()[:150]
                            break
                    
                    if not snippet:
                        # 如果没有找到包含关键词的行，取开头部分
                        snippet = content[:150].strip()
                    
                    results.append({
                        "slug": slug,
                        "title": title,
                        "date": date,
                        "snippet": snippet + "..." if len(snippet) > 150 else snippet,
                        "relevance": relevance,
                        "file_name": file_path.name
                    })
                    
            except Exception as e:
                logger.error(f"搜索文章文件 {file_path} 时出错: {e}")
                continue
        
        # 按相关度排序
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results
    
    except Exception as e:
        logger.error(f"搜索文章失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索文章失败: {str(e)}")

@articles_router.get("/content/{slug}")
async def get_article_content(slug: str) -> Dict[str, Any]:
    """获取文章内容"""
    try:
        # 查找匹配的文件（支持.md或.markdown扩展名）
        possible_files = [
            ARTICLES_DIR / f"{slug}.md",
            ARTICLES_DIR / f"{slug}.markdown",
            ARTICLES_DIR / slug  # 如果slug包含扩展名
        ]
        
        file_path = None
        for pf in possible_files:
            if pf.exists() and pf.is_file():
                file_path = pf
                break
        
        if not file_path:
            # 如果没有找到精确匹配，尝试查找包含该slug的文件
            md_files = get_article_files()
            for md_file in md_files:
                if slug.lower() in md_file.stem.lower():
                    file_path = md_file
                    break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 读取文件内容
        content = file_path.read_text(encoding='utf-8')
        
        # 提取元数据
        metadata = extract_metadata(content)
        
        # 提取目录
        toc = extract_toc(content)
        
        # 转换markdown为HTML
        html_content = markdown.markdown(
            content,
            extensions=[
                'fenced_code',  # 代码块
                'codehilite',   # 代码高亮
                'tables',       # 表格
                'admonition',   # 警告框
                TocExtension(toc_depth="2-6"),  # 目录，只包含2-6级标题
            ]
        )
        
        # 获取文件修改时间
        stat = file_path.stat()
        import datetime
        date = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
        
        # 如果没有元数据中的标题，使用文件名
        title = metadata.get('title') or file_path.stem
        
        return {
            "slug": slug,
            "title": title,
            "date": date,
            "content": html_content,
            "toc": toc,
            "raw_content": content,  # 原始markdown内容，用于编辑等
            "file_name": file_path.name
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章内容失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文章内容失败: {str(e)}")

@articles_router.get("/toc/{slug}")
async def get_article_toc(slug: str) -> List[Dict[str, str]]:
    """获取文章目录（单独接口）"""
    try:
        content_response = await get_article_content(slug)
        toc = content_response.get("toc", [])
        if isinstance(toc, List):
            return toc
        else:
            return []
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章目录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文章目录失败: {str(e)}")

@articles_router.get("/recent")
async def get_recent_articles(limit: int = 5) -> List[Dict[str, str]]:
    """获取最近更新的文章"""
    try:
        articles = await get_article_list()
        # 按日期倒序排序（假设日期格式为YYYY-MM-DD）
        articles.sort(key=lambda x: x['date'], reverse=True)
        return articles[:limit]
    except Exception as e:
        logger.error(f"获取最近文章失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取最近文章失败: {str(e)}")

@articles_router.get("/count")
async def get_article_count() -> Dict[str, int]:
    """获取文章总数"""
    try:
        md_files = get_article_files()
        return {"count": len(md_files)}
    except Exception as e:
        logger.error(f"获取文章数量失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文章数量失败: {str(e)}")

# 健康检查端点
@articles_router.get("/health")
async def health_check():
    """文章模块健康检查"""
    return {
        "status": "healthy",
        "articles_dir": str(ARTICLES_DIR),
        "articles_count": len(get_article_files())
    }