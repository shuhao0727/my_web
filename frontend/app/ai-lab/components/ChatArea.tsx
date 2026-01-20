'use client';

import React, { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  SendOutlined, UserOutlined, LoadingOutlined,
  MessageOutlined
} from '@ant-design/icons';
import {
  Button, Input, Avatar, Typography,
  Spin, Card, Badge
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
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{selectedAgent.icon}</div>
              <div>
                <div className="font-semibold">{selectedAgent.name}</div>
                <div className="text-sm text-gray-500">{selectedAgent.description}</div>
              </div>
            </div>
          ) : (
            <div>选择智能体开始对话</div>
          )
        }
        className="h-full"
      >
        {/* 消息区域 */}
        <div className="h-[650px] overflow-y-auto p-4 bg-gray-50 rounded-lg mb-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <MessageOutlined className="text-5xl mb-4" />
              <div className="text-lg">开始与 {selectedAgent?.name} 对话</div>
              <div className="text-sm mt-2">输入消息并发送</div>
            </div>
          ) : (
            messages.map(message => (
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
                        <span className="mr-2">{selectedAgent?.icon || '🤖'}</span>
                        <Text strong>{selectedAgent?.name || 'AI助手'}</Text>
                      </>
                    ) : (
                      <>
                        <Avatar 
                          size="small" 
                          icon={<UserOutlined />} 
                          className="mr-2 bg-gray-400"
                        />
                        <Text strong>{user?.username}</Text>
                      </>
                    )}
                    <Text type="secondary" className="ml-2 text-xs">
                      {message.timestamp}
                    </Text>
                  </div>
                  <div className="markdown-content">
                    {message.role === 'assistant' ? (
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h1: (props: any) => <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />,
                          h2: (props: any) => <h2 className="text-xl font-bold mt-3 mb-2" {...props} />,
                          h3: (props: any) => <h3 className="text-lg font-bold mt-2 mb-1" {...props} />,
                          h4: (props: any) => <h4 className="text-base font-bold mt-2 mb-1" {...props} />,
                          h5: (props: any) => <h5 className="text-sm font-bold mt-1 mb-1" {...props} />,
                          h6: (props: any) => <h6 className="text-xs font-bold mt-1 mb-1" {...props} />,
                          p: (props: any) => <p className="mb-2" {...props} />,
                          ul: (props: any) => <ul className="list-disc pl-5 mb-2" {...props} />,
                          ol: (props: any) => <ol className="list-decimal pl-5 mb-2" {...props} />,
                          li: (props: any) => <li className="mb-1" {...props} />,
                          blockquote: (props: any) => <blockquote className="border-l-4 border-gray-300 pl-3 italic my-2" {...props} />,
                          code: (props: any) => {
                            const { inline, ...restProps } = props;
                            return inline ? 
                              <code className="bg-gray-100 rounded px-1 py-0.5 text-sm font-mono" {...restProps} /> : 
                              <code className="block bg-gray-100 rounded p-2 my-2 text-sm font-mono overflow-x-auto" {...restProps} />;
                          },
                          pre: (props: any) => <pre className="bg-gray-100 rounded p-2 my-2 overflow-x-auto" {...props} />,
                          a: (props: any) => <a className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer" {...props} />,
                          table: (props: any) => <table className="border-collapse border border-gray-300 my-2" {...props} />,
                          thead: (props: any) => <thead className="bg-gray-100" {...props} />,
                          tbody: (props: any) => <tbody {...props} />,
                          tr: (props: any) => <tr className="border-b border-gray-300" {...props} />,
                          th: (props: any) => <th className="border border-gray-300 px-2 py-1 font-bold" {...props} />,
                          td: (props: any) => <td className="border border-gray-300 px-2 py-1" {...props} />,
                          strong: (props: any) => <strong className="font-bold" {...props} />,
                          em: (props: any) => <em className="italic" {...props} />,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    ) : (
                      <Paragraph className="mb-0 whitespace-pre-wrap">
                        {message.content}
                      </Paragraph>
                    )}
                  </div>
                  {message.tokens && (
                    <div className="text-xs text-gray-500 mt-2">
                      消耗token: {message.tokens}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border rounded-lg px-4 py-3">
                <div className="flex items-center">
                  <span className="mr-2">{selectedAgent?.icon || '🤖'}</span>
                  <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} />
                  <Text className="ml-2">正在思考...</Text>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="flex space-x-2">
          <TextArea
            value={inputMessage}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder={`向${selectedAgent?.name || 'AI智能体'}提问...`}
            autoSize={{ minRows: 2, maxRows: 4 }}
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault();
                onSendMessage();
              }
            }}
            className="flex-1"
            disabled={!selectedAgent}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={onSendMessage}
            disabled={!inputMessage.trim() || !selectedAgent || isLoading}
            loading={isLoading}
            className="h-auto px-6"
          >
            发送
          </Button>
        </div>

        {/* 对话信息 */}
        {selectedConversation && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="flex items-center justify-between text-sm text-gray-500">
              <div>
                对话ID: {selectedConversation.session_id}
              </div>
              <div>
                总消息: {selectedConversation.total_messages} • 
                总token: {selectedConversation.total_tokens}
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
