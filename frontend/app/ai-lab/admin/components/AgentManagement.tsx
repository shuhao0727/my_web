import React, { useState } from 'react';
import { 
  PlusOutlined, DeleteOutlined, SearchOutlined,
  CheckOutlined, CloseOutlined
} from '@ant-design/icons';
import { 
  Button, Input, Card, Typography, Spin, 
  Switch, Table, Badge, Popconfirm, Tooltip, Modal, Form, Select, Space 
} from 'antd';
import type { AgentManagementProps, AiAgent } from './types';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Option } = Select;

interface InternalAgentManagementProps extends AgentManagementProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onToggleAgentStatus: (agentId: number, isActive: boolean) => void;
  onDeleteAgent: (agentId: number) => void;
}

const AgentManagement: React.FC<InternalAgentManagementProps> = ({
  adminAgents,
  loading,
  user,
  onRefresh,
  onCreateAgent,
  searchQuery,
  onSearchChange,
  onToggleAgentStatus,
  onDeleteAgent
}) => {
  const [showCreateAgentModal, setShowCreateAgentModal] = useState(false);
  const [newAgentForm, setNewAgentForm] = useState({
    name: '',
    description: '',
    icon: '🤖',
    api_type: 'mock',
  });

  // 筛选智能体
  const filteredAgents = adminAgents.filter(agent =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.api_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateAgent = () => {
    // 这里应该调用父组件的创建函数
    onCreateAgent();
    setShowCreateAgentModal(false);
    setNewAgentForm({ name: '', description: '', icon: '🤖', api_type: 'mock' });
  };

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6 flex-shrink-0">
        <div className="flex justify-between items-center">
          <div>
            <Title level={3}>智能体管理</Title>
            <Text type="secondary">创建、编辑和管理AI智能体</Text>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setShowCreateAgentModal(true)}
          >
            创建新智能体
          </Button>
        </div>
      </div>
      
      <div className="flex-grow overflow-hidden">
        <Card className="h-full">
          <div className="mb-4">
            <Input
              placeholder="搜索智能体..."
              prefix={<SearchOutlined />}
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              allowClear
              className="max-w-md"
            />
          </div>

          <Table
            dataSource={filteredAgents}
            loading={loading}
            rowKey="id"
            columns={[
              {
                title: '图标',
                dataIndex: 'icon',
                key: 'icon',
                width: 80,
                render: (icon) => <div className="text-2xl">{icon}</div>,
              },
              {
                title: '名称',
                dataIndex: 'name',
                key: 'name',
                render: (text, record) => (
                  <div className="flex items-center space-x-2">
                    <span>{text}</span>
                    {!record.is_active && (
                      <Badge status="default" text="已禁用" />
                    )}
                  </div>
                ),
              },
              {
                title: '描述',
                dataIndex: 'description',
                key: 'description',
                render: (text) => text || '--',
              },
              {
                title: 'API类型',
                dataIndex: 'api_type',
                key: 'api_type',
                width: 120,
              },
              {
                title: '创建时间',
                dataIndex: 'created_at',
                key: 'created_at',
                width: 140,
                render: (text) => {
                  // 避免hydration错误，使用稳定的日期格式
                  if (!text) return '--';
                  try {
                    const date = new Date(text);
                    return date.toISOString().split('T')[0];
                  } catch {
                    return text;
                  }
                },
              },
              {
                title: '状态',
                dataIndex: 'is_active',
                key: 'is_active',
                width: 120,
                render: (isActive, record) => (
                  <Tooltip title={isActive ? "禁用" : "启用"}>
                    <Switch
                      checked={isActive}
                      onChange={() => onToggleAgentStatus(record.id, isActive)}
                      checkedChildren={<CheckOutlined />}
                      unCheckedChildren={<CloseOutlined />}
                    />
                  </Tooltip>
                ),
              },
              {
                title: '操作',
                key: 'actions',
                width: 120,
                render: (_, record) => (
                  <Space size="small">
                    <Popconfirm
                      title="确定要删除这个智能体吗？"
                      onConfirm={() => onDeleteAgent(record.id)}
                    >
                      <Button danger size="small" icon={<DeleteOutlined />}>
                        删除
                      </Button>
                    </Popconfirm>
                  </Space>
                ),
              },
            ]}
            pagination={{ pageSize: 10 }}
            scroll={{ y: 'calc(100vh - 300px)' }}
          />
        </Card>
      </div>

      {/* 创建智能体模态框 */}
      <Modal
        title="创建新智能体"
        open={showCreateAgentModal}
        onCancel={() => setShowCreateAgentModal(false)}
        onOk={handleCreateAgent}
        confirmLoading={false}
      >
        <Form layout="vertical">
          <Form.Item label="名称" required>
            <Input
              value={newAgentForm.name}
              onChange={(e) => setNewAgentForm({ ...newAgentForm, name: e.target.value })}
              placeholder="请输入智能体名称"
            />
          </Form.Item>
          
          <Form.Item label="描述">
            <Input.TextArea
              value={newAgentForm.description}
              onChange={(e) => setNewAgentForm({ ...newAgentForm, description: e.target.value })}
              placeholder="请输入智能体描述"
              rows={3}
            />
          </Form.Item>
          
          <Form.Item label="图标">
            <Select
              value={newAgentForm.icon}
              onChange={(value) => setNewAgentForm({ ...newAgentForm, icon: value })}
            >
              <Option value="🤖">🤖 机器人</Option>
              <Option value="🧮">🧮 数学</Option>
              <Option value="💻">💻 代码</Option>
              <Option value="⚡">⚡ 算法</Option>
              <Option value="📚">📚 学习</Option>
              <Option value="🎓">🎓 教育</Option>
              <Option value="🔍">🔍 搜索</Option>
            </Select>
          </Form.Item>
          
          <Form.Item label="API类型">
            <Select
              value={newAgentForm.api_type}
              onChange={(value) => setNewAgentForm({ ...newAgentForm, api_type: value })}
            >
              <Option value="mock">模拟API</Option>
              <Option value="echo">回声测试</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AgentManagement;
