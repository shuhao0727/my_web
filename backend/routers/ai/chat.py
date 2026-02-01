"""
AI智能体 - 聊天路由
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime
import json
import logging
import os
import re
from pydantic import BaseModel

from config.database import get_ai_db
from models.ai_models import AiConversation, AiMessage, AiAgent, AiUser
from services.deepseek_client import DeepSeekClient
from services.dify_client import DifyClient
from services.api_client import ApiCallRecorder

# 导入simple_ai_chat模块
from services.simple_ai_chat import chat_with_agent_id, test_agent_connection

# 请求/响应模型
class ChatRequest(BaseModel):
    user_id: int
    agent_id: int
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    success: bool
    conversation: dict
    messages: list[dict]
    message: str

logger = logging.getLogger(__name__)

def markdown_to_html(text: str) -> str:
    """将Markdown转换为HTML（基本转换）"""
    if not text:
        return text
    
    # 这里我们保留Markdown，由前端react-markdown库进行渲染
    # 所以直接返回原始文本
    return text

router = APIRouter(redirect_slashes=False)

@router.post("/", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_ai_db)
):
    """与AI智能体聊天"""
    # 从请求中获取参数
    user_id = chat_request.user_id
    agent_id = chat_request.agent_id
    message = chat_request.message
    conversation_id = chat_request.conversation_id
    
    # 检查用户是否存在
    user = db.query(AiUser).filter(AiUser.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查智能体是否存在且活跃
    from sqlalchemy import true
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id, AiAgent.is_active.is_(true())).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="智能体不存在或不可用")
    
    # 检查对话是否存在
    conversation = None
    if conversation_id:
        conversation = db.query(AiConversation).filter(
            AiConversation.id == conversation_id,
            AiConversation.user_id == user_id,
            AiConversation.agent_id == agent_id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在或不属于该用户")
    
    # 如果没有对话，创建一个新的
    if not conversation:
        session_id = str(uuid.uuid4())
        conversation = AiConversation(
            session_id=session_id,
            user_id=user_id,
            agent_id=agent_id,
            title=f"与{agent.name}的对话",
            start_time=datetime.now(),
            total_messages=0,
            total_tokens=0,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # 保存用户消息
    user_message = AiMessage(
        conversation_id=conversation.id,
        role="user",
        content=message,
        tokens=len(message) // 4,  # 简单估算：每个token约4个字符
    )
    db.add(user_message)
    
    # 根据智能体类型生成回复
    ai_response = ""
    api_call_record = None
    start_time = datetime.now()
    
    try:
        # 调用simple_ai_chat模块中的chat_with_agent_id函数
        # 数据库路径：znt.db 位于backend目录下
        db_path = os.path.join(os.path.dirname(__file__), "../../znt.db")
        ai_response = await chat_with_agent_id(db_path, agent_id, message, user_id)
        
        # 记录API调用
        end_time = datetime.now()
        api_call_record = ApiCallRecorder.record_call(
            api_type=str(agent.api_type),  # type: ignore
            agent_id=agent.id,  # type: ignore
            user_id=user.id,  # type: ignore
            conversation_id=conversation.id if conversation else None,  # type: ignore
            request_data={"message": message},
            response_data={"response": ai_response},
            start_time=start_time,
            end_time=end_time,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"AI智能体回复生成失败: {e}")
        end_time = datetime.now()
        ai_response = f"抱歉，{agent.name}暂时无法处理您的请求。错误信息：{str(e)}"
        # 记录失败的API调用
        api_call_record = ApiCallRecorder.record_call(
            api_type=str(agent.api_type),  # type: ignore
            agent_id=agent.id,  # type: ignore
            user_id=user.id,  # type: ignore
            conversation_id=conversation.id if conversation else None,  # type: ignore
            request_data={"message": message},
            response_data={"error": str(e)},
            start_time=start_time,
            end_time=end_time,
            status="error",
            error_message=str(e)
        )
    
    # 保留Markdown格式，前端使用react-markdown渲染
    # 使用markdown_to_html函数（目前直接返回原始文本）
    processed_ai_response = markdown_to_html(ai_response)
    
    # 保存AI回复（保留Markdown格式）
    ai_message = AiMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=processed_ai_response,
        tokens=len(processed_ai_response) // 4,
    )
    db.add(ai_message)
    
    # 更新对话统计
    # 使用setattr避免Pylance类型检查错误
    setattr(conversation, 'total_messages', conversation.total_messages + 2)
    setattr(conversation, 'total_tokens', (conversation.total_tokens or 0) + (user_message.tokens or 0) + (ai_message.tokens or 0))
    setattr(conversation, 'end_time', datetime.now())
    
    # 如果需要，可以保存API调用记录到数据库（这里仅打印日志）
    if api_call_record:
        logger.info(f"API调用记录: {api_call_record}")
    
    db.commit()
    
    # 获取对话中的所有消息，按ID升序排列（最旧的在最前） - ID自增，能准确反映插入顺序
    messages = db.query(AiMessage).filter(
        AiMessage.conversation_id == conversation.id
    ).order_by(AiMessage.id.asc()).all()
    
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
        "messages": [
            {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content,
                "tokens": msg.tokens,
                "created_at": msg.created_at,
            }
            for msg in messages
        ],
        "message": "消息发送成功"
    }

@router.post("/stream")
async def chat_stream(
    chat_request: ChatRequest,
    db: Session = Depends(get_ai_db)
):
    """流式聊天（简化版本，返回完整响应）"""
    # 使用非流式聊天接口
    result = await chat(chat_request, db)
    
    # 返回相同格式，标记为流式
    return {
        "success": True,
        "conversation": result["conversation"],
        "messages": result["messages"],
        "message": "流式消息发送成功",
        "stream": True
    }

@router.get("/agents/{agent_id}/test")
async def test_agent_api(
    agent_id: int,
    db: Session = Depends(get_ai_db)
):
    """测试智能体API连通性 - 使用新的test_agent_connection函数"""
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    try:
        # 构建智能体配置，处理可能的空值
        config = {
            "id": agent.id,
            "name": str(agent.name) if agent.name is not None else "",
            "api_type": str(agent.api_type) if agent.api_type is not None else "",
            "api_key": str(agent.api_key) if agent.api_key is not None else "",
            "base_url": str(agent.base_url) if agent.base_url is not None else "",
            "model": str(agent.model) if agent.model is not None else "",
            "app_id": str(agent.app_id) if agent.app_id is not None else "",
            "is_active": bool(agent.is_active) if agent.is_active is not None else False
        }
        
        # 使用新的test_agent_connection函数进行测试
        test_result = await test_agent_connection(config)
        
        # 构建响应
        return {
            "success": True,
            "agent": {
                "id": agent.id,
                "name": agent.name,
                "api_type": agent.api_type,
                "is_active": agent.is_active,
            },
            "test_message": "你好，测试消息",
            "response": test_result.get("test_response", test_result.get("message", "连接测试完成")),
            "tokens": len(test_result.get("test_response", test_result.get("message", ""))) // 4,
            "status": "success" if test_result.get("success") else "failed",
            "test_result": test_result  # 包含详细的测试结果信息
        }
    except Exception as e:
        logger.error(f"测试智能体API连接失败: {e}")
        return {
            "success": True,
            "agent": {
                "id": agent.id,
                "name": agent.name,
                "api_type": agent.api_type,
                "is_active": agent.is_active,
            },
            "test_message": "你好，测试消息",
            "response": f"测试过程中出现错误：{str(e)}",
            "tokens": 1,
            "status": "error",
            "error": str(e)
        }
