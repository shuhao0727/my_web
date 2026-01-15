'use client';

import { Button } from 'antd';
import { RobotOutlined, BookOutlined, TeamOutlined } from '@ant-design/icons';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            AI教育平台
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            面向高中信息技术老师、信息学竞赛教练和AI爱好者的智能教育平台。
            集成Dify AI智能体，提供个性化学习体验，助力学生成长。
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="bg-white p-6 rounded-xl shadow-lg border">
            <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
              <RobotOutlined className="text-2xl text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">AI智能体辅导</h3>
            <p className="text-gray-600">
              集成Dify AI智能体，提供24小时个性化学习辅导，解答编程问题，指导算法思路。
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg border">
            <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center mb-4">
              <BookOutlined className="text-2xl text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">丰富学习资源</h3>
            <p className="text-gray-600">
              编程教程、算法竞赛题目、AI/机器学习资料、数据结构详解，满足不同层次学生需求。
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg border">
            <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center mb-4">
              <TeamOutlined className="text-2xl text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">教师内容管理</h3>
            <p className="text-gray-600">
              教师可发布文章、教程、竞赛题目，管理学生数据，分析学习效果，实现精准教学。
            </p>
          </div>
        </div>

        <div className="text-center">
          <div className="space-x-4">
            <Link href="/login">
              <Button type="primary" size="large">
                学生登录
              </Button>
            </Link>
            <Link href="/about">
              <Button size="large">
                关于我们
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
