'use client';

import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Paragraph, Text } = Typography;

const blogPosts = [
  {
    id: 1,
    title: 'Python编程入门指南',
    excerpt: '针对高中生的Python编程基础教程',
    date: '2026-01-10',
  },
  {
    id: 2,
    title: '算法竞赛中的动态规划',
    excerpt: '动态规划的基本原理和常见问题',
    date: '2026-01-08',
  },
  {
    id: 3,
    title: '人工智能在教育中的应用',
    excerpt: '探讨AI技术如何改变传统教育模式',
    date: '2026-01-05',
  },
  {
    id: 4,
    title: '数据结构学习路线图',
    excerpt: '系统性的数据结构学习路径',
    date: '2026-01-03',
  },
];

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-2xl mx-auto p-4">
        <div className="space-y-6">
          {blogPosts.map((post) => (
            <Card key={post.id} className="hover:shadow-md transition-shadow">
              <Title level={4} className="mb-2">{post.title}</Title>
              <Paragraph className="text-gray-600 mb-3">{post.excerpt}</Paragraph>
              <Text type="secondary">{post.date}</Text>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
