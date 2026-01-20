"""
AI智能体 - 数据库模型（存储在独立的znt.db数据库中）
按照用户原始需求设计：用户表、智能体表、对话表、消息表
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, BigInteger, Index, func
from sqlalchemy.orm import relationship
from config.database import AiBase

class AiUser(AiBase):
    """AI智能体系统用户表（学生和管理员）"""
    __tablename__ = "ai_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)  # 用户名（唯一，作为姓名显示）
    password_hash = Column(String(255), nullable=False)                     # 密码哈希（实际应用需加密）
    student_id = Column(String(50), unique=True, index=True)               # 学号（学生专用）
    class_name = Column(String(100), nullable=True, index=True)            # 班级名称
    
    # 关系
    conversations = relationship("AiConversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AiUser(id={self.id}, username={self.username})>"

class AiAgent(AiBase):
    """AI智能体表"""
    __tablename__ = "ai_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)                  # 智能体名称
    api_type = Column(String(20), nullable=False)                           # API类型：deepseek 或 dify
    api_key = Column(String(255))                                           # API密钥
    base_url = Column(String(255))                                          # 基础URL
    model = Column(String(100))                                             # 模型名称（DeepSeek类用）
    app_id = Column(String(100))                                            # 应用ID（Dify类用）
    is_active = Column(Boolean, default=True, index=True)                  # 是否可用（admin可控制）
    created_at = Column(DateTime, server_default=func.now())               # 创建时间
    
    # 关系
    conversations = relationship("AiConversation", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AiAgent(id={self.id}, name={self.name}, api_type={self.api_type})>"

class AiConversation(AiBase):
    """AI对话会话表（记录每次对话的会话信息）"""
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("ai_users.id"), nullable=False, index=True)      # 用户ID
    agent_id = Column(Integer, ForeignKey("ai_agents.id"), nullable=False, index=True)    # 智能体ID
    session_id = Column(String(100), unique=True, index=True)                            # 会话ID（唯一）
    title = Column(String(200))                                                           # 对话标题（自动生成）
    start_time = Column(DateTime, server_default=func.now())               # 开始时间
    end_time = Column(DateTime)                                            # 结束时间
    total_messages = Column(Integer, default=0)                                           # 总消息数
    total_tokens = Column(BigInteger, default=0)                                          # 总token数
    conversation_metadata = Column(JSON)                                                  # 会话元数据（JSON格式）
    created_at = Column(DateTime, server_default=func.now())               # 创建时间
    updated_at = Column(DateTime, onupdate=func.now())                     # 更新时间
    
    # 关系
    user = relationship("AiUser", back_populates="conversations")
    agent = relationship("AiAgent", back_populates="conversations")
    messages = relationship("AiMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AiMessage.created_at")
    
    def __repr__(self):
        return f"<AiConversation(id={self.id}, user_id={self.user_id}, agent_id={self.agent_id})>"

class AiMessage(AiBase):
    """AI消息表（记录每条对话消息）"""
    __tablename__ = "ai_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False, index=True)  # 对话ID
    role = Column(String(20), nullable=False)                                                          # 角色：user/assistant
    content = Column(Text, nullable=False)                                                             # 消息内容
    tokens = Column(Integer)                                                                           # 消息消耗的token数
    message_metadata = Column(JSON)                                                                    # 消息元数据（JSON格式）
    created_at = Column(DateTime, server_default=func.now(), index=True)               # 创建时间（时间戳）
    
    # 关系
    conversation = relationship("AiConversation", back_populates="messages")
    
    def __repr__(self):
        return f"<AiMessage(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"

# 创建索引以提高查询性能
Index('ix_ai_conversations_user_agent', AiConversation.user_id, AiConversation.agent_id)
Index('ix_ai_messages_conversation_created', AiMessage.conversation_id, AiMessage.created_at)
Index('ix_ai_agents_active', AiAgent.is_active)
