import React, { useState } from 'react';
import { 
  PlusOutlined, DeleteOutlined, SearchOutlined,
  CheckOutlined, CloseOutlined, EditOutlined, ThunderboltOutlined
} from '@ant-design/icons';
import { 
  Button, Input, Card, Typography, 
  Switch, Table, Badge, Popconfirm, Tooltip, Modal, Form, Select, Space, Radio, Input as AntInput, message
} from 'antd';
import type { AgentManagementProps, AiAgent, CreateAgentForm } from './types';
import type { ColumnsType } from 'antd/es/table';
import { testConnectionWithFeedback, TestConnectionParams } from '@/lib/agentTestService';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = AntInput;

interface InternalAgentManagementProps extends AgentManagementProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onToggleAgentStatus: (agentId: number, isActive: boolean) => void;
  onDeleteAgent: (agentId: number) => void;
  onCreateAgent: (form: CreateAgentForm) => void;
  onEditAgent?: (agentId: number, form: CreateAgentForm) => void;
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
  onDeleteAgent,
  onEditAgent
}) => {
  const [showCreateAgentModal, setShowCreateAgentModal] = useState(false);
  const [editingAgent, setEditingAgent] = useState<AiAgent | null>(null);
  const [newAgentForm, setNewAgentForm] = useState<CreateAgentForm>({
    name: '',
    api_type: 'deepseek',
    api_key: '',
    base_url: '',
    model: '',
    app_id: '',
    is_active: true,
  });

  // 筛选智能体
  const filteredAgents = adminAgents.filter(agent =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.api_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.model?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.app_id?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateAgent = () => {
    // 调用父组件的创建函数，传递表单数据
    onCreateAgent(newAgentForm);
    setShowCreateAgentModal(false);
    resetForm();
  };

  const handleEditAgent = (agent: AiAgent) => {
    setEditingAgent(agent);
    setNewAgentForm({
      name: agent.name,
      api_type: agent.api_type,
      api_key: agent.api_key || '',
      base_url: agent.base_url || '',
      model: agent.model || '',
      app_id: agent.app_id || '',
      is_active: agent.is_active,
    });
    setShowCreateAgentModal(true);
  };

  const handleUpdateAgent = () => {
    if (editingAgent && onEditAgent) {
      onEditAgent(editingAgent.id, newAgentForm);
    } else {
      // 如果没有提供编辑函数，则调用创建函数（理论上不应该发生）
      onCreateAgent(newAgentForm);
    }
    setShowCreateAgentModal(false);
    resetForm();
    setEditingAgent(null);
  };

  const resetForm = () => {
    setNewAgentForm({
      name: '',
      api_type: 'deepseek',
      api_key: '',
      base_url: '',
      model: '',
      app_id: '',
      is_active: true,
    });
  };

  const handleModalCancel = () => {
    setShowCreateAgentModal(false);
    resetForm();
    setEditingAgent(null);
  };

  const handleModalOk = () => {
    if (editingAgent) {
      handleUpdateAgent();
    } else {
      handleCreateAgent();
    }
  };

  // 测试连接功能
  const [testingConnection, setTestingConnection] = useState(false);
  
  const handleTestConnection = async () => {
    // 确保必填字段有值（按钮的 disabled 状态应该已经保证）
    if (!newAgentForm.api_key || !newAgentForm.base_url) {
      message.error('请先填写API密钥和基础URL');
      return;
    }
    
    setTestingConnection(true);
    try {
      const params: TestConnectionParams = {
        api_type: newAgentForm.api_type,
        api_key: newAgentForm.api_key,
        base_url: newAgentForm.base_url,
        model: newAgentForm.model,
        app_id: newAgentForm.app_id,
        agentId: editingAgent?.id,
      };
      
      await testConnectionWithFeedback(params, true);
    } catch (error: any) {
      console.error('测试连接出错:', error);
      message.error(`测试连接失败: ${error.message || '未知错误'}`);
    } finally {
      setTestingConnection(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex-grow overflow-hidden">
        <Card className="h-full">
          <div className="mb-4 flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Input
                placeholder="搜索智能体（名称、API类型、模型等）..."
                prefix={<SearchOutlined />}
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                allowClear
                className="max-w-md"
              />
            </div>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setShowCreateAgentModal(true)}
            >
              创建新智能体
            </Button>
          </div>

          <Table
            dataSource={filteredAgents}
            loading={loading}
            rowKey="id"
            columns={[
              {
                title: '名称',
                dataIndex: 'name',
                key: 'name',
                width: 120,
                render: (text, record) => (
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{text}</span>
                    {!record.is_active && (
                      <Badge status="default" text="已禁用" />
                    )}
                  </div>
                ),
              },
              {
                title: 'API类型',
                dataIndex: 'api_type',
                key: 'api_type',
                width: 120,
                render: (text) => (
                  <Badge 
                    text={text === 'deepseek' ? 'DeepSeek类' : 'Dify类'} 
                    color={text === 'deepseek' ? 'blue' : 'green'} 
                  />
                ),
              },
              {
                title: 'API',
                key: 'api',
                width: 240,
                render: (_, record) => {
                  const url = record.base_url || '--';
                  return (
                    <Tooltip title={url}>
                      <span className="truncate block max-w-full text-blue-600 font-mono text-sm">
                        {url}
                      </span>
                    </Tooltip>
                  );
                },
              },
              {
                title: '状态',
                dataIndex: 'is_active',
                key: 'is_active',
                width: 90,
                align: 'center' as const,
                render: (isActive, record) => (
                  <Tooltip title={isActive ? "点击禁用" : "点击启用"}>
                    <Switch
                      checked={isActive}
                      onChange={() => onToggleAgentStatus(record.id, isActive)}
                      checkedChildren={<CheckOutlined />}
                      unCheckedChildren={<CloseOutlined />}
                      size="small"
                    />
                  </Tooltip>
                ),
              },
              {
                title: '操作',
                key: 'actions',
                width: 110,
                align: 'center' as const,
                render: (_, record) => (
                  <Space size="small">
                    <Tooltip title="编辑">
                      <Button 
                        size="small" 
                        icon={<EditOutlined />}
                        onClick={() => handleEditAgent(record)}
                      />
                    </Tooltip>
                    <Popconfirm
                      title="确定要删除这个智能体吗？"
                      onConfirm={() => onDeleteAgent(record.id)}
                    >
                      <Tooltip title="删除">
                        <Button danger size="small" icon={<DeleteOutlined />} />
                      </Tooltip>
                    </Popconfirm>
                  </Space>
                ),
              },
            ]}
            pagination={{ 
              pageSize: 10,
              showSizeChanger: false,
              showQuickJumper: false,
              simple: true 
            }}
            scroll={{ y: 'calc(100vh - 180px)' }}
            size="middle"
          />
        </Card>
      </div>

      {/* 创建/编辑智能体模态框 */}
      <Modal
        title={
          <div>
            <div className="font-bold text-lg">
              {editingAgent ? `编辑智能体: ${editingAgent.name}` : "创建新智能体"}
            </div>
            <div className="text-gray-500 text-sm mt-1">
              {editingAgent ? "修改智能体的配置信息" : "配置新的AI智能体，支持DeepSeek和Dify两种类型"}
            </div>
          </div>
        }
        open={showCreateAgentModal}
        onCancel={handleModalCancel}
        onOk={handleModalOk}
        confirmLoading={loading}
        width={700}
      >
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <div className="flex items-center">
            <span className="text-blue-600 text-sm">
              {newAgentForm.api_type === 'deepseek' 
                ? 'DeepSeek类：'
                : 'Dify类：'}
            </span>
          </div>
        </div>
        
        <Form layout="vertical">
          <div className="grid grid-cols-2 gap-4">
            {/* 第一列 */}
            <div className="space-y-4">
              <Form.Item 
                label="智能体名称" 
                required
              >
                <Input
                  value={newAgentForm.name}
                  onChange={(e) => setNewAgentForm({ ...newAgentForm, name: e.target.value })}
                  placeholder="请输入智能体名称"
                  maxLength={50}
                  showCount
                />
              </Form.Item>
              
              <Form.Item 
                label="智能体类型" 
                required
              >
                <Radio.Group
                  value={newAgentForm.api_type}
                  onChange={(e) => setNewAgentForm({ ...newAgentForm, api_type: e.target.value })}
                  className="w-full"
                >
                  <div className="flex flex-col space-y-2">
                    <Radio value="deepseek" className="!mb-2">
                      <div>
                        <div className="font-medium">DeepSeek类</div>
                      </div>
                    </Radio>
                    <Radio value="dify">
                      <div>
                        <div className="font-medium">Dify类</div>
                      </div>
                    </Radio>
                  </div>
                </Radio.Group>
              </Form.Item>

              <Form.Item 
                label="API密钥" 
                required
              >
                <Input.Password
                  value={newAgentForm.api_key}
                  onChange={(e) => setNewAgentForm({ ...newAgentForm, api_key: e.target.value })}
                  placeholder={
                    newAgentForm.api_type === 'deepseek'
                      ? "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                      : "app-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                  }
                />
              </Form.Item>
            </div>

            {/* 第二列 */}
            <div className="space-y-4">
              <Form.Item 
                label="基础URL" 
                required
              >
                <Input
                  value={newAgentForm.base_url}
                  onChange={(e) => setNewAgentForm({ ...newAgentForm, base_url: e.target.value })}
                  placeholder={
                    newAgentForm.api_type === 'deepseek' 
                      ? "例如: https://api.deepseek.com" 
                      : "例如: http://localhost:6606/v1"
                  }
                />
              </Form.Item>

              {newAgentForm.api_type === 'deepseek' ? (
                <Form.Item 
                  label="模型名称" 
                  required
                >
                  <Input
                    value={newAgentForm.model}
                    onChange={(e) => setNewAgentForm({ ...newAgentForm, model: e.target.value })}
                    placeholder="例如: deepseek-chat"
                  />
                </Form.Item>
              ) : (
                <Form.Item 
                  label="应用ID" 
                  required
                >
                  <Input
                    value={newAgentForm.app_id}
                    onChange={(e) => setNewAgentForm({ ...newAgentForm, app_id: e.target.value })}
                    placeholder="请输入Dify应用ID"
                  />
                </Form.Item>
              )}

              <Form.Item 
                label="状态控制"
              >
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">智能体状态</div>
                    <div className="text-gray-500 text-xs">
                      {newAgentForm.is_active ? "已启用，学生可以使用" : "已禁用，学生不可见"}
                    </div>
                  </div>
                  <Switch
                    checked={newAgentForm.is_active}
                    onChange={(checked) => setNewAgentForm({ ...newAgentForm, is_active: checked })}
                    checkedChildren="启用"
                    unCheckedChildren="禁用"
                  />
                </div>
              </Form.Item>
            </div>
          </div>

          {/* 底部提示 */}
          <div className="mt-6 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-start">
              <div className="text-gray-700 text-sm">
                <div className="font-medium mb-1">配置提示：</div>
                <ul className="list-disc pl-4 space-y-1">
                  <li>确保API密钥和基础URL正确，创建后可点击"测试连接"验证</li>
                  <li>DeepSeek类需要填写模型名称，Dify类需要填写应用ID</li>
                  <li>智能体创建后可以随时编辑或禁用</li>
                </ul>
              </div>
            </div>
          </div>

          {/* 测试连接按钮 */}
          <div className="mt-6 flex justify-end">
            <Button
              type="default"
              icon={<ThunderboltOutlined />}
              onClick={handleTestConnection}
              loading={testingConnection}
              disabled={
                !newAgentForm.api_key || 
                !newAgentForm.base_url ||
                (newAgentForm.api_type === 'deepseek' && !newAgentForm.model) ||
                (newAgentForm.api_type === 'dify' && !newAgentForm.app_id)
              }
            >
              测试连接
            </Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default AgentManagement;
