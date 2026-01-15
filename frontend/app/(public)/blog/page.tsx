'use client';

import { Card, Typography, Space } from 'antd';
import { CalendarOutlined, UserOutlined, TagOutlined } from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

const blogPosts = [
    {
        id: 1,
        title: 'Python编程入门指南',
        excerpt: '针对高中生的Python编程基础教程，从零开始学习编程思维。',
        author: '张老师',
        date: '2026-01-10',
        tags: ['Python', '编程基础', '入门'],
    },
    {
        id: 2,
        title: '算法竞赛中的动态规划',
        excerpt: '深入浅出讲解动态规划的基本原理和常见问题。',
        author: '李老师',
        date: '2026-01-08',
        tags: ['算法', '动态规划', '竞赛'],
    },
    {
        id: 3,
        title: '人工智能在教育中的应用',
        excerpt: '探讨AI技术如何改变传统教育模式，提升学习效率。',
        author: '王老师',
        date: '2026-01-05',
        tags: ['AI', '教育技术', '创新'],
    },
    {
        id: 4,
        title: '数据结构学习路线图',
        excerpt: '系统性的数据结构学习路径，适合信息学竞赛学生。',
        author: '赵老师',
        date: '2026-01-03',
        tags: ['数据结构', '学习路线', '竞赛'],
    },
];

export default function BlogPage() {
    return (
        <div className="min-h-screen bg-gray-50 py-12">
            <div className="container mx-auto px-4">
                <div className="text-center mb-12">
                    <Title level={1} className="text-4xl md:text-5xl font-bold">技术博客</Title>
                    <Paragraph className="text-gray-600 text-lg max-w-3xl mx-auto">
                        分享编程技巧、算法解析、AI技术应用等高质量技术文章
                    </Paragraph>
                </div>

                <div className="max-w-4xl mx-auto">
                    <div className="space-y-8">
                        {blogPosts.map((post) => (
                            <Card key={post.id} className="border-0 shadow-sm hover:shadow-md transition-shadow">
                                <div className="mb-4">
                                    <Title level={3}>{post.title}</Title>
                                    <Paragraph className="text-gray-600">{post.excerpt}</Paragraph>
                                </div>

                                <Space size="large">
                                    <div className="flex items-center gap-1">
                                        <UserOutlined className="text-gray-400" />
                                        <Text type="secondary">{post.author}</Text>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <CalendarOutlined className="text-gray-400" />
                                        <Text type="secondary">{post.date}</Text>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <TagOutlined className="text-gray-400" />
                                        <Space size="small">
                                            {post.tags.map((tag, index) => (
                                                <span key={index} className="px-2 py-1 bg-blue-100 text-blue-600 rounded text-sm">
                                                    {tag}
                                                </span>
                                            ))}
                                        </Space>
                                    </div>
                                </Space>
                            </Card>
                        ))}
                    </div>

                    <div className="mt-12 text-center">
                        <Paragraph className="text-gray-600">
                            更多精彩文章正在编写中，敬请期待...
                        </Paragraph>
                    </div>
                </div>
            </div>
        </div>
    );
}
