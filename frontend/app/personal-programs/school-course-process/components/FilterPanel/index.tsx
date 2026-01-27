"use client";

import React from 'react';
import { Card, Row, Col, Select, Form, Button, Space, Spin, Input, InputNumber } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';

const { Option } = Select;

interface FilterPanelProps {
  filters: {
    year?: number;
    grade?: string;
    semester?: string;
    class?: string;
  };
  setFilters: (filters: any) => void;
  availableYears: number[];
  availableGrades: string[];
  availableSemesters: string[];
  availableClasses: string[];
  loading: boolean;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  setFilters,
  availableYears,
  availableGrades,
  availableSemesters,
  availableClasses,
  loading,
}) => {
  const [form] = Form.useForm();

  React.useEffect(() => {
    form.setFieldsValue(filters);
  }, [filters, form]);

  const handleSearch = (values: any) => {
    setFilters(values);
  };

  const handleReset = () => {
    form.resetFields();
    setFilters({});
  };

  return (
    <Card size="small">
      <Spin spinning={loading}>
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <Form
            form={form}
            layout="inline"
            onFinish={handleSearch}
            initialValues={filters}
            style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}
          >
            <Form.Item 
              label="年份"
              name="year"
              style={{ marginBottom: 0 }}
            >
              <InputNumber 
                placeholder="输入年份" 
                style={{ width: '100px' }}
                min={2000}
                max={2100}
              />
            </Form.Item>
            <Form.Item 
              label="学年"
              name="semester"
              style={{ marginBottom: 0 }}
            >
              <Select
                placeholder="请选择学年"
                allowClear
                style={{ width: '120px' }}
              >
                {(availableSemesters || []).map((semester) => (
                  <Option key={semester} value={semester}>
                    {semester}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item 
              label="年级"
              name="grade"
              style={{ marginBottom: 0 }}
            >
              <Select
                placeholder="请选择年级"
                allowClear
                style={{ width: '100px' }}
              >
                {(availableGrades || []).map((grade) => (
                  <Option key={grade} value={grade}>
                    {grade}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item 
              label="班级"
              name="class"
              style={{ marginBottom: 0 }}
            >
              <Select
                placeholder="请选择班级"
                allowClear
                style={{ width: '120px' }}
              >
                {(availableClasses || []).map((cls) => (
                  <Option key={cls} value={cls}>
                    {cls}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item 
              label="搜索"
              name="searchText"
              style={{ marginBottom: 0 }}
            >
              <Input
                placeholder="输入姓名、教师、课程代码等"
                allowClear
                style={{ width: '200px' }}
              />
            </Form.Item>
            <Form.Item style={{ marginBottom: 0 }}>
              <Space>
                <Button
                  type="primary"
                  icon={<SearchOutlined />}
                  htmlType="submit"
                >
                  筛选
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={handleReset}
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </div>
      </Spin>
    </Card>
  );
};

export default FilterPanel;
