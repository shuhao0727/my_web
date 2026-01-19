// AI实验室组件类型定义

// 消息类型
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tokens?: number;
}

// 智能体类型
export interface AiAgent {
  id: number;
  name: string;
  description?: string;
  icon: string;
  api_type: string;
  api_config?: any;
  is_active: boolean;
}

// 对话类型
export interface Conversation {
  id: number;
  session_id: string;
  title: string;
  ai_agent: string;
  start_time: string;
  total_messages: number;
  total_tokens: number;
}

// 用户类型（与后端返回的用户数据对齐）
export interface User {
  id: number;
  username: string;
  student_id: string;
  class_name?: string;
  isAdmin: boolean; // 根据用户名是否为'admin'判断
}

// 登录表单类型
export interface LoginForm {
  username: string;
  studentId: string;
}

// 创建智能体表单类型
export interface CreateAgentForm {
  name: string;
  description: string;
  icon: string;
  api_type: string;
}
