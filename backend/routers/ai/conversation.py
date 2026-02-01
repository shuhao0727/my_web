"""
AI智能体 - 对话管理路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from config.database import get_ai_db
from models.ai_models import AiConversation, AiAgent

router = APIRouter(redirect_slashes=False)

@router.get("", include_in_schema=False)
@router.get("/")
async def get_conversations(
    user_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    include_messages: bool = False,
    db: Session = Depends(get_ai_db)
):
    """获取对话列表"""
    query = db.query(AiConversation)
    
    if user_id:
        query = query.filter(AiConversation.user_id == user_id)
    
    if agent_id:
        query = query.filter(AiConversation.agent_id == agent_id)
    
    conversations = query.order_by(AiConversation.start_time.desc()).offset(offset).limit(limit).all()
    
    # 获取对话总数
    total = query.count()
    
    # 如果不需要消息，只返回对话基本信息
    if not include_messages:
        return {
            "success": True,
            "conversations": [
                {
                    "id": conv.id,
                    "session_id": conv.session_id,
                    "user_id": conv.user_id,
                    "agent_id": conv.agent_id,
                    "title": conv.title,
                    "start_time": conv.start_time,
                    "end_time": conv.end_time,
                    "total_messages": conv.total_messages,
                    "total_tokens": conv.total_tokens,
                    "created_at": conv.created_at,
                    "updated_at": conv.updated_at,
                }
                for conv in conversations
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    # 如果需要消息，则包含消息
    result = []
    for conv in conversations:
        conv_data = {
            "id": conv.id,
            "session_id": conv.session_id,
            "user_id": conv.user_id,
            "agent_id": conv.agent_id,
            "title": conv.title,
            "start_time": conv.start_time,
            "end_time": conv.end_time,
            "total_messages": conv.total_messages,
            "total_tokens": conv.total_tokens,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
        }
        
        # 添加消息（如果有）
        if conv.messages:
            conv_data["messages"] = [
                {
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "role": msg.role,
                    "content": msg.content,
                    "tokens": msg.tokens,
                    "created_at": msg.created_at,
                }
                for msg in conv.messages
            ]
        else:
            conv_data["messages"] = []
        
        result.append(conv_data)
    
    return {
        "success": True,
        "conversations": result,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.post("/")
async def create_conversation(
    user_id: int,
    agent_id: int,
    title: Optional[str] = None,
    db: Session = Depends(get_ai_db)
):
    """创建新对话"""
    # 检查用户和智能体是否存在
    # 注意：这里我们假设用户和智能体都存在，为了简化不进行详细检查
    # 在实际应用中，应该检查用户和智能体的存在性
    
    # 生成会话ID
    session_id = str(uuid.uuid4())
    
    # 创建对话
    conversation = AiConversation(
        session_id=session_id,
        user_id=user_id,
        agent_id=agent_id,
        title=title or f"与AI的对话",
        start_time=datetime.now(),
        total_messages=0,
        total_tokens=0,
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return {
        "success": True,
        "conversation": {
            "id": conversation.id,
            "session_id": conversation.session_id,
            "user_id": conversation.user_id,
            "agent_id": conversation.agent_id,
            "title": conversation.title,
            "start_time": conversation.start_time,
            "end_time": conversation.end_time,
            "total_messages": conversation.total_messages,
            "total_tokens": conversation.total_tokens,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        },
        "message": "对话创建成功"
    }

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    include_messages: bool = True,
    db: Session = Depends(get_ai_db)
):
    """获取单个对话详情"""
    conversation = db.query(AiConversation).filter(AiConversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    result = {
        "id": conversation.id,
        "session_id": conversation.session_id,
        "user_id": conversation.user_id,
        "agent_id": conversation.agent_id,
        "title": conversation.title,
        "start_time": conversation.start_time,
        "end_time": conversation.end_time,
        "total_messages": conversation.total_messages,
        "total_tokens": conversation.total_tokens,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }
    
    if include_messages and conversation.messages:
        result["messages"] = [
            {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content,
                "tokens": msg.tokens,
                "created_at": msg.created_at,
            }
            for msg in conversation.messages
        ]
    else:
        result["messages"] = []
    
    return {
        "success": True,
        "conversation": result
    }

@router.put("/{conversation_id}")
async def update_conversation(
    conversation_id: int,
    title: Optional[str] = None,
    end_time: Optional[datetime] = None,
    total_messages: Optional[int] = None,
    total_tokens: Optional[int] = None,
    db: Session = Depends(get_ai_db)
):
    """更新对话信息"""
    conversation = db.query(AiConversation).filter(AiConversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    if title is not None:
        conversation.title = title  # type: ignore
    
    if end_time is not None:
        conversation.end_time = end_time  # type: ignore
    
    if total_messages is not None:
        conversation.total_messages = total_messages  # type: ignore
    
    if total_tokens is not None:
        conversation.total_tokens = total_tokens  # type: ignore
    
    db.commit()
    db.refresh(conversation)
    
    return {
        "success": True,
        "conversation": {
            "id": conversation.id,
            "session_id": conversation.session_id,
            "user_id": conversation.user_id,
            "agent_id": conversation.agent_id,
            "title": conversation.title,
            "start_time": conversation.start_time,
            "end_time": conversation.end_time,
            "total_messages": conversation.total_messages,
            "total_tokens": conversation.total_tokens,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        },
        "message": "对话更新成功"
    }

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_ai_db)
):
    """删除对话"""
    conversation = db.query(AiConversation).filter(AiConversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    db.delete(conversation)
    db.commit()
    
    return {
        "success": True,
        "message": "对话删除成功"
    }

@router.get("/user/{user_id}/summary")
async def get_user_conversation_summary(
    user_id: int,
    db: Session = Depends(get_ai_db)
):
    """获取用户对话统计摘要"""
    conversations = db.query(AiConversation).filter(AiConversation.user_id == user_id).all()
    
    total_conversations = len(conversations)
    total_messages = sum(conv.total_messages for conv in conversations)
    total_tokens = sum(conv.total_tokens for conv in conversations)
    
    # 按智能体统计
    agent_stats = {}
    for conv in conversations:
        agent_id = conv.agent_id
        if agent_id not in agent_stats:
            agent_stats[agent_id] = {
                "count": 0,
                "messages": 0,
                "tokens": 0
            }
        
        agent_stats[agent_id]["count"] += 1
        agent_stats[agent_id]["messages"] += conv.total_messages
        agent_stats[agent_id]["tokens"] += conv.total_tokens
    
    # 获取智能体名称
    agent_details = []
    for agent_id, stats in agent_stats.items():
        agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
        agent_name = agent.name if agent else f"智能体{agent_id}"
        agent_details.append({
            "agent_id": agent_id,
            "agent_name": agent_name,
            **stats
        })
    
    return {
        "success": True,
        "summary": {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "agent_breakdown": agent_details
        }
    }
