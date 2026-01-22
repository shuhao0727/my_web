"use client";

import React, { useState, useEffect } from 'react';
import { Modal, Card, Row, Col, Statistic, Table, Progress, Space, Typography, Button } from 'antd';
import { BarChartOutlined, DownloadOutlined } from '@ant-design/icons';
import { Filters, DataSet } from '../../types/data.types';
import { fetchAnalysis } from '../../utils/api';

const { Title, Text } = Typography;

interface AnalysisPanelProps {
  visible: boolean;
  onCancel: () => void;
  data: DataSet;
  filters: Filters;
}

const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ visible, onCancel, data, filters }) => {
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (visible) {
      loadAnalysisData();
    }
  }, [visible, filters]);

  const loadAnalysisData = async () => {
    try {
      setLoading(true);
      const result = await fetchAnalysis(filters);
      setAnalysisData(result);
    } catch (error) {
      console.error('Failed to load analysis data:', error);
    } finally {
      setLoading(false);
    }
  };

  const courseStatsColumns = [
    {
      title: '课程代码',
      dataIndex: '课程代码',
      key: '课程代码',
    },
    {
      title: '课程名称',
      dataIndex: '课程名称',
      key: '课程名称',
    },
    {
      title: '限报人数',
      dataIndex: '限报人数',
      key: '限报人数',
    },
    {
      title: '已选人数',
      dataIndex: '已选人数',
      key: '已选人数',
    },
    {
      title: '剩余名额',
      dataIndex: '剩余名额',
      key: '剩余名额',
    },
    {
      title: '选课率',
      dataIndex: '选课率',
      key: '选课率',
      render: (value: number) => <Progress percent={value} size="small" />,
    },
  ];

  const studentsWithoutCoursesColumns = [
    {
      title: '班级',
      dataIndex: '班级',
      key: '班级',
    },
    {
      title: '学号',
      dataIndex: '学号',
      key: '学号',
    },
    {
      title: '姓名',
      dataIndex: '姓名',
      key: '姓名',
    },
  ];

  const generateCourseStats = () => {
    if (!data.mergedData.length) return [];

    const courseMap = new Map();
    data.mergedData.forEach((item) => {
      if (!courseMap.has(item.课程代码)) {
        courseMap.set(item.课程代码, {
          课程代码: item.课程代码,
          课程名称: item.课程名称,
          限报人数: item.各班限报人数 || 0,
          已选人数: 0,
        });
      }
      const course = courseMap.get(item.课程代码);
      course.已选人数 += 1;
    });

    return Array.from(courseMap.values()).map((course: any) => ({
      ...course,
      剩余名额: course.限报人数 - course.已选人数,
      选课率: course.限报人数 ? Math.round((course.已选人数 / course.限报人数) * 100) : 0,
    }));
  };

  const courseStats = generateCourseStats();
  const totalCourses = courseStats.length;
  const totalSelected = data.mergedData.length;
  const averageCapacity = courseStats.reduce((sum, course) => sum + course.限报人数, 0) / totalCourses || 0;
  const fullyBooked = courseStats.filter((course) => course.剩余名额 <= 0).length;
  const availableCourses = courseStats.filter((course) => course.剩余名额 > 0).length;

  return (
    <Modal
      title="数据分析"
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={1200}
      style={{ top: 20 }}
    >
      <div style={{ marginBottom: 24 }}>
        <Space>
          <Title level={4}>数据分析面板</Title>
          <Text type="secondary">
            {filters.year && `年份: ${filters.year} `}
            {filters.grade && `年级: ${filters.grade} `}
            {filters.class && `班级: ${filters.class}`}
          </Text>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总课程数"
              value={totalCourses}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总选课人数"
              value={totalSelected}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均限报人数"
              value={averageCapacity.toFixed(1)}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已报满课程"
              value={fullyBooked}
              suffix={`/ ${totalCourses}`}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={16}>
          <Card title="课程选课统计" loading={loading}>
            <div className="dataTableContainer" style={{ height: '300px' }}>
              <Table
                dataSource={courseStats}
                columns={courseStatsColumns}
                rowKey="课程代码"
                pagination={false}
                size="small"
              />
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="选课率分布" loading={loading}>
            <div style={{ padding: '0 16px' }}>
              {courseStats.slice(0, 5).map((course) => (
                <div key={course.课程代码} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text ellipsis style={{ maxWidth: '60%' }}>{course.课程名称}</Text>
                    <Text type="secondary">{course.选课率}%</Text>
                  </div>
                  <Progress percent={course.选课率} size="small" />
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card
            title="未选课学生"
            loading={loading}
            extra={
              <Button type="primary" icon={<DownloadOutlined />} size="small">
                导出名单
              </Button>
            }
          >
            {analysisData?.studentsWithoutCourses?.length > 0 ? (
              <div className="dataTableContainer" style={{ height: '300px' }}>
                <Table
                  dataSource={analysisData.studentsWithoutCourses}
                  columns={studentsWithoutCoursesColumns}
                  rowKey="学号"
                  pagination={false}
                  size="small"
                />
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 24 }}>
                <Text type="secondary">暂无未选课学生</Text>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      <div style={{ marginTop: 24, textAlign: 'center' }}>
        <Button type="primary" onClick={onCancel}>
          关闭
        </Button>
      </div>
    </Modal>
  );
};

export default AnalysisPanel;
