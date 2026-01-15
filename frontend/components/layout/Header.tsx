import React from 'react';
import { Menu, Button, Space, Avatar, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { UserOutlined, HomeOutlined, BookOutlined, RobotOutlined, DashboardOutlined, LoginOutlined } from '@ant-design/icons';
import Link from 'next/link';

const Header: React.FC = () => {
    const navItems = [
        {
            key: 'home',
            label: '首页',
            icon: <HomeOutlined />,
            link: '/',
        },
        {
            key: 'about',
            label: '关于',
            icon: <UserOutlined />,
            link: '/about',
        },
        {
            key: 'blog',
            label: '博客',
            icon: <BookOutlined />,
            link: '/blog',
        },
        {
            key: 'ai-chat',
            label: 'AI智能体',
            icon: <RobotOutlined />,
            link: '/ai-chat',
        },
        {
            key: 'resources',
            label: '学习资源',
            icon: <BookOutlined />,
            link: '/resources',
        },
    ];

    const userMenuItems: MenuProps['items'] = [
        {
            key: 'profile',
            label: '个人中心',
            icon: <UserOutlined />,
        },
        {
            key: 'dashboard',
            label: '仪表板',
            icon: <DashboardOutlined />,
        },
        {
            type: 'divider',
        },
        {
            key: 'logout',
            label: '退出登录',
        },
    ];

    const isLoggedIn = false; // 暂时设置为未登录状态

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                <div className="flex items-center gap-8">
                    <Link href="/" className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
                            <RobotOutlined className="text-white text-lg" />
                        </div>
                        <span className="text-xl font-bold text-gray-900">AI教育平台</span>
                    </Link>

                    <nav className="hidden md:flex">
                        <Menu
                            mode="horizontal"
                            items={navItems.map(item => ({
                                key: item.key,
                                label: <Link href={item.link}>{item.label}</Link>,
                                icon: item.icon,
                            }))}
                            className="border-0"
                        />
                    </nav>
                </div>

                <div className="flex items-center gap-4">
                    {isLoggedIn ? (
                        <>
                            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
                                <div className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 hover:bg-gray-100">
                                    <Avatar icon={<UserOutlined />} />
                                    <span className="hidden md:inline">学生用户</span>
                                </div>
                            </Dropdown>
                            <Button type="primary" icon={<DashboardOutlined />}>
                                教师后台
                            </Button>
                        </>
                    ) : (
                        <Space>
                            <Link href="/login">
                                <Button icon={<LoginOutlined />}>学生登录</Button>
                            </Link>
                            <Link href="/register">
                                <Button type="primary">免费注册</Button>
                            </Link>
                        </Space>
                    )}
                </div>
            </div>

            {/* 移动端导航 */}
            <div className="md:hidden border-t">
                <div className="container mx-auto px-4 py-2">
                    <Menu
                        mode="horizontal"
                        items={navItems.map(item => ({
                            key: item.key,
                            label: <Link href={item.link}>{item.label}</Link>,
                            icon: item.icon,
                        }))}
                        className="border-0 justify-center"
                    />
                </div>
            </div>
        </header>
    );
};

export default Header;
