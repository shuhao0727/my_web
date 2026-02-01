"""
AI智能体 - 智能体管理路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from config.database import get_ai_db
from models.ai_models import AiAgent

router = APIRouter(redirect_slashes=False)

# Pydantic models for request/response
class AgentCreateRequest(BaseModel):
    name: str
    api_type: str  # 'deepseek' or 'dify'
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    app_id: Optional[str] = None
    is_active: bool = True

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    api_type: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    app_id: Optional[str] = None
    is_active: Optional[bool] = None

class AgentStatusUpdateRequest(BaseModel):
    is_active: bool

@router.get("", include_in_schema=False)
@router.get("/")
async def get_agents(
    active_only: bool = False,
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
            (AiAgent.model.ilike(search_term)) |
            (AiAgent.app_id.ilike(search_term))
        )
    
    if api_type:
        query = query.filter(AiAgent.api_type == api_type)
    
    agents = query.order_by(AiAgent.created_at.desc()).all()
    
    return {
        "success": True,
        "agents": [
            {
                "id": agent.id,
                "name": agent.name,
                "api_type": agent.api_type,
                "api_key": agent.api_key,
                "base_url": agent.base_url,
                "model": agent.model,
                "app_id": agent.app_id,
                "is_active": agent.is_active,
                "created_at": agent.created_at,
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
            "api_type": agent.api_type,
            "api_key": agent.api_key,
            "base_url": agent.base_url,
            "model": agent.model,
            "app_id": agent.app_id,
            "is_active": agent.is_active,
            "created_at": agent.created_at,
        }
    }

@router.post("", include_in_schema=False)
@router.post("/")
async def create_agent(
    agent_data: AgentCreateRequest,
    db: Session = Depends(get_ai_db)
):
    """创建智能体（管理员）"""
    # 检查名称是否已存在
    existing = db.query(AiAgent).filter(AiAgent.name == agent_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="智能体名称已存在")
    
    # 验证api_type必须是deepseek或dify
    if agent_data.api_type not in ['deepseek', 'dify']:
        raise HTTPException(status_code=400, detail="API类型必须是'deepseek'或'dify'")
    
    # 处理Dify智能体的app_id：如果未提供但api_key以'app-'开头，则从api_key提取
    app_id = agent_data.app_id
    if agent_data.api_type == 'dify' and (not app_id or app_id.strip() == ''):
        if agent_data.api_key and agent_data.api_key.startswith('app-'):
            app_id = agent_data.api_key.replace('app-', '')
    
    agent = AiAgent(
        name=agent_data.name,
        api_type=agent_data.api_type,
        api_key=agent_data.api_key,
        base_url=agent_data.base_url,
        model=agent_data.model,
        app_id=app_id,
        is_active=agent_data.is_active,
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return {
        "success": True,
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "api_type": agent.api_type,
            "api_key": agent.api_key,
            "base_url": agent.base_url,
            "model": agent.model,
            "app_id": agent.app_id,
            "is_active": agent.is_active,
            "created_at": agent.created_at,
        },
        "message": "智能体创建成功"
    }

@router.put("/{agent_id}")
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdateRequest,
    db: Session = Depends(get_ai_db)
):
    """更新智能体（管理员）"""
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    # 更新名称（如果提供）
    if agent_data.name is not None:
        # 检查名称是否与其他智能体冲突
        existing = db.query(AiAgent).filter(AiAgent.name == agent_data.name, AiAgent.id != agent_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="智能体名称已存在")
        agent.name = agent_data.name  # type: ignore
    
        # 更新API类型（如果提供）
        if agent_data.api_type is not None:
            if agent_data.api_type not in ['deepseek', 'dify']:
                raise HTTPException(status_code=400, detail="API类型必须是'deepseek'或'dify'")
            agent.api_type = agent_data.api_type  # type: ignore
    
            # 更新API密钥（如果提供）
            if agent_data.api_key is not None:
                agent.api_key = agent_data.api_key  # type: ignore
                
                # 如果更新了API密钥且是Dify类型，且app_id为空，尝试从新api_key提取
                app_id_value = agent.app_id
                api_type_value = agent.api_type
                # 获取实际的列值进行判断
                if api_type_value == 'dify' and (app_id_value is None or (app_id_value is not None and str(app_id_value).strip() == '')):  # type: ignore
                    if agent_data.api_key and agent_data.api_key.startswith('app-'):
                        agent.app_id = agent_data.api_key.replace('app-', '')  # type: ignore
    
    # 更新基础URL（如果提供）
    if agent_data.base_url is not None:
        agent.base_url = agent_data.base_url  # type: ignore
    
    # 更新模型（如果提供）
    if agent_data.model is not None:
        agent.model = agent_data.model  # type: ignore
    
    # 更新应用ID（如果提供）
    if agent_data.app_id is not None:
        agent.app_id = agent_data.app_id  # type: ignore
    
    # 更新状态（如果提供）
    if agent_data.is_active is not None:
        agent.is_active = agent_data.is_active  # type: ignore
    
    db.commit()
    db.refresh(agent)
    
    return {
        "success": True,
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "api_type": agent.api_type,
            "api_key": agent.api_key,
            "base_url": agent.base_url,
            "model": agent.model,
            "app_id": agent.app_id,
            "is_active": agent.is_active,
            "created_at": agent.created_at,
        },
        "message": "智能体更新成功"
    }

@router.put("/{agent_id}/status")
async def update_agent_status(
    agent_id: int,
    status_data: AgentStatusUpdateRequest,
    db: Session = Depends(get_ai_db)
):
    """更新智能体状态"""
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    agent.is_active = status_data.is_active  # type: ignore
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

@router.post("/{agent_id}/test-connection")
async def test_agent_connection(agent_id: int, db: Session = Depends(get_ai_db)):
    """测试智能体连接"""
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    try:
        # 检查必要的配置
        api_key = str(agent.api_key) if agent.api_key is not None else ""
        base_url = str(agent.base_url) if agent.base_url is not None else ""
        
        if not api_key.strip():
            return {
                "success": False,
                "message": "API密钥未设置",
                "agent": {
                    "id": agent.id,
                    "name": agent.name,
                    "api_type": agent.api_type
                }
            }
        
        if not base_url.strip():
            return {
                "success": False,
                "message": "基础URL未设置",
                "agent": {
                    "id": agent.id,
                    "name": agent.name,
                    "api_type": agent.api_type
                }
            }
        
        # 根据智能体类型创建相应的客户端
        agent_api_type = agent.api_type
        if agent_api_type == 'dify':  # type: ignore
            from services.dify_client import DifyClient
            # 对于Dify，使用DifyClient，并传入app_id（如果存在）
            app_id_val = agent.app_id
            app_id = str(app_id_val) if app_id_val is not None else None
            client = DifyClient(
                api_key=api_key,
                base_url=base_url,
                app_id=app_id,
                timeout=10
            )
        elif agent_api_type == 'deepseek':  # type: ignore
            from services.deepseek_client import DeepSeekClient
            client = DeepSeekClient(
                api_key=api_key,
                base_url=base_url,
                timeout=10
            )
        else:
            from services.api_client import ApiClient
            client = ApiClient(
                api_key=api_key,
                base_url=base_url,
                timeout=10
            )
        
        # 测试连接
        test_result = await client.test_connection()
        
        # 根据实际测试结果返回，而不是总是返回成功
        return {
            "success": test_result.get("success", False),
            "message": test_result.get("message", "连接测试完成"),
            "test_result": test_result,
            "agent": {
                "id": agent.id,
                "name": agent.name,
                "api_type": agent.api_type
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"连接测试失败: {str(e)}",
            "agent": {
                "id": agent.id,
                "name": agent.name,
                "api_type": agent.api_type
            }
        }
