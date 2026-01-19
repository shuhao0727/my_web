'use client';

import React from 'react';
import { 
  SearchOutlined, PlusOutlined,
  HistoryOutlined
} from '@ant-design/icons';
import { 
  Input, Card, Divider, Button, 
  Spin, Typography
} from 'antd';
import { AiAgent, Conversation, User } from './types';

const { Text } = Typography;

interface SidebarProps {
  user: User | null;
  aiAgents: AiAgent[];
  loadingAgents: boolean;
  conversations: Conversation[];
  selectedAgent: AiAgent | null;
  selectedConversation: Conversation | null;
  searchQuery: string;
  onSelectAgent: (agent: AiAgent) => void;
  onSelectConversation: (conversation: Conversation) => void;
  onNewConversation: () => void;
  onSearchChange: (query: string) => void;
}

export default function Sidebar({
  user,
  aiAgents,
  loadingAgents,
  conversations,
  selectedAgent,
  selectedConversation,
  searchQuery,
  onSelectAgent,
  onSelectConversation,
  onNewConversation,
  onSearchChange,
}: SidebarProps) {
  const filteredAgents = aiAgents.filter(agent =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="lg:w-1/4 h-full">
      <Card className="h-full">
        {/* 搜索框 */}
        <div className="mb-4">
          <Input
            placeholder="搜索智能体..."
            prefix={<SearchOutlined />}
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            allowClear
          />
        </div>

        {/* 智能体列表 */}
        <div className="mb-4">
          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
            {loadingAgents ? (
              <div className="text-center py-4">
                <Spin size="small" />
                <div className="text-xs text-gray-500 mt-1">加载中...</div>
              </div>
            ) : (
              filteredAgents.map(agent => (
                <Card
                  key={agent.id}
                  size="small"
                  hoverable
                  onClick={() => onSelectAgent(agent)}
                  className={`cursor-pointer transition-all ${
                    selectedAgent?.id === agent.id ? 'border-blue-500 bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-xl">{agent.icon}</div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{agent.name}</div>
                      <div className="text-xs text-gray-500 truncate">
                        {agent.description || '暂无描述'}
                      </div>
                    </div>
                    {agent.is_active ? (
                      <span className="text-xs text-green-500">✓</span>
                    ) : (
                      <span className="text-xs text-gray-400">✗</span>
                    )}
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>

        {/* 对话历史 */}
        <Divider>
          <div className="flex items-center space-x-2">
            <HistoryOutlined className="text-gray-400" />
            <span>对话历史</span>
          </div>
        </Divider>

        <div className="space-y-2">
          <Button
            icon={<PlusOutlined />}
            block
            type="dashed"
            size="small"
            onClick={onNewConversation}
          >
            新对话
          </Button>

          <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
            {conversations.length === 0 ? (
              <div className="text-center py-4 text-gray-400">
                <div className="text-sm">暂无对话历史</div>
              </div>
            ) : (
              conversations.map(conv => (
                <Card
                  key={conv.id}
                  size="small"
                  hoverable
                  onClick={() => onSelectConversation(conv)}
                  className={`cursor-pointer ${
                    selectedConversation?.id === conv.id ? 'border-blue-500 bg-blue-50' : ''
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">{conv.title}</div>
                      <div className="text-xs text-gray-500 truncate">
                        {conv.ai_agent} • {conv.total_messages} 条消息
                      </div>
                    </div>
                    <div className="text-xs text-gray-400">
                      {new Date(conv.start_time).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
