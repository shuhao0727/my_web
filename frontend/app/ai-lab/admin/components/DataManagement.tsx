import React from 'react';
import { Alert, Card, Typography, Statistic, Tag, Badge } from 'antd';
import type { DataManagementProps } from './types';

const { Title, Text } = Typography;

const DataManagement: React.FC<DataManagementProps> = ({
  dataStats,
  adminAgents,
  user
}) => {
  return (
    <div className="h-full flex flex-col">
      <div className="mb-6 flex-shrink-0">
        <Title level={3}>智能体数据管理</Title>
        <Text type="secondary">查看系统数据统计和分析</Text>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8 flex-shrink-0">
        <Card>
          <Statistic title="总对话数" value={dataStats.total_conversations} />
        </Card>
        <Card>
          <Statistic title="总消息数" value={dataStats.total_messages} />
        </Card>
        <Card>
          <Statistic title="总Token数" value={dataStats.total_tokens} />
        </Card>
        <Card>
          <Statistic title="活跃智能体" value={dataStats.active_agents} />
        </Card>
        <Card>
          <Statistic title="总用户数" value={dataStats.total_users} />
        </Card>
      </div>
      
      <div className="flex-grow overflow-auto">
        <Card title="使用统计" className="h-full">
          <Alert
            title="统计功能开发中"
            description="详细的数据分析图表和报告功能正在开发中，将展示更详细的使用统计和趋势分析。"
            type="info"
            className="mb-4"
          />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
            <Card title="智能体使用排行" className="h-full">
              <div className="space-y-4 h-full overflow-auto">
                {adminAgents.slice(0, 5).map((agent, index) => (
                  <div key={agent.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Badge count={index + 1} />
                      <div className="text-lg">{agent.icon}</div>
                      <div>
                        <div className="font-medium">{agent.name}</div>
                        <div className="text-xs text-gray-500">{agent.api_type}</div>
                      </div>
                    </div>
                    <div className="text-gray-500">--</div>
                  </div>
                ))}
              </div>
            </Card>
            
            <Card title="系统状态" className="h-full">
              <div className="space-y-4 h-full">
                <div className="flex justify-between items-center">
                  <span>数据库状态</span>
                  <Tag color="green">正常</Tag>
                </div>
                <div className="flex justify-between items-center">
                  <span>API服务状态</span>
                  <Tag color="green">正常</Tag>
                </div>
                <div className="flex justify-between items-center">
                  <span>系统负载</span>
                  <Tag color="blue">低</Tag>
                </div>
                <div className="flex justify-between items-center">
                  <span>存储空间</span>
                  <Tag color="blue">充足</Tag>
                </div>
              </div>
            </Card>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default DataManagement;
