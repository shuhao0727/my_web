"""
GitHub仓库同步API路由
"""
import os
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from fastapi.responses import Response, FileResponse
from datetime import datetime

from services.repo_sync_service import repo_sync_service
from scheduler.sync_scheduler import repo_sync_scheduler

router = APIRouter(prefix="/api/repo", tags=["repository"])

@router.get("/status")
async def get_repo_status():
    """获取仓库状态"""
    status = repo_sync_service.get_repo_status()
    return status

@router.post("/sync")
async def sync_repository(force_clone: bool = False):
    """同步仓库（克隆或拉取更新）"""
    result = repo_sync_service.sync_repository(force_clone=force_clone)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "同步失败"))
    
    return result

@router.get("/structure")
async def get_repo_structure():
    """获取仓库结构概览"""
    result = repo_sync_service.get_repo_structure()
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "获取结构失败"))
    
    return result

@router.get("/list")
async def list_files(path: str = ""):
    """列出指定路径下的文件和目录"""
    result = repo_sync_service.list_files(path)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "路径不存在"))
    
    return result

@router.get("/file")
async def get_file_content(path: str = Query(..., description="文件相对路径")):
    """获取文件内容"""
    result = repo_sync_service.get_file_content(path)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "文件不存在或读取失败"))
    
    return result

@router.get("/main-typ")
async def get_main_typ():
    """获取main.typ文件内容（仓库目录文件）"""
    result = repo_sync_service.get_file_content("main.typ")
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "main.typ文件不存在"))
    
    return result

@router.get("/chapters")
async def list_chapters():
    """列出所有章节"""
    result = repo_sync_service.list_files("chapters")
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "chapters目录不存在"))
    
    return result

@router.get("/chapters/{chapter_path:path}")
async def list_chapter_files(chapter_path: str):
    """列出特定章节目录下的文件"""
    full_path = f"chapters/{chapter_path}" if chapter_path else "chapters"
    result = repo_sync_service.list_files(full_path)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "章节路径不存在"))
    
    return result

@router.get("/chapter-file/{file_path:path}")
async def get_chapter_file(file_path: str):
    """获取章节文件内容"""
    # file_path 已经包含 chapters/ 前缀
    result = repo_sync_service.get_file_content(file_path)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "章节文件不存在"))
    
    return result

@router.get("/chapter-pdf/{file_path:path}")
async def get_chapter_pdf(file_path: str):
    """获取章节文件的PDF版本（编译或从缓存返回），设置为内联显示"""
    # file_path 已经包含 chapters/ 前缀
    result = repo_sync_service.compile_to_pdf(file_path)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "PDF编译失败"))
    
    # 返回PDF文件，设置为内联显示
    return Response(
        content=result["content"],
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline",  # 只设置inline，不提供文件名
            "Content-Length": str(result["size"])
        }
    )

@router.get("/chapter-pdf-static/{file_path:path}")
async def get_chapter_pdf_static(file_path: str):
    """直接返回静态PDF文件（如果存在），设置为内联显示，不提供文件名"""
    # file_path 已经包含 chapters/ 前缀
    pdf_path = repo_sync_service.get_static_pdf_path(file_path)
    
    if not pdf_path:
        # 如果静态PDF不存在，尝试编译
        result = repo_sync_service.compile_to_pdf(file_path)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "PDF编译失败"))
        
        # 返回编译的PDF，设置为内联显示
        return Response(
            content=result["content"],
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline",  # 只设置inline，不提供文件名
                "Content-Length": str(result["size"]),
                "X-Content-Type-Options": "nosniff"  # 防止MIME类型嗅探
            }
        )
    
    # 返回静态PDF文件，设置为内联显示，不提供文件名
    return Response(
        content=open(pdf_path, "rb").read(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline",  # 只设置inline，不提供文件名
            "Content-Length": str(os.path.getsize(pdf_path)),
            "X-Content-Type-Options": "nosniff",  # 防止MIME类型嗅探
            "Cache-Control": "public, max-age=3600"  # 缓存1小时
        }
    )

@router.get("/chapter-pdf-url/{file_path:path}")
async def get_chapter_pdf_url(file_path: str):
    """获取章节PDF的静态URL"""
    # file_path 已经包含 chapters/ 前缀
    pdf_url = repo_sync_service.get_static_pdf_url(file_path)
    
    if not pdf_url:
        # 如果PDF不存在，尝试编译
        result = repo_sync_service.compile_to_pdf(file_path)
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "PDF编译失败"))
        
        # 返回新生成的PDF的URL
        pdf_url = repo_sync_service.get_static_pdf_url(file_path)
    
    return {
        "success": True,
        "file_path": file_path,
        "pdf_url": pdf_url,
        "pdf_filename": pdf_url.split("/")[-1] if pdf_url else None
    }

@router.get("/pdf-cache/info")
async def get_pdf_cache_info():
    """获取PDF缓存信息"""
    result = repo_sync_service.get_pdf_cache_info()
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "获取PDF缓存信息失败"))
    
    return result

@router.post("/pdf-cache/generate")
async def generate_pdf_cache():
    """手动触发生成所有PDF缓存"""
    result = repo_sync_service.generate_all_pdf_cache()
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "生成PDF缓存失败"))
    
    return result

@router.get("/style")
async def list_style_files():
    """列出style目录下的文件"""
    result = repo_sync_service.list_files("style")
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "style目录不存在"))
    
    return result

@router.get("/image")
async def list_image_files():
    """列出image目录下的文件"""
    result = repo_sync_service.list_files("image")
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "image目录不存在"))
    
    return result

@router.get("/sync-scheduler/status")
async def get_sync_scheduler_status():
    """获取自动同步调度器状态"""
    try:
        status = repo_sync_scheduler.get_status()
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取调度器状态失败: {str(e)}")

@router.post("/sync-scheduler/start")
async def start_sync_scheduler():
    """启动自动同步调度器"""
    try:
        success = repo_sync_scheduler.start()
        return {
            "success": success,
            "message": "调度器已启动" if success else "调度器启动失败或已在运行",
            "status": repo_sync_scheduler.get_status(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动调度器失败: {str(e)}")

@router.post("/sync-scheduler/stop")
async def stop_sync_scheduler():
    """停止自动同步调度器"""
    try:
        repo_sync_scheduler.stop()
        return {
            "success": True,
            "message": "调度器已停止",
            "status": repo_sync_scheduler.get_status(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止调度器失败: {str(e)}")
