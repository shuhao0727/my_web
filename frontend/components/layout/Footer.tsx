import React from 'react';
import { Layout, Row, Col, Typography, Space, Divider } from 'antd';
import { GithubOutlined, WechatOutlined, MailOutlined, PhoneOutlined, EnvironmentOutlined } from '@ant-design/icons';
import Link from 'next/link';

const { Footer: AntFooter } = Layout;
const { Text, Title, Link: AntLink } = Typography;

const Footer: React.FC = () => {
    const currentYear = new Date().getFullYear();

    const footerLinks = {
        快速链接: [
            { label: '首页', href: '/' },
            { label: '关于我们', href: '/about' },
            { label: '博客文章', href: '/blog' },
            { label: 'AI智能体', href: '/ai-chat' },
            { label: '学习资源', href: '/resources' },
        ],
        学习资源: [
            { label: '编程教程', href: '/resources/programming' },
            { label: 'AI/机器学习', href: '/resources/ai-ml' },
            { label: '算法竞赛', href: '/resources/algorithms' },
            { label: '数据结构', href: '/resources/data-structures' },
            { label: '在线课程', href: '/resources/courses' },
        ],
        支持帮助: [
            { label: '学生指南', href: '/help/student-guide' },
            { label: '教师手册', href: '/help/teacher-manual' },
            { label: '常见问题', href: '/help/faq' },
            { label: '联系我们', href: '/contact' },
            { label: '意见反馈', href: '/feedback' },
        ],
        政策条款: [
            { label: '隐私政策', href: '/privacy' },
            { label: '服务条款', href: '/terms' },
            { label: '使用协议', href: '/agreement' },
            { label: '数据安全', href: '/data-security' },
            { label: '版权声明', href: '/copyright' },
        ],
    };

    const contactInfo = [
        { icon: <MailOutlined />, text: 'contact@ai-edu.com', href: 'mailto:contact@ai-edu.com' },
        { icon: <PhoneOutlined />, text: '(010) 1234-5678', href: 'tel:01012345678' },
        { icon: <EnvironmentOutlined />, text: '北京市海淀区中关村大街1号', href: '#' },
    ];

    return (
        <AntFooter className="bg-gray-50 border-t mt-auto">
            <div className="container mx-auto px-4 py-8">
                <Row gutter={[32, 32]}>
                    {/* 平台介绍 */}
                    <Col xs={24} md={8}>
                        <div className="mb-6">
                            <div className="flex items-center gap-2 mb-4">
                                <div className="h-10 w-10 rounded-lg bg-blue-600 flex items-center justify-center">
                                    <span className="text-white text-xl font-bold">AI</span>
                                </div>
                                <Title level={3} className="mb-0">AI教育平台</Title>
                            </div>
                            <Text type="secondary" className="text-base">
                                面向高中信息技术老师、信息学竞赛教练和AI爱好者的智能教育平台。
                                集成Dify AI智能体，提供个性化学习体验，助力学生成长。
                            </Text>
                        </div>

                        <Space orientation="vertical" size="small">
                            {contactInfo.map((item, index) => (
                                <div key={index} className="flex items-center gap-2">
                                    <span className="text-gray-400">{item.icon}</span>
                                    {item.href === '#' ? (
                                        <Text type="secondary" className="text-sm">{item.text}</Text>
                                    ) : (
                                        <AntLink href={item.href} target="_blank" className="text-sm">
                                            {item.text}
                                        </AntLink>
                                    )}
                                </div>
                            ))}
                        </Space>
                    </Col>

                    {/* 链接部分 */}
                    {Object.entries(footerLinks).map(([title, links]) => (
                        <Col xs={12} md={4} key={title}>
                            <Title level={5} className="mb-4">{title}</Title>
                            <ul className="list-none p-0 m-0 space-y-2">
                                {links.map((link, index) => (
                                    <li key={index}>
                                        <Link href={link.href} className="text-gray-600 hover:text-blue-600 transition-colors">
                                            {link.label}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </Col>
                    ))}
                </Row>

                <Divider className="my-8" />

                <Row justify="space-between" align="middle">
                    <Col>
                        <Text type="secondary">
                            © {currentYear} AI教育平台 版权所有。保留所有权利。
                        </Text>
                    </Col>
                    <Col>
                        <Space size="large">
                            <AntLink href="https://github.com/ai-education-platform" target="_blank">
                                <GithubOutlined className="text-xl hover:text-blue-600 transition-colors" />
                            </AntLink>
                            <AntLink href="#">
                                <WechatOutlined className="text-xl hover:text-blue-600 transition-colors" />
                            </AntLink>
                            <AntLink href="/sitemap">
                                <Text className="hover:text-blue-600 transition-colors">网站地图</Text>
                            </AntLink>
                            <AntLink href="/admin">
                                <Text className="hover:text-blue-600 transition-colors">教师入口</Text>
                            </AntLink>
                        </Space>
                    </Col>
                </Row>

                {/* 备案信息 */}
                <div className="mt-6 text-center">
                    <Text type="secondary" className="text-sm">
                        <Space size="middle">
                            <span>京ICP备12345678号</span>
                            <span>京公网安备11010102001234号</span>
                            <AntLink href="http://www.beian.gov.cn" target="_blank">
                                公安机关备案号
                            </AntLink>
                        </Space>
                    </Text>
                </div>
            </div>
        </AntFooter>
    );
};

export default Footer;
