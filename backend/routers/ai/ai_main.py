"""
AI智能体主路由 - 整合所有AI相关路由
前缀: /api/ai
"""
from fastapi import APIRouter

# 导入子路由
from .auth import router as auth_router
from .agents import router as agents_router
from .conversation import router as conversation_router
from .chat import router as chat_router
from .user_management import router as user_management_router
from .data import router as data_router

# 创建主路由器 - 禁用斜杠重定向
router = APIRouter(redirect_slashes=False)

# 包含子路由
router.include_router(auth_router, prefix="/auth", tags=["ai-auth"])
router.include_router(agents_router, prefix="/agents", tags=["ai-agents"])
router.include_router(conversation_router, prefix="/conversations", tags=["ai-conversations"])
router.include_router(chat_router, prefix="/chat", tags=["ai-chat"])
router.include_router(user_management_router, prefix="/user-management", tags=["ai-user-management"])
router.include_router(data_router, prefix="/data", tags=["ai-data"])

@router.get("/")
async def ai_root():
    """AI模块根路由"""
    return {
        "module": "AI智能体",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/ai/auth/*",
            "agents": "/api/ai/agents/*",
            "conversations": "/api/ai/conversations/*",
            "chat": "/api/ai/chat/*",
            "user-management": "/api/ai/user-management/*",
            "data": "/api/ai/data/*",
        },
        "status": "active"
    }

@router.get("/health")
async def ai_health():
    """AI模块健康检查"""
    return {
        "status": "healthy",
        "module": "AI智能体",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/ai/auth/*",
            "agents": "/api/ai/agents/*",
            "conversations": "/api/ai/conversations/*",
            "chat": "/api/ai/chat/*",
            "user-management": "/api/ai/user-management/*",
            "data": "/api/ai/data/*",
        }
    }
