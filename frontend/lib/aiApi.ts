/**
 * AI智能体API客户端
 * 注意：后端路由前缀为 /api/ai，各个子路由有自己的前缀
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// 请求封装
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // 动态设置headers：如果body是FormData，让浏览器自动设置Content-Type
  const headers = options.body instanceof FormData
    ? { ...options.headers }  // 不添加默认Content-Type
    : {
        'Content-Type': 'application/json',
        ...options.headers,
      };

  try {
    const response = await fetch(url, { ...options, headers });
    
    if (!response.ok) {
      // 尝试解析错误响应
      let errorDetail = `请求失败: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || errorData.message || errorDetail;
      } catch {
        // 如果无法解析JSON，使用默认错误信息
      }
      throw new Error(errorDetail);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    // 处理网络错误（如fetch失败）
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      throw new Error(`无法连接到后端服务。请确保后端服务正在运行在 ${API_BASE_URL}`);
    }
    
    // 确保抛出的总是 Error 对象，并提供有意义的错误消息
    if (error instanceof Error) {
      throw error;
    } else if (typeof error === 'string') {
      throw new Error(error);
    } else {
      // 如果是普通对象或其他类型，转换为错误消息
      const errorMessage = error && typeof error === 'object' && 'message' in error
        ? String(error.message)
        : `API请求失败: ${JSON.stringify(error)}`;
      throw new Error(errorMessage);
    }
  }
}

// 用户API
export const userApi = {
  // 用户登录 - 不抛出错误，返回包含错误信息的对象
  login: async (username: string, studentId?: string) => {
    try {
      const response = await request<any>('/api/ai/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, student_id: studentId }),
      });
      // 将新版本的响应结构转换为旧版本，以保持兼容
      return {
        success: response.success,
        user: response.user,
        token: response.access_token || response.token, // 优先使用access_token，如果不存在则使用token（旧版本）
        message: response.message
      };
    } catch (error) {
      // 返回一个包含错误信息的对象，而不是抛出错误
      return {
        success: false,
        user: null,
        token: '',
        message: error instanceof Error ? error.message : '登录失败',
      };
    }
  },

  // 获取当前用户信息
  getCurrentUser: async () => {
    try {
      // 获取本地存储的token
      const token = localStorage.getItem('ai_token');
      if (!token) {
        return { success: false, user: null, message: '未登录' };
      }
      
      const response = await request<{ success: boolean; user: any }>('/api/ai/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      return response;
    } catch (error) {
      return {
        success: false,
        user: null,
        message: error instanceof Error ? error.message : '获取用户信息失败',
      };
    }
  },

  // 获取用户列表（测试用）
  getUsers: () => 
    request<{ success: boolean; users: any[]; total: number }>('/api/ai/auth/users'),
};

// 用户管理API（管理员）
export const userManagementApi = {
  // 获取用户列表（带分页和搜索）
  getUsers: (
    page: number = 1,
    pageSize: number = 20,
    search?: string,
    role?: string,
    isActive?: boolean
  ) => {
    let url = `/api/ai/user-management/users?page=${page}&page_size=${pageSize}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (role) url += `&role=${encodeURIComponent(role)}`;
    if (isActive !== undefined) url += `&is_active=${isActive}`;
    return request<{
      success: boolean;
      users: any[];
      total: number;
      page: number;
      page_size: number;
    }>(url);
  },

  // 创建用户
  createUser: (data: {
    username: string;
    student_id: string;
    role?: string;
    class_name?: string;
    is_active?: boolean;
  }) => 
    request<{ success: boolean; user: any; message: string }>('/api/ai/user-management/users', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 更新用户
  updateUser: (userId: number, data: {
    username?: string;
    student_id?: string;
    class_name?: string;
    role?: string;
    is_active?: boolean;
  }) => 
    request<{ success: boolean; user: any; message: string }>(`/api/ai/user-management/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // 删除用户
  deleteUser: (userId: number) => 
    request<{ success: boolean; message: string }>(`/api/ai/user-management/users/${userId}`, {
      method: 'DELETE',
    }),

  // 导入Excel文件
  importUsers: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<{
      success: boolean;
      imported_count: number;
      skipped_count: number;
      errors: string[];
    }>('/api/ai/user-management/users/import', {
      method: 'POST',
      body: formData,
    });
  },

  // 导出Excel模板
  exportTemplate: () => 
    request<{ success: boolean; filename: string; content: string }>('/api/ai/user-management/users/export-template'),
};

// AI智能体API
export const aiAgentApi = {
  // 获取所有智能体
  getAgents: (activeOnly = false, search?: string, apiType?: string) => {
    let url = `/api/ai/agents/?active_only=${activeOnly}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (apiType) url += `&api_type=${encodeURIComponent(apiType)}`;
    return request<{ success: boolean; agents: any[]; total: number }>(url);
  },

  // 获取单个智能体详情
  getAgent: (agentId: number) => 
    request<{ success: boolean; agent: any }>(`/api/ai/agents/${agentId}`),

  // 创建智能体（管理员）
  createAgent: (data: {
    name: string;
    api_type: string;  // 'deepseek' or 'dify'
    api_key?: string;
    base_url?: string;
    model?: string;
    app_id?: string;
    is_active?: boolean;
  }) => 
    request<{ success: boolean; agent: any; message: string }>('/api/ai/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 更新智能体（管理员）
  updateAgent: (
    agentId: number,
    data: {
      name?: string;
      api_type?: string;
      api_key?: string;
      base_url?: string;
      model?: string;
      app_id?: string;
      is_active?: boolean;
    }
  ) => 
    request<{ success: boolean; agent: any; message: string }>(`/api/ai/agents/${agentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // 更新智能体状态
  updateAgentStatus: (agentId: number, isActive: boolean) =>
    request<{ success: boolean; agent: any; message: string }>(`/api/ai/agents/${agentId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ is_active: isActive }),
    }),

  // 删除智能体（管理员）
  deleteAgent: (agentId: number) => 
    request<{ success: boolean; message: string }>(`/api/ai/agents/${agentId}`, {
      method: 'DELETE',
    }),

  // 获取智能体类型
  getAgentTypes: () =>
    request<{ success: boolean; types: string[] }>('/api/ai/agents/types'),

  // 获取智能体统计摘要
  getAgentsSummary: () =>
    request<{ success: boolean; summary: any }>('/api/ai/agents/stats/summary'),

  // 测试智能体连接
  testAgentConnection: (agentId: number) =>
    request<{
      success: boolean;
      message: string;
      test_result?: any;
      agent: { id: number; name: string; api_type: string };
    }>(`/api/ai/agents/${agentId}/test-connection`, {
      method: 'POST',
    }),
};

// 对话API
export const conversationApi = {
  // 获取用户对话列表
  getConversations: (userId?: number, agentId?: number, limit = 20, offset = 0, includeMessages = false) => {
    let url = `/api/ai/conversations?limit=${limit}&offset=${offset}&include_messages=${includeMessages}`;
    if (userId) url += `&user_id=${userId}`;
    if (agentId) url += `&agent_id=${agentId}`;
    return request<{ success: boolean; conversations: any[]; total: number; limit: number; offset: number }>(url);
  },

  // 创建新对话
  createConversation: (userId: number, agentId: number, title?: string) => 
    request<{ success: boolean; conversation: any; message: string }>('/api/ai/conversations', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, agent_id: agentId, title }),
    }),

  // 获取对话详情
  getConversation: (conversationId: number, includeMessages = true) => 
    request<{ success: boolean; conversation: any }>(
      `/api/ai/conversations/${conversationId}?include_messages=${includeMessages}`
    ),

  // 更新对话
  updateConversation: (conversationId: number, data: { title?: string; end_time?: string; total_messages?: number; total_tokens?: number }) =>
    request<{ success: boolean; conversation: any; message: string }>(`/api/ai/conversations/${conversationId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // 删除对话
  deleteConversation: (conversationId: number) => 
    request<{ success: boolean; message: string }>(`/api/ai/conversations/${conversationId}`, {
      method: 'DELETE',
    }),

  // 获取用户对话统计摘要
  getUserConversationSummary: (userId: number) =>
    request<{ success: boolean; summary: any }>(`/api/ai/conversations/user/${userId}/summary`),
};

// 消息API
export const messageApi = {
  // 获取消息列表
  getMessages: (conversationId?: number, role?: string, limit = 50, offset = 0) => {
    let url = `/api/ai/messages?limit=${limit}&offset=${offset}`;
    if (conversationId) url += `&conversation_id=${conversationId}`;
    if (role) url += `&role=${role}`;
    return request<{ success: boolean; messages: any[]; total: number; limit: number; offset: number }>(url);
  },

  // 创建消息
  createMessage: (conversationId: number, role: 'user' | 'assistant', content: string, tokens?: number) => 
    request<{ success: boolean; message_data: any; message: string }>('/api/ai/messages', {
      method: 'POST',
      body: JSON.stringify({ conversation_id: conversationId, role, content, tokens }),
    }),

  // 更新消息
  updateMessage: (messageId: number, data: { content?: string; tokens?: number }) =>
    request<{ success: boolean; message_data: any; message: string }>(`/api/ai/messages/${messageId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // 删除消息
  deleteMessage: (messageId: number) =>
    request<{ success: boolean; message: string }>(`/api/ai/messages/${messageId}`, {
      method: 'DELETE',
    }),

  // 获取对话消息统计摘要
  getConversationMessagesSummary: (conversationId: number) =>
    request<{ success: boolean; summary: any }>(`/api/ai/messages/conversation/${conversationId}/summary`),
};

// 聊天API
export const chatApi = {
  // 与AI智能体聊天
  chat: (userId: number, agentId: number, message: string, conversationId?: number) => 
    request<{
      success: boolean;
      conversation: any;
      messages: any[];
      message: string;
    }>('/api/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, agent_id: agentId, message, conversation_id: conversationId }),
    }),

  // 流式聊天
  chatStream: (userId: number, agentId: number, message: string, conversationId?: number) => 
    request<{
      success: boolean;
      conversation: any;
      messages: any[];
      message: string;
    }>('/api/ai/chat/stream', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, agent_id: agentId, message, conversation_id: conversationId }),
    }),

  // 测试智能体API连通性
  testAgentApi: (agentId: number) =>
    request<{ success: boolean; agent: any; test_message: string; response: string; tokens: number; status: string }>(
      `/api/ai/chat/agents/${agentId}/test`
    ),
};

// 统计API（兼容旧版，实际调用新的数据API）
export const statsApi = {
  // 获取系统总体统计摘要
  getSystemSummary: () =>
    request<{ success: boolean; stats: any }>('/api/ai/data/stats'),

  // 获取使用趋势（暂不支持，返回空数据）
  getUsageTrend: (days: number = 7) =>
    Promise.resolve({
      success: true,
      trend: {
        labels: [],
        data: []
      }
    }),

  // 获取智能体使用排名
  getAgentsRanking: (limit: number = 10) =>
    request<{ success: boolean; ranking: any[] }>(`/api/ai/data/agents/ranking?limit=${limit}`),

  // 获取用户使用排名（暂不支持，返回空数据）
  getUsersRanking: (limit: number = 10) =>
    Promise.resolve({
      success: true,
      ranking: []
    }),

  // 获取用户详细统计（暂不支持，返回空数据）
  getUserDetailedStats: (userId: number) =>
    Promise.resolve({
      success: true,
      user: { id: userId },
      stats: {},
      agent_breakdown: [],
      usage_by_hour: []
    }),
};

// 数据管理API（新增）
export const dataApi = {
  // 获取学生使用统计列表
  getStudentStats: (
    class_name?: string,
    search?: string,
    page: number = 1,
    page_size: number = 20
  ) => {
    let url = `/api/ai/data/students?page=${page}&page_size=${page_size}`;
    if (class_name) url += `&class_name=${encodeURIComponent(class_name)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    return request<{
      success: boolean;
      students: any[];
      total: number;
      page: number;
      page_size: number;
    }>(url);
  },

  // 获取系统总体统计
  getSystemStats: () =>
    request<{ success: boolean; stats: any }>('/api/ai/data/stats'),

  // 获取智能体使用排名
  getAgentsRanking: (limit: number = 10) =>
    request<{ success: boolean; ranking: any[] }>(`/api/ai/data/agents/ranking?limit=${limit}`),

  // 获取学生对话列表
  getStudentConversations: (
    student_id: number,
    start_date?: string,
    end_date?: string,
    page: number = 1,
    page_size: number = 10
  ) => {
    let url = `/api/ai/data/students/${student_id}/conversations?page=${page}&page_size=${page_size}`;
    if (start_date) url += `&start_date=${encodeURIComponent(start_date)}`;
    if (end_date) url += `&end_date=${encodeURIComponent(end_date)}`;
    return request<{
      success: boolean;
      conversations: any[];
      total: number;
      page: number;
      page_size: number;
    }>(url);
  },

  // 获取对话详情
  getConversationDetails: (conversation_id: number) =>
    request<{
      success: boolean;
      conversation: any;
      messages: any[];
    }>(`/api/ai/data/conversations/${conversation_id}`),
};

// 导出所有API
export default {
  user: userApi,
  userManagement: userManagementApi,
  agent: aiAgentApi,
  conversation: conversationApi,
  message: messageApi,
  chat: chatApi,
  stats: statsApi,
  data: dataApi,
};
