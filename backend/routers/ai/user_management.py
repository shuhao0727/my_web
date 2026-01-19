"""
AI智能体 - 用户管理路由（包含Excel导入）
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd
import io
from datetime import datetime
import hashlib
import uuid

from config.database import get_ai_db
from models.ai_models import AiUser

router = APIRouter(tags=["ai-user-management"])

# 请求和响应模型
class UserCreate(BaseModel):
    username: str
    student_id: str
    class_name: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    student_id: Optional[str] = None
    class_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    student_id: str
    class_name: Optional[str] = None

class UserListResponse(BaseModel):
    success: bool
    users: List[UserResponse]
    total: int
    page: int
    page_size: int

class ImportResult(BaseModel):
    success: bool
    imported_count: int
    skipped_count: int
    errors: List[str]

# 辅助函数
def generate_default_password(student_id: str) -> str:
    """生成默认密码（学号后6位）"""
    if len(student_id) >= 6:
        return student_id[-6:]
    return student_id

def hash_password(password: str) -> str:
    """密码哈希（SHA256）"""
    return hashlib.sha256(password.encode()).hexdigest()

# 用户管理API
@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（用户名、姓名、学号）"),
    db: Session = Depends(get_ai_db)
):
    """获取用户列表（带分页和搜索）"""
    query = db.query(AiUser)
    
    # 搜索
    if search:
        query = query.filter(
            or_(
                AiUser.username.ilike(f"%{search}%"),
                AiUser.student_id.ilike(f"%{search}%"),
                AiUser.class_name.ilike(f"%{search}%")
            )
        )
    
    # 总数
    total = query.count()
    
    # 分页（按ID降序，最新创建的在前）
    users = query.order_by(AiUser.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
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
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_ai_db)
):
    """创建新用户"""
    # 检查用户名是否已存在
    existing_user = db.query(AiUser).filter(AiUser.username == user_data.username).first()  # type: ignore
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查学号是否已存在
    if user_data.student_id:
        existing_student = db.query(AiUser).filter(AiUser.student_id == user_data.student_id).first()  # type: ignore
        if existing_student is not None:
            raise HTTPException(status_code=400, detail="学号已存在")
    
    # 生成默认密码
    default_password = generate_default_password(user_data.student_id)
    password_hash = hash_password(default_password)
    
    # 创建用户
    new_user = AiUser(
        username=user_data.username,
        password_hash=password_hash,
        student_id=user_data.student_id,
        class_name=user_data.class_name,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "success": True,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "student_id": new_user.student_id,
            "class_name": new_user.class_name,
        },
        "message": "用户创建成功"
    }

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_ai_db)
):
    """更新用户信息"""
    user = db.query(AiUser).filter(AiUser.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新字段
    if user_data.username is not None:
        user.username = user_data.username  # type: ignore
    
    if user_data.student_id is not None:
        # 检查学号是否已被其他用户使用
        existing_student = db.query(AiUser).filter(
            AiUser.student_id == user_data.student_id,
            AiUser.id != user_id
        ).first()
        if existing_student is not None:
            raise HTTPException(status_code=400, detail="学号已被其他用户使用")
        user.student_id = user_data.student_id  # type: ignore
    
    if user_data.class_name is not None:
        user.class_name = user_data.class_name  # type: ignore
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "student_id": user.student_id,
            "class_name": user.class_name,
        },
        "message": f"用户 {user.username} 更新成功"
    }

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_ai_db)
):
    """删除用户"""
    user: Optional[AiUser] = db.query(AiUser).filter(AiUser.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    else:
        # 不允许删除admin用户
        if user.username == "admin":
            raise HTTPException(status_code=400, detail="不能删除管理员账户")
        
        db.delete(user)
        db.commit()
        
        return {"success": True, "message": f"用户 {user.username} 删除成功"}

@router.post("/users/import")
async def import_users_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_ai_db)
):
    """从Excel导入用户"""
    # 检查文件类型
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):  # type: ignore
        raise HTTPException(status_code=400, detail="只支持Excel文件（.xlsx或.xls）")
    
    content = await file.read()
    
    try:
        # 读取Excel文件
        df = pd.read_excel(io.BytesIO(content))
        
        # 检查必要的列 - 根据实际数据库要求：用户名、学号、班级
        required_columns = ['用户名', '学号', '班级']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Excel文件缺少必要列: {col}")  # type: ignore
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        # 处理每一行
        for index, row in df.iterrows():
            try:
                # 检查用户名是否已存在
                existing_user = db.query(AiUser).filter(AiUser.username == str(row['用户名'])).first()
                if existing_user is not None:
                    errors.append(f"第{int(index)+2}行: 用户名'{row['用户名']}'已存在，跳过")  # type: ignore
                    skipped_count += 1
                    continue
                
                # 检查学号是否已存在
                if pd.notna(row['学号']):
                    student_id = str(row['学号'])
                    existing_student = db.query(AiUser).filter(AiUser.student_id == student_id).first()
                    if existing_student is not None:
                        errors.append(f"第{int(index)+2}行: 学号'{row['学号']}'已存在，跳过")  # type: ignore
                        skipped_count += 1
                        continue
                else:
                    student_id = str(uuid.uuid4())[:8]  # 生成随机学号
                
                # 解析班级
                class_name = None
                if pd.notna(row['班级']):
                    class_name = str(row['班级']).strip()
                
                # 生成默认密码（使用学号后6位，如果学号长度不足则使用整个学号）
                default_password = generate_default_password(student_id)
                password_hash = hash_password(default_password)
                
                # 创建用户 - 用户名作为姓名，班级可选
                username = str(row['用户名'])
                new_user = AiUser(
                    username=username,
                    password_hash=password_hash,
                    student_id=student_id,
                    class_name=class_name,
                )
                
                # 尝试添加并提交每个用户，独立事务
                try:
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)  # 刷新以获取数据库生成的id
                    imported_count += 1
                except Exception as e:
                    db.rollback()  # 回滚当前用户的插入
                    errors.append(f"第{int(index)+2}行: 插入数据库失败 - {str(e)}")  # type: ignore
                    skipped_count += 1
                
            except Exception as e:
                errors.append(f"第{int(index)+2}行: 处理失败 - {str(e)}")  # type: ignore
                skipped_count += 1
        
        return {
            "success": True,
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "errors": errors[:10]  # 只返回前10个错误，避免响应过大
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Excel文件处理失败: {str(e)}")  # type: ignore

@router.get("/users/export-template")
async def export_template():
    """导出Excel模板"""
    # 创建模板数据 - 实际数据库字段要求：用户名、学号、班级
    template_data = {
        '用户名': ['张三', '李四'],
        '学号': ['20230001', '20230002'],
        '班级': ['13', '12']
    }
    
    df = pd.DataFrame(template_data)
    
    # 将DataFrame写入Excel字节流
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='模板', index=False)
    
    output.seek(0)
    excel_data = output.getvalue()
    
    # 返回二进制响应，设置正确的Content-Type和Content-Disposition
    # 使用ASCII文件名避免编码问题
    return Response(
        content=excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=student_import_template.xlsx"
        }
    )
