'use client';

import React, { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  SendOutlined, UserOutlined, LoadingOutlined,
  MessageOutlined, ClockCircleOutlined
} from '@ant-design/icons';
import {
  Button, Input, Avatar, Typography,
  Spin, Card, Badge, Space
} from 'antd';
import { Message, AiAgent, User, Conversation } from './types';

const { Paragraph, Text, Title } = Typography;
const { TextArea } = Input;

interface ChatAreaProps {
  user: User | null;
  selectedAgent: AiAgent | null;
  selectedConversation: Conversation | null;
  messages: Message[];
  inputMessage: string;
  isLoading: boolean;
  onSendMessage: () => void;
  onInputChange: (value: string) => void;
}

export default function ChatArea({
  user,
  selectedAgent,
  selectedConversation,
  messages,
  inputMessage,
  isLoading,
  onSendMessage,
  onInputChange,
}: ChatAreaProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="lg:w-3/4 h-full">
      <Card 
        title={
          selectedAgent ? (
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-gradient-to-br from-blue-100 to-purple-100 rounded-xl text-2xl">
                {selectedAgent.icon}
              </div>
              <div>
                <div className="font-bold text-gray-800 text-lg">{selectedAgent.name}</div>
                <div className="text-sm text-gray-600 flex items-center">
                  <ClockCircleOutlined className="mr-1" />
                  {selectedAgent.description}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-lg text-gray-600">选择智能体开始对话</div>
          )
        }
        className="h-full shadow-lg border-0 rounded-xl overflow-hidden"
        styles={{
          body: {
            padding: '1.5rem',
            height: 'calc(100% - 4rem)',
            display: 'flex',
            flexDirection: 'column'
          }
        }}
      >
        <div className="flex-1 flex flex-col">
          {/* 消息区域 */}
          <div className="h-[750px] overflow-y-auto p-4 bg-gray-50 rounded-lg mb-4 custom-chat-scrollbar">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <div className="text-6xl mb-4">🤖</div>
                <div className="text-2xl font-semibold text-gray-600 mb-2">
                  开始与 {selectedAgent?.name} 对话
                </div>
                <div className="text-gray-500">输入消息并发送，开始智能对话</div>
              </div>
            ) : (
              messages.map(message => (
                <div
                  key={message.id}
                  className={`flex mb-6 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-white text-gray-800 border border-gray-200'
                    }`}
                  >
                    <div className="flex items-center mb-3">
                      {message.role === 'assistant' ? (
                        <>
                          <span className="mr-2 text-lg">{selectedAgent?.icon || '🤖'}</span>
                            <Text
                              strong
                              className="text-gray-800"
                            >
                              {selectedAgent?.name || 'AI助手'}
                            </Text>
                        </>
                      ) : (
                        <>
                          <Avatar 
                            size="small" 
                            icon={<UserOutlined />} 
                            className="mr-2 bg-white text-blue-500 border border-blue-200"
                          />
                          <Text 
                            strong 
                            className="text-white"
                          >
                            {user?.username}
                          </Text>
                        </>
                      )}
                      <Text 
                        type="secondary" 
                        className={`ml-2 text-xs ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}
                      >
                        {message.timestamp}
                      </Text>
                    </div>
                    <div className={`markdown-content ${message.role === 'user' ? 'text-white' : ''}`}>
                      {message.role === 'assistant' ? (
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          components={{
                            h1: (props: any) => <h1 className={`text-2xl font-bold mt-4 mb-2 ${message.role === 'user' ? 'text-white' : 'text-gray-800'}`} {...props} />,
                            h2: (props: any) => <h2 className={`text-xl font-bold mt-3 mb-2 ${message.role === 'user' ? 'text-white' : 'text-gray-800'}`} {...props} />,
                            h3: (props: any) => <h3 className={`text-lg font-bold mt-2 mb-1 ${message.role === 'user' ? 'text-white' : 'text-gray-800'}`} {...props} />,
                            h4: (props: any) => <h4 className={`text-base font-bold mt-2 mb-1 ${message.role === 'user' ? 'text-white' : 'text-gray-800'}`} {...props} />,
                            h5: (props: any) => <h5 className={`text-sm font-bold mt-1 mb-1 ${message.role === 'user' ? 'text-white' : 'text-gray-800'}`} {...props} />,
                            h6: (props: any) => <h6 className={`text-xs font-bold mt-1 mb-1 ${message.role === 'user' ? 'text-white' : 'text-gray-800'}`} {...props} />,
                            p: (props: any) => <p className={`mb-2 ${message.role === 'user' ? 'text-white' : 'text-gray-700'}`} {...props} />,
                            ul: (props: any) => <ul className="list-disc pl-5 mb-2" {...props} />,
                            ol: (props: any) => <ol className="list-decimal pl-5 mb-2" {...props} />,
                            li: (props: any) => <li className={`mb-1 ${message.role === 'user' ? 'text-white' : 'text-gray-700'}`} {...props} />,
                            blockquote: (props: any) => <blockquote className={`border-l-4 border-gray-300 pl-3 italic my-2 ${message.role === 'user' ? 'text-white' : 'text-gray-700'}`} {...props} />,
                            code: (props: any) => {
                              const { inline, ...restProps } = props;
                              return inline ? 
                            <code className={`bg-gray-100 rounded px-1 py-0.5 text-sm font-mono ${message.role === 'user' ? 'bg-blue-400 text-white' : 'bg-gray-100'}`} {...restProps} /> : 
                            <code className={`block bg-gray-100 rounded p-2 my-2 text-sm font-mono overflow-x-auto ${message.role === 'user' ? 'bg-blue-400 text-white' : 'bg-gray-100'}`} {...restProps} />;
                            },
                            pre: (props: any) => <pre className={`bg-gray-100 rounded p-2 my-2 overflow-x-auto ${message.role === 'user' ? 'bg-blue-400' : 'bg-gray-100'}`} {...props} />,
                            a: (props: any) => <a className="text-blue-200 hover:underline" target="_blank" rel="noopener noreferrer" {...props} />,
                            table: (props: any) => <table className="border-collapse border border-gray-300 my-2" {...props} />,
                            thead: (props: any) => <thead className="bg-gray-100" {...props} />,
                            tbody: (props: any) => <tbody {...props} />,
                            tr: (props: any) => <tr className="border-b border-gray-300" {...props} />,
                            th: (props: any) => <th className={`border border-gray-300 px-2 py-1 font-bold ${message.role === 'user' ? 'text-white' : ''}`} {...props} />,
                            td: (props: any) => <td className={`border border-gray-300 px-2 py-1 ${message.role === 'user' ? 'text-white' : ''}`} {...props} />,
                            strong: (props: any) => <strong className="font-bold" {...props} />,
                            em: (props: any) => <em className="italic" {...props} />,
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      ) : (
                        <Paragraph className={`mb-0 whitespace-pre-wrap ${message.role === 'user' ? 'text-white' : 'text-gray-700'}`}>
                          {message.content}
                        </Paragraph>
                      )}
                    </div>
                    {message.tokens && (
                      <div className={`text-xs mt-3 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                        <Space>
                          <Badge 
                            count={`${message.tokens} tokens`} 
                            style={{ backgroundColor: message.role === 'user' ? '#40a9ff' : '#1890ff' }}
                          />
                        </Space>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start mb-6">
                <div className="bg-white border border-gray-100 rounded-2xl px-4 py-3 shadow-sm">
                  <div className="flex items-center">
                    <span className="mr-2 text-lg">{selectedAgent?.icon || '🤖'}</span>
                    <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} />
                    <Text className="ml-2 text-gray-600">正在思考...</Text>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className="flex space-x-3">
            <TextArea
              value={inputMessage}
              onChange={(e) => onInputChange(e.target.value)}
              placeholder={`向"${selectedAgent?.name || 'AI智能体'}"提问...`}
              autoSize={{ minRows: 2, maxRows: 6 }}
              onPressEnter={(e) => {
                if (!e.shiftKey) {
                  e.preventDefault();
                  onSendMessage();
                }
              }}
              className="flex-1 rounded-xl border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              disabled={!selectedAgent}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={onSendMessage}
              disabled={!inputMessage.trim() || !selectedAgent || isLoading}
              loading={isLoading}
              className="h-auto px-6 bg-gradient-to-r from-blue-500 to-purple-500 border-0 hover:from-blue-600 hover:to-purple-600 text-white"
            >
              发送
            </Button>
          </div>
        </div>

        {/* 对话信息 */}
        {selectedConversation && (
          <div className="mt-4 pt-4 border-t border-gray-100 bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center space-x-4">
                <Text type="secondary">对话ID:</Text>
                <Text code className="text-xs">{selectedConversation.session_id}</Text>
              </div>
              <div className="flex items-center space-x-4">
                <Text type="secondary">总消息:</Text>
                <Badge 
                  count={selectedConversation.total_messages} 
                  color="blue"
                />
                <Text type="secondary">Tokens:</Text>
                <Badge 
                  count={selectedConversation.total_tokens} 
                  color="purple"
                />
              </div>
            </div>
          </div>
        )}
      </Card>
      
      <style jsx>{`
        .custom-chat-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-chat-scrollbar::-webkit-scrollbar-track {
          background: #f8fafc;
          border-radius: 4px;
        }
        .custom-chat-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 4px;
        }
        .custom-chat-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>
    </div>
  );
}
