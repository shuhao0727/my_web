"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { LogoutOutlined, UserOutlined, BookOutlined, LoginOutlined } from '@ant-design/icons';
import { Button, Dropdown, Typography, Form, Input, Modal, message } from 'antd';

const { Text } = Typography;

export default function PersonalProgramsPage() {
  // 用户状态管理
  const [user, setUser] = useState<{ name: string; studentId: string; isLoggedIn: boolean }>({
    name: '',
    studentId: '',
    isLoggedIn: false,
  });
  
  // 登录模态框状态
  const [loginModalVisible, setLoginModalVisible] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginForm] = Form.useForm();

  // 个人程序卡片数据 - 简洁版本
  const programItems = [
    {
      icon: <BookOutlined />,
      title: '校本课处理',
      link: '/personal-programs/school-course-process',
      color: '#1890ff',
    },
  ];

  // 用户操作菜单
  const userMenuItems = [
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />,
      danger: true,
    },
  ];

  // 页面加载时检查登录状态
  useEffect(() => {
    const savedUser = localStorage.getItem('xbk_user');
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setUser({
          name: parsedUser.name,
          studentId: parsedUser.student_id,
          isLoggedIn: true,
        });
      } catch (error) {
        console.error('解析用户信息失败:', error);
        localStorage.removeItem('xbk_user');
      }
    }
  }, []);

  const handleMenuClick = (e: any) => {
    if (e.key === 'logout') {
      handleLogout();
    }
  };

  // 登录函数 - 使用JWT安全认证
  const handleLogin = async (values: { name: string; studentId: string }) => {
    setLoginLoading(true);
    try {
      const response = await fetch('/api/xbk/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: values.name,
          student_id: values.studentId,
        }),
      });

      // 检查响应内容类型
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('非JSON响应:', text.substring(0, 200));
        throw new Error(`服务器返回了非JSON响应 (${response.status}): ${text.substring(0, 100)}`);
      }

      const data = await response.json();

      if (response.ok && data.success) {
        // 保存用户信息和JWT token到localStorage
        const userData = {
          ...data.user,
          access_token: data.access_token,
          expires_in: data.expires_in,
          token_type: data.token_type,
        };
        localStorage.setItem('xbk_user', JSON.stringify(userData));
        setUser({
          name: data.user.name,
          studentId: data.user.student_id,
          isLoggedIn: true,
        });
        message.success(data.message || '登录成功');
        setLoginModalVisible(false);
        loginForm.resetFields();
      } else {
        throw new Error(data.detail || data.message || `登录失败: ${response.status}`);
      }
    } catch (error: any) {
      console.error('登录错误:', error);
      message.error(error.message || '登录失败，请检查姓名和学号');
    } finally {
      setLoginLoading(false);
    }
  };

  // 退出函数
  const handleLogout = () => {
    localStorage.removeItem('xbk_user');
    setUser({
      name: '',
      studentId: '',
      isLoggedIn: false,
    });
    message.success('已退出登录');
    // 刷新页面以清除状态
    window.location.href = '/personal-programs';
  };

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
          {/* 用户状态栏 */}
          <div className="flex justify-end mb-12">
            {user.isLoggedIn ? (
              <div className="flex items-center space-x-4">
                <Dropdown
                  menu={{
                    items: userMenuItems,
                    onClick: handleMenuClick,
                  }}
                  placement="bottomRight"
                >
                  <Button 
                    type="text" 
                    icon={<UserOutlined />}
                    className="flex items-center"
                  >
                    {user.name}
                  </Button>
                </Dropdown>
                <Button 
                  type="default" 
                  icon={<LogoutOutlined />}
                  onClick={handleLogout}
                >
                  退出
                </Button>
              </div>
            ) : (
              <Button 
                type="primary" 
                icon={<LoginOutlined />}
                onClick={() => setLoginModalVisible(true)}
              >
                登录
              </Button>
            )}
          </div>

          {/* 主要内容区域 - 卡片网格 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {programItems.map((item, index) => {
              const cardContent = (
                <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100 hover:border-transparent">
                  {/* 渐变背景 */}
                  <div className={`absolute inset-0 bg-gradient-to-br from-blue-400 to-blue-600 opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity duration-300`}></div>
                  
                  {/* 图标容器 */}
                  <div className="relative z-10 flex flex-col items-center">
                    <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6 transition-all duration-300 group-hover:scale-110 bg-blue-50">
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

              // 如果链接存在，则包裹Link
              if (item.link && user.isLoggedIn) {
                return (
                  <Link
                    key={index}
                    href={item.link}
                    className="block transform transition-transform duration-300 hover:scale-105"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {cardContent}
                  </Link>
                );
              } else {
                return (
                  <div 
                    key={index} 
                    className="block transform transition-transform duration-300 hover:scale-105 cursor-pointer"
                    onClick={() => {
                      if (!user.isLoggedIn) {
                        message.warning('请先登录');
                        setLoginModalVisible(true);
                      }
                    }}
                  >
                    {cardContent}
                  </div>
                );
              }
            })}
          </div>
        </div>
      </div>

      {/* 登录模态框 */}
      <Modal
        title="登录"
        open={loginModalVisible}
        onCancel={() => {
          setLoginModalVisible(false);
          loginForm.resetFields();
        }}
        footer={null}
        destroyOnHidden
      >
        <Form
          form={loginForm}
          layout="vertical"
          onFinish={handleLogin}
        >
          <Form.Item
            name="name"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>
          <Form.Item
            name="studentId"
            label="学号"
            rules={[{ required: true, message: '请输入学号' }]}
          >
            <Input.Password placeholder="请输入学号" />
          </Form.Item>
          <Form.Item>
            <div className="flex justify-end space-x-2">
              <Button onClick={() => setLoginModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={loginLoading}>
                登录
              </Button>
            </div>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
