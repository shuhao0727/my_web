"use client";

import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Space, Button, message, Modal, Select } from 'antd';
import {
  UploadOutlined,
  DownloadOutlined,
  BarChartOutlined,
  ReloadOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import FilterPanel from './components/FilterPanel';
import DataTable from './components/DataTable';
import ImportModal from './components/ImportModal';
import ExportModal from './components/ExportModal';
import AnalysisPanel from './components/AnalysisPanel';
import { useFilter } from './hooks/useFilter';
import { useData } from './hooks/useData';
import styles from './page.module.css';

const { Title, Text } = Typography;
const { Option } = Select;

export default function SchoolCourseProcessPage() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const {
    filters,
    setFilters,
    availableYears,
    availableGrades,
    availableClasses,
    loading: filterLoading,
  } = useFilter();

  const {
    data,
    loading: dataLoading,
    refreshData,
    importData,
    exportData,
    deleteData,
  } = useData(filters);

  const [importModalVisible, setImportModalVisible] = React.useState(false);
  const [exportModalVisible, setExportModalVisible] = React.useState(false);
  const [analysisVisible, setAnalysisVisible] = React.useState(false);
  const [deleteModalVisible, setDeleteModalVisible] = React.useState(false);
  const [deleteType, setDeleteType] = React.useState('all');
  const [deleteYear, setDeleteYear] = React.useState<number | undefined>(undefined);
  const [deleteGrade, setDeleteGrade] = React.useState<string | undefined>(undefined);

  const handleImport = async (files: File[], settings: any) => {
    try {
      await importData(files, settings);
      message.success('数据导入成功');
      setImportModalVisible(false);
    } catch (error) {
      message.error('数据导入失败');
    }
  };

  const handleExport = async (settings: any) => {
    try {
      await exportData(settings);
      message.success('数据导出成功');
      setExportModalVisible(false);
    } catch (error) {
      message.error('数据导出失败');
    }
  };

  const handleDelete = async (type: string, year?: number, grade?: string) => {
    try {
      // 使用传入的年份和年级，如果未传入则使用当前筛选条件
      const deleteFilters = {
        ...filters,
        year: year !== undefined ? year : filters.year,
        grade: grade !== undefined ? grade : filters.grade,
      };
      await deleteData(type, deleteFilters);
      message.success('数据删除成功');
      setDeleteModalVisible(false);
    } catch (error) {
      message.error('数据删除失败');
    }
  };

  const showDeleteModal = () => {
    setDeleteType('all');
    setDeleteYear(undefined);
    setDeleteGrade(undefined);
    setDeleteModalVisible(true);
  };

  const handleDeleteConfirm = () => {
    handleDelete(deleteType, deleteYear, deleteGrade);
  };

  // 在客户端渲染之前，返回null，避免hydration不匹配
  if (!isClient) {
    return null;
  }

  return (
    <div className={styles.container}>
      <Card className={styles.filterCard}>
        <FilterPanel
          filters={filters}
          setFilters={setFilters}
          availableYears={availableYears}
          availableGrades={availableGrades}
          availableClasses={availableClasses}
          loading={filterLoading}
        />
      </Card>

      <Row gutter={[16, 16]} className={styles.actionsRow}>
        <Col>
          <Button
            type="primary"
            icon={<UploadOutlined />}
            onClick={() => setImportModalVisible(true)}
          >
            导入数据
          </Button>
        </Col>
        <Col>
          <Button
            icon={<DownloadOutlined />}
            onClick={() => setExportModalVisible(true)}
          >
            导出数据
          </Button>
        </Col>
        <Col>
          <Button
            icon={<BarChartOutlined />}
            onClick={() => setAnalysisVisible(true)}
          >
            数据分析
          </Button>
        </Col>
        <Col>
          <Button
            icon={<DeleteOutlined />}
            danger
            onClick={showDeleteModal}
          >
            删除数据
          </Button>
        </Col>
        <Col>
          <Button
            icon={<ReloadOutlined />}
            onClick={refreshData}
            loading={dataLoading}
          >
            刷新数据
          </Button>
        </Col>
      </Row>

      <Card className={styles.dataCard}>
        <DataTable 
          data={data} 
          loading={dataLoading} 
          filters={filters} 
          onRefresh={refreshData} 
        />
      </Card>

      <ImportModal
        visible={importModalVisible}
        onCancel={() => setImportModalVisible(false)}
        onOk={handleImport}
        filters={filters}
      />

      <ExportModal
        visible={exportModalVisible}
        onCancel={() => setExportModalVisible(false)}
        onOk={handleExport}
        filters={filters}
        availableYears={availableYears}
        availableGrades={availableGrades}
      />

      <AnalysisPanel
        visible={analysisVisible}
        onCancel={() => setAnalysisVisible(false)}
        data={data}
        filters={filters}
      />

      <Modal
        title="删除数据"
        open={deleteModalVisible}
        onOk={handleDeleteConfirm}
        onCancel={() => setDeleteModalVisible(false)}
        okText="确认删除"
        cancelText="取消"
        okButtonProps={{ danger: true }}
        width={500}
      >
        <p>请选择要删除的数据类型：</p>
        <Select
          style={{ width: '100%', marginBottom: '16px' }}
          value={deleteType}
          onChange={(value) => setDeleteType(value)}
        >
          <Option value="all">全部数据（根据当前筛选条件）</Option>
          <Option value="student-info">学生信息</Option>
          <Option value="catalog">课程目录</Option>
          <Option value="course-selection">选课结果</Option>
          <Option value="merged-data">合并数据</Option>
        </Select>

        <p>选择删除的年份（可选）：</p>
        <Select
          style={{ width: '100%', marginBottom: '16px' }}
          placeholder="请选择年份"
          allowClear
          value={deleteYear}
          onChange={(value) => setDeleteYear(value)}
        >
          {availableYears.map(year => (
            <Option key={year} value={year}>{year}</Option>
          ))}
        </Select>

        <p>选择删除的年级（可选）：</p>
        <Select
          style={{ width: '100%', marginBottom: '16px' }}
          placeholder="请选择年级"
          allowClear
          value={deleteGrade}
          onChange={(value) => setDeleteGrade(value)}
        >
          {availableGrades.map(grade => (
            <Option key={grade} value={grade}>{grade}</Option>
          ))}
        </Select>

        <p style={{ marginTop: '16px', color: '#ff4d4f' }}>
          警告：此操作不可逆，请谨慎操作！
          <br />
          {deleteYear || deleteGrade ? 
            `将删除${deleteYear ? ` ${deleteYear}年` : ''}${deleteGrade ? ` ${deleteGrade}` : ''}的${deleteType === 'all' ? '全部数据' : deleteType}。` : 
            '将根据当前筛选条件删除数据。'
          }
        </p>
      </Modal>
    </div>
  );
}
