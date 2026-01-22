"use client";

import React, { useState } from 'react';
import { Modal, Form, Select, Radio, Button, message, Row, Col, Input } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { Filters, ExportSettings } from '../../types/data.types';

const { Option } = Select;

interface ExportModalProps {
  visible: boolean;
  onCancel: () => void;
  onOk: (settings: ExportSettings) => void;
  filters: Filters;
  availableYears: number[];
  availableGrades: string[];
}

const ExportModal: React.FC<ExportModalProps> = ({ 
  visible, 
  onCancel, 
  onOk, 
  filters,
  availableYears,
  availableGrades 
}) => {
  const [form] = Form.useForm();
  const [exporting, setExporting] = useState(false);
  const [exportType, setExportType] = useState<'course-selection' | 'distribution' | 'teacher-distribution'>('course-selection');

  React.useEffect(() => {
    if (visible) {
      // 设置默认值：基于数据库实际数据
      const defaultYear = availableYears.length > 0 ? availableYears[0] : new Date().getFullYear();
      const defaultGrade = availableGrades.length > 0 ? availableGrades[0] : '高一';
      const currentYear = new Date().getFullYear();
      
      form.setFieldsValue({
        year: filters.year || defaultYear,   // 用于数据库筛选的年份
        grade: filters.grade || defaultGrade, // 用于数据库筛选的年级
        yearStart: currentYear - 1,          // 用于标题的起始年份
        yearEnd: currentYear,                // 用于标题的结束年份
        type: 'course-selection',
      });
    }
  }, [visible, filters, form, availableYears, availableGrades]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setExporting(true);

      // 调用父组件的导出函数，固定格式为xlsx
      await onOk({
        year: values.year,           // 用于数据库筛选的年份
        grade: values.grade,         // 用于数据库筛选的年级
        yearStart: values.yearStart, // 用于标题的起始年份
        yearEnd: values.yearEnd,     // 用于标题的结束年份
        type: values.type,
        format: 'xlsx', // 固定为xlsx格式
      });

      message.success('导出成功！文件正在下载中...');
      onCancel();
    } catch (error) {
      message.error('导出失败');
      console.error('Export failed:', error);
    } finally {
      setExporting(false);
    }
  };

  const exportTypes = [
    {
      value: 'course-selection',
      label: '学生选课表',
    },
    {
      value: 'distribution',
      label: '各班分发表',
    },
    {
      value: 'teacher-distribution',
      label: '教师分发表',
    },
  ];

  return (
    <Modal
      title="导出数据"
      open={visible}
      onCancel={onCancel}
      onOk={handleSubmit}
      confirmLoading={exporting}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        style={{ padding: '0 8px' }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="年份"
              name="year"
              rules={[{ required: true, message: '请选择年份（用于数据库筛选）' }]}
            >
              <Select placeholder="选择年份（筛选用）">
                {/* 基于数据库实际数据生成年份选项 */}
                {availableYears.map(year => (
                  <Option key={year} value={year}>{year}</Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              label="年级"
              name="grade"
              rules={[{ required: true, message: '请选择年级（用于数据库筛选）' }]}
            >
              <Select placeholder="选择年级（筛选用）">
                {/* 基于数据库实际数据生成年级选项 */}
                {availableGrades.map(grade => (
                  <Option key={grade} value={grade}>{grade}</Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="起始年份"
              name="yearStart"
              rules={[{ required: true, message: '请输入起始年份（用于标题）' }]}
            >
              <Input type="number" placeholder="例如：2024" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              label="结束年份"
              name="yearEnd"
              rules={[{ required: true, message: '请输入结束年份（用于标题）' }]}
            >
              <Input type="number" placeholder="例如：2025" />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          label="导出类型"
          name="type"
          rules={[{ required: true, message: '请选择导出类型' }]}
        >
          <Radio.Group
            onChange={(e) => setExportType(e.target.value)}
            optionType="button"
            buttonStyle="solid"
            style={{ width: '100%', display: 'flex' }}
          >
            <Radio.Button value="course-selection" style={{ flex: 1, textAlign: 'center' }}>
              学生选课表
            </Radio.Button>
            <Radio.Button value="distribution" style={{ flex: 1, textAlign: 'center' }}>
              各班分发表
            </Radio.Button>
            <Radio.Button value="teacher-distribution" style={{ flex: 1, textAlign: 'center' }}>
              教师分发表
            </Radio.Button>
          </Radio.Group>
        </Form.Item>

        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            size="large"
            onClick={handleSubmit}
            loading={exporting}
            style={{ minWidth: 200 }}
          >
            {exporting ? '正在导出...' : '开始导出'}
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

export default ExportModal;
