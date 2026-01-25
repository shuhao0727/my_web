"use client";

import React, { useMemo, useState } from 'react';
import { Tabs, Table, Space, Typography, Empty, Button, message } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import EditModal from '../EditModal';
import { CourseCatalog, StudentInfo, CourseSelection, MergedData, Filters } from '../../types/data.types';

const { Text } = Typography;

interface DataTableProps {
  data: {
    courseCatalog: CourseCatalog[];
    studentInfo: StudentInfo[];
    courseSelection: CourseSelection[];
    mergedData: MergedData[];
  };
  loading: boolean;
  filters: Filters;
  onRefresh?: () => void;
}

// 按数字排序函数
const sortByNumber = (a: string, b: string): number => {
  const numA = parseInt(a, 10);
  const numB = parseInt(b, 10);
  if (isNaN(numA) && isNaN(numB)) return a.localeCompare(b);
  if (isNaN(numA)) return 1;
  if (isNaN(numB)) return -1;
  return numA - numB;
};

// 安全字符串比较函数，处理null/undefined值
const safeStringCompare = (a: string | null | undefined, b: string | null | undefined): number => {
  if (a == null && b == null) return 0;
  if (a == null) return 1;  // null值排在后面
  if (b == null) return -1; // null值排在后面
  return a.localeCompare(b);
};

const DataTable: React.FC<DataTableProps> = ({ data, loading, filters, onRefresh }) => {
  // 编辑模态框状态
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState<any>(null);
  const [editingDataType, setEditingDataType] = useState<'courseCatalog' | 'studentInfo' | 'courseSelection'>('courseCatalog');

  // 打开编辑模态框
  const handleEdit = (record: any, dataType: 'courseCatalog' | 'studentInfo' | 'courseSelection') => {
    setEditingRecord(record);
    setEditingDataType(dataType);
    setEditModalVisible(true);
  };

  // 关闭编辑模态框
  const handleEditModalCancel = () => {
    setEditModalVisible(false);
    setEditingRecord(null);
  };

  // 编辑成功回调
  const handleEditSuccess = () => {
    message.success('数据更新成功');
    setEditModalVisible(false);
    setEditingRecord(null);
    // 刷新数据
    if (onRefresh) {
      onRefresh();
    }
  };

  // 对课程目录按课程代码数字升序排序
  const sortedCourseCatalog = useMemo(() => {
    return [...data.courseCatalog].sort((a, b) => sortByNumber(a.课程代码, b.课程代码));
  }, [data.courseCatalog]);

  // 对学生信息按班级、学号升序排序
  const sortedStudentInfo = useMemo(() => {
    return [...data.studentInfo].sort((a, b) => {
      const classCompare = safeStringCompare(a.班级, b.班级);
      if (classCompare !== 0) return classCompare;
      return sortByNumber(a.学号, b.学号);
    });
  }, [data.studentInfo]);

  // 对选课结果按班级、学号、课程代码升序排序
  const sortedCourseSelection = useMemo(() => {
    return [...data.courseSelection].sort((a, b) => {
      const classCompare = safeStringCompare(a.班级, b.班级);
      if (classCompare !== 0) return classCompare;
      const studentIdCompare = sortByNumber(a.学号, b.学号);
      if (studentIdCompare !== 0) return studentIdCompare;
      return sortByNumber(a.课程代码, b.课程代码);
    });
  }, [data.courseSelection]);

  // 对合并数据按班级、学号、课程代码升序排序
  const sortedMergedData = useMemo(() => {
    return [...data.mergedData].sort((a, b) => {
      const classCompare = safeStringCompare(a.班级, b.班级);
      if (classCompare !== 0) return classCompare;
      const studentIdCompare = sortByNumber(a.学号, b.学号);
      if (studentIdCompare !== 0) return studentIdCompare;
      return sortByNumber(a.课程代码, b.课程代码);
    });
  }, [data.mergedData]);

  const courseCatalogColumns = [
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
      title: '课程负责人',
      dataIndex: '课程负责人',
      key: '课程负责人',
    },
    {
      title: '限报人数',
      dataIndex: '各班限报人数',
      key: '各班限报人数',
      render: (value: number) => value || '-',
    },
    {
      title: '上课地点',
      dataIndex: '上课地点',
      key: '上课地点',
      render: (value: string) => value || '-',
    },
    {
      title: '操作',
      key: 'operation',
      width: 80,
      render: (_: any, record: any) => (
        <Button
          type="link"
          size="small"
          icon={<EditOutlined />}
          onClick={() => handleEdit(record, 'courseCatalog')}
        >
          编辑
        </Button>
      ),
    },
  ];

  const studentInfoColumns = [
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
    {
      title: '操作',
      key: 'operation',
      width: 80,
      render: (_: any, record: any) => (
        <Button
          type="link"
          size="small"
          icon={<EditOutlined />}
          onClick={() => handleEdit(record, 'studentInfo')}
        >
          编辑
        </Button>
      ),
    },
  ];

  const courseSelectionColumns = [
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
    {
      title: '课程代码',
      dataIndex: '课程代码',
      key: '课程代码',
    },
    {
      title: '操作',
      key: 'operation',
      width: 80,
      render: (_: any, record: any) => (
        <Button
          type="link"
          size="small"
          icon={<EditOutlined />}
          onClick={() => handleEdit(record, 'courseSelection')}
        >
          编辑
        </Button>
      ),
    },
  ];

  const mergedDataColumns = [
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
      title: '课程负责人',
      dataIndex: '课程负责人',
      key: '课程负责人',
      render: (value: string) => value || '-',
    },
    {
      title: '限报人数',
      dataIndex: '各班限报人数',
      key: '各班限报人数',
      render: (value: number) => value || '-',
    },
    {
      title: '上课地点',
      dataIndex: '上课地点',
      key: '上课地点',
      render: (value: string) => value || '-',
    },
  ];

  const renderTableInfo = (dataSource: any[], title: string) => {
    if (dataSource.length === 0) {
      return <Empty description={`暂无${title}数据`} />;
    }
      return (
        <Space orientation="vertical" style={{ width: '100%' }}>
          <Text type="secondary">
            共 {dataSource.length} 条数据
            {filters.year && `，年份: ${filters.year}`}
            {filters.grade && `，年级: ${filters.grade}`}
            {filters.class && `，班级: ${filters.class}`}
          </Text>
          <div className="dataTableContainer">
            <Table
              dataSource={dataSource}
              columns={
                title === '课程目录'
                  ? courseCatalogColumns
                  : title === '学生信息'
                  ? studentInfoColumns
                  : title === '选课结果'
                  ? courseSelectionColumns
                  : mergedDataColumns
              }
              rowKey="id"
              pagination={false}
              size="small"
              scroll={{ x: 'max-content' }}
            />
          </div>
        </Space>
      );
  };

  const items = [
    {
      key: 'mergedData',
      label: '合并数据',
      children: renderTableInfo(sortedMergedData, '合并数据'),
    },
    {
      key: 'courseCatalog',
      label: '课程目录',
      children: renderTableInfo(sortedCourseCatalog, '课程目录'),
    },
    {
      key: 'studentInfo',
      label: '学生信息',
      children: renderTableInfo(sortedStudentInfo, '学生信息'),
    },
    {
      key: 'courseSelection',
      label: '选课结果',
      children: renderTableInfo(sortedCourseSelection, '选课结果'),
    },
  ];

  return (
    <>
      <Tabs defaultActiveKey="mergedData" items={items} />
      <EditModal
        visible={editModalVisible}
        dataType={editingDataType}
        record={editingRecord}
        onCancel={handleEditModalCancel}
        onSuccess={handleEditSuccess}
      />
    </>
  );
};

export default DataTable;
