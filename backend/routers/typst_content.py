"""
Typst内容API路由
提供Typst文件内容、文件树结构等API
"""
import os
from pathlib import Path
import subprocess
import tempfile
import base64
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import logging
from typing import List, Optional
import json

logger = logging.getLogger(__name__)

router = APIRouter(redirect_slashes=False)

# 获取内容目录路径
def get_content_dir() -> Path:
    """获取内容目录路径"""
    content_dir = os.getenv("CONTENT_DIR", "./content")
    return Path(content_dir)

def get_repo_dir() -> Path:
    """获取仓库目录路径"""
    repo_name = os.getenv("GITHUB_REPO_NAME", "2-My-notes")
    return get_content_dir() / repo_name

@router.get("/tree")
async def get_typst_tree(path: str = ""):
    """获取Typst文件树结构
    
    Args:
        path: 相对路径，默认为根目录
    """
    try:
        repo_dir = get_repo_dir()
        target_dir = repo_dir / path if path else repo_dir
        
        if not target_dir.exists():
            raise HTTPException(status_code=404, detail=f"路径不存在: {path}")
        
        if not target_dir.is_dir():
            raise HTTPException(status_code=400, detail=f"路径不是目录: {path}")
        
        # 排除的目录和文件
        exclude_names = {".git", "__pycache__", ".DS_Store"}
        
        files = []
        for item in target_dir.iterdir():
            if item.name in exclude_names:
                continue
                
            is_dir = item.is_dir()
            # 如果是文件且不是.typ文件，跳过（除非是图片或样式文件）
            if not is_dir and not item.name.endswith(".typ"):
                # 允许图片和样式文件
                allowed_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".sty"}
                if item.suffix.lower() not in allowed_extensions:
                    continue
            
            file_info = {
                "name": item.name,
                "path": str(item.relative_to(repo_dir)),
                "type": "directory" if is_dir else "file",
                "size": item.stat().st_size if not is_dir else 0,
                "extension": item.suffix if not is_dir else "",
                "is_typst": item.suffix.lower() == ".typ" if not is_dir else False,
            }
            files.append(file_info)
        
        # 排序：目录在前，文件在后，按自然排序
        files.sort(key=lambda x: (x["type"] != "directory", natural_sort_key(x["name"])))
        
        return {
            "success": True,
            "path": path,
            "files": files,
            "count": len(files),
            "repo_path": str(repo_dir),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件树失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文件树失败: {str(e)}")

@router.get("/content/{filepath:path}")
async def get_typst_content(filepath: str):
    """获取Typst文件内容
    
    Args:
        filepath: 文件相对路径，如 "chapters/1.basics/1.1-introduction.typ"
    """
    try:
        repo_dir = get_repo_dir()
        file_path = repo_dir / filepath
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在: {filepath}")
        
        if file_path.is_dir():
            raise HTTPException(status_code=400, detail=f"路径是目录，不是文件: {filepath}")
        
        # 检查文件扩展名
        if file_path.suffix.lower() != ".typ":
            # 如果是图片文件，返回二进制信息
            if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg"}:
                return {
                    "success": True,
                    "path": filepath,
                    "type": "image",
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix,
                }
            # 其他文件类型
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_path.suffix}")
        
        # 读取Typst文件内容
        content = file_path.read_text(encoding="utf-8")
        
        # 获取文件依赖（导入的其他Typst文件）
        imports = extract_imports(content)
        
        return {
            "success": True,
            "path": filepath,
            "content": content,
            "size": len(content),
            "imports": imports,
            "encoding": "utf-8",
        }
        
    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="文件编码不是UTF-8")
    except Exception as e:
        logger.error(f"读取文件内容失败: {e}")
        raise HTTPException(status_code=500, detail=f"读取文件内容失败: {str(e)}")

@router.get("/structure")
async def get_typst_structure():
    """获取Typst仓库的整体结构"""
    try:
        repo_dir = get_repo_dir()
        
        if not repo_dir.exists():
            raise HTTPException(status_code=404, detail="仓库目录不存在")
        
        structure = {
            "chapters": {
                "exists": (repo_dir / "chapters").exists(),
                "count": len(list((repo_dir / "chapters").glob("**/*.typ"))) if (repo_dir / "chapters").exists() else 0,
                "subdirectories": [d.name for d in (repo_dir / "chapters").iterdir() if d.is_dir()] if (repo_dir / "chapters").exists() else [],
            },
            "style": {
                "exists": (repo_dir / "style").exists(),
                "files": [f.name for f in (repo_dir / "style").iterdir() if f.is_file()] if (repo_dir / "style").exists() else [],
            },
            "image": {
                "exists": (repo_dir / "image").exists(),
                "count": len(list((repo_dir / "image").iterdir())) if (repo_dir / "image").exists() else 0,
                "extensions": list(set(f.suffix for f in (repo_dir / "image").iterdir() if f.is_file())) if (repo_dir / "image").exists() else [],
            },
            "main_typ": {
                "exists": (repo_dir / "main.typ").exists(),
                "size": (repo_dir / "main.typ").stat().st_size if (repo_dir / "main.typ").exists() else 0,
            },
        }
        
        # 获取所有章节分类
        chapters_dir = repo_dir / "chapters"
        if chapters_dir.exists():
            categories = []
            for category_dir in chapters_dir.iterdir():
                if category_dir.is_dir():
                    # 获取文件并按自然排序
                    files = [f.name for f in category_dir.glob("*.typ")]
                    files.sort(key=natural_sort_key)
                    
                    category_info = {
                        "name": category_dir.name,
                        "display_name": format_category_name(category_dir.name),
                        "file_count": len(files),
                        "files": files,
                    }
                    categories.append(category_info)
            
            # 对分类按自然排序
            categories.sort(key=lambda x: natural_sort_key(x["name"]))
            structure["chapters"]["categories"] = categories
        
        return {
            "success": True,
            "structure": structure,
            "repo_path": str(repo_dir),
        }
        
    except Exception as e:
        logger.error(f"获取仓库结构失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取仓库结构失败: {str(e)}")

@router.get("/search")
async def search_typst_files(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    file_ext: Optional[str] = Query(".typ", description="文件扩展名过滤")
):
    """搜索Typst文件
    
    Args:
        query: 搜索关键词
        file_ext: 文件扩展名，默认为.typ
    """
    try:
        repo_dir = get_repo_dir()
        
        if not repo_dir.exists():
            raise HTTPException(status_code=404, detail="仓库目录不存在")
        
        results = []
        search_pattern = f"**/*{file_ext}"
        
        for file_path in repo_dir.glob(search_pattern):
            # 跳过.git目录
            if ".git" in str(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if query.lower() in content.lower():
                    results.append({
                        "path": str(file_path.relative_to(repo_dir)),
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
        logger.error(f"搜索文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索文件失败: {str(e)}")

def extract_imports(content: str) -> List[str]:
    """从Typst内容中提取导入语句
    
    Args:
        content: Typst文件内容
        
    Returns:
        导入的文件路径列表
    """
    imports = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        # 匹配导入语句，如：#import "chapters/1.basics/1.1-introduction.typ"
        if line.startswith('#import "') or line.startswith('#import "') or line.startswith('//'):
            # 跳过注释
            if line.startswith('//'):
                continue
                
            # 提取引号内的路径
            import_match = None
            if '#import "' in line:
                import_match = line.split('#import "')[1].split('"')[0]
            elif '#import "' in line:
                import_match = line.split('#import "')[1].split('"')[0]
            
            if import_match and import_match.endswith(".typ"):
                imports.append(import_match)
    
    return imports

def format_category_name(category: str) -> str:
    """格式化分类名称
    
    Args:
        category: 原始分类名称，如 "1.basics"
        
    Returns:
        格式化后的名称，如 "1. Basics"
    """
    # 分离数字和名称
    if '.' in category:
        parts = category.split('.', 1)
        if len(parts) == 2 and parts[0].isdigit():
            number = parts[0]
            name = parts[1].replace('-', ' ').title()
            return f"{number}. {name}"
    
    return category.replace('-', ' ').title()

# 健康检查端点
@router.get("/health")
async def typst_health_check():
    """Typst API健康检查"""
    try:
        repo_dir = get_repo_dir()
        exists = repo_dir.exists()
        
        return {
            "status": "healthy" if exists else "warning",
            "repo_exists": exists,
            "repo_path": str(repo_dir),
            "message": "Typst API服务正常" if exists else "仓库目录不存在",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }

def natural_sort_key(s: str) -> list:
    """生成自然排序键，支持数字和文本混合的字符串
    
    Args:
        s: 要排序的字符串
        
    Returns:
        用于排序的键列表
    """
    import re
    # 将字符串分割为数字和非数字部分
    parts = re.split(r'(\d+)', s)
    # 转换数字部分为整数，非数字部分保持原样
    key = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            # 对于非数字部分，转换为小写进行比较
            key.append(part.lower())
    return key

@router.post("/compile")
async def compile_typst(request: dict):
    """编译Typst文档
    
    Args:
        request: 包含typst内容和文件路径的JSON对象
            {
                "content": "Typst源代码",
                "filepath": "相对路径",
                "output_format": "svg"  # 可选: svg 或 pdf，默认为svg
            }
    """
    try:
        content = request.get("content", "")
        filepath = request.get("filepath", "")
        output_format = request.get("output_format", "svg").lower()
        
        if not content:
            raise HTTPException(status_code=400, detail="内容不能为空")
        
        if output_format not in ["svg", "pdf"]:
            raise HTTPException(status_code=400, detail="输出格式必须是'svg'或'pdf'")
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建临时Typst文件
            tmp_typst_path = os.path.join(tmpdir, "temp.typ")
            with open(tmp_typst_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # 设置输出路径
            output_filename = f"output.{output_format}"
            output_path = os.path.join(tmpdir, output_filename)
            
            # 构建编译命令
            cmd = ["typst", "compile", tmp_typst_path, output_path]
            
            # 执行编译
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30秒超时
            )
            
            # 检查输出文件是否存在，即使有警告也继续
            if result.returncode != 0 and not os.path.exists(output_path):
                error_msg = f"编译失败: {result.stderr}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
            
            # 即使有警告，如果输出文件存在，也继续处理
            if not os.path.exists(output_path):
                error_msg = f"编译失败: 输出文件未生成。stderr: {result.stderr}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
            
            # 读取输出文件
            if output_format == "svg":
                with open(output_path, "r", encoding="utf-8") as f:
                    compiled_content = f.read()
                content_type = "image/svg+xml"
            else:  # pdf
                with open(output_path, "rb") as f:
                    compiled_content = f.read()
                # 返回base64编码
                compiled_content = base64.b64encode(compiled_content).decode("utf-8")
                content_type = "application/pdf"
            
            return {
                "success": True,
                "format": output_format,
                "content": compiled_content,
                "content_type": content_type,
                "size": len(compiled_content),
            }
            
    except subprocess.TimeoutExpired:
        error_msg = "编译超时（30秒）"
        logger.error(error_msg)
        raise HTTPException(status_code=504, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"编译过程出错: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/render/{filepath:path}")
async def render_typst_file(filepath: str, output_format: str = Query("svg", regex="^(svg|pdf)$")):
    """渲染Typst文件为SVG或PDF
    
    Args:
        filepath: Typst文件的相对路径
        output_format: 输出格式，svg或pdf，默认为svg
    """
    try:
        repo_dir = get_repo_dir()
        typst_file = repo_dir / filepath
        
        if not typst_file.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在: {filepath}")
        
        if typst_file.is_dir():
            raise HTTPException(status_code=400, detail=f"路径是目录，不是文件: {filepath}")
        
        # 检查文件扩展名
        if typst_file.suffix.lower() != ".typ":
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {typst_file.suffix}")
        
        # 创建临时目录用于输出
        with tempfile.TemporaryDirectory() as tmpdir:
            if output_format == "svg":
                # 对于SVG，使用页码模板输出多页
                output_filename = "output-{p}.svg"
                output_path_template = os.path.join(tmpdir, output_filename)
                # 构建编译命令，设置根目录为仓库目录，以便找到样式和资源
                cmd = ["typst", "compile", "--root", str(repo_dir), str(typst_file), output_path_template]
                
                # 执行编译
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30  # 30秒超时
                )
                
                # 收集所有生成的SVG文件
                svg_files = []
                for f in os.listdir(tmpdir):
                    if f.startswith("output-") and f.endswith(".svg"):
                        svg_files.append(f)
                
                # 按页码排序
                def extract_page_number(filename):
                    # 文件名格式：output-1.svg, output-2.svg, ...
                    try:
                        return int(filename.split('-')[1].split('.')[0])
                    except:
                        return 0
                
                svg_files.sort(key=extract_page_number)
                
                # 如果没有生成任何SVG文件，则视为失败
                if not svg_files:
                    error_msg = f"编译失败: 未生成SVG文件。stderr: {result.stderr}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=500, detail=error_msg)
                
                # 读取所有SVG文件内容
                svg_contents = []
                total_size = 0
                for svg_file in svg_files:
                    svg_path = os.path.join(tmpdir, svg_file)
                    with open(svg_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    svg_contents.append(content)
                    total_size += len(content)
                
                # 返回多个SVG内容
                return {
                    "success": True,
                    "format": output_format,
                    "content": svg_contents,  # 现在是数组
                    "content_type": "image/svg+xml",
                    "size": total_size,
                    "page_count": len(svg_contents),
                }
            else:  # pdf
                # 对于PDF，输出单个文件
                output_filename = f"output.pdf"
                output_path = os.path.join(tmpdir, output_filename)
                cmd = ["typst", "compile", "--root", str(repo_dir), str(typst_file), output_path]
                
                # 执行编译
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30  # 30秒超时
                )
                
                # 检查输出文件是否存在，即使有警告也继续
                if result.returncode != 0 and not os.path.exists(output_path):
                    error_msg = f"编译失败: {result.stderr}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=500, detail=error_msg)
                
                # 即使有警告，如果输出文件存在，也继续处理
                if not os.path.exists(output_path):
                    error_msg = f"编译失败: 输出文件未生成。stderr: {result.stderr}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=500, detail=error_msg)
                
                with open(output_path, "rb") as f:
                    compiled_content = f.read()
                # 返回base64编码
                compiled_content = base64.b64encode(compiled_content).decode("utf-8")
                content_type = "application/pdf"
                return {
                    "success": True,
                    "format": output_format,
                    "content": compiled_content,
                    "content_type": content_type,
                    "size": len(compiled_content),
                }
            
    except subprocess.TimeoutExpired:
        error_msg = "编译超时（30秒）"
        logger.error(error_msg)
        raise HTTPException(status_code=504, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"渲染过程出错: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    # 测试代码
    import asyncio
    
    async def test():
        print("测试Typst API路由...")
        
        # 测试获取结构
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        
        client = TestClient(app)
        
        response = client.get("/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
        
        response = client.get("/structure")
        print(f"结构信息: {response.status_code} - {response.json()}")
        
        # 测试文件树
        response = client.get("/tree")
        print(f"文件树: {response.status_code} - {response.json()}")
    
    asyncio.run(test())
