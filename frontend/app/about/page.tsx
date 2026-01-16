'use client';

import React from 'react';
import { MailOutlined, PhoneOutlined } from '@ant-design/icons';
import { Typography, Space } from 'antd';

const { Title, Paragraph, Text } = Typography;

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-2xl mx-auto p-4">
        <Title level={2} className="mb-6">关于我</Title>
        
        <Paragraph className="text-gray-600 mb-6">
          专注于信息技术教学与竞赛辅导，致力于通过技术手段提升教学质量，
          帮助学生掌握编程思维和算法能力。
        </Paragraph>
        
        <div className="space-y-4 mb-8">
          <div>
            <Text strong className="block mb-1">• 信息技术教师</Text>
            <Text type="secondary" className="block pl-4">
              Python编程、数据结构、Web开发
            </Text>
          </div>
          
          <div>
            <Text strong className="block mb-1">• 信息学竞赛教练</Text>
            <Text type="secondary" className="block pl-4">
              CSP/NOIP竞赛辅导、算法训练
            </Text>
          </div>
        </div>

        <Title level={4} className="mb-4">联系信息</Title>
        
        <Space direction="vertical" size="middle" className="w-full mb-6" orientation="vertical">
          <div className="flex items-center">
            <MailOutlined className="text-blue-600 mr-3" />
            <div>
              <Text strong className="block">电子邮件</Text>
              <Text type="secondary">teacher.wang@example.com</Text>
            </div>
          </div>
          
          <div className="flex items-center">
            <PhoneOutlined className="text-green-600 mr-3" />
            <div>
              <Text strong className="block">联系电话</Text>
              <Text type="secondary">138-XXXX-XXXX</Text>
            </div>
          </div>
        </Space>
      </div>
    </div>
  );
}
