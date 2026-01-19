"""
AI智能体 - 用户认证路由
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import hashlib
import time
from datetime import datetime

from config.database import get_ai_db
from models.ai_models import AiUser

router = APIRouter(tags=["ai-auth"])
security = HTTPBearer()

# 请求模型
class LoginRequest(BaseModel):
    username: str
    student_id: Optional[str] = None

# 模拟token生成和验证（实际应用中应使用JWT等安全机制）
def create_token(user_id: int, username: str) -> str:
    """创建模拟token"""
    import base64
    raw = f"{user_id}:{username}:{time.time()}"
    # 使用base64编码，便于解码
    token = base64.b64encode(raw.encode()).decode()
    return token

def verify_token(token: str) -> Optional[dict]:
    """验证token（模拟，实际应检查有效期等）"""
    import base64
    try:
        # 解码token
        raw = base64.b64decode(token.encode()).decode()
        parts = raw.split(":")
        if len(parts) == 3:
            user_id, username, _ = parts
            return {"user_id": int(user_id), "username": username}
    except:
        pass
    return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_ai_db)
) -> AiUser:
    """获取当前用户"""
    token = credentials.credentials
    user_info = verify_token(token)
    if user_info is None:
        raise HTTPException(status_code=401, detail="无效的token")
    
    user = db.query(AiUser).filter(AiUser.id == user_info["user_id"]).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    return user

@router.post("/login")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_ai_db)
):
    """用户登录"""
    # 根据用户名查找用户
    user = db.query(AiUser).filter(AiUser.username == request.username).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查学号（如果提供了student_id且非空）
    if request.student_id is not None and request.student_id != "":
        if user.student_id is None or user.student_id != request.student_id:
            raise HTTPException(status_code=400, detail="学号不正确")
    
    # 生成token
    token = create_token(user.id, user.username)  # type: ignore
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "student_id": user.student_id,
            "class_name": user.class_name,
        },
        "token": token,
        "message": "登录成功"
    }

@router.get("/users")
async def get_users(
    current_user: AiUser = Depends(get_current_user),
    db: Session = Depends(get_ai_db)
):
    """获取用户列表（需要管理员权限）"""
    # 检查是否为admin用户（用户名必须为"admin"）
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    users = db.query(AiUser).all()
    
    return {
        "success": True,
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "student_id": user.student_id,
                "class_name": user.class_name,
            }
            for user in users
        ],
        "total": len(users)
    }

@router.get("/me")
async def get_current_user_info(current_user: AiUser = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "student_id": current_user.student_id,
            "class_name": current_user.class_name,
        }
    }
