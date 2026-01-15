'use client';

import { useState } from 'react';
import { Form, Input, Button, Card, Typography, Space, Divider, Alert, Tabs, Row, Col } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined, BookOutlined } from '@ant-design/icons';
import Link from 'next/link';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

export default function LoginPage() {
    const [loading, setLoading] = useState(false);
    const [form] = Form.useForm();

    const onFinish = async (values: any) => {
        setLoading(true);
        console.log('Login values:', values);
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000));
        setLoading(false);
        alert(`欢迎登录！${values.username || values.email}`);
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
            <div className="container mx-auto px-4">
                <div className="max-w-4xl mx-auto">
                    <div className="text-center mb-12">
                        <Title level={1} className="text-4xl md:text-5xl font-bold">学生登录</Title>
                        <Paragraph className="text-gray-600 text-lg">
                            登录后即可使用AI智能体辅导、访问学习资源、查看个人学习数据
                        </Paragraph>
                    </div>

                    <Row gutter={[32, 32]}>
                        <Col xs={24} lg={14}>
                            <Card className="border-0 shadow-xl">
                                <Tabs defaultActiveKey="student" size="large">
                                    <TabPane tab="学生登录" key="student">
                                        <Form
                                            form={form}
                                            name="login"
                                            onFinish={onFinish}
                                            layout="vertical"
                                            className="mt-6"
                                        >
                                            <Form.Item
                                                name="username"
                                                rules={[
                                                    { required: true, message: '请输入学号或邮箱' },
                                                    { min: 3, message: '用户名至少3个字符' },
                                                ]}
                                            >
                                                <Input
                                                    size="large"
                                                    prefix={<UserOutlined />}
                                                    placeholder="学号或邮箱"
                                                />
                                            </Form.Item>

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

                                            <Form.Item>
                                                <div className="flex justify-between items-center mb-4">
                                                    <Form.Item name="remember" valuePropName="checked" noStyle>
                                                        <label className="flex items-center">
                                                            <input type="checkbox" className="mr-2" />
                                                            <Text>记住我</Text>
                                                        </label>
                                                    </Form.Item>
                                                    <Link href="/forgot-password" className="text-blue-600 hover:text-blue-800">
                                                        忘记密码？
                                                    </Link>
                                                </div>
                                            </Form.Item>

                                            <Form.Item>
                                                <Button
                                                    type="primary"
                                                    htmlType="submit"
                                                    size="large"
                                                    loading={loading}
                                                    block
                                                >
                                                    登录
                                                </Button>
                                            </Form.Item>

                                            <Divider>其他登录方式</Divider>

                                            <Space direction="vertical" className="w-full">
                                                <Button
                                                    icon={<MailOutlined />}
                                                    size="large"
                                                    block
                                                    className="flex items-center justify-center"
                                                >
                                                    使用邮箱验证码登录
                                                </Button>
                                                <Button
                                                    icon={<PhoneOutlined />}
                                                    size="large"
                                                    block
                                                    className="flex items-center justify-center"
                                                >
                                                    使用手机号登录
                                                </Button>
                                            </Space>
                                        </Form>
                                    </TabPane>

                                    <TabPane tab="教师登录" key="teacher">
                                        <Alert
                                            message="教师登录入口"
                                            description="教师请使用专属账号登录，登录后进入教师管理后台"
                                            type="info"
                                            showIcon
                                            className="mb-6"
                                        />
                                        <Form
                                            name="teacherLogin"
                                            onFinish={onFinish}
                                            layout="vertical"
                                        >
                                            <Form.Item
                                                name="teacherId"
                                                rules={[{ required: true, message: '请输入教师工号' }]}
                                            >
                                                <Input
                                                    size="large"
                                                    prefix={<BookOutlined />}
                                                    placeholder="教师工号"
                                                />
                                            </Form.Item>

                                            <Form.Item
                                                name="password"
                                                rules={[{ required: true, message: '请输入密码' }]}
                                            >
                                                <Input.Password
                                                    size="large"
                                                    prefix={<LockOutlined />}
                                                    placeholder="密码"
                                                />
                                            </Form.Item>

                                            <Form.Item>
                                                <Button
                                                    type="primary"
                                                    htmlType="submit"
                                                    size="large"
                                                    loading={loading}
                                                    block
                                                >
                                                    教师登录
                                                </Button>
                                            </Form.Item>
                                        </Form>
                                    </TabPane>
                                </Tabs>
                            </Card>
                        </Col>

                        <Col xs={24} lg={10}>
                            <Space direction="vertical" size="large" className="w-full">
                                <Card className="border-0 shadow-lg bg-gradient-to-r from-blue-600 to-blue-800 text-white">
                                    <div className="text-center">
                                        <Title level={3} className="!text-white">新用户注册</Title>
                                        <Paragraph className="text-blue-100">
                                            还没有账号？立即注册，享受完整的AI教育服务
                                        </Paragraph>
                                        <Link href="/register">
                                            <Button type="default" size="large" className="mt-4 bg-white text-blue-600 hover:bg-gray-100">
                                                免费注册
                                            </Button>
                                        </Link>
                                    </div>
                                </Card>

                                <Card className="border-0 shadow-lg">
                                    <Title level={4} className="mb-4">登录后您可以：</Title>
                                    <Space direction="vertical" size="middle">
                                        <div className="flex items-start gap-3">
                                            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                                                <UserOutlined className="text-blue-600" />
                                            </div>
                                            <div>
                                                <Text strong>使用AI智能体</Text>
                                                <Paragraph className="text-gray-600 text-sm m-0">
                                                    24小时AI学习助手，解答编程问题
                                                </Paragraph>
                                            </div>
                                        </div>
                                        <div className="flex items-start gap-3">
                                            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                                                <BookOutlined className="text-green-600" />
                                            </div>
                                            <div>
                                                <Text strong>访问学习资源</Text>
                                                <Paragraph className="text-gray-600 text-sm m-0">
                                                    编程教程、竞赛题目、视频课程
                                                </Paragraph>
                                            </div>
                                        </div>
                                        <div className="flex items-start gap-3">
                                            <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                                                <BookOutlined className="text-purple-600" />
                                            </div>
                                            <div>
                                                <Text strong>查看学习数据</Text>
                                                <Paragraph className="text-gray-600 text-sm m-0">
                                                    个人学习进度、成绩分析、能力评估
                                                </Paragraph>
                                            </div>
                                        </div>
                                        <div className="flex items-start gap-3">
                                            <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
                                                <BookOutlined className="text-orange-600" />
                                            </div>
                                            <div>
                                                <Text strong>与教师互动</Text>
                                                <Paragraph className="text-gray-600 text-sm m-0">
                                                    向教师提问、提交作业、获取反馈
                                                </Paragraph>
                                            </div>
                                        </div>
                                    </Space>
                                </Card>

                                <Alert
                                    message="安全提示"
                                    description="请妥善保管您的账号密码，不要与他人共享。定期修改密码以确保账户安全。"
                                    type="warning"
                                    showIcon
                                />
                            </Space>
                        </Col>
                    </Row>

                    <div className="mt-12 text-center">
                        <Text type="secondary">
                            遇到登录问题？请联系管理员：
                            <Link href="mailto:support@ai-education.com" className="ml-2 text-blue-600">
                                support@ai-education.com
                            </Link>
                        </Text>
                    </div>
                </div>
            </div>
        </div>
    );
}
