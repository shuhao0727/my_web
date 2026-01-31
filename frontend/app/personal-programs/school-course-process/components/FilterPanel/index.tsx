"use client";

import React from 'react';
import { Card, Row, Col, Select, Form, Button, Space, Spin, Input, InputNumber } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';

const { Option } = Select;

interface FilterPanelProps {
  filters: {
    year?: number;
    grade?: string;
    class?: string;
  };
  setFilters: (filters: any) => void;
  availableYears: number[];
  availableGrades: string[];
  availableClasses: string[];
  loading: boolean;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  setFilters,
  availableYears,
  availableGrades,
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
        <Form
          form={form}
          layout="inline"
          onFinish={handleSearch}
          initialValues={filters}
        >
          <Row gutter={[12, 8]} style={{ width: '100%' }}>
            <Col xs={24} sm={12} md={6}>
              <Form.Item label="年份" name="year">
                <InputNumber 
                  placeholder="输入年份" 
                  style={{ width: '100%' }}
                  min={2000}
                  max={2100}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Form.Item label="年级" name="grade">
                <Select
                  placeholder="请选择年级"
                  allowClear
                  style={{ width: '100%' }}
                >
                  {availableGrades.map((grade) => (
                    <Option key={grade} value={grade}>
                      {grade}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Form.Item label="班级" name="class">
                <Select
                  placeholder="请选择班级"
                  allowClear
                  style={{ width: '100%' }}
                >
                  {availableClasses.map((cls) => (
                    <Option key={cls} value={cls}>
                      {cls}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Form.Item label="搜索" name="searchText">
                <Input
                  placeholder="输入姓名、教师、课程代码等"
                  allowClear
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={12}>
              <Form.Item>
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
            </Col>
          </Row>
        </Form>
      </Spin>
    </Card>
  );
};

export default FilterPanel;
