"use client";

import React from 'react';
import { Typography } from 'antd';

const { Title, Text } = Typography;

export default function SchoolCourseProcessApp() {
  return (
    <div className="p-8 rounded-lg border border-gray-300 bg-white">
      <div className="text-center">
        <Title level={2} className="mb-4">校本课处理应用</Title>
        <Text type="secondary" className="block mb-8">
          这是一个用于处理校本课程的应用。
        </Text>
        <div className="mt-8">
          <Text type="secondary" className="text-sm">
            您可以在这里设计具体的功能页面。
          </Text>
        </div>
      </div>
    </div>
  );
}
