"""
XBK数据处理 - 安全认证路由
使用JWT提供安全的用户认证，基于学生信息表验证
"""
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from .database import get_db as get_xbk_db

router = APIRouter(prefix="/auth", tags=["xbk-auth"])
security = HTTPBearer()

# 从环境变量获取JWT密钥，如果不存在则使用安全的默认值
JWT_SECRET_KEY = os.getenv("XBK_JWT_SECRET_KEY", "xbk-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 请求/响应模型
class LoginRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    student_id: str = Field(..., min_length=1, max_length=50)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒数

class UserInfo(BaseModel):
    name: str
    student_id: str
    class_name: Optional[str] = None
    user_type: str = "student"  # student 或 admin

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
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInfo:
    """获取当前用户（使用JWT验证）"""
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token或token已过期",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    student_id = payload.get("student_id")
    name = payload.get("name")
    user_type = payload.get("user_type", "student")
    class_name = payload.get("class_name")
    
    if student_id is None or name is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 如果是管理员用户，直接返回（不需要查询student_info表）
    if user_type == "admin":
        return UserInfo(
            name=name,
            student_id=student_id,
            class_name=class_name,
            user_type=user_type
        )
    
    # 学生用户需要验证student_info表
    db = get_xbk_db()
    try:
        cursor = db.cursor()
        
        # 获取当前系统配置的年份和年级
        cursor.execute("SELECT config_value FROM system_config WHERE config_key='current_year'")
        current_year_row = cursor.fetchone()
        cursor.execute("SELECT config_value FROM system_config WHERE config_key='current_grade'")
        current_grade_row = cursor.fetchone()
        
        current_year = current_year_row[0] if current_year_row else None
        current_grade = current_grade_row[0] if current_grade_row else None
        
        if not current_year or not current_grade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统配置不完整，请先配置当前年份和年级"
            )
        
        # 查询学生信息
        cursor.execute("""
            SELECT 学号, 姓名, 班级 
            FROM student_info 
            WHERE 年份=? AND 年级=? AND 学号=? AND 姓名=?
        """, (current_year, current_grade, student_id, name))
        
        student = cursor.fetchone()
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或信息不匹配",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return UserInfo(
            name=student[1],
            student_id=student[0],
            class_name=student[2] if len(student) > 2 else None,
            user_type="student"
        )
    finally:
        db.close()

@router.post("/login")
async def login(request: LoginRequest):
    """用户登录（支持管理员和学生）"""
    try:
        db = get_xbk_db()
        try:
            cursor = db.cursor()
            
            # 1. 首先检查denglu表（管理员用户）
            cursor.execute(
                "SELECT name, student_id FROM denglu WHERE name = ? AND student_id = ?",
                (request.name, request.student_id)
            )
            admin_user = cursor.fetchone()
            
            user_type = "student"
            class_name = None
            
            if admin_user:
                # 管理员用户
                user_type = "admin"
            else:
                # 2. 如果不是管理员，检查学生信息表
                # 获取当前系统配置的年份和年级
                cursor.execute("SELECT config_value FROM system_config WHERE config_key='current_year'")
                current_year_row = cursor.fetchone()
                cursor.execute("SELECT config_value FROM system_config WHERE config_key='current_grade'")
                current_grade_row = cursor.fetchone()
                
                current_year = current_year_row[0] if current_year_row else None
                current_grade = current_grade_row[0] if current_grade_row else None
                
                if not current_year or not current_grade:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="系统配置不完整，请先配置当前年份和年级"
                    )
                
                # 根据学号和姓名查找学生
                cursor.execute("""
                    SELECT 学号, 姓名, 班级 
                    FROM student_info 
                    WHERE 年份=? AND 年级=? AND 学号=? AND 姓名=?
                """, (current_year, current_grade, request.student_id, request.name))
                
                student = cursor.fetchone()
                
                if student is None:
                    # 为防止用户名枚举攻击，返回相同的错误信息
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="姓名或学号不正确"
                    )
                
                class_name = student[2] if len(student) > 2 else None
            
            # 创建token
            access_token = create_access_token(data={
                "student_id": request.student_id,
                "name": request.name,
                "class_name": class_name,
                "user_type": user_type
            })
            
            return {
                "success": True,
                "user": {
                    "name": request.name,
                    "student_id": request.student_id,
                    "class_name": class_name,
                    "user_type": user_type
                },
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "message": "登录成功"
            }
        finally:
            db.close()
    except HTTPException:
        # 重新抛出HTTPException，FastAPI会处理为JSON响应
        raise
    except Exception as e:
        # 捕获其他异常，返回JSON格式的500错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(current_user: UserInfo = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "success": True,
        "user": {
            "name": current_user.name,
            "student_id": current_user.student_id,
            "class_name": current_user.class_name,
        }
    }
