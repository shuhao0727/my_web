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

  // 登录函数 - 使用JWT安全认证（修复响应体重复读取问题，增强调试输出）
  const handleLogin = async (values: { name: string; studentId: string }) => {
    setLoginLoading(true);
    try {
      console.log('登录请求发送:', values);
      
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

      // 先读取响应文本（避免重复读取响应体）
      const responseText = await response.text();
      console.log('登录响应状态:', response.status, response.statusText);
      console.log('登录响应文本:', responseText.substring(0, 300));
      
      let data: any;
      try {
        // 尝试解析JSON
        data = JSON.parse(responseText);
        console.log('JSON解析成功:', data);
      } catch (parseError) {
        // JSON解析失败，说明服务器返回了非JSON响应（可能是HTML错误页面或纯文本错误）
        console.error('JSON解析失败，响应文本:', responseText.substring(0, 200));
        
        // 检查是否为HTML错误页面（包含<html>标签）
        if (responseText.toLowerCase().includes('<html>') || 
            responseText.toLowerCase().includes('<!doctype html>')) {
          // 这是HTML错误页面
          if (response.status >= 500) {
            throw new Error('服务器发生内部错误，请稍后重试');
          } else if (response.status >= 400) {
            throw new Error('请求错误，请检查网络连接');
          } else {
            throw new Error('服务器返回了非预期的响应格式');
          }
        } else if (responseText.includes('Internal Server Error')) {
          // 纯文本的Internal Server Error
          throw new Error('服务器内部错误，请稍后重试');
        } else {
          // 其他文本响应
          throw new Error(`服务器响应格式错误 (${response.status}): ${responseText.substring(0, 100)}`);
        }
      }

      if (response.ok && data.success) {
        console.log('登录成功，用户数据:', data.user);
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
        // 处理错误响应（包括401、500等）
        const errorMessage = data.error?.message || 
                           data.detail || 
                           data.message || 
                           `登录失败: ${response.status} ${response.statusText}`;
        console.error('登录失败:', errorMessage, data);
        throw new Error(errorMessage);
      }
    } catch (error: any) {
      console.error('登录错误:', error);
      // 提供更友好的错误信息
      let userMessage = error.message || '登录失败，请检查姓名和学号';
      if (userMessage.includes('Internal Server Error') || userMessage.includes('服务器内部错误') || userMessage.includes('服务器发生内部错误')) {
        userMessage = '服务器暂时不可用，请稍后重试';
      } else if (userMessage.includes('UNAUTHORIZED') || userMessage.includes('姓名或学号不正确')) {
        userMessage = '姓名或学号不正确，请检查输入';
      } else if (userMessage.includes('String should have at least 1 character')) {
        userMessage = '用户名和学号不能为空';
      } else if (userMessage.includes('请求错误，请检查网络连接')) {
        userMessage = '网络连接错误，请检查代理配置';
      }
      message.error(userMessage);
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
    <div className="min-h-screen flex flex-col bg-white">
      {/* 用户状态栏 - 只保留右侧用户信息 */}
      <div className="border-b border-gray-100 bg-white px-4 py-3">
        <div className="container mx-auto flex items-center justify-end">
          {/* 只保留用户信息与退出按钮 */}
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
                  />
                </Dropdown>
                <Button 
                  type="default" 
                  icon={<LogoutOutlined />}
                  onClick={handleLogout}
                  className="hidden md:inline-flex"
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
      </div>

      {/* 主要内容区域 - 卡片网格 */}
      <div className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* 程序卡片网格 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {programItems.map((item, index) => {
              const cardContent = (
                <div className="p-6 rounded-lg border border-gray-300 bg-white hover:border-blue-300 hover:shadow-md transition-all duration-200 h-full">
                  <div 
                    className="w-14 h-14 rounded-lg flex items-center justify-center mb-4 mx-auto"
                    style={{ backgroundColor: `${item.color}15` }}
                  >
                    <div style={{ color: item.color, fontSize: '24px' }}>
                      {item.icon}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-gray-900 group-hover:text-blue-600">
                      {item.title}
                    </div>
                  </div>
                </div>
              );

              // 如果链接存在，则包裹Link
              if (item.link && user.isLoggedIn) {
                return (
                  <Link
                    key={index}
                    href={item.link}
                    className="group block h-full"
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
                    className="group block h-full cursor-pointer"
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
