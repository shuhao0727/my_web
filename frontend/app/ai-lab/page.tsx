'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Spin, Modal, Form, Input, Select, Button } from 'antd';
import { useRouter } from 'next/navigation';
import aiApi from '@/lib/aiApi';

// 导入组件
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';

// 导入类型
import { 
  User, AiAgent, Conversation, Message, 
  CreateAgentForm 
} from './components/types';

const { Option } = Select;

export default function AiLabPage() {
  const router = useRouter();
  
  // 用户状态
  const [user, setUser] = useState<User | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  // AI智能体状态
  const [aiAgents, setAiAgents] = useState<AiAgent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<AiAgent | null>(null);
  const [loadingAgents, setLoadingAgents] = useState(false);

  // 对话状态
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 搜索状态
  const [searchQuery, setSearchQuery] = useState('');

  // 初始化数据
  useEffect(() => {
    const savedUser = localStorage.getItem('ai_lab_user');
    if (savedUser) {
      const userData = JSON.parse(savedUser);
      setUser(userData);
      setIsLoggedIn(true);
      loadAiAgents();
      loadUserConversations(userData.id);
    }
    setLoading(false);
  }, []);

  // 加载AI智能体
  const loadAiAgents = async () => {
    setLoadingAgents(true);
    try {
      const response = await aiApi.agent.getAgents();
      if (response.success && response.agents.length > 0) {
        setAiAgents(response.agents);
        setSelectedAgent(response.agents[0]);
      } else {
        // 如果没有智能体，创建一些默认的
        const defaultAgents: AiAgent[] = [
          { id: 1, name: '数学辅导助手', description: '解答数学问题', icon: '🧮', api_type: 'mock', is_active: true },
          { id: 2, name: '代码审查专家', description: '审查代码风格', icon: '💻', api_type: 'mock', is_active: true },
          { id: 3, name: '算法竞赛导师', description: '讲解竞赛算法', icon: '⚡', api_type: 'mock', is_active: true },
          { id: 4, name: '学习规划顾问', description: '制定学习计划', icon: '📚', api_type: 'mock', is_active: true },
        ];
        setAiAgents(defaultAgents);
        setSelectedAgent(defaultAgents[0]);
      }
    } catch (error) {
      console.error('加载AI智能体失败:', error);
      // 使用默认数据
      const defaultAgents: AiAgent[] = [
        { id: 1, name: '数学辅导助手', description: '解答数学问题', icon: '🧮', api_type: 'mock', is_active: true },
        { id: 2, name: '代码审查专家', description: '审查代码风格', icon: '💻', api_type: 'mock', is_active: true },
        { id: 3, name: '算法竞赛导师', description: '讲解竞赛算法', icon: '⚡', api_type: 'mock', is_active: true },
        { id: 4, name: '学习规划顾问', description: '制定学习计划', icon: '📚', api_type: 'mock', is_active: true },
      ];
      setAiAgents(defaultAgents);
      setSelectedAgent(defaultAgents[0]);
    } finally {
      setLoadingAgents(false);
    }
  };

  // 加载用户对话
  const loadUserConversations = async (userId: number) => {
    try {
      const response = await aiApi.conversation.getConversations(userId);
      if (response.success) {
        setConversations(response.conversations);
      }
    } catch (error) {
      console.error('加载对话失败:', error);
    }
  };

  // 处理登录（实际上，这个页面假设用户已经登录，否则会重定向到登录页面）
  // 注意：登录功能在登录页面，这里只处理登出

  // 处理登出
  const handleLogout = () => {
    setUser(null);
    setIsLoggedIn(false);
    setSelectedAgent(null);
    setAiAgents([]);
    setConversations([]);
    setMessages([]);
    localStorage.removeItem('ai_lab_user');
    // 重定向到登录页面
    router.push('/ai-lab/login');
  };

  // 处理发送消息
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedAgent || !user) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await aiApi.chat.chat(
        user.id,
        selectedAgent.id,
        inputMessage,
        selectedConversation?.id
      );

      if (response.success) {
        // 添加AI回复
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.messages[1]?.content || `收到您的消息："${inputMessage}"。`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          tokens: response.messages[1]?.tokens,
        };

        setMessages([...newMessages, aiMessage]);
        
        // 如果这是新对话，添加到对话列表
        if (!selectedConversation && response.conversation) {
          const newConv: Conversation = {
            id: response.conversation.id,
            session_id: response.conversation.session_id,
            title: response.conversation.title || `与${selectedAgent.name}的对话`,
            ai_agent: selectedAgent.name,
            start_time: new Date().toISOString(),
            total_messages: 2,
            total_tokens: (response.messages[0]?.tokens || 0) + (response.messages[1]?.tokens || 0),
          };
          setConversations([newConv, ...conversations]);
          setSelectedConversation(newConv);
        } else {
          // 刷新对话列表
          loadUserConversations(user.id);
        }
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      // 模拟AI回复
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `收到您的消息："${inputMessage}"。作为${selectedAgent.name}，我会尽力帮助您。`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages([...newMessages, aiMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // 加载对话消息
  const loadConversationMessages = async (conversationId: number) => {
    try {
      const response = await aiApi.conversation.getConversation(conversationId, true);
      if (response.success && response.conversation.messages) {
        const loadedMessages: Message[] = response.conversation.messages.map((msg: any) => ({
          id: msg.id.toString(),
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          tokens: msg.tokens,
        }));
        setMessages(loadedMessages);
      }
    } catch (error) {
      console.error('加载对话消息失败:', error);
    }
  };

  // 选择对话
  const handleSelectConversation = (conversation: Conversation) => {
    setSelectedConversation(conversation);
    loadConversationMessages(conversation.id);
  };

  // 开始新对话
  const handleNewConversation = () => {
    setSelectedConversation(null);
    setMessages([]);
  };

  // 打开管理员面板（在新标签页中打开）
  const handleOpenAdminPanel = () => {
    window.open('/ai-lab/admin', '_blank');
  };

  // 如果正在加载，显示加载动画
  if (loading) {
    return <Spin fullscreen tip="正在加载..." />;
  }

  // 如果没有登录，重定向到登录页面
  if (!isLoggedIn) {
    // 使用 useEffect 进行重定向，避免 SSR 问题
    // 但因为我们使用了 'use client'，可以直接使用 window.location
    if (typeof window !== 'undefined') {
      window.location.href = '/ai-lab/login';
    }
    return <Spin fullscreen tip="正在跳转到登录页面..." />;
  }

  return (
    <div className="min-h-screen bg-white">
      {/* 顶部工具栏 */}
      <Header 
        user={user}
        onOpenAdminPanel={handleOpenAdminPanel}
        onLogout={handleLogout}
      />

      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* 左侧边栏 */}
          <Sidebar
            user={user}
            aiAgents={aiAgents}
            loadingAgents={loadingAgents}
            conversations={conversations}
            selectedAgent={selectedAgent}
            selectedConversation={selectedConversation}
            searchQuery={searchQuery}
            onSelectAgent={setSelectedAgent}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            onSearchChange={setSearchQuery}
          />

          {/* 右侧主区域 */}
          <ChatArea
            user={user}
            selectedAgent={selectedAgent}
            selectedConversation={selectedConversation}
            messages={messages}
            inputMessage={inputMessage}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onInputChange={setInputMessage}
          />
        </div>
      </div>
    </div>
  );
}
