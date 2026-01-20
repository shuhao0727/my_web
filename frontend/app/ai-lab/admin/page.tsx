'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Spin, message } from 'antd';
import AdminLayout from './components/AdminLayout';
import StudentManagement from './components/StudentManagement';
import AgentManagement from './components/AgentManagement';
import DataManagement from './components/DataManagement';
import type { AiAgent, Student, DataStats } from './components/types';
import aiApi from '@/lib/aiApi';

export default function AiLabAdminPage() {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [activeMenu, setActiveMenu] = useState('students');
  
  // 学生信息相关状态
  const [students, setStudents] = useState<Student[]>([]);
  const [studentsLoading, setStudentsLoading] = useState(false);
  
  // 智能体管理相关状态
  const [adminAgents, setAdminAgents] = useState<AiAgent[]>([]);
  const [agentsLoading, setAgentsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // 数据管理相关状态
  const [dataStats, setDataStats] = useState<DataStats>({
    total_conversations: 0,
    total_messages: 0,
    total_tokens: 0,
    active_agents: 0,
    total_users: 0,
  });

  // 标记为客户端
  useEffect(() => {
    setIsClient(true);
  }, []);

  // 检查用户权限
  useEffect(() => {
    if (!isClient) return;

    const savedUser = localStorage.getItem('ai_lab_user');
    if (savedUser) {
      const userData = JSON.parse(savedUser);
      setUser(userData);
      
      if (!userData.isAdmin) {
        // 如果不是管理员，重定向到主页面
        router.push('/ai-lab');
        return;
      }
      
      // 根据当前菜单加载数据
      loadDataByMenu(activeMenu);
    } else {
      // 未登录，重定向到登录页面
      router.push('/ai-lab/login');
    }
  }, [router, isClient]);

  // 根据菜单加载数据
  const loadDataByMenu = async (menu: string) => {
    switch (menu) {
      case 'students':
        await loadStudents();
        break;
      case 'agents':
        await loadAdminAgents();
        break;
      case 'data':
        await loadDataStats();
        break;
      default:
        await loadStudents();
    }
    setLoading(false);
  };

  // 加载学生信息 - 从真实API获取
  const loadStudents = async () => {
    setStudentsLoading(true);
    try {
      // 调用真实API获取学生列表
      const response = await aiApi.userManagement.getUsers(1, 50, undefined, 'student');
      if (response.success) {
        // 将API响应转换为Student类型
        const studentsFromApi: Student[] = response.users.map((user: any) => ({
          id: user.id,
          username: user.username,
          student_id: user.student_id,
          class_name: user.class_name || undefined,
          role: user.role,
          is_active: user.is_active,
          last_login: user.last_login,
          created_at: user.created_at,
          updated_at: user.updated_at,
          // 暂时使用0作为占位值，后续可以从其他API获取实际数据
          total_conversations: 0,
          total_messages: 0
        }));
        setStudents(studentsFromApi);
      } else {
        // API调用失败，不设置模拟数据，保留原有数据或空数组
        console.error('学生信息API调用失败，返回数据不成功');
        // 不清空数据，但可以显示错误消息
        message.error('加载学生数据失败');
      }
    } catch (error) {
      console.error('加载学生信息失败:', error);
      // 网络错误或其他异常，不清空数据
      message.error('加载学生数据失败，请检查网络连接');
    } finally {
      setStudentsLoading(false);
    }
  };

  // 加载管理智能体
  const loadAdminAgents = async () => {
    setAgentsLoading(true);
    try {
      const response = await aiApi.agent.getAgents(false);
      if (response.success) {
        // 转换API响应到新的AiAgent类型
        const agents: AiAgent[] = response.agents.map((agent: any) => ({
          id: agent.id,
          name: agent.name,
          api_type: agent.api_type,
          api_key: agent.api_key,
          base_url: agent.base_url,
          model: agent.model,
          app_id: agent.app_id,
          is_active: agent.is_active,
          created_at: agent.created_at,
        }));
        setAdminAgents(agents);
      } else {
        // 使用符合新结构的模拟数据
        const mockAgents: AiAgent[] = [
          { 
            id: 1, 
            name: '数学辅导助手', 
            api_type: 'deepseek', 
            api_key: 'sk-xxx',
            base_url: 'https://api.deepseek.com',
            model: 'deepseek-chat',
            is_active: true, 
            created_at: '2026-01-18T07:54:57' 
          },
          { 
            id: 2, 
            name: '代码审查专家', 
            api_type: 'dify', 
            api_key: 'app-xxx',
            base_url: 'http://localhost:6606/v1',
            app_id: 'code-review-app',
            is_active: true, 
            created_at: '2026-01-18T08:12:33' 
          },
        ];
        setAdminAgents(mockAgents);
      }
    } catch (error) {
      console.error('加载管理智能体失败:', error);
      // 使用符合新结构的模拟数据
      const mockAgents: AiAgent[] = [
        { 
          id: 1, 
          name: '数学辅导助手', 
          api_type: 'deepseek', 
          api_key: 'sk-xxx',
          base_url: 'https://api.deepseek.com',
          model: 'deepseek-chat',
          is_active: true, 
          created_at: '2026-01-18T07:54:57' 
        },
        { 
          id: 2, 
          name: '代码审查专家', 
          api_type: 'dify', 
          api_key: 'app-xxx',
          base_url: 'http://localhost:6606/v1',
          app_id: 'code-review-app',
          is_active: true, 
          created_at: '2026-01-18T08:12:33' 
        },
      ];
      setAdminAgents(mockAgents);
    } finally {
      setAgentsLoading(false);
    }
  };

  // 加载数据统计
  const loadDataStats = async () => {
    try {
      // 暂时使用模拟数据
      const mockStats: DataStats = {
        total_conversations: 24,
        total_messages: 215,
        total_tokens: 12450,
        active_agents: 3,
        total_users: 8,
      };
      setDataStats(mockStats);
    } catch (error) {
      console.error('加载数据统计失败:', error);
    }
  };

  // 创建新智能体
  const handleCreateAgent = async (form: any) => {
    try {
      console.log('创建智能体:', form);
      // 调用API创建智能体
      const response = await aiApi.agent.createAgent(form);
      if (response.success) {
        message.success('智能体创建成功');
        await loadAdminAgents();
      } else {
        message.error('创建智能体失败: ' + (response.message || '未知错误'));
      }
    } catch (error) {
      console.error('创建智能体失败:', error);
      message.error('创建智能体失败，请检查网络连接');
    }
  };

  // 编辑智能体
  const handleEditAgent = async (agentId: number, form: any) => {
    try {
      console.log('编辑智能体:', agentId, form);
      // 调用API更新智能体
      const response = await aiApi.agent.updateAgent(agentId, form);
      if (response.success) {
        message.success('智能体更新成功');
        await loadAdminAgents();
      } else {
        message.error('更新智能体失败: ' + (response.message || '未知错误'));
      }
    } catch (error) {
      console.error('更新智能体失败:', error);
      message.error('更新智能体失败，请检查网络连接');
    }
  };

  // 更新智能体状态
  const handleToggleAgentStatus = async (agentId: number, isActive: boolean) => {
    try {
      await aiApi.agent.updateAgentStatus(agentId, !isActive);
      loadAdminAgents();
    } catch (error) {
      console.error('更新智能体状态失败:', error);
    }
  };

  // 删除智能体
  const handleDeleteAgent = async (agentId: number) => {
    try {
      await aiApi.agent.deleteAgent(agentId);
      loadAdminAgents();
    } catch (error) {
      console.error('删除智能体失败:', error);
    }
  };

  // 服务器端渲染时只显示空的div，避免hydration不匹配
  if (!isClient) {
    return <div className="min-h-screen bg-gray-50" suppressHydrationWarning />;
  }

  // 客户端加载状态
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Spin size="large" />
      </div>
    );
  }

  // 客户端渲染后，检查用户权限
  if (!user || !user.isAdmin) {
    // 这里实际上应该已经重定向了，但以防万一显示一个加载状态
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Spin size="large" />
      </div>
    );
  }

  // 渲染内容区域
  const renderContent = () => {
    switch (activeMenu) {
      case 'students':
        return (
          <StudentManagement 
            students={students}
            loading={studentsLoading}
            user={user}
            onRefresh={loadStudents}
          />
        );
        
      case 'agents':
        return (
          <AgentManagement 
            adminAgents={adminAgents}
            loading={agentsLoading}
            user={user}
            onRefresh={loadAdminAgents}
            onCreateAgent={handleCreateAgent}
            onEditAgent={handleEditAgent}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onToggleAgentStatus={handleToggleAgentStatus}
            onDeleteAgent={handleDeleteAgent}
          />
        );
        
      case 'data':
        return (
          <DataManagement 
            user={user}
          />
        );
        
      default:
        return null;
    }
  };

  const handleMenuSelect = (key: string) => {
    setActiveMenu(key);
    loadDataByMenu(key);
  };

  return (
    <div suppressHydrationWarning data-no-translate translate="no">
      <AdminLayout 
        user={user}
        activeMenu={activeMenu}
        onMenuSelect={handleMenuSelect}
      >
        {renderContent()}
      </AdminLayout>
    </div>
  );
}
