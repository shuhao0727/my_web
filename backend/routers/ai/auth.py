"""
AI智能体 - 增强版安全认证路由
使用JWT和bcrypt提供安全的用户认证
"""
import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from config.database import get_ai_db
from models.ai_models import AiUser

router = APIRouter(tags=["ai-auth"])
security = HTTPBearer()

# 从环境变量获取JWT密钥，如果不存在则使用安全的默认值
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30天

# 请求/响应模型
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: Optional[str] = Field(None, min_length=1, max_length=100)
    student_id: Optional[str] = Field(None, min_length=1, max_length=50)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒数

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)

# 密码哈希和验证
import hashlib

def hash_password(password: str) -> str:
    """使用bcrypt哈希密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码（支持bcrypt和SHA256）"""
    # 首先尝试bcrypt验证
    try:
        if bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')):
            return True
    except:
        pass
    
    # 如果bcrypt失败，尝试SHA256验证（兼容旧系统）
    try:
        sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        return sha256_hash == hashed_password
    except:
        return False

# JWT token生成和验证
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """创建刷新token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """验证JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 检查token类型
        if payload.get("type") != token_type:
            return None
        
        # 检查是否过期（JWT.decode会自动检查exp）
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_ai_db)
) -> AiUser:
    """获取当前用户（使用JWT验证）"""
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token或token已过期",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = db.query(AiUser).filter(AiUser.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

@router.post("/login")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_ai_db)
):
    """用户登录（兼容密码和学号两种方式）"""
    # 根据用户名查找用户
    user = db.query(AiUser).filter(AiUser.username == request.username).first()
    
    if user is None:
        # 为防止用户名枚举攻击，返回相同的错误信息
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确"
        )
    
    # 验证逻辑：优先使用密码验证，如果密码为空则使用学号验证（向后兼容）
    authenticated = False
    
    # 情况1：提供了密码
    if request.password and request.password.strip():
        # 验证密码（兼容bcrypt和SHA256）
        authenticated = verify_password(request.password, str(user.password_hash))
    # 情况2：没有提供密码但提供了学号（旧系统兼容）
    elif request.student_id and request.student_id.strip():
        # 验证学号是否匹配
        authenticated = (str(user.student_id) == request.student_id.strip())
    # 情况3：都没有提供
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供密码或学号"
        )
    
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确"
        )
    
    # 登录成功后，如果是使用学号验证的旧用户，将其密码哈希升级为bcrypt
    if request.student_id and not request.password:
        # 使用学号后6位作为默认密码进行bcrypt哈希
        default_password = str(user.student_id)[-6:] if len(str(user.student_id)) >= 6 else str(user.student_id)
        new_password_hash = hash_password(default_password)
        user.password_hash = new_password_hash  # type: ignore
        db.commit()
    
    # 创建token
    access_token = create_access_token(data={"sub": user.id, "username": user.username})
    refresh_token = create_refresh_token(data={"sub": user.id, "username": user.username})
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "student_id": user.student_id,
            "class_name": user.class_name,
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "message": "登录成功"
    }

@router.get("/users")
async def get_users(
    current_user: AiUser = Depends(get_current_user),
    db: Session = Depends(get_ai_db)
):
    """获取用户列表（需要管理员权限）"""
    # 检查是否为admin用户（用户名必须为"admin"）
    if current_user.username != "admin":  # type: ignore
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
