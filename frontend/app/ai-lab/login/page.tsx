'use client';

import React, { useState } from 'react';
import { 
  UserOutlined, RobotOutlined, TeamOutlined, LockOutlined 
} from '@ant-design/icons';
import { 
  Button, Input, Card, Typography, Form 
} from 'antd';
import aiApi from '@/lib/aiApi';
import { useRouter } from 'next/navigation';

const { Title, Text } = Typography;

export default function AiLabLoginPage() {
  const router = useRouter();
  const [loginForm, setLoginForm] = useState({
    username: '',
    studentId: '',
  });
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState('');

  // 处理登录
  const handleLogin = async () => {
    const trimmedUsername = loginForm.username.trim();
    const trimmedStudentId = loginForm.studentId.trim();
    
    if (!trimmedUsername) {
      setLoginError('请输入用户名');
      return;
    }

    // 新增：验证学号不能为空
    if (!trimmedStudentId) {
      setLoginError('请输入学号');
      return;
    }

    setLoginLoading(true);
    setLoginError('');
    
    // 调用API登录（现在不会抛出错误，总是返回一个对象）
    const response = await aiApi.user.login(trimmedUsername, trimmedStudentId);
    
    if (response.success) {
      // 使用后端返回的用户信息
      const userData = {
        id: response.user.id,
        username: response.user.username,
        student_id: response.user.student_id,
        class_name: response.user.class_name,
        isAdmin: response.user.username === 'admin',
      };
      
      // 保存到本地存储
      localStorage.setItem('ai_lab_user', JSON.stringify(userData));
      
      // 提示用户登录成功
      setLoginError('登录成功！正在跳转到AI智能体界面...');
      
      // 跳转到主页面
      router.push('/ai-lab');
      
      // 重置表单
      setLoginForm({ username: '', studentId: '' });
    } else {
      // 显示具体的错误信息
      const errorMsg = response.message || '登录失败，请检查用户名和学号';
      setLoginError(errorMsg.includes('学号不正确') ? '学号不正确' : errorMsg);
    }
    
    setLoginLoading(false);
  };

  // 处理回车键
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full shadow-xl">
        <div className="text-center mb-8">
          <div className="inline-block p-4 bg-blue-100 rounded-2xl mb-4">
            <RobotOutlined className="text-4xl text-blue-600" />
          </div>
          <Title level={2}>AI智能体</Title>

        </div>

        {loginError && (
          <div className={`mb-4 p-3 rounded ${loginError.includes('成功') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {loginError}
          </div>
        )}

        <Form layout="vertical" onKeyUp={handleKeyPress}>
          <Form.Item label="用户名" required>
            <Input
              size="large"
              placeholder="请输入用户名"
              value={loginForm.username}
              onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
              prefix={<UserOutlined />}
            />
          </Form.Item>
          
          <Form.Item label="学号" required>
            <Input.Password
              size="large"
              placeholder="请输入学号"
              value={loginForm.studentId}
              onChange={(e) => setLoginForm({ ...loginForm, studentId: e.target.value })}
              prefix={<TeamOutlined />}
              visibilityToggle={true}
            />
          </Form.Item>

          <Button
            type="primary"
            size="large"
            block
            loading={loginLoading}
            onClick={handleLogin}
            icon={<LockOutlined />}
          >
            登录
          </Button>
        </Form>

     
      </Card>
    </div>
  );
}
