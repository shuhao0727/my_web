import React, { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';
import {
  Card,
  Typography,
  Table,
  Tag,
  Spin,
  message,
  Form,
  Select,
  DatePicker,
  Button,
  Input,
  Space,
  Modal,
  Row,
  Col,
  Dropdown,
  Menu,
  Popconfirm,
  Descriptions,
  Divider,
  Progress,
} from 'antd';
import {
  SearchOutlined,
  EyeOutlined,
  DownloadOutlined,
  DeleteOutlined,
  MoreOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import type { DataManagementProps, Conversation, Student, Agent, ConversationDetail } from './types';
import type { ColumnsType } from 'antd/es/table';
import type { RangePickerProps } from 'antd/es/date-picker';
import aiApi from '@/lib/aiApi';
import dayjs from 'dayjs';
import {
  handleBatchExport,
  loadConversations as loadConversationsHelper,
  handleViewDetail as handleViewDetailHelper,
  handleExport as handleExportHelper,
  handleDelete as handleDeleteHelper,
  handleSelectAll as handleSelectAllHelper,
} from './dataManagementHelpers';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const DataManagement: React.FC<DataManagementProps> = ({ user }) => {
  const [isClient, setIsClient] = useState(false);
  const [loading, setLoading] = useState(true);
  const [students, setStudents] = useState<Student[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  
  // 筛选条件
  const [selectedStudent, setSelectedStudent] = useState<number | undefined>();
  const [selectedClass, setSelectedClass] = useState<string | undefined>();
  const [selectedAgent, setSelectedAgent] = useState<number | undefined>();
  const [dateRange, setDateRange] = useState<[string, string] | undefined>();
  const [searchText, setSearchText] = useState<string>('');
  
  // 详情模态框
  const [detailVisible, setDetailVisible] = useState(false);
  const [currentConversation, setCurrentConversation] = useState<ConversationDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  
  // 导出状态
  const [exporting, setExporting] = useState(false);
  
  // 批量选择
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [batchExporting, setBatchExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportTotal, setExportTotal] = useState(0);
  const [progressModalVisible, setProgressModalVisible] = useState(false);
  
  // 标记为客户端
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  // 处理批量选择
  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    setSelectedRowKeys(newSelectedRowKeys);
  };
  
  // 选择/取消选择所有
  const handleSelectAll = () => {
    if (selectedRowKeys.length === conversations.length) {
      setSelectedRowKeys([]);
    } else {
      setSelectedRowKeys(conversations.map(conv => `${conv.user_id}-${conv.id}`));
    }
  };
  
  // 批量导出为Excel（包含详细对话内容）
  const handleBatchExportWrapper = async () => {
    await handleBatchExport(
      selectedRowKeys,
      conversations,
      setBatchExporting,
      setExportProgress,
      setExportTotal,
      setProgressModalVisible,
      setSelectedRowKeys
    );
  };
    
  // 进度模态框
  const renderProgressModal = () => {
    const percent = exportTotal > 0 ? Math.round((exportProgress / exportTotal) * 100) : 0;
    const currentTitle = conversations.find(conv => 
      `${conv.user_id}-${conv.id}` === selectedRowKeys[exportProgress - 1]
    )?.title || '';
    
    return (
      <Modal
        title="导出进度"
        open={progressModalVisible}
        width={600}
        footer={null}
        closable={false}
      >
        <Spin spinning={batchExporting}>
          <div className="text-center">
            <Progress 
              type="circle" 
              percent={percent} 
              status={batchExporting ? "active" : "success"}
              format={(percent) => `${percent}%`}
              size={120}
            />
            
            <div className="mt-6">
              <Title level={5}>正在导出对话记录</Title>
              <Text type="secondary">
                正在处理: {exportProgress} / {exportTotal} 个对话
              </Text>
              
              {currentTitle && (
                <div className="mt-2">
                  <Text type="secondary">
                    当前对话: {currentTitle}
                  </Text>
                </div>
              )}
              
              <div className="mt-4">
                <Progress 
                  percent={percent} 
                  status="active" 
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': '#87d068',
                  }}
                />
              </div>
              
              <div className="mt-4">
                <Text type="secondary">
                  正在获取对话详细内容并生成Excel文件，请稍候...
                </Text>
              </div>
            </div>
          </div>
        </Spin>
      </Modal>
    );
  };
    
  // 加载学生列表和智能体列表
  useEffect(() => {
    if (!isClient) return;
    
    const loadInitialData = async () => {
      try {
        // 加载学生列表
        const studentsRes = await aiApi.data.getStudentStats(undefined, undefined, 1, 1000);
        if (studentsRes.success) {
          setStudents(studentsRes.students);
        }
        
        // 加载智能体列表（从agents API获取）
        const agentsRes = await aiApi.agent.getAgents(true);
        if (agentsRes.success) {
          setAgents(agentsRes.agents);
        }
        
        // 加载对话列表
        await loadConversationsWrapper(1, pageSize);
      } catch (error) {
        console.error('加载初始数据失败:', error);
        message.error('加载初始数据失败');
      } finally {
        setLoading(false);
      }
    };
    
    loadInitialData();
  }, [isClient]);
  
  // 加载对话列表的包装函数
  const loadConversationsWrapper = async (currentPage: number, currentPageSize: number) => {
    await loadConversationsHelper(
      currentPage,
      currentPageSize,
      students,
      agents,
      selectedStudent,
      selectedClass,
      selectedAgent,
      dateRange,
      searchText,
      setLoading,
      setConversations,
      setTotal,
      setPage,
      setPageSize
    );
  };

  // 格式化时间显示，确保显示正确的本地时间（亚洲/上海时区）
  // 格式化UTC时间显示，转换为上海时区
  const formatUTCTime = (dateInput: Date | string): string => {
    if (!dateInput) return '-';
    
    let date: Date;
    
    if (typeof dateInput === 'string') {
      // 从API返回的字符串，需要解析为UTC时间
      let isoString = dateInput.trim();
      
      // 如果已经是ISO格式（包含T），确保有Z表示UTC
      if (isoString.includes('T')) {
        if (!isoString.endsWith('Z')) {
          isoString += 'Z';
        }
      } else {
        // 假设是"YYYY-MM-DD HH:MM:SS"格式，转换为ISO格式并添加Z表示UTC
        isoString = isoString.replace(' ', 'T') + 'Z';
      }
      
      date = new Date(isoString);
      
      // 如果解析失败，尝试直接解析
      if (isNaN(date.getTime())) {
        console.warn('时间解析失败，使用直接解析:', dateInput);
        date = new Date(dateInput);
      }
    } else {
      // 用户消息的Date对象，直接使用（本地时间）
      date = dateInput;
    }
    
    // 如果仍然无效，返回-
    if (isNaN(date.getTime())) {
      return '-';
    }
    
    // 使用亚洲/上海时区显示时间，确保正确转换UTC到本地时间
    const formattedTime = date.toLocaleString('zh-CN', { 
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
      timeZone: 'Asia/Shanghai'
    });
    
    return formattedTime;
  };

  // 格式化本地时间显示，不进行时区转换
  const formatLocalTime = (dateInput: Date | string): string => {
    if (!dateInput) return '-';
    
    let date: Date;
    
    if (typeof dateInput === 'string') {
      // 直接解析字符串，不添加Z标记
      date = new Date(dateInput);
      
      // 如果解析失败，尝试ISO格式
      if (isNaN(date.getTime())) {
        // 尝试清理字符串
        let isoString = dateInput.trim();
        if (isoString.includes('T')) {
          // 已经是ISO格式，直接使用
          date = new Date(isoString);
        } else {
          // 尝试添加T分隔符
          isoString = isoString.replace(' ', 'T');
          date = new Date(isoString);
        }
      }
    } else {
      date = dateInput;
    }
    
    // 如果仍然无效，返回-
    if (isNaN(date.getTime())) {
      return '-';
    }
    
    // 直接使用本地时区显示，不进行时区转换
    const formattedTime = date.toLocaleString('zh-CN', { 
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
      // 不指定timeZone，使用本地时区
    });
    
    return formattedTime;
  };
  
  // 处理筛选
  const handleFilter = () => {
    loadConversationsWrapper(1, pageSize);
  };
  
  // 重置筛选
  const handleReset = () => {
    setSelectedStudent(undefined);
    setSelectedClass(undefined);
    setSelectedAgent(undefined);
    setDateRange(undefined);
    setSearchText('');
    loadConversationsWrapper(1, pageSize);
  };
  
  // 查看对话详情
  const handleViewDetail = async (conversationId: number) => {
    await handleViewDetailHelper(
      conversationId,
      setDetailLoading,
      setCurrentConversation,
      setDetailVisible
    );
  };
  
  // 导出对话
  const handleExport = async (conversationId: number) => {
    await handleExportHelper(
      conversationId,
      currentConversation,
      exporting,
      setExporting
    );
  };
  
  // 删除对话
  const handleDelete = async (conversationId: number) => {
    await handleDeleteHelper(
      conversationId,
      page,
      pageSize,
      () => loadConversationsWrapper(page, pageSize)
    );
  };
  
  // 表格列定义
  const columns: ColumnsType<Conversation> = [
    {
      title: '学生',
      dataIndex: 'student_name',
      key: 'student_name',
      width: 120,
      render: (text: string, record) => (
        <div>
          <div className="font-medium">{text}</div>
          {record.class_name && (
            <div className="text-xs text-gray-500">{record.class_name}</div>
          )}
        </div>
      ),
    },
    {
      title: '对话标题',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record) => (
        <div>
          <div className="font-medium">{text}</div>
          <div className="text-xs text-gray-500">智能体: {record.agent_name}</div>
        </div>
      ),
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 180,
      render: (text: string) => formatLocalTime(text),
      sorter: (a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime(),
    },
    {
      title: '消息数',
      dataIndex: 'total_messages',
      key: 'total_messages',
      width: 100,
      render: (count: number) => (
        <Tag color={count > 10 ? 'blue' : count > 5 ? 'green' : 'orange'}>
          {count} 条
        </Tag>
      ),
    },
    {
      title: 'Token数',
      dataIndex: 'total_tokens',
      key: 'total_tokens',
      width: 120,
      render: (tokens: number) => (
        <Tag color={tokens > 1000 ? 'red' : tokens > 500 ? 'blue' : 'green'}>
          {tokens?.toLocaleString() || 0}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record.id)}
            title="查看详情"
          />
          <Button
            type="text"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleExport(record.id)}
            title="导出对话"
          />
          <Popconfirm
            title="确定要删除这条对话记录吗？"
            description="删除后无法恢复，请谨慎操作。"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              size="small"
              danger
              icon={<DeleteOutlined />}
              title="删除对话"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];
  
  // 详情模态框内容
  const renderDetailModal = () => {
    if (!currentConversation) return null;
    
    // 从agents数组中查找对应的agent信息，获取model等详细数据
    const agentInfo = agents.find(agent => agent.id === currentConversation.agent?.id);
    const agentModel = agentInfo?.model;
    const agentName = currentConversation.agent?.name || '未知智能体';
    
    return (
      <Modal
        title="对话详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        width={800}
        footer={[
          <Button key="export" icon={<DownloadOutlined />} onClick={() => handleExport(currentConversation.id)}>
            导出对话
          </Button>,
          <Button key="close" onClick={() => setDetailVisible(false)}>
            关闭
          </Button>,
        ]}
      >
        <Spin spinning={detailLoading}>
          <Descriptions title="基本信息" bordered column={2} size="small">
            <Descriptions.Item label="对话标题">{currentConversation.title}</Descriptions.Item>
            <Descriptions.Item label="学生">{currentConversation.user?.username || '未知用户'}</Descriptions.Item>
            <Descriptions.Item label="智能体">
              {agentName}{agentModel ? `（${agentModel}）` : ''}
            </Descriptions.Item>
            <Descriptions.Item label="开始时间">
              {currentConversation.start_time ? formatLocalTime(currentConversation.start_time) : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="消息数">{currentConversation.total_messages || 0}</Descriptions.Item>
            <Descriptions.Item label="Token数">{currentConversation.total_tokens || 0}</Descriptions.Item>
          </Descriptions>
          
          <Divider />
          
          <div className="max-h-96 overflow-y-auto">
            <Title level={5}>对话内容</Title>
            {currentConversation.messages && currentConversation.messages.length > 0 ? (
              currentConversation.messages.map((msg, index) => (
                <div key={msg.id || index} className={`mb-4 p-3 rounded ${msg.role === 'user' ? 'bg-blue-50' : 'bg-gray-50'}`}>
                  <div className="flex justify-between mb-2">
                    <Tag color={msg.role === 'user' ? 'blue' : 'green'}>
                      {msg.role === 'user' ? 
                        `提问者：${currentConversation.user?.username || '未知用户'}` : 
                        `AI回答：${agentName}${agentModel ? `（${agentModel}）` : ''}`
                      }
                    </Tag>
                    <Text type="secondary" className="text-xs">
                      {msg.created_at ? formatUTCTime(msg.created_at) : '未知时间'}
                      {msg.tokens && ` • ${msg.tokens} tokens`}
                    </Text>
                  </div>
                  <div className="whitespace-pre-wrap">{msg.content || '无内容'}</div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                暂无消息内容
              </div>
            )}
          </div>
        </Spin>
      </Modal>
    );
  };
  
  // 服务器端渲染时返回空的div，避免hydration不匹配
  if (!isClient) {
    return <div className="h-full" suppressHydrationWarning />;
  }
  
  if (loading && conversations.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <Spin size="large" />
      </div>
    );
  }
  
  return (
    <div className="h-full flex flex-col p-4">
      <Card className="mb-6">
        <Form layout="vertical">
          <Row gutter={16}>
            <Col xs={24} sm={12} md={4}>
              <Form.Item label="选择学生">
                <Select
                  placeholder="全部学生"
                  allowClear
                  value={selectedStudent}
                  onChange={setSelectedStudent}
                  loading={students.length === 0}
                >
                  {students.map(student => (
                    <Option key={student.id} value={student.id}>
                      {student.username} {student.student_id && `(${student.student_id})`}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col xs={24} sm={12} md={4}>
              <Form.Item label="选择班级">
                <Select
                  placeholder="全部班级"
                  allowClear
                  value={selectedClass}
                  onChange={setSelectedClass}
                  loading={students.length === 0}
                >
                  {Array.from(new Set(students
                    .filter(s => s.class_name)
                    .map(s => s.class_name as string)
                  )).map((className, index) => (
                    <Option key={index} value={className}>
                      {className}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col xs={24} sm={12} md={4}>
              <Form.Item label="选择智能体">
                <Select
                  placeholder="全部智能体"
                  allowClear
                  value={selectedAgent}
                  onChange={setSelectedAgent}
                  loading={agents.length === 0}
                >
                  {agents.map(agent => (
                    <Option key={agent.id} value={agent.id}>
                      {agent.name} ({agent.api_type})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col xs={24} sm={12} md={6}>
              <Form.Item label="时间范围">
                <RangePicker
                  style={{ width: '100%' }}
                  onChange={(dates) => {
                    if (dates && dates[0] && dates[1]) {
                      setDateRange([
                        dates[0].format('YYYY-MM-DD'),
                        dates[1].format('YYYY-MM-DD'),
                      ]);
                    } else {
                      setDateRange(undefined);
                    }
                  }}
                  value={dateRange ? [dayjs(dateRange[0]), dayjs(dateRange[1])] as [dayjs.Dayjs, dayjs.Dayjs] : undefined}
                />
              </Form.Item>
            </Col>
            
            <Col xs={24} sm={12} md={6}>
              <Form.Item label="搜索">
                <Input
                  placeholder="搜索标题、学生、智能体..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  allowClear
                  onPressEnter={handleFilter}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row>
            <Col span={24} style={{ textAlign: 'right' }}>
              <Space>
                <Button onClick={handleReset}>重置</Button>
                <Button type="primary" onClick={handleFilter} icon={<SearchOutlined />}>
                  筛选
                </Button>
              </Space>
            </Col>
          </Row>
        </Form>
      </Card>
      
      {/* 批量操作工具栏 */}
      {selectedRowKeys.length > 0 && (
        <Card className="mb-4">
          <Space>
            <Text strong>已选择 {selectedRowKeys.length} 条记录</Text>
            <Button onClick={handleSelectAll}>
              {selectedRowKeys.length === conversations.length ? '取消全选' : '全选'}
            </Button>
            <Button 
              type="primary" 
              icon={<DownloadOutlined />} 
              onClick={handleBatchExportWrapper}
              loading={batchExporting}
            >
              批量导出为Excel
            </Button>
            <Button onClick={() => setSelectedRowKeys([])}>清空选择</Button>
          </Space>
        </Card>
      )}
      
      <Card className="flex-grow">
        <Table
          columns={columns}
          dataSource={conversations}
          rowKey={(record) => `${record.user_id}-${record.id}`}
          loading={loading}
          rowSelection={{
            selectedRowKeys,
            onChange: onSelectChange,
            selections: [
              Table.SELECTION_ALL,
              Table.SELECTION_INVERT,
              Table.SELECTION_NONE,
            ],
          }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条对话记录`,
            onChange: (page, pageSize) => loadConversationsWrapper(page, pageSize),
          }}
          scroll={{ x: true }}
        />
      </Card>
      
      {renderDetailModal()}
      {renderProgressModal()}
    </div>
  );
};

export default DataManagement;
