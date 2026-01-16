"""
竞赛文档API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List

from database.connection import get_db
from models import CompetitionDocument, DocumentChapter, DocumentContent as DContent, SyncTask as SyncTaskModel
from schemas.competition import (
    CompetitionDocumentCreate,
    CompetitionDocumentUpdate,
    CompetitionDocumentWithChapters,
    DocumentChapterCreate,
    DocumentChapterUpdate,
    DocumentChapterWithContent,
    DocumentContentCreate,
    DocumentContentUpdate,
    DocumentContent,
    DocumentQueryParams,
    PaginatedResponse,
    SyncTaskCreate,
    SyncTask,
    SyncResponse,
    FullDocumentStructure,
)
from services.competition import (
    create_document,
    get_documents,
    get_document_by_id,
    update_document,
    delete_document,
    create_chapter,
    get_chapters_by_document,
    get_chapter_by_id,
    update_chapter,
    delete_chapter,
    create_content,
    get_content_by_id,
    update_content,
    sync_from_github,
)

router = APIRouter(prefix="/api/competition", tags=["competition"])

# 文档相关接口
@router.post("/documents", response_model=CompetitionDocumentWithChapters)
def create_document_endpoint(
    document: CompetitionDocumentCreate,
    db: Session = Depends(get_db)
):
    """创建新文档"""
    return create_document(db=db, document=document)

@router.get("/documents", response_model=PaginatedResponse)
def list_documents(
    category: Optional[str] = Query(None, description="按分类筛选"),
    difficulty: Optional[str] = Query(None, description="按难度筛选"),
    tag: Optional[str] = Query(None, description="按标签筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    is_published: Optional[bool] = Query(True, description="是否只显示已发布的"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    db: Session = Depends(get_db)
):
    """获取文档列表（支持分页和筛选）"""
    query_params = DocumentQueryParams(
        category=category,
        difficulty=difficulty,
        tag=tag,
        search=search,
        is_published=is_published,
        skip=skip,
        limit=limit
    )
    return get_documents(db=db, query_params=query_params)

@router.get("/documents/{document_id}", response_model=FullDocumentStructure)
def get_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db)
):
    """获取文档详情（包含章节和内容）"""
    document = get_document_by_id(db=db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document

@router.put("/documents/{document_id}", response_model=CompetitionDocumentWithChapters)
def update_document_endpoint(
    document_id: int,
    document_update: CompetitionDocumentUpdate,
    db: Session = Depends(get_db)
):
    """更新文档"""
    document = update_document(db=db, document_id=document_id, document_update=document_update)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document

@router.delete("/documents/{document_id}")
def delete_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db)
):
    """删除文档"""
    success = delete_document(db=db, document_id=document_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"message": "文档删除成功"}

# 章节相关接口
@router.post("/documents/{document_id}/chapters", response_model=DocumentChapterWithContent)
def create_chapter_endpoint(
    document_id: int,
    chapter: DocumentChapterCreate,
    db: Session = Depends(get_db)
):
    """创建章节"""
    # 确保document_id一致
    chapter.document_id = document_id
    return create_chapter(db=db, chapter=chapter)

@router.get("/documents/{document_id}/chapters", response_model=List[DocumentChapterWithContent])
def list_chapters_endpoint(
    document_id: int,
    db: Session = Depends(get_db)
):
    """获取文档的所有章节"""
    return get_chapters_by_document(db=db, document_id=document_id)

@router.get("/chapters/{chapter_id}", response_model=DocumentChapterWithContent)
def get_chapter_endpoint(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """获取章节详情"""
    chapter = get_chapter_by_id(db=db, chapter_id=chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return chapter

@router.put("/chapters/{chapter_id}", response_model=DocumentChapterWithContent)
def update_chapter_endpoint(
    chapter_id: int,
    chapter_update: DocumentChapterUpdate,
    db: Session = Depends(get_db)
):
    """更新章节"""
    chapter = update_chapter(db=db, chapter_id=chapter_id, chapter_update=chapter_update)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return chapter

@router.delete("/chapters/{chapter_id}")
def delete_chapter_endpoint(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """删除章节"""
    success = delete_chapter(db=db, chapter_id=chapter_id)
    if not success:
        raise HTTPException(status_code=404, detail="章节不存在")
    return {"message": "章节删除成功"}

# 内容相关接口
@router.post("/contents", response_model=DocumentContent)
def create_content_endpoint(
    content: DocumentContentCreate,
    db: Session = Depends(get_db)
):
    """创建内容"""
    return create_content(db=db, content=content)

@router.get("/contents/{content_id}", response_model=DocumentContent)
def get_content_endpoint(
    content_id: int,
    db: Session = Depends(get_db)
):
    """获取内容"""
    content = get_content_by_id(db=db, content_id=content_id)
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    # 将SQLAlchemy模型转换为Pydantic模型
    return DocumentContent.from_orm(content)

@router.put("/contents/{content_id}", response_model=DocumentContent)
def update_content_endpoint(
    content_id: int,
    content_update: DocumentContentUpdate,
    db: Session = Depends(get_db)
):
    """更新内容"""
    content = update_content(db=db, content_id=content_id, content_update=content_update)
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    # 将SQLAlchemy模型转换为Pydantic模型
    return DocumentContent.from_orm(content)

# 同步相关接口
@router.post("/sync", response_model=SyncResponse)
def sync_documents_endpoint(
    background_tasks: BackgroundTasks,
    sync_task: SyncTaskCreate,
    db: Session = Depends(get_db)
):
    """触发GitHub同步（后台任务）"""
    # 这里可以立即返回任务ID，然后在后台执行同步
    task = sync_from_github(db=db, sync_task=sync_task, background_tasks=background_tasks)
    # 使用类型忽略注释，因为task.id和task.status在运行时已经是Python类型
    task_id: int = task.id if task.id is not None else 0  # type: ignore
    task_status: str = task.status if task.status is not None else "pending"  # type: ignore
    return SyncResponse(
        task_id=task_id,
        status=task_status,
        message="同步任务已启动，将在后台执行"
    )

@router.get("/sync/tasks/{task_id}", response_model=SyncTask)
def get_sync_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取同步任务状态"""
    task = db.query(SyncTaskModel).filter(SyncTaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="同步任务不存在")
    return SyncTask.from_orm(task)

# 其他实用接口
@router.get("/categories")
def get_categories_endpoint(db: Session = Depends(get_db)):
    """获取所有文档分类"""
    categories = db.query(CompetitionDocument.category).distinct().all()
    return [category[0] for category in categories if category[0]]

@router.get("/tags")
def get_tags_endpoint(db: Session = Depends(get_db)):
    """获取所有标签"""
    tags_set = set()
    documents = db.query(CompetitionDocument.tags).filter(CompetitionDocument.tags.isnot(None)).all()
    for doc in documents:
        if doc.tags:
            tags_set.update(doc.tags)
    return list(tags_set)

@router.get("/tree")
def get_document_tree(db: Session = Depends(get_db)):
    """获取文档树形结构（用于导航）"""
    documents = db.query(CompetitionDocument).filter(CompetitionDocument.is_published == True).all()
    
    tree = []
    for doc in documents:
        doc_data = {
            "id": doc.id,
            "title": doc.title,
            "category": doc.category,
            "difficulty": doc.difficulty,
            "chapters": []
        }
        
        # 获取章节（只获取第一级）
        chapters = db.query(DocumentChapter).filter(
            DocumentChapter.document_id == doc.id,
            DocumentChapter.parent_id.is_(None)
        ).order_by(DocumentChapter.order_index).all()
        
        for chapter in chapters:
            doc_data["chapters"].append({
                "id": chapter.id,
                "title": chapter.title,
                "slug": chapter.slug,
                "level": chapter.level
            })
        
        tree.append(doc_data)
    
    return tree
