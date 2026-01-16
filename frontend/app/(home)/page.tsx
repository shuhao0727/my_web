'use client';

import React from 'react';
import Link from 'next/link';
import { 
  RobotOutlined, TrophyOutlined, BookOutlined, 
  UserOutlined, CloudOutlined, ApiOutlined
} from '@ant-design/icons';

export default function HomePage() {
  // 简洁导航项
  const navItems = [
    {
      icon: <RobotOutlined />,
      title: 'AI智能体实验室',
      description: '与AI对话学习',
      link: '/ai-lab',
      color: '#1890ff',
      external: false,
    },
    {
      icon: <TrophyOutlined />,
      title: '信息学竞赛',
      description: '竞赛辅导资源',
      link: '/competition',
      color: '#52c41a',
      external: false,
    },
    {
      icon: <BookOutlined />,
      title: '信息技术教学',
      description: '课程体系介绍',
      link: '/teaching',
      color: '#722ed1',
      external: false,
    },
    {
      icon: <UserOutlined />,
      title: '关于我',
      description: '教师介绍',
      link: '/about',
      color: '#fa8c16',
      external: false,
    },
    {
      icon: <CloudOutlined />,
      title: 'NAS导航页',
      description: '内部服务门户',
      link: 'http://wangsh.cn:5000',
      color: '#13c2c2',
      external: true,
    },
    {
      icon: <ApiOutlined />,
      title: 'Dify应用平台',
      description: 'AI应用开发平台',
      link: 'http://wangsh.cn:6606',
      color: '#eb2f96',
      external: true,
    },
  ];

  return (
    <div 
      className="min-h-screen flex flex-col items-center justify-center px-4 bg-white"
    >
      <div className="max-w-4xl mx-auto w-full">
  
        {/* 核心导航 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {navItems.map((item, index) => {
            const cardContent = (
              <div className="p-6 rounded-lg border border-gray-300 bg-white hover:border-blue-300 hover:shadow-md transition-all duration-200">
                <div 
                  className="w-14 h-14 rounded-lg flex items-center justify-center mb-4 mx-auto"
                  style={{ backgroundColor: `${item.color}15` }}
                >
                  <div style={{ color: item.color, fontSize: '24px' }}>
                    {item.icon}
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600">
                    {item.title}
                  </div>
                  <div className="text-sm text-gray-500">
                    {item.description}
                  </div>
                </div>
              </div>
            );

            if (item.external) {
              return (
                <a
                  key={index}
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group block"
                >
                  {cardContent}
                </a>
              );
            } else {
              return (
                <Link
                  key={index}
                  href={item.link}
                  className="group block"
                >
                  {cardContent}
                </Link>
              );
            }
          })}
        </div>
      </div>
    </div>
  );
}
