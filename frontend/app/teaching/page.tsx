'use client';

import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Paragraph } = Typography;

// 课程数据
const courses = [
  {
    id: 1,
    title: 'Python编程基础',
    description: '从零开始学习Python编程，掌握基本语法和流程控制',
    tags: ['Python', '编程入门'],
  },
  {
    id: 2,
    title: '数据结构与算法',
    description: '学习常用数据结构和算法，培养计算思维',
    tags: ['算法', '数据结构'],
  },
  {
    id: 3,
    title: 'Web前端开发',
    description: '学习HTML、CSS、JavaScript和现代Web开发',
    tags: ['Web开发', '前端'],
  },
  {
    id: 4,
    title: '人工智能入门',
    description: '了解机器学习基本概念，使用Python实现简单AI模型',
    tags: ['AI', '机器学习'],
  },
];

export default function TeachingPage() {
  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto p-4">
        {/* 课程列表 */}
        <div className="space-y-6">
          {courses.map(course => (
            <Card key={course.id} className="hover:shadow-md transition-shadow">
              <Title level={4} className="mb-3">{course.title}</Title>
              <Paragraph className="text-gray-600 mb-4">
                {course.description}
              </Paragraph>
              <div className="flex flex-wrap gap-2">
                {course.tags.map(tag => (
                  <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                    {tag}
                  </span>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
