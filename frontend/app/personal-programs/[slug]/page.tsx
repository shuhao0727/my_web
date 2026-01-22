"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Spin, message, Typography, Button } from 'antd';
import { ArrowLeftOutlined, AppstoreOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

// 导入应用组件（如果有的话）
import SchoolCourseProcessApp from '../apps/school-course-process';

export default function ApplicationDetailPage() {
  const router = useRouter();
  const params = useParams();
  const slug = params.slug as string;
  
  // 状态管理
  const [isClient, setIsClient] = useState(false);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState<boolean>(false);
  const [appTitle, setAppTitle] = useState<string>('');
  
  // 检查客户端渲染
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  // 认证和加载应用信息
  useEffect(() => {
    if (!isClient || !slug) return;
    
    const checkAuthAndLoadApp = async () => {
      try {
        // 1. 检查用户登录状态（使用xbk_user）
        const savedUser = localStorage.getItem('xbk_user');
        if (!savedUser) {
          throw new Error('未登录');
        }
        
        // 2. 加载应用信息（用于获取标题）
        // 注意：目前暂时使用slug作为标题，未来可以扩展从后端获取应用信息
        const userData = JSON.parse(savedUser);
        setAppTitle(slug === 'school-course-process' ? '校本课处理' : slug);
        setAuthenticated(true);
        
        // 3. 验证用户有效性（可选：可以调用后端API验证用户是否仍然有效）
        try {
          const response = await fetch('/api/xbk/health');
          if (!response.ok) {
            console.warn('后端健康检查失败，但继续显示应用');
          }
        } catch (error) {
          console.warn('后端连接失败，继续显示应用');
        }
      } catch (error: any) {
        console.error('认证或加载失败:', error);
        if (error.message === '未登录') {
          message.error('请先登录');
          router.push('/personal-programs');
        } else {
          message.error('加载应用失败');
        }
      } finally {
        setLoading(false);
      }
    };
    
    checkAuthAndLoadApp();
  }, [isClient, slug, router]);
  
  // 返回列表
  const handleBackToList = () => {
    router.push('/personal-programs');
  };
  
  // 渲染应用内容
  const renderAppContent = () => {
    switch (slug) {
      case 'school-course-process':
        return <SchoolCourseProcessApp />;
      default:
        return (
          <div className="p-8 rounded-lg border border-gray-300 bg-white">
            <div className="text-center">
              <Title level={2} className="mb-4">{appTitle}</Title>
              <Text type="secondary" className="block mb-8">
                应用页面待开发
              </Text>
            </div>
          </div>
        );
    }
  };
  
  // 服务器端渲染时返回空的div
  if (!isClient) {
    return <div className="h-full" suppressHydrationWarning />;
  }
  
  // 加载中
  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Spin size="large" />
      </div>
    );
  }
  
  // 认证失败（会自动跳转，这里只是备用显示）
  if (!authenticated) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8">
        <div className="text-center">
          <AppstoreOutlined className="text-6xl text-gray-300 mb-6" />
          <Title level={3}>认证失败</Title>
          <Text type="secondary" className="mb-6 block">
            请检查登录状态
          </Text>
          <Button 
            type="primary" 
            icon={<ArrowLeftOutlined />}
            onClick={handleBackToList}
          >
            返回应用列表
          </Button>
        </div>
      </div>
    );
  }
  
  // 主界面 - 认证成功，显示应用内容
  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* 简单的顶部栏 */}
      <div className="border-b border-gray-100 bg-white px-4 py-3">
        <div className="container mx-auto flex items-center justify-between">
          <Button 
            type="text" 
            icon={<ArrowLeftOutlined />}
            onClick={handleBackToList}
          >
            返回
          </Button>
          <div className="text-lg font-medium">{appTitle}</div>
          <div className="w-20"></div> {/* 占位保持对称 */}
        </div>
      </div>
      
      {/* 应用内容区域 */}
      <div className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {renderAppContent()}
        </div>
      </div>
    </div>
  );
}
