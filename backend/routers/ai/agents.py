"""
AI智能体 - 智能体管理路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from config.database import get_ai_db
from models.ai_models import AiAgent

router = APIRouter()

@router.get("/")
async def get_agents(
    active_only: bool = True,
    search: Optional[str] = None,
    api_type: Optional[str] = None,
    db: Session = Depends(get_ai_db)
):
    """获取智能体列表"""
    query = db.query(AiAgent)
    
    if active_only:
        query = query.filter(AiAgent.is_active == True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (AiAgent.name.ilike(search_term)) | 
            (AiAgent.description.ilike(search_term))
        )
    
    if api_type:
        query = query.filter(AiAgent.api_type == api_type)
    
    agents = query.all()
    
    return {
        "success": True,
        "agents": [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "icon": agent.icon,
                "api_type": agent.api_type,
                "api_config": agent.api_config,
                "is_active": agent.is_active,
                "created_at": agent.created_at,
                "updated_at": agent.updated_at,
            }
            for agent in agents
        ],
        "total": len(agents)
    }

@router.get("/types")
async def get_agent_types(db: Session = Depends(get_ai_db)):
    """获取智能体类型列表"""
    types = db.query(AiAgent.api_type).distinct().all()
    return {
        "success": True,
        "types": [t[0] for t in types]
    }

@router.get("/{agent_id}")
async def get_agent(agent_id: int, db: Session = Depends(get_ai_db)):
    """获取单个智能体详情"""
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    return {
        "success": True,
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "icon": agent.icon,
            "api_type": agent.api_type,
            "api_config": agent.api_config,
            "is_active": agent.is_active,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
        }
    }

@router.post("/")
async def create_agent(
    name: str,
    description: Optional[str] = None,
    icon: str = "🤖",
    api_type: str = "mock",
    api_config: Optional[dict] = None,
    is_active: bool = True,
    db: Session = Depends(get_ai_db)
):
    """创建智能体（管理员）"""
    # 检查名称是否已存在
    existing = db.query(AiAgent).filter(AiAgent.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="智能体名称已存在")
    
    agent = AiAgent(
        name=name,
        description=description,
        icon=icon,
        api_type=api_type,
        api_config=api_config or {},
        is_active=is_active,
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return {
        "success": True,
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "icon": agent.icon,
            "api_type": agent.api_type,
            "api_config": agent.api_config,
            "is_active": agent.is_active,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
        },
        "message": "智能体创建成功"
    }

@router.put("/{agent_id}")
async def update_agent(
    agent_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    api_type: Optional[str] = None,
    api_config: Optional[dict] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_ai_db)
):
    """更新智能体（管理员）"""
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    if name is not None:
        # 检查名称是否与其他智能体冲突
        existing = db.query(AiAgent).filter(AiAgent.name == name, AiAgent.id != agent_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="智能体名称已存在")
        agent.name = name
    
    if description is not None:
        agent.description = description
    
    if icon is not None:
        agent.icon = icon
    
    if api_type is not None:
        agent.api_type = api_type
    
    if api_config is not None:
        agent.api_config = api_config
    
    if is_active is not None:
        agent.is_active = is_active
    
    db.commit()
    db.refresh(agent)
    
    return {
        "success": True,
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "icon": agent.icon,
            "api_type": agent.api_type,
            "api_config": agent.api_config,
            "is_active": agent.is_active,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
        },
        "message": "智能体更新成功"
    }

@router.put("/{agent_id}/status")
async def update_agent_status(
    agent_id: int,
    is_active: bool,
    db: Session = Depends(get_ai_db)
):
    """更新智能体状态"""
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    agent.is_active = is_active
    db.commit()
    
    return {
        "success": True,
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "is_active": agent.is_active,
        },
        "message": "智能体状态更新成功"
    }

@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_ai_db)):
    """删除智能体（管理员）"""
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    db.delete(agent)
    db.commit()
    
    return {
        "success": True,
        "message": "智能体删除成功"
    }
