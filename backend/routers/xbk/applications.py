"""
XBK登录路由 - 使用denglu表进行认证
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
import os
from config.database import XBK_DB_PATH, get_absolute_db_path

xbk_router = APIRouter(tags=["xbk"])

# 请求/响应模型
class LoginRequest(BaseModel):
    name: str
    student_id: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: dict

# 数据库连接函数
def get_db():
    """获取XBK数据库连接"""
    db_path = XBK_DB_PATH  # "backend/xbk.db"
    absolute_db_path = get_absolute_db_path(db_path)
    conn = sqlite3.connect(absolute_db_path)
    conn.row_factory = sqlite3.Row  # 返回字典格式的结果
    return conn

# 登录路由
@xbk_router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """登录验证，使用denglu表"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, student_id FROM denglu WHERE name = ? AND student_id = ?",
        (login_request.name, login_request.student_id)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或学号不正确"
        )
    
    return {
        "success": True,
        "message": "登录成功",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "student_id": user["student_id"]
        }
    }

# 健康检查端点
@xbk_router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

# 获取用户列表（可选，用于调试）
@xbk_router.get("/users")
async def get_users():
    """获取所有用户（仅用于调试）"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, student_id FROM denglu")
    rows = cursor.fetchall()
    conn.close()
    
    users = [dict(row) for row in rows]
    
    return {
        "success": True,
        "users": users
    }
