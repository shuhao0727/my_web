'use client';

import React from 'react';
import { 
  SearchOutlined, PlusOutlined,
  HistoryOutlined, RobotOutlined
} from '@ant-design/icons';
import { 
  Input, Card, Divider, Button, 
  Spin, Typography, Tag
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
    <div className="lg:w-80 h-full">
      <Card 
        className="h-full"
      >
        {/* 搜索框 */}
        <div className="mb-4">
          <Input
            placeholder="🔍 搜索智能体..."
            prefix={<SearchOutlined className="text-gray-400" />}
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            allowClear
            className="rounded-lg border-gray-200 focus:border-blue-500"
          />
        </div>

        {/* 智能体列表 */}
        <div className="mb-6">
          <div className="flex items-center mb-3">
            <RobotOutlined className="text-blue-500 mr-2" />
            <Text className="font-semibold text-gray-700">AI智能体</Text>
          </div>
          <div className="space-y-2 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
            {loadingAgents ? (
              <div className="text-center py-8">
                <Spin size="small" />
                <div className="text-xs text-gray-500 mt-2">加载中...</div>
              </div>
            ) : (
              filteredAgents.map(agent => (
                <Card
                  key={agent.id}
                  size="small"
                  hoverable
                  onClick={() => onSelectAgent(agent)}
                  className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                    selectedAgent?.id === agent.id 
                      ? 'border-blue-500 bg-blue-50 shadow-md' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl p-2 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
                      {agent.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-gray-800 mb-1">{agent.name}</div>
                      <div className="text-xs text-gray-500 mb-1">
                        {agent.description || '暂无描述'}
                      </div>
                      <Tag 
                        color={agent.is_active ? 'green' : 'default'} 
                        className="text-xs"
                      >
                        {agent.is_active ? '在线' : '离线'}
                      </Tag>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>

        {/* 对话历史 */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <HistoryOutlined className="text-gray-500 mr-2" />
              <Text className="font-semibold text-gray-700">对话历史</Text>
            </div>
            <span className="text-xs text-gray-400">{conversations.length}</span>
          </div>

          <div className="space-y-3">
            <Button
              icon={<PlusOutlined />}
              block
              type="primary"
              size="middle"
              onClick={onNewConversation}
              className="bg-gradient-to-r from-blue-500 to-purple-500 border-0 hover:from-blue-600 hover:to-purple-600"
            >
              新建对话
            </Button>

            <div className="space-y-2 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
              {conversations.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <div className="text-sm mb-1">📭</div>
                  <div className="text-sm">暂无对话历史</div>
                </div>
              ) : (
                conversations.map(conv => (
                  <Card
                    key={conv.id}
                    size="small"
                    hoverable
                    onClick={() => onSelectConversation(conv)}
                    className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                      selectedConversation?.id === conv.id 
                        ? 'border-blue-500 bg-blue-50 shadow-md' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1 min-w-0 mr-2">
                        <div className="font-medium text-sm text-gray-800 truncate mb-1">
                          {conv.title}
                        </div>
                        <div className="flex items-center space-x-2 text-xs text-gray-500">
                          <span className="truncate">{conv.ai_agent}</span>
                          <span>•</span>
                          <span>{conv.total_messages} 条消息</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end">
                        <div className="text-xs text-gray-400 mb-1">
                          {new Date(conv.start_time).toLocaleDateString()}
                        </div>
                        <div className="text-xs text-gray-400">
                          {conv.total_tokens} tokens
                        </div>
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          </div>
        </div>
      </Card>
      
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #c1c1c1;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #a1a1a1;
        }
      `}</style>
    </div>
  );
}
