'use client';

import { Form, Input, Button, Card, Typography, Space, Alert } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined, BookOutlined } from '@ant-design/icons';
import Link from 'next/link';

const { Title, Paragraph, Text } = Typography;

export default function RegisterPage() {
    const [form] = Form.useForm();

    const onFinish = async (values: any) => {
        console.log('Register values:', values);
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000));
        alert('注册成功！请登录。');
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
            <div className="container mx-auto px-4">
                <div className="max-w-2xl mx-auto">
                    <Card className="border-0 shadow-xl">
                        <div className="text-center mb-8">
                            <Title level={1} className="text-3xl font-bold">学生注册</Title>
                            <Paragraph className="text-gray-600">
                                创建账号，开启AI智能学习之旅
                            </Paragraph>
                        </div>

                        <Form
                            form={form}
                            name="register"
                            onFinish={onFinish}
                            layout="vertical"
                            className="space-y-6"
                        >
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Form.Item
                                    name="studentId"
                                    rules={[
                                        { required: true, message: '请输入学号' },
                                        { pattern: /^[0-9]+$/, message: '学号必须是数字' },
                                    ]}
                                >
                                    <Input
                                        size="large"
                                        prefix={<BookOutlined />}
                                        placeholder="学号"
                                    />
                                </Form.Item>

                                <Form.Item
                                    name="name"
                                    rules={[{ required: true, message: '请输入姓名' }]}
                                >
                                    <Input
                                        size="large"
                                        prefix={<UserOutlined />}
                                        placeholder="姓名"
                                    />
                                </Form.Item>
                            </div>

                            <Form.Item
                                name="email"
                                rules={[
                                    { required: true, message: '请输入邮箱' },
                                    { type: 'email', message: '请输入有效的邮箱地址' },
                                ]}
                            >
                                <Input
                                    size="large"
                                    prefix={<MailOutlined />}
                                    placeholder="邮箱"
                                />
                            </Form.Item>

                            <Form.Item
                                name="phone"
                                rules={[
                                    { required: false },
                                    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' },
                                ]}
                            >
                                <Input
                                    size="large"
                                    prefix={<PhoneOutlined />}
                                    placeholder="手机号（可选）"
                                />
                            </Form.Item>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Form.Item
                                    name="password"
                                    rules={[
                                        { required: true, message: '请输入密码' },
                                        { min: 6, message: '密码至少6个字符' },
                                    ]}
                                >
                                    <Input.Password
                                        size="large"
                                        prefix={<LockOutlined />}
                                        placeholder="密码"
                                    />
                                </Form.Item>

                                <Form.Item
                                    name="confirmPassword"
                                    dependencies={['password']}
                                    rules={[
                                        { required: true, message: '请确认密码' },
                                        ({ getFieldValue }) => ({
                                            validator(_, value) {
                                                if (!value || getFieldValue('password') === value) {
                                                    return Promise.resolve();
                                                }
                                                return Promise.reject(new Error('两次输入的密码不一致'));
                                            },
                                        }),
                                    ]}
                                >
                                    <Input.Password
                                        size="large"
                                        prefix={<LockOutlined />}
                                        placeholder="确认密码"
                                    />
                                </Form.Item>
                            </div>

                            <Form.Item>
                                <Alert
                                    message="注册须知"
                                    description="注册后即可使用AI智能体辅导、访问学习资源。请确保填写的信息真实有效。"
                                    type="info"
                                    showIcon
                                    className="mb-6"
                                />
                            </Form.Item>

                            <Form.Item>
                                <Button
                                    type="primary"
                                    htmlType="submit"
                                    size="large"
                                    block
                                >
                                    注册账号
                                </Button>
                            </Form.Item>

                            <div className="text-center">
                                <Text type="secondary">
                                    已有账号？<Link href="/login" className="text-blue-600">立即登录</Link>
                                </Text>
                            </div>
                        </Form>
                    </Card>
                </div>
            </div>
        </div>
    );
}
