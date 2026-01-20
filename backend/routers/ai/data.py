"""
AI智能体数据管理路由
提供学生使用统计、对话记录查看等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from config.database import get_ai_db
from models.ai_models import AiUser, AiAgent, AiConversation, AiMessage

router = APIRouter()


@router.get("/students")
async def get_student_stats(
    class_name: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_ai_db)
):
    """获取学生使用统计列表"""
    # 基础查询：获取所有用户
    query = db.query(AiUser)

    # 班级筛选
    if class_name:
        query = query.filter(AiUser.class_name == class_name)

    # 搜索（姓名或学号）
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (AiUser.username.ilike(search_term)) |
            (AiUser.student_id.ilike(search_term))
        )

    # 计算总数
    total = query.count()

    # 分页
    offset = (page - 1) * page_size
    students = query.order_by(AiUser.username).offset(offset).limit(page_size).all()

    # 获取每个学生的统计信息
    student_stats = []
    for student in students:
        # 对话数
        conversation_count = db.query(AiConversation).filter(
            AiConversation.user_id == student.id
        ).count()

        # 消息数
        message_count = db.query(AiMessage).join(AiConversation).filter(
            AiConversation.user_id == student.id
        ).count()

        # 最后活跃时间（最新对话的创建时间）
        last_conversation = db.query(AiConversation).filter(
            AiConversation.user_id == student.id
        ).order_by(desc(AiConversation.start_time)).first()

        last_active = last_conversation.start_time if last_conversation else None

        student_stats.append({
            "id": student.id,
            "username": student.username,
            "student_id": student.student_id,
            "class_name": student.class_name,
            "conversation_count": conversation_count,
            "message_count": message_count,
            "last_active": last_active,
            "created_at": None,  # AiUser模型没有created_at字段
            "is_active": True,   # AiUser模型没有is_active字段，默认设为True
        })

    return {
        "success": True,
        "students": student_stats,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/stats")
async def get_system_stats(db: Session = Depends(get_ai_db)):
    """获取系统总体统计"""
    # 总对话数
    total_conversations = db.query(AiConversation).count()

    # 总消息数
    total_messages = db.query(AiMessage).count()

    # 总用户数
    total_users = db.query(AiUser).count()

    # 活跃用户数（有对话的用户）
    active_users = db.query(func.count(func.distinct(AiConversation.user_id))).scalar()

    # 活跃智能体数
    active_agents = db.query(AiAgent).filter(AiAgent.is_active == True).count()

    # 今日新增对话数
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_conversations = db.query(AiConversation).filter(
        AiConversation.start_time >= today_start
    ).count()

    # 今日新增消息数
    today_messages = db.query(AiMessage).filter(
        AiMessage.created_at >= today_start
    ).count()

    return {
        "success": True,
        "stats": {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_users": total_users,
            "active_users": active_users,
            "active_agents": active_agents,
            "today_conversations": today_conversations,
            "today_messages": today_messages,
        }
    }


@router.get("/agents/ranking")
async def get_agents_ranking(
    limit: int = 10,
    db: Session = Depends(get_ai_db)
):
    """获取智能体使用排名"""
    # 按对话数排名
    agent_ranking = db.query(
        AiAgent.id,
        AiAgent.name,
        AiAgent.api_type,
        func.count(AiConversation.id).label('conversation_count')
    ).outerjoin(AiConversation, AiAgent.id == AiConversation.agent_id)\
     .group_by(AiAgent.id)\
     .order_by(desc('conversation_count'))\
     .limit(limit)\
     .all()

    result = []
    for agent in agent_ranking:
        result.append({
            "id": agent.id,
            "name": agent.name,
            "api_type": agent.api_type,
            "conversation_count": agent.conversation_count,
        })

    return {
        "success": True,
        "ranking": result
    }


@router.get("/students/{student_id}/conversations")
async def get_student_conversations(
    student_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_ai_db)
):
    """获取学生对话列表"""
    # 验证用户存在
    student = db.query(AiUser).filter(AiUser.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 基础查询
    query = db.query(AiConversation).filter(AiConversation.user_id == student_id)

    # 时间范围筛选
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(AiConversation.start_time >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="开始日期格式错误，请使用YYYY-MM-DD格式")

    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
            # 结束日期包含当天
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            query = query.filter(AiConversation.start_time <= end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="结束日期格式错误，请使用YYYY-MM-DD格式")

    # 计算总数
    total = query.count()

    # 分页
    offset = (page - 1) * page_size
    conversations = query.order_by(desc(AiConversation.start_time)).offset(offset).limit(page_size).all()

    # 获取对话详情
    conversation_list = []
    for conv in conversations:
        # 获取智能体名称
        agent = db.query(AiAgent).filter(AiAgent.id == conv.agent_id).first()
        agent_name = agent.name if agent else "未知智能体"

        conversation_list.append({
            "id": conv.id,
            "title": conv.title,
            "agent_name": agent_name,
            "start_time": conv.start_time,
            "total_messages": conv.total_messages,
            "total_tokens": conv.total_tokens,
        })

    return {
        "success": True,
        "conversations": conversation_list,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation_details(
    conversation_id: int,
    db: Session = Depends(get_ai_db)
):
    """获取对话详情"""
    conversation = db.query(AiConversation).filter(AiConversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 获取消息列表
    messages = db.query(AiMessage).filter(
        AiMessage.conversation_id == conversation_id
    ).order_by(AiMessage.created_at).all()

    # 获取用户信息
    user = db.query(AiUser).filter(AiUser.id == conversation.user_id).first()
    agent = db.query(AiAgent).filter(AiAgent.id == conversation.agent_id).first()

    # 格式化消息
    message_list = []
    for msg in messages:
        message_list.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at,
            "tokens": msg.tokens,
        })

    return {
        "success": True,
        "conversation": {
            "id": conversation.id,
            "title": conversation.title,
            "user": {
                "id": user.id if user else None,
                "username": user.username if user else "未知用户",
            },
            "agent": {
                "id": agent.id if agent else None,
                "name": agent.name if agent else "未知智能体",
            },
            "start_time": conversation.start_time,
            "total_messages": conversation.total_messages,
            "total_tokens": conversation.total_tokens,
        },
        "messages": message_list,
    }
