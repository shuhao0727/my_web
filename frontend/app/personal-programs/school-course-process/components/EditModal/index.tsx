"use client";

import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, InputNumber, Button, message } from 'antd';
import { EditOutlined } from '@ant-design/icons';

interface EditModalProps {
  visible: boolean;
  dataType: 'courseCatalog' | 'studentInfo' | 'courseSelection';
  record: any;
  onCancel: () => void;
  onSuccess: () => void;
}

const EditModal: React.FC<EditModalProps> = ({ 
  visible, 
  dataType, 
  record, 
  onCancel, 
  onSuccess 
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (visible && record) {
      form.setFieldsValue(record);
    }
  }, [visible, record, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      // 根据数据类型确定API端点
      let apiDataType = '';
      if (dataType === 'courseCatalog') apiDataType = 'catalog';
      if (dataType === 'studentInfo') apiDataType = 'student-info';
      if (dataType === 'courseSelection') apiDataType = 'course-selection';

      // 调用后端API更新数据
      const response = await fetch(
        `/api/xbk/data/${apiDataType}/${record.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(values),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '更新失败');
      }

      const result = await response.json();
      
      message.success('数据更新成功');
      onSuccess();
      onCancel();
    } catch (error) {
      console.error('更新失败:', error);
      message.error(error instanceof Error ? error.message : '更新失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const getFormFields = () => {
    switch (dataType) {
      case 'courseCatalog':
        return (
          <>
            <Form.Item
              label="课程代码"
              name="课程代码"
              rules={[{ required: true, message: '请输入课程代码' }]}
            >
              <Input placeholder="请输入课程代码" />
            </Form.Item>
            <Form.Item
              label="课程名称"
              name="课程名称"
              rules={[{ required: true, message: '请输入课程名称' }]}
            >
              <Input placeholder="请输入课程名称" />
            </Form.Item>
            <Form.Item
              label="课程负责人"
              name="课程负责人"
              rules={[{ required: true, message: '请输入课程负责人' }]}
            >
              <Input placeholder="请输入课程负责人" />
            </Form.Item>
            <Form.Item
              label="各班限报人数"
              name="各班限报人数"
              rules={[{ required: true, message: '请输入限报人数' }]}
            >
              <InputNumber 
                min={1} 
                max={100} 
                placeholder="请输入限报人数"
                style={{ width: '100%' }}
              />
            </Form.Item>
            <Form.Item
              label="上课地点"
              name="上课地点"
            >
              <Input placeholder="请输入上课地点" />
            </Form.Item>
          </>
        );

      case 'studentInfo':
        return (
          <>
            <Form.Item
              label="班级"
              name="班级"
              rules={[{ required: true, message: '请输入班级' }]}
            >
              <Input placeholder="请输入班级" />
            </Form.Item>
            <Form.Item
              label="学号"
              name="学号"
              rules={[{ required: true, message: '请输入学号' }]}
            >
              <Input placeholder="请输入学号" />
            </Form.Item>
            <Form.Item
              label="姓名"
              name="姓名"
              rules={[{ required: true, message: '请输入姓名' }]}
            >
              <Input placeholder="请输入姓名" />
            </Form.Item>
          </>
        );

      case 'courseSelection':
        return (
          <>
            <Form.Item
              label="班级"
              name="班级"
              rules={[{ required: true, message: '请输入班级' }]}
            >
              <Input placeholder="请输入班级" />
            </Form.Item>
            <Form.Item
              label="学号"
              name="学号"
              rules={[{ required: true, message: '请输入学号' }]}
            >
              <Input placeholder="请输入学号" />
            </Form.Item>
            <Form.Item
              label="姓名"
              name="姓名"
              rules={[{ required: true, message: '请输入姓名' }]}
            >
              <Input placeholder="请输入姓名" />
            </Form.Item>
            <Form.Item
              label="课程代码"
              name="课程代码"
              rules={[{ required: true, message: '请输入课程代码' }]}
            >
              <Input placeholder="请输入课程代码" />
            </Form.Item>
          </>
        );

      default:
        return null;
    }
  };

  const getModalTitle = () => {
    switch (dataType) {
      case 'courseCatalog': return '编辑课程目录';
      case 'studentInfo': return '编辑学生信息';
      case 'courseSelection': return '编辑选课结果';
      default: return '编辑数据';
    }
  };

  return (
    <Modal
      title={getModalTitle()}
      open={visible}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          取消
        </Button>,
        <Button
          key="submit"
          type="primary"
          loading={loading}
          onClick={handleSubmit}
        >
          保存
        </Button>,
      ]}
      width={600}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        preserve={false}
      >
        {getFormFields()}
      </Form>
    </Modal>
  );
};

export default EditModal;
