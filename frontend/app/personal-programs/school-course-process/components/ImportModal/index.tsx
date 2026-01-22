"use client";

import React, { useState } from 'react';
import { Modal, Form, Select, Upload, Button, message, Row, Col, Progress } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { Filters, ImportSettings } from '../../types/data.types';

const { Option } = Select;

interface ImportModalProps {
  visible: boolean;
  onCancel: () => void;
  onOk: (files: File[], settings: ImportSettings) => void;
  filters: Filters;
}

const ImportModal: React.FC<ImportModalProps> = ({ visible, onCancel, onOk, filters }) => {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleBeforeUpload = (file: File) => {
    // 限制文件类型为Excel
    const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                   file.type === 'application/vnd.ms-excel';
    if (!isExcel) {
      message.error('只能上传Excel文件!');
      return false;
    }
    // 不自动上传，由手动控制
    return false;
  };

  const handleFileChange = ({ fileList }: any) => {
    const files = fileList.map((file: any) => file.originFileObj).filter(Boolean);
    setFileList(files);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (fileList.length === 0) {
        message.error('请选择要上传的文件');
        return;
      }

      setUploading(true);
      setProgress(0);

      // 模拟上传进度
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 200);

      // 调用父组件的导入函数
      await onOk(fileList, {
        year: values.year,
        grade: values.grade,
        type: values.type,
      });

      clearInterval(interval);
      setProgress(100);
      message.success('导入成功！');
      
      // 重置表单
      form.resetFields();
      setFileList([]);
      setProgress(0);
      onCancel();
    } catch (error) {
      message.error('导入失败');
      console.error('Import failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const importTypes = [
    { value: 'catalog', label: '课程目录' },
    { value: 'student-info', label: '学生信息' },
    { value: 'course-selection', label: '选课结果' },
  ];

  return (
    <Modal
      title="导入数据"
      open={visible}
      onCancel={onCancel}
      onOk={handleSubmit}
      confirmLoading={uploading}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          year: filters.year || 2025,
          grade: filters.grade || '高一',
          type: 'catalog',
        }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="年份"
              name="year"
              rules={[{ required: true, message: '请选择年份' }]}
            >
              <Select placeholder="请选择年份">
                <Option value={2024}>2024</Option>
                <Option value={2025}>2025</Option>
                <Option value={2026}>2026</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              label="年级"
              name="grade"
              rules={[{ required: true, message: '请选择年级' }]}
            >
              <Select placeholder="请选择年级">
                <Option value="高一">高一</Option>
                <Option value="高二">高二</Option>
                <Option value="高三">高三</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          label="导入类型"
          name="type"
          rules={[{ required: true, message: '请选择导入类型' }]}
        >
          <Select placeholder="请选择导入类型">
            {importTypes.map((type) => (
              <Option key={type.value} value={type.value}>
                {type.label}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="选择文件"
          required
        >
          <Upload
            multiple
            beforeUpload={handleBeforeUpload}
            onChange={handleFileChange}
            fileList={fileList.map((file, index) => ({
              uid: `${index}`,
              name: file.name,
              status: 'done',
            }))}
            accept=".xlsx,.xls"
          >
            <Button icon={<UploadOutlined />}>选择Excel文件</Button>
          </Upload>
          <div style={{ marginTop: 8 }}>
            <small>支持 .xlsx, .xls 格式，可多选</small>
          </div>
        </Form.Item>

        {fileList.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div>已选择 {fileList.length} 个文件：</div>
            {fileList.map((file, index) => (
              <div key={index} style={{ fontSize: 12, color: '#666' }}>
                {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </div>
            ))}
          </div>
        )}

        {uploading && (
          <Form.Item label="导入进度">
            <Progress percent={progress} status="active" />
            <div style={{ textAlign: 'center', marginTop: 8 }}>
              正在处理文件...
            </div>
          </Form.Item>
        )}
      </Form>
    </Modal>
  );
};

export default ImportModal;
