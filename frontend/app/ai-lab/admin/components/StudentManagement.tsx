import React, { useState } from 'react';
import {
  UserOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ImportOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import {
  Card,
  Table,
  Tag,
  Space,
  Button,
  Typography,
  Input,
  Modal,
  Form,
  message,
  Upload,
} from 'antd';
import aiApi from '@/lib/aiApi';
import type { StudentManagementProps } from './types';

const { Title } = Typography;
const { Search } = Input;

// 编辑表单字段类型
interface EditFormValues {
  username: string;
  student_id: string;
  class_name?: string;
}

const StudentManagement: React.FC<StudentManagementProps> = ({
  students,
  loading,
  user,
  onRefresh
}) => {
  // 状态管理
  const [searchText, setSearchText] = useState('');
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [editingStudent, setEditingStudent] = useState<any>(null);
  const [originalStudentData, setOriginalStudentData] = useState<any>(null);
  const [editForm] = Form.useForm();
  const [importLoading, setImportLoading] = useState(false);

  // 根据搜索文本过滤学生
  const filteredStudents = React.useMemo(() => {
    if (!searchText.trim()) return students;
    
    const searchLower = searchText.toLowerCase();
    return students.filter(student => 
      student.username?.toLowerCase().includes(searchLower) ||
      student.student_id?.toLowerCase().includes(searchLower) ||
      student.class_name?.toLowerCase().includes(searchLower)
    );
  }, [students, searchText]);

  // 处理编辑操作
  const handleEdit = (student: any) => {
    setEditingStudent(student);
    // 保存原始数据，用于比较变化
    setOriginalStudentData({
      username: student.username,
      student_id: student.student_id,
      class_name: student.class_name || '',
    });
    editForm.setFieldsValue({
      username: student.username,
      student_id: student.student_id,
      class_name: student.class_name || '',
    });
    setIsEditModalVisible(true);
  };

  // 处理删除操作
  const handleDelete = async (studentId: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除该学生吗？此操作不可恢复。',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const result = await aiApi.userManagement.deleteUser(studentId);
          if (result.success) {
            message.success('学生删除成功');
            // 触发重新加载数据
            if (onRefresh) onRefresh();
          } else {
            message.error(result.message || '删除失败');
          }
        } catch (error: any) {
          console.error('删除请求失败:', error);
          message.error(`删除失败: ${error.message || '网络请求失败'}`);
        }
      },
    });
  };

  // 保存编辑
  const handleSaveEdit = async () => {
    try {
      const values = await editForm.validateFields();
      
      // 直接发送所有字段，不比较变化
      const result = await aiApi.userManagement.updateUser(editingStudent.id, values);
      // 处理两种响应格式：
      // 1. {success: boolean, user: any, message: string}
      // 2. {id: number, username: string, ...} (直接返回用户对象)
      let success = false;
      let msg = '';
      if (result && typeof result === 'object') {
        if ('success' in result) {
          success = result.success;
          msg = result.message || '';
        } else if ('id' in result) {
          // 如果返回的是用户对象，则认为成功
          success = true;
          msg = '学生信息更新成功';
        }
      }
      if (success) {
        message.success(msg);
        setIsEditModalVisible(false);
        // 触发重新加载数据
        if (onRefresh) onRefresh();
      } else {
        message.error(msg || '更新失败');
      }
    } catch (error: any) {
      console.error('更新失败:', error);
      message.error(`更新失败: ${error.message || '请检查表单'}`);
    }
  };

  // 处理Excel导入 - 使用aiApi
  const handleImport = async (file: File) => {
    setImportLoading(true);
    
    try {
      const result = await aiApi.userManagement.importUsers(file);
      if (result.success) {
        message.success(`导入成功 ${result.imported_count} 条记录`);
        // 触发重新加载数据
        if (onRefresh) onRefresh();
        // 清空搜索文本，确保显示所有数据（包括新导入的）
        setSearchText('');
        // 添加短暂延迟确保数据加载
        setTimeout(() => {
          if (onRefresh) onRefresh();
        }, 300);
      } else {
        message.error(`导入失败: ${result.errors?.join(', ') || '未知错误'}`);
      }
    } catch (error: any) {
      console.error('导入请求失败:', error);
      message.error(`导入失败: ${error.message || '网络请求失败'}`);
    } finally {
      setImportLoading(false);
    }
    
    return false; // 阻止默认上传行为
  };

  // 下载模板 - 使用直接下载链接避免fetch错误
  const handleDownloadTemplate = () => {
    try {
      const link = document.createElement('a');
      link.href = 'http://localhost:8000/api/ai/user-management/users/export-template';
      link.target = '_blank';
      // 不指定download属性，让浏览器根据后端响应头处理文件名
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      message.success('模板下载开始');
    } catch (error) {
      console.error('模板下载失败:', error);
      message.error('模板下载失败，请检查网络连接');
    }
  };

  // 关闭编辑模态框
  const handleCancelEdit = () => {
    setIsEditModalVisible(false);
    setOriginalStudentData(null);
    editForm.resetFields();
  };

  return (
    <div className="h-full flex flex-col">
      {/* 标题和功能区域 */}
      <div className="mb-6 flex-shrink-0 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <Title level={3} className="mb-0">学生信息管理</Title>
          <Space>
            {/* 搜索框 */}
              <Search
              placeholder="搜索姓名、学号或班级"
              allowClear
              enterButton={<SearchOutlined />}
              size="middle"
              style={{ width: 300 }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onSearch={(value) => setSearchText(value)}
            />
            
            {/* 导入按钮 */}
            <Upload
              accept=".xlsx,.xls"
              beforeUpload={handleImport}
              showUploadList={false}
            >
              <Button
                icon={<ImportOutlined />}
                loading={importLoading}
              >
                导入Excel
              </Button>
            </Upload>
            
            {/* 模板下载 */}
            <Button
              icon={<DownloadOutlined />}
              onClick={handleDownloadTemplate}
            >
              下载模板
            </Button>
          </Space>
        </div>
        
      </div>
      
      <div className="flex-grow overflow-hidden mb-6">
        <Card className="h-full">
          <Table
            dataSource={filteredStudents}
            loading={loading}
            rowKey="id"
            columns={[
              {
                title: '唯一ID',
                dataIndex: 'id',
                key: 'id',
                width: 80,
              },
              {
                title: '姓名',
                dataIndex: 'username',
                key: 'username',
                render: (text) => (
                  <div className="flex items-center">
                    <UserOutlined className="mr-2 text-gray-400" />
                    <span>{text}</span>
                  </div>
                ),
              },
              {
                title: '学号',
                dataIndex: 'student_id',
                key: 'student_id',
              },
              {
                title: '班级',
                dataIndex: 'class_name',
                key: 'class_name',
                render: (text) => text || <span className="text-gray-400">未分配</span>,
              },
              {
                title: '操作',
                key: 'actions',
                width: 200,
                render: (_, record) => (
                  <Space size="small">
                    <Button 
                      size="small" 
                      icon={<EditOutlined />}
                      onClick={() => handleEdit(record)}
                    >
                      编辑
                    </Button>
                    <Button 
                      size="small" 
                      icon={<DeleteOutlined />}
                      danger
                      onClick={() => handleDelete(record.id)}
                    >
                      删除
                    </Button>
                  </Space>
                ),
              },
            ]}
            pagination={{ 
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `${range[0]}-${range[1]} 条，共 ${total} 条`
            }}
            scroll={{ y: 'calc(100vh - 400px)' }}
          />
        </Card>
      </div>

      {/* 编辑学生信息模态框 */}
      <Modal
        title="编辑学生信息"
        open={isEditModalVisible}
        onOk={handleSaveEdit}
        onCancel={handleCancelEdit}
        okText="保存"
        cancelText="取消"
        width={600}
      >
        <Form
          form={editForm}
          layout="vertical"
          name="editStudentForm"
        >
          <Form.Item
            name="username"
            label="姓名"
            rules={[{ required: true, message: '请输入姓名' }]}
          >
            <Input placeholder="请输入学生姓名" />
          </Form.Item>
          
          
          <Form.Item
            name="student_id"
            label="学号"
            rules={[{ required: true, message: '请输入学号' }]}
          >
            <Input placeholder="请输入学号" />
          </Form.Item>
          
          <Form.Item
            name="class_name"
            label="班级"
          >
            <Input placeholder="请输入班级编号（例如：13）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default StudentManagement;
