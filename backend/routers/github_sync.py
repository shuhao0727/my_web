"""
GitHub同步API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from database.connection import get_db
from models import SyncTask as SyncTaskModel
from schemas.competition import SyncTask, SyncTaskCreate
from services.repo_sync_service import repo_sync_service
from config.github_sync import github_client, github_config

router = APIRouter(prefix="/github", tags=["github-sync"])


@router.get("/config")
async def get_github_config():
    """获取GitHub配置信息"""
    repo_info = github_client.get_repository_info()
    
    if not repo_info:
        raise HTTPException(
            status_code=400, 
            detail="无法连接到GitHub仓库，请检查配置"
        )
    
    # 获取最后提交信息
    last_commit = github_client.get_last_commit()
    
    return {
        "configured": github_config.is_configured(),
        "repository": {
            "owner": github_config.owner,
            "name": github_config.repo,
            "branch": github_config.branch,
            "base_path": github_config.base_path,
            "full_name": repo_info.get("full_name"),
            "description": repo_info.get("description"),
            "html_url": repo_info.get("html_url"),
            "private": repo_info.get("private"),
            "updated_at": repo_info.get("updated_at"),
        },
        "last_commit": {
            "sha": last_commit.get("sha")[:8] if last_commit else None,
            "message": last_commit.get("commit", {}).get("message") if last_commit else None,
            "author": last_commit.get("commit", {}).get("author", {}).get("name") if last_commit else None,
            "date": last_commit.get("commit", {}).get("author", {}).get("date") if last_commit else None,
        } if last_commit else None,
    }


@router.get("/files")
async def list_typst_files():
    """列出仓库中的所有Typst文件"""
    if not github_config.is_configured():
        raise HTTPException(
            status_code=400, 
            detail="GitHub配置未完成，请先设置GITHUB_ACCESS_TOKEN"
        )
    
    typst_files = github_client.get_typst_files()
    
    return {
        "files": typst_files,
        "count": len(typst_files),
        "summary": {
            "total": len(typst_files),
            "by_category": {},
            "by_difficulty": {
                "简单": 0,
                "中等": 0,
                "困难": 0
            }
        }
    }


@router.post("/sync", response_model=SyncTask)
async def trigger_github_sync(
    sync_task: Optional[SyncTaskCreate] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """触发GitHub同步"""
    raise HTTPException(status_code=501, detail="此功能暂时不可用，请使用 /api/repo/sync 替代")


@router.get("/sync/tasks", response_model=List[SyncTask])
async def list_sync_tasks(
    limit: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取同步任务列表"""
    query = db.query(SyncTaskModel).order_by(SyncTaskModel.created_at.desc())
    
    if status:
        query = query.filter(SyncTaskModel.status == status)
    
    tasks = query.limit(limit).all()
    return tasks


@router.get("/sync/tasks/{task_id}", response_model=SyncTask)
async def get_sync_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取特定同步任务详情"""
    task = db.query(SyncTaskModel).filter(SyncTaskModel.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task


@router.post("/sync/file")
async def sync_single_file(
    file_path: str,
    db: Session = Depends(get_db)
):
    """同步单个文件"""
    raise HTTPException(status_code=501, detail="此功能暂时不可用")

@router.post("/sync/full")
async def trigger_full_sync_endpoint(db: Session = Depends(get_db)):
    """触发全量同步（清理旧内容，下载新内容）"""
    raise HTTPException(status_code=501, detail="此功能暂时不可用，请使用 /api/repo/sync 替代")


@router.get("/status")
async def get_sync_status():
    """获取同步状态概览"""
    # 检查配置状态
    config_status = github_config.is_configured()
    
    # 获取仓库信息（如果配置了）
    repo_info = None
    if config_status:
        repo_info = github_client.get_repository_info()
    
    return {
        "configured": config_status,
        "repository_accessible": repo_info is not None,
        "config": {
            "owner": github_config.owner,
            "repo": github_config.repo,
            "branch": github_config.branch,
            "base_path": github_config.base_path,
        } if config_status else None,
        "requires_setup": not config_status,
        "setup_instructions": {
            "token_required": True,
            "scopes_needed": ["repo"],
            "steps": [
                "1. 访问 https://github.com/settings/tokens",
                "2. 点击 'Generate new token (classic)'",
                "3. 选择 'repo' 权限",
                "4. 设置合适过期时间",
                "5. 复制生成的token",
                "6. 在.env文件中添加: GITHUB_ACCESS_TOKEN=你的token"
            ]
        } if not config_status else None,
    }
