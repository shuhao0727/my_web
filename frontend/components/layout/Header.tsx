'use client';

import React from 'react';
import Link from 'next/link';
import { UserOutlined, HomeOutlined, BookOutlined, RobotOutlined, TrophyOutlined, DashboardOutlined, LoginOutlined, UserAddOutlined } from '@ant-design/icons';
import { Button, Avatar, Dropdown } from 'antd';
import type { MenuProps } from 'antd';

const Header: React.FC = () => {
  const isLoggedIn = false; // 暂时设置为未登录状态
  const isAdmin = false; // 暂时设置为非管理员

  // 传统导航菜单项
  const navItems = [
    {
      key: 'home',
      label: '首页',
      icon: <HomeOutlined />,
      link: '/',
      description: '网站主页'
    },
    {
      key: 'ai-lab',
      label: 'AI智能体实验室',
      icon: <RobotOutlined />,
      link: '/ai-lab',
      description: '与AI智能体对话学习'
    },
    {
      key: 'competition',
      label: '信息学竞赛',
      icon: <TrophyOutlined />,
      link: '/competition',
      description: '竞赛教程与资源'
    },
    {
      key: 'teaching',
      label: '信息技术教学',
      icon: <BookOutlined />,
      link: '/teaching',
      description: '课程体系与教学资源'
    },
    {
      key: 'resources',
      label: '学习资源',
      icon: <BookOutlined />,
      link: '/resources',
      description: '教程、题解、模板'
    },
    {
      key: 'blog',
      label: '教学博客',
      icon: <BookOutlined />,
      link: '/blog',
      description: '教学心得与技术分享'
    },
    {
      key: 'about',
      label: '关于我',
      icon: <UserOutlined />,
      link: '/about',
      description: '教师介绍'
    }
  ];

  // 管理员专用菜单项
  const adminNavItems = [
    {
      key: 'admin-dashboard',
      label: '管理仪表板',
      icon: <DashboardOutlined />,
      link: '/admin/dashboard',
      description: '数据统计与分析'
    },
    {
      key: 'admin-students',
      label: '学生管理',
      icon: <UserOutlined />,
      link: '/admin/students',
      description: '学生账户管理'
    },
    {
      key: 'admin-agents',
      label: '智能体管理',
      icon: <RobotOutlined />,
      link: '/admin/agents',
      description: 'AI智能体配置'
    }
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      label: '个人中心',
      icon: <UserOutlined />,
    },
    {
      key: 'my-interactions',
      label: '我的对话记录',
      icon: <BookOutlined />,
    },
    {
      key: 'my-resources',
      label: '我的学习资源',
      icon: <BookOutlined />,
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      label: '退出登录',
    },
  ];

  return (
    <header className="bg-white shadow-md">
      {/* 主导航栏 */}
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo区域 */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3">
              <div className="bg-blue-600 text-white p-2 rounded-lg">
                <RobotOutlined className="text-xl" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">wangsh</h1>
              </div>
            </Link>
          </div>

          {/* 桌面端导航菜单 */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.key}
                href={item.link}
                className="group relative px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors duration-200"
              >
                <div className="flex items-center space-x-2">
                  {item.icon}
                  <span className="font-medium">{item.label}</span>
                </div>
                <div className="absolute top-full left-0 mt-1 w-48 bg-white shadow-lg rounded-md p-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <p className="text-sm text-gray-600">{item.description}</p>
                </div>
              </Link>
            ))}
            
            {/* 管理员菜单（如果用户是管理员） */}
            {isAdmin && adminNavItems.map((item) => (
              <Link
                key={item.key}
                href={item.link}
                className="px-4 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors duration-200 flex items-center space-x-2"
              >
                {item.icon}
                <span className="font-medium">{item.label}</span>
              </Link>
            ))}
          </nav>

          {/* 用户操作区域 */}
          <div className="flex items-center space-x-4">
            {isLoggedIn ? (
              <>
                <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
                  <div className="flex items-center space-x-2 cursor-pointer hover:bg-gray-100 p-2 rounded-md">
                    <Avatar icon={<UserOutlined />} className="bg-blue-500" />
                    <div className="hidden md:block">
                      <p className="text-sm font-medium">学生姓名</p>
                      <p className="text-xs text-gray-500">高一(1)班</p>
                    </div>
                  </div>
                </Dropdown>
                {isAdmin && (
                  <Link href="/admin/dashboard">
                    <Button type="primary" icon={<DashboardOutlined />}>
                      管理后台
                    </Button>
                  </Link>
                )}
              </>
            ) : (
              <div className="flex items-center space-x-3">
                <Link href="/login">
                  <Button icon={<LoginOutlined />} className="flex items-center">
                    <span className="hidden sm:inline">学生登录</span>
                  </Button>
                </Link>
                <Link href="/register">
                  <Button type="primary" icon={<UserAddOutlined />} className="flex items-center">
                    <span className="hidden sm:inline">注册账号</span>
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 移动端导航菜单 */}
      <div className="lg:hidden border-t">
        <div className="container mx-auto px-4 py-2">
          <div className="grid grid-cols-3 gap-1">
            {navItems.slice(0, 6).map((item) => (
              <Link
                key={item.key}
                href={item.link}
                className="flex flex-col items-center justify-center p-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
              >
                {item.icon}
                <span className="text-xs mt-1">{item.label}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
