// 智能体类型（简化版，与数据库对齐）
export interface AiAgent {
  id: number;
  name: string;
  api_type: 'deepseek' | 'dify';  // 只能是这两种类型
  api_key?: string;
  base_url?: string;
  model?: string;      // DeepSeek类使用
  app_id?: string;     // Dify类使用
  is_active: boolean;
  created_at: string;
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
  api_type: 'deepseek' | 'dify';
  api_key?: string;
  base_url?: string;
  model?: string;      // DeepSeek类使用
  app_id?: string;     // Dify类使用
  is_active?: boolean;
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
  onCreateAgent: (form: CreateAgentForm) => void;
  onEditAgent?: (agentId: number, form: CreateAgentForm) => void;
}

export interface DataManagementProps {
  user: any;
}

export interface CreateAgentModalProps {
  open: boolean;
  onCancel: () => void;
  onOk: (form: CreateAgentForm) => void;
  loading?: boolean;
}

// 数据管理相关类型
export interface Conversation {
  id: number;
  title: string;
  agent_name: string;
  start_time: string;
  total_messages: number;
  total_tokens: number;
  user_id: number;
  student_name: string;
  student_id?: string;
  class_name?: string;
}

export interface Agent {
  id: number;
  name: string;
  api_type: string;
  model?: string;
}

export interface ConversationDetail {
  id: number;
  title: string;
  user: { id: number; username: string };
  agent: { id: number; name: string };
  start_time: string;
  total_messages: number;
  total_tokens: number;
  messages: Array<{
    id: number;
    role: string;
    content: string;
    created_at: string;
    tokens: number;
  }>;
}

export interface ExcelExportData {
  // 暂时留空，可根据需要扩展
}

// 数据管理筛选条件
export interface DataFilterConditions {
  selectedStudent?: number;
  selectedClass?: string;
  selectedAgent?: number;
  dateRange?: [string, string];
  searchText?: string;
}
