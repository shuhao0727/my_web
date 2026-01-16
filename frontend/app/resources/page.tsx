'use client';

import React, { useState } from 'react';
import { SearchOutlined, DownloadOutlined } from '@ant-design/icons';
import { 
  Card, Typography, Input, Button, Tag, 
  Select
} from 'antd';

const { Title, Paragraph } = Typography;
const { Search } = Input;
const { Option } = Select;

// 资源数据
const resources = [
  {
    id: '1',
    title: 'Python编程教程',
    description: '完整的Python编程教程，包含基础语法和实战项目',
    type: '教程',
    tags: ['Python', '入门', '实战'],
    format: 'Typst',
  },
  {
    id: '2',
    title: 'C++ STL详解',
    description: '深入讲解C++ STL的各个组件，包含大量代码示例',
    type: '参考书',
    tags: ['C++', 'STL', '模板'],
    format: 'PDF',
  },
  {
    id: '3',
    title: '动态规划算法',
    description: '动态规划算法的系统讲解，包含经典例题',
    type: '教程',
    tags: ['算法', '动态规划', '竞赛'],
    format: 'Typst',
  },
  {
    id: '4',
    title: '数据结构与算法分析',
    description: '常用数据结构和算法的详细讲解与复杂度分析',
    type: '参考书',
    tags: ['数据结构', '算法', '复杂度'],
    format: 'PDF',
  },
];

// 类型选项
const typeOptions = [
  { label: '全部', value: 'all' },
  { label: '教程', value: '教程' },
  { label: '参考书', value: '参考书' },
];

// 格式选项
const formatOptions = [
  { label: '全部', value: 'all' },
  { label: 'Typst', value: 'Typst' },
  { label: 'PDF', value: 'PDF' },
];

export default function ResourcesPage() {
  const [searchText, setSearchText] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedFormat, setSelectedFormat] = useState('all');

  // 过滤资源
  const filteredResources = resources.filter(resource => {
    if (searchText && !resource.title.toLowerCase().includes(searchText.toLowerCase()) && 
        !resource.description.toLowerCase().includes(searchText.toLowerCase())) {
      return false;
    }
    
    if (selectedType !== 'all' && resource.type !== selectedType) {
      return false;
    }
    
    if (selectedFormat !== 'all' && resource.format !== selectedFormat) {
      return false;
    }
    
    return true;
  });

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto p-4">
        {/* 筛选区域 */}
        <div className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <Search
                placeholder="搜索资源..."
                allowClear
                enterButton={<SearchOutlined />}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
              />
            </div>
            <div>
              <Select
                className="w-full"
                value={selectedType}
                onChange={setSelectedType}
                placeholder="资源类型"
              >
                {typeOptions.map(type => (
                  <Option key={type.value} value={type.value}>
                    {type.label}
                  </Option>
                ))}
              </Select>
            </div>
            <div>
              <Select
                className="w-full"
                value={selectedFormat}
                onChange={setSelectedFormat}
                placeholder="文件格式"
              >
                {formatOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </div>
          </div>
        </div>

        {/* 资源列表 */}
        {filteredResources.length > 0 ? (
          <div className="space-y-6">
            {filteredResources.map(resource => (
              <Card key={resource.id} className="hover:shadow-md transition-shadow">
                <Title level={4} className="mb-3">{resource.title}</Title>
                <Paragraph className="text-gray-600 mb-4">
                  {resource.description}
                </Paragraph>
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                    {resource.type}
                  </span>
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                    {resource.format}
                  </span>
                  {resource.tags.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                </div>
                <Button type="primary" size="small">
                  下载
                </Button>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Paragraph className="text-gray-500">
              未找到相关资源
            </Paragraph>
          </div>
        )}
      </div>
    </div>
  );
}
