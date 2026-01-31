'use client';

import React from 'react';
import Link from 'next/link';
import { HomeOutlined, BookOutlined, RobotOutlined, TrophyOutlined, CodeOutlined, FileTextOutlined } from '@ant-design/icons';

const Header: React.FC = () => {
  // 导航菜单项 - 精简版
  const navItems = [
    {
      key: 'home',
      label: '首页',
      icon: <HomeOutlined />,
      link: '/',
    },
    {
      key: 'ai-lab',
      label: 'AI智能体',
      icon: <RobotOutlined />,
      link: '/ai-lab',
    },
    {
      key: 'competition',
      label: '信息学竞赛',
      icon: <TrophyOutlined />,
      link: '/competition',
    },
    {
      key: 'teaching',
      label: '信息技术',
      icon: <BookOutlined />,
      link: '/teaching',
    },
    {
      key: 'personal-programs',
      label: '个人程序',
      icon: <CodeOutlined />,
      link: '/personal-programs',
    },
    {
      key: 'articles',
      label: '文章',
      icon: <FileTextOutlined />,
      link: '/articles',
    }
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-100 relative z-50" suppressHydrationWarning translate="no">
      {/* 主导航栏 */}
      <div className="container mx-auto px-4">
        <div className="relative h-16">
          {/* Logo区域 - 左侧 */}
          <div className="absolute left-0 top-0 h-full flex items-center">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="bg-gradient-to-br from-blue-500 to-blue-700 text-white p-2.5 rounded-xl shadow-sm group-hover:shadow-md transition-all duration-300">
                <RobotOutlined className="text-lg" />
              </div>
              <div className="flex flex-col">
                <h1 className="text-xl font-bold text-gray-900 tracking-tight">wangsh</h1>
              </div>
            </Link>
          </div>

          {/* 桌面端导航菜单 - 绝对居中（忽略Logo） */}
          <nav className="hidden lg:flex items-center justify-center absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="flex items-center space-x-1 bg-gray-50/80 backdrop-blur-sm rounded-xl p-1.5 shadow-inner">
              {navItems.map((item) => (
                <Link
                  key={item.key}
                  href={item.link}
                  className="relative px-4 py-2.5 text-gray-700 hover:text-blue-600 rounded-lg transition-all duration-300 group/nav"
                >
                  <div className="flex items-center space-x-2.5">
                    <div className="text-gray-500 group-hover/nav:text-blue-500 transition-colors duration-300">
                      {item.icon}
                    </div>
                    <span className="font-medium text-sm tracking-wide whitespace-nowrap">
                      {item.label}
                    </span>
                  </div>
                  {/* 活动状态指示器 */}
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 bg-blue-500 rounded-full opacity-0 group-hover/nav:opacity-100 transition-opacity duration-300"></div>
                </Link>
              ))}
            </div>
          </nav>

        </div>
      </div>

      {/* 移动端导航菜单 */}
      <div className="lg:hidden border-t border-gray-100 bg-gray-50/50">
        <div className="container mx-auto px-4 py-3">
          <div className="grid grid-cols-3 gap-2">
            {navItems.map((item) => (
              <Link
                key={item.key}
                href={item.link}
                className="flex flex-col items-center justify-center p-3 text-gray-700 hover:text-blue-600 hover:bg-white rounded-xl transition-all duration-300 shadow-sm hover:shadow"
              >
                <div className="text-lg mb-1.5">{item.icon}</div>
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
