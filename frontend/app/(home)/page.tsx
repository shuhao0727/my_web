'use client';

import React from 'react';
import Link from 'next/link';
import { 
  RobotOutlined, TrophyOutlined, BookOutlined, 
  CloudOutlined, ApiOutlined, CodeOutlined, FileTextOutlined
} from '@ant-design/icons';

export default function HomePage() {
  // 简洁导航项 - 无描述版本
  const navItems = [
    {
      icon: <RobotOutlined />,
      title: 'AI智能体',
      link: '/ai-lab',
      color: '#1890ff',
      bgColor: 'from-blue-400 to-blue-600',
      external: false,
    },
    {
      icon: <TrophyOutlined />,
      title: '信息学竞赛',
      link: '/competition',
      color: '#52c41a',
      bgColor: 'from-green-400 to-green-600',
      external: false,
    },
    {
      icon: <BookOutlined />,
      title: '信息技术',
      link: '/teaching',
      color: '#722ed1',
      bgColor: 'from-purple-400 to-purple-600',
      external: false,
    },
    {
      icon: <CodeOutlined />,
      title: '个人程序',
      link: '/personal-programs',
      color: '#fa8c16',
      bgColor: 'from-orange-400 to-orange-600',
      external: false,
    },
    {
      icon: <FileTextOutlined />,
      title: '文章',
      link: '/articles',
      color: '#13c2c2',
      bgColor: 'from-cyan-400 to-cyan-600',
      external: false,
    },
    {
      icon: <CloudOutlined />,
      title: 'NAS导航页',
      link: 'http://wangsh.cn:5000',
      color: '#eb2f96',
      bgColor: 'from-pink-400 to-pink-600',
      external: true,
    },
    {
      icon: <ApiOutlined />,
      title: 'Dify应用平台',
      link: 'http://wangsh.cn:6606',
      color: '#722ed1',
      bgColor: 'from-indigo-400 to-indigo-600',
      external: true,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse"></div>
        <div className="absolute -bottom-20 -left-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-cyan-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-2000"></div>
      </div>

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-12">
        <div className="max-w-6xl mx-auto w-full">
          {/* 标题区域 */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
      
            </h1>
            <p className="text-lg text-gray-600">
             
            </p>
          </div>

          {/* 核心导航网格 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {navItems.map((item, index) => {
              const cardContent = (
                <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100 hover:border-transparent">
                  {/* 渐变背景 */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${item.bgColor} opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity duration-300`}></div>
                  
                  {/* 图标容器 */}
                  <div className="relative z-10 flex flex-col items-center">
                    <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-6 transition-all duration-300 group-hover:scale-110 ${
                      item.bgColor.includes('blue') ? 'bg-blue-50' :
                      item.bgColor.includes('green') ? 'bg-green-50' :
                      item.bgColor.includes('purple') ? 'bg-purple-50' :
                      item.bgColor.includes('orange') ? 'bg-orange-50' :
                      item.bgColor.includes('cyan') ? 'bg-cyan-50' :
                      item.bgColor.includes('pink') ? 'bg-pink-50' :
                      'bg-indigo-50'
                    }`}>
                      <div 
                        className="text-3xl transition-all duration-300 group-hover:scale-125"
                        style={{ color: item.color }}
                      >
                        {item.icon}
                      </div>
                    </div>
                    
                    <h3 className="text-lg font-semibold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                      {item.title}
                    </h3>
                  </div>

                  {/* 悬停效果遮罩 */}
                  <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl pointer-events-none"></div>
                </div>
              );

              if (item.external) {
                return (
                  <a
                    key={index}
                    href={item.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block transform transition-transform duration-300 hover:scale-105"
                  >
                    {cardContent}
                  </a>
                );
              } else {
                return (
                  <Link
                    key={index}
                    href={item.link}
                    className="block transform transition-transform duration-300 hover:scale-105"
                  >
                    {cardContent}
                  </Link>
                );
              }
            })}
          </div>

          {/* 底部信息 */}
          <div className="text-center mt-16">
            <p className="text-gray-500 text-sm">
              © 2025 教学管理系统 - 专为信息学竞赛设计
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
