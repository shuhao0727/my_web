// 智能体类型
export interface AiAgent {
  id: number;
  name: string;
  description?: string;
  icon: string;
  api_type: string;
  api_config?: any;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

// 学生类型（与数据库ai_users表对齐）
export interface Student {
  id: number;
  username: string;
  student_id: string;
  class_name?: string;
  last_login?: string;
  created_at: string;
  updated_at?: string;
  // 注意：数据库中没有以下字段，暂时保留以供未来扩展
  total_conversations?: number;
  total_messages?: number;
}

// 数据管理统计类型
export interface DataStats {
  total_conversations: number;
  total_messages: number;
  total_tokens: number;
  active_agents: number;
  total_users: number;
}

// 创建智能体表单类型
export interface CreateAgentForm {
  name: string;
  description: string;
  icon: string;
  api_type: string;
}

// 组件属性类型
export interface AdminLayoutProps {
  user: any;
  activeMenu: string;
  onMenuSelect: (key: string) => void;
  children: React.ReactNode;
}

export interface StudentManagementProps {
  students: Student[];
  loading: boolean;
  user: any;
  onRefresh: () => void;
}

export interface AgentManagementProps {
  adminAgents: AiAgent[];
  loading: boolean;
  user: any;
  onRefresh: () => void;
  onCreateAgent: () => void;
}

export interface DataManagementProps {
  dataStats: DataStats;
  adminAgents: AiAgent[];
  user: any;
}

export interface CreateAgentModalProps {
  open: boolean;
  onCancel: () => void;
  onOk: (form: CreateAgentForm) => void;
  loading?: boolean;
}
