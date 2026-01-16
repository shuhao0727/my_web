'use client';

import React, { useState, useRef, useEffect } from 'react';
import { 
  SendOutlined, UserOutlined,
  LoadingOutlined
} from '@ant-design/icons';
import { 
  Button, Input, Avatar, Typography, 
  Spin, Select
} from 'antd';

const { Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// 消息类型
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// AI智能体数据
const aiAgents = [
  {
    id: 'math_tutor',
    name: '数学辅导助手',
    icon: '🧮',
    description: '解答数学问题',
  },
  {
    id: 'code_reviewer',
    name: '代码审查专家',
    icon: '💻',
    description: '审查代码风格',
  },
  {
    id: 'algorithm_teacher',
    name: '算法竞赛导师',
    icon: '⚡',
    description: '讲解竞赛算法',
  },
  {
    id: 'learning_advisor',
    name: '学习规划顾问',
    icon: '📚',
    description: '制定学习计划',
  },
];

// 初始对话
const initialMessages: Message[] = [
  { 
    id: '1', 
    role: 'assistant', 
    content: '您好！我是AI学习助手，请问有什么可以帮您？', 
    timestamp: '09:00' 
  },
];

export default function AiLabPage() {
  const [selectedAgent, setSelectedAgent] = useState(aiAgents[0]);
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 发送消息
  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputMessage('');
    setIsLoading(true);

    // 模拟AI回复
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `收到您的消息："${inputMessage}"。作为${selectedAgent.name}，我会尽力帮助您。这是模拟回复，实际应用中AI会根据您的问题提供专业解答。`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto p-4">
        {/* 智能体选择 */}
        <div className="mb-6">
          <Select
            className="w-full"
            value={selectedAgent.id}
            onChange={(value) => {
              const agent = aiAgents.find(a => a.id === value);
              if (agent) setSelectedAgent(agent);
            }}
          >
            {aiAgents.map(agent => (
              <Option key={agent.id} value={agent.id}>
                <div className="flex items-center">
                  <span className="text-xl mr-3">{agent.icon}</span>
                  <div>
                    <div className="font-medium">{agent.name}</div>
                    <div className="text-xs text-gray-500">{agent.description}</div>
                  </div>
                </div>
              </Option>
            ))}
          </Select>
        </div>

        {/* 对话界面 */}
        <div className="bg-gray-50 rounded-lg border">
          {/* 对话头部 */}
          <div className="border-b p-4 bg-white rounded-t-lg">
            <div className="flex items-center">
              <div className="text-2xl mr-3">{selectedAgent.icon}</div>
              <div>
                <div className="font-semibold text-lg">{selectedAgent.name}</div>
                <div className="text-sm text-gray-500">{selectedAgent.description}</div>
              </div>
            </div>
          </div>

          {/* 消息区域 */}
          <div className="h-[400px] overflow-y-auto p-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex mb-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-100 text-gray-800'
                      : 'bg-white text-gray-800 border'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    {message.role === 'assistant' ? (
                      <>
                        <span className="mr-2">{selectedAgent.icon}</span>
                        <Text strong>{selectedAgent.name}</Text>
                      </>
                    ) : (
                      <>
                        <Avatar 
                          size="small" 
                          icon={<UserOutlined />} 
                          className="mr-2 bg-gray-400"
                        />
                        <Text strong>我</Text>
                      </>
                    )}
                    <Text type="secondary" className="ml-2 text-xs">
                      {message.timestamp}
                    </Text>
                  </div>
                  <Paragraph className="mb-0 whitespace-pre-wrap">
                    {message.content}
                  </Paragraph>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border rounded-lg px-4 py-3">
                  <div className="flex items-center">
                    <span className="mr-2">{selectedAgent.icon}</span>
                    <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} />
                    <Text className="ml-2">正在思考...</Text>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className="border-t p-4 bg-white rounded-b-lg">
            <div className="flex space-x-2">
              <TextArea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={`向${selectedAgent.name}提问...`}
                autoSize={{ minRows: 2, maxRows: 4 }}
                onPressEnter={(e) => {
                  if (!e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                className="flex-1"
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                loading={isLoading}
                className="h-auto px-6"
              >
                发送
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
