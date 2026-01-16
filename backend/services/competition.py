"""
竞赛文档服务层
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime

from models import (
    CompetitionDocument, 
    DocumentChapter, 
    DocumentContent, 
    SyncTask,
    User
)
from schemas.competition import (
    CompetitionDocumentCreate,
    CompetitionDocumentUpdate,
    DocumentChapterCreate,
    DocumentChapterUpdate,
    DocumentContentCreate,
    DocumentContentUpdate,
    DocumentQueryParams,
    PaginatedResponse,
    SyncTaskCreate,
)

def create_document(db: Session, document: CompetitionDocumentCreate) -> CompetitionDocument:
    """创建新文档"""
    db_document = CompetitionDocument(
        title=document.title,
        description=document.description,
        file_path=document.file_path,
        github_url=document.github_url,
        category=document.category,
        difficulty=document.difficulty,
        author=document.author,
        tags=document.tags,
        version=document.version,
        typst_source=document.typst_source,
        html_content=document.html_content,
        order_index=document.order_index,
        is_published=document.is_published,
        sync_status="manual",
        last_synced_at=datetime.utcnow(),
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_documents(db: Session, query_params: DocumentQueryParams) -> PaginatedResponse:
    """获取文档列表（支持分页和筛选）"""
    query = db.query(CompetitionDocument)
    
    # 应用筛选条件
    if query_params.category:
        query = query.filter(CompetitionDocument.category == query_params.category)
    
    if query_params.difficulty:
        query = query.filter(CompetitionDocument.difficulty == query_params.difficulty)
    
    if query_params.tag:
        query = query.filter(CompetitionDocument.tags.contains([query_params.tag]))
    
    if query_params.search:
        search_term = f"%{query_params.search}%"
        query = query.filter(
            or_(
                CompetitionDocument.title.ilike(search_term),
                CompetitionDocument.description.ilike(search_term),
                CompetitionDocument.tags.contains([query_params.search])
            )
        )
    
    if query_params.is_published is not None:
        query = query.filter(CompetitionDocument.is_published == query_params.is_published)
    
    # 获取总数
    total = query.count()
    
    # 应用分页和排序
    query = query.order_by(CompetitionDocument.order_index, CompetitionDocument.created_at.desc())
    db_items = query.offset(query_params.skip).limit(query_params.limit).all()
    
    # 转换为Pydantic模型
    from schemas.competition import CompetitionDocumentWithChapters
    items = []
    for doc in db_items:
        # 获取章节
        chapters = db.query(DocumentChapter).filter(
            DocumentChapter.document_id == doc.id
        ).order_by(DocumentChapter.order_index).all()
        # 将SQLAlchemy对象转换为字典，然后创建Pydantic模型
        doc_dict = {c.name: getattr(doc, c.name) for c in doc.__table__.columns}
        doc_dict['chapters'] = chapters
        pydantic_doc = CompetitionDocumentWithChapters(**doc_dict)
        items.append(pydantic_doc)
    
    return PaginatedResponse(
        items=items,
        total=total,
        skip=query_params.skip,
        limit=query_params.limit,
        has_more=(query_params.skip + len(items)) < total
    )

def get_document_by_id(db: Session, document_id: int) -> Optional[CompetitionDocument]:
    """根据ID获取文档（包含章节和内容）"""
    document = db.query(CompetitionDocument).filter(CompetitionDocument.id == document_id).first()
    if not document:
        return None
    
    # 获取所有章节
    chapters = db.query(DocumentChapter).filter(
        DocumentChapter.document_id == document_id
    ).order_by(DocumentChapter.order_index).all()
    
    # 为每个章节获取内容
    chapters_with_content = []
    for chapter in chapters:
        chapter_data = chapter
        if chapter.content_id:
            chapter_data.content = db.query(DocumentContent).filter(
                DocumentContent.id == chapter.content_id
            ).first()
        else:
            chapter_data.content = None
        chapters_with_content.append(chapter_data)
    
    # 设置文档的章节
    document.chapters = chapters
    document.chapters_with_content = chapters_with_content
    
    return document

def update_document(db: Session, document_id: int, document_update: CompetitionDocumentUpdate) -> Optional[CompetitionDocument]:
    """更新文档"""
    db_document = db.query(CompetitionDocument).filter(CompetitionDocument.id == document_id).first()
    if not db_document:
        return None
    
    update_data = document_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db_document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_document(db: Session, document_id: int) -> bool:
    """删除文档（同时删除相关章节和内容）"""
    db_document = db.query(CompetitionDocument).filter(CompetitionDocument.id == document_id).first()
    if not db_document:
        return False
    
    # 删除相关章节
    chapters = db.query(DocumentChapter).filter(DocumentChapter.document_id == document_id).all()
    for chapter in chapters:
        # 删除章节相关内容
        if chapter.content_id:
            db.query(DocumentContent).filter(DocumentContent.id == chapter.content_id).delete()
        db.delete(chapter)
    
    # 删除文档
    db.delete(db_document)
    db.commit()
    return True

def create_chapter(db: Session, chapter: DocumentChapterCreate) -> DocumentChapter:
    """创建章节"""
    db_chapter = DocumentChapter(
        document_id=chapter.document_id,
        parent_id=chapter.parent_id,
        title=chapter.title,
        slug=chapter.slug,
        level=chapter.level,
        order_index=chapter.order_index,
        content_id=chapter.content_id,
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    
    # 如果提供了内容ID，获取内容
    if db_chapter.content_id:
        db_chapter.content = db.query(DocumentContent).filter(
            DocumentContent.id == db_chapter.content_id
        ).first()
    else:
        db_chapter.content = None
    
    return db_chapter

def get_chapters_by_document(db: Session, document_id: int) -> List[DocumentChapter]:
    """获取文档的所有章节（带内容）"""
    chapters = db.query(DocumentChapter).filter(
        DocumentChapter.document_id == document_id
    ).order_by(DocumentChapter.order_index).all()
    
    # 为每个章节获取内容
    for chapter in chapters:
        if chapter.content_id:
            chapter.content = db.query(DocumentContent).filter(
                DocumentContent.id == chapter.content_id
            ).first()
        else:
            chapter.content = None
    
    return chapters

def get_chapter_by_id(db: Session, chapter_id: int) -> Optional[DocumentChapter]:
    """根据ID获取章节（带内容）"""
    chapter = db.query(DocumentChapter).filter(DocumentChapter.id == chapter_id).first()
    if not chapter:
        return None
    
    if chapter.content_id:
        chapter.content = db.query(DocumentContent).filter(
            DocumentContent.id == chapter.content_id
        ).first()
    else:
        chapter.content = None
    
    return chapter

def update_chapter(db: Session, chapter_id: int, chapter_update: DocumentChapterUpdate) -> Optional[DocumentChapter]:
    """更新章节"""
    db_chapter = db.query(DocumentChapter).filter(DocumentChapter.id == chapter_id).first()
    if not db_chapter:
        return None
    
    update_data = chapter_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_chapter, field, value)
    
    db_chapter.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_chapter)
    
    # 获取更新后的内容
    if db_chapter.content_id:
        db_chapter.content = db.query(DocumentContent).filter(
            DocumentContent.id == db_chapter.content_id
        ).first()
    else:
        db_chapter.content = None
    
    return db_chapter

def delete_chapter(db: Session, chapter_id: int) -> bool:
    """删除章节"""
    db_chapter = db.query(DocumentChapter).filter(DocumentChapter.id == chapter_id).first()
    if not db_chapter:
        return False
    
    # 删除相关内容
    if db_chapter.content_id:
        db.query(DocumentContent).filter(DocumentContent.id == db_chapter.content_id).delete()
    
    db.delete(db_chapter)
    db.commit()
    return True

def create_content(db: Session, content: DocumentContentCreate) -> DocumentContent:
    """创建内容"""
    # 计算字数和阅读时间
    word_count = 0
    reading_time_minutes = 0
    
    if content.html_content:
        # 简单计算：去除HTML标签后的文本字数
        import re
        text = re.sub(r'<[^>]+>', '', content.html_content)
        word_count = len(text.split())
        reading_time_minutes = max(1, word_count // 200)  # 假设每分钟200字
    
    db_content = DocumentContent(
        raw_content=content.raw_content,
        html_content=content.html_content,
        toc_json=content.toc_json,
        word_count=word_count,
        reading_time_minutes=reading_time_minutes,
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def get_content_by_id(db: Session, content_id: int) -> Optional[DocumentContent]:
    """根据ID获取内容"""
    return db.query(DocumentContent).filter(DocumentContent.id == content_id).first()

def update_content(db: Session, content_id: int, content_update: DocumentContentUpdate) -> Optional[DocumentContent]:
    """更新内容"""
    db_content = db.query(DocumentContent).filter(DocumentContent.id == content_id).first()
    if not db_content:
        return None
    
    update_data = content_update.dict(exclude_unset=True)
    
    # 重新计算字数和阅读时间
    if 'html_content' in update_data and update_data['html_content']:
        import re
        text = re.sub(r'<[^>]+>', '', update_data['html_content'])
        update_data['word_count'] = len(text.split())
        update_data['reading_time_minutes'] = max(1, update_data['word_count'] // 200)
    
    for field, value in update_data.items():
        setattr(db_content, field, value)
    
    db_content.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_content)
    return db_content

def sync_from_github(db: Session, sync_task: SyncTaskCreate, background_tasks) -> SyncTask:
    """从GitHub同步文档（简化版，实际需要实现GitHub API调用）"""
    # 创建同步任务记录
    db_task = SyncTask(
        task_type=sync_task.task_type,
        github_repo=sync_task.github_repo,
        github_branch=sync_task.github_branch,
        file_path=sync_task.file_path,
        document_id=sync_task.document_id,
        status="pending",
        started_at=datetime.utcnow(),
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 在实际应用中，这里会调用GitHub API获取Typst文件
    # 然后解析Typst文件，更新数据库
    # 这里我们只模拟同步过程
    
    def perform_sync():
        try:
            # 更新任务状态为运行中
            db_task.status = "running"
            db.commit()
            
            # 模拟同步过程
            # TODO: 实际实现GitHub API调用和Typst解析
            
            db_task.status = "success"
            db_task.completed_at = datetime.utcnow()
            db_task.log_message = "同步完成（模拟）"
        except Exception as e:
            db_task.status = "failed"
            db_task.completed_at = datetime.utcnow()
            db_task.error_message = str(e)
        finally:
            db.commit()
    
    # 在后台执行同步
    background_tasks.add_task(perform_sync)
    
    return db_task
