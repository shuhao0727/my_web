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
      // 初始加载所有对话
      loadUserConversations(userData.id);
    }
    setLoading(false);
  }, []);

  // 加载AI智能体
  const loadAiAgents = async () => {
    setLoadingAgents(true);
    try {
      // 只获取活跃的智能体，用户只能看到活跃的智能体
      const response = await aiApi.agent.getAgents(true);
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

  // 加载用户对话，可选按智能体筛选
  const loadUserConversations = async (userId: number, agentId?: number) => {
    try {
      const response = await aiApi.conversation.getConversations(userId, agentId);
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

  // 处理选择智能体
  const handleSelectAgent = async (agent: AiAgent) => {
    // 保存当前智能体
    const previousAgent = selectedAgent;
    setSelectedAgent(agent);
    
    // 加载新智能体的对话
    if (user) {
      await loadUserConversations(user.id, agent.id);
    }
    
    // 检查当前选中的对话是否属于新智能体
    // 如果当前对话属于之前的智能体，或者不属于任何智能体，则清空选中的对话和消息
    if (selectedConversation) {
      const conversationBelongsToNewAgent = conversations.some(
        conv => conv.id === selectedConversation.id && conv.ai_agent === agent.name
      );
      
      if (!conversationBelongsToNewAgent) {
        setSelectedConversation(null);
        setMessages([]);
      }
    } else {
      // 如果没有选中的对话，清空消息
      setMessages([]);
    }
  };

  // 处理发送消息
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedAgent || !user) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: formatTimeForDisplay(new Date()),
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
        // 使用API返回的全部消息来更新前端消息状态，确保一致性
        // API返回的消息按ID升序排列（最旧的在最前），直接使用即可（最新的在底部）
        const updatedMessages: Message[] = response.messages.map((msg: any) => ({
          id: msg.id.toString(),
          role: msg.role,
          content: msg.content,
          timestamp: formatTimeForDisplay(msg.created_at),
          tokens: msg.tokens,
        }));
        
        setMessages(updatedMessages);
        
        // 如果这是新对话，添加到对话列表
        if (!selectedConversation && response.conversation) {
          const newConv: Conversation = {
            id: response.conversation.id,
            session_id: response.conversation.session_id,
            title: response.conversation.title || `与${selectedAgent.name}的对话`,
            ai_agent: selectedAgent.name,
            start_time: new Date().toISOString(),
            total_messages: response.conversation.total_messages,
            total_tokens: response.conversation.total_tokens,
          };
          setConversations([newConv, ...conversations]);
          setSelectedConversation(newConv);
        } else {
          // 刷新对话列表
          loadUserConversations(user.id, selectedAgent.id);
        }
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      // 模拟AI回复
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `收到您的消息："${inputMessage}"。作为${selectedAgent.name}，我会尽力帮助您。`,
        timestamp: formatTimeForDisplay(new Date()),
      };
      setMessages([...newMessages, aiMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // 调试函数：输出时间解析的详细信息
  const debugTimeParse = (input: string): Date => {
    console.log('调试时间解析，输入:', input);
    
    // 尝试多种解析方式
    let parsedDate: Date | null = null;
    
    // 方式1: 如果包含空格，替换为T并添加Z（假设是UTC时间）
    if (input.includes(' ')) {
      const isoString = input.replace(' ', 'T') + 'Z';
      parsedDate = new Date(isoString);
      console.log('方式1 - ISO字符串:', isoString, '解析结果:', parsedDate.toString());
    }
    
    // 方式2: 直接作为Date构造参数
    if (!parsedDate || isNaN(parsedDate.getTime())) {
      parsedDate = new Date(input);
      console.log('方式2 - 直接解析结果:', parsedDate.toString());
    }
    
    // 方式3: 正则表达式解析（之前的逻辑）
    if (!parsedDate || isNaN(parsedDate.getTime())) {
      const match = input.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/);
      if (match) {
        const [, year, month, day, hour, minute, second] = match;
        // 注意：月份从0开始（0=一月）
        const utcDate = new Date(Date.UTC(
          parseInt(year, 10),
          parseInt(month, 10) - 1,
          parseInt(day, 10),
          parseInt(hour, 10),
          parseInt(minute, 10),
          parseInt(second, 10)
        ));
        parsedDate = utcDate;
        console.log('方式3 - UTC解析结果:', parsedDate.toString());
      }
    }
    
    // 如果所有解析都失败，使用当前时间
    if (!parsedDate || isNaN(parsedDate.getTime())) {
      parsedDate = new Date();
      console.log('方式4 - 使用当前时间:', parsedDate.toString());
    }
    
    console.log('最终解析结果:', parsedDate.toString(), '本地时间:', parsedDate.toLocaleString('zh-CN'));
    return parsedDate;
  };

  // 格式化时间显示，确保显示正确的本地时间（亚洲/上海时区）
  const formatTimeForDisplay = (dateInput: Date | string): string => {
    let date: Date;
    
    if (typeof dateInput === 'string') {
      // 从API返回的字符串，需要解析为UTC时间
      let isoString = dateInput.trim();
      
      // 如果已经是ISO格式（包含T），确保有Z表示UTC
      if (isoString.includes('T')) {
        if (!isoString.endsWith('Z')) {
          isoString += 'Z';
        }
      } else {
        // 假设是"YYYY-MM-DD HH:MM:SS"格式，转换为ISO格式并添加Z表示UTC
        isoString = isoString.replace(' ', 'T') + 'Z';
      }
      
      date = new Date(isoString);
      
      // 调试信息
      if (process.env.NODE_ENV === 'development') {
        console.log('时间解析调试:', {
          输入: dateInput,
          ISO字符串: isoString,
          解析结果: date.toString(),
          UTC时间: date.toUTCString(),
          本地时间: date.toLocaleString('zh-CN'),
          时区偏移: date.getTimezoneOffset(),
          getUTCHours: date.getUTCHours(),
          getHours: date.getHours()
        });
      }
    } else {
      // 用户消息的Date对象，直接使用（本地时间）
      date = dateInput;
    }
    
    // 使用亚洲/上海时区显示完整的日期时间
    const formattedTime = date.toLocaleString('zh-CN', { 
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
      timeZone: 'Asia/Shanghai'
    });
    
    // 调试：输出格式化结果
    if (process.env.NODE_ENV === 'development') {
      console.log('时间格式化:', {
        输入: dateInput,
        格式化结果: formattedTime,
        原始日期: date.toString(),
        使用时区: 'Asia/Shanghai'
      });
    }
    
    return formattedTime;
  };

  // 加载对话消息
  const loadConversationMessages = async (conversationId: number) => {
    try {
      const response = await aiApi.conversation.getConversation(conversationId, true);
      if (response.success && response.conversation.messages) {
        // API返回的消息按ID升序排列（最旧的在最前），直接使用即可（最新的在底部）
        const loadedMessages: Message[] = response.conversation.messages.map((msg: any) => ({
          id: msg.id.toString(),
          role: msg.role,
          content: msg.content,
          timestamp: formatTimeForDisplay(msg.created_at),
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
            onSelectAgent={handleSelectAgent}
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
