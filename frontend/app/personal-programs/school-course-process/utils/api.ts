import { Filters, DataSet, ImportSettings, ExportSettings, SystemConfig } from '../types/data.types';

const API_BASE = '/api/xbk';

// 获取系统配置
export const fetchSystemConfig = async (): Promise<SystemConfig> => {
  try {
    const response = await fetch(`${API_BASE}/config/system`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return {
      currentYear: result.current_year,
      currentGrade: result.current_grade,
      currentSemester: result.current_semester,
      availableYears: result.available_years || [],
      availableGrades: result.available_grades || [],
      availableSemesters: result.available_semesters || ['上半学年', '下半学年'],
      availableClasses: result.available_classes || [],
    };
  } catch (error) {
    console.error('Failed to fetch system config:', error);
    // 返回默认配置作为fallback
    return {
      currentYear: 2025,
      currentGrade: '高一',
      currentSemester: '上半学年',
      availableYears: [2024, 2025, 2026],
      availableGrades: ['高一', '高二', '高三'],
      availableSemesters: ['上半学年', '下半学年'],
      availableClasses: ['1班', '2班', '3班', '4班', '5班', '6班'],
    };
  }
};

// 获取数据
export const fetchData = async (filters: Filters): Promise<DataSet> => {
  try {
    const { year, grade, semester, class: className, searchText } = filters;
    
    // 并行请求所有数据类型
    const dataTypes = ['catalog', 'student-info', 'course-selection', 'merged-data'];
    const requests = dataTypes.map(async (dataType) => {
      const params = new URLSearchParams();
      if (year) params.append('year', year.toString());
      if (grade) params.append('grade', grade);
      if (semester) params.append('semester', semester);
      if (className) params.append('class_name', className);
      if (searchText) params.append('search_text', searchText);
      // 设置较大的page_size以获取所有数据
      params.append('page_size', '1000');
      
      const url = `${API_BASE}/data/${dataType}?${params.toString()}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch ${dataType}: ${response.status}`);
      }
      const result = await response.json();
      return { dataType, data: result.data || [] };
    });

    const results = await Promise.all(requests);
    
    // 将结果转换为DataSet格式
    const dataSet: DataSet = {
      courseCatalog: [],
      studentInfo: [],
      courseSelection: [],
      mergedData: [],
    };

    results.forEach(({ dataType, data }) => {
      switch (dataType) {
        case 'catalog':
          dataSet.courseCatalog = data;
          break;
        case 'student-info':
          dataSet.studentInfo = data;
          break;
        case 'course-selection':
          dataSet.courseSelection = data;
          break;
        case 'merged-data':
          dataSet.mergedData = data;
          break;
      }
    });

    return dataSet;
  } catch (error) {
    console.error('Failed to fetch data:', error);
    // 返回空数据集作为fallback
    return {
      courseCatalog: [],
      studentInfo: [],
      courseSelection: [],
      mergedData: [],
    };
  }
};

// 导入数据
export const importData = async (files: File[], settings: ImportSettings): Promise<void> => {
  try {
    const formData = new FormData();
    formData.append('file', files[0]);
    
    const params = new URLSearchParams({
      year: settings.year.toString(),
      grade: settings.grade,
    });

    const response = await fetch(`${API_BASE}/import/${settings.type}?${params.toString()}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Import failed with status: ${response.status}`);
    }

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Import failed');
    }
  } catch (error) {
    console.error('Failed to import data:', error);
    throw error;
  }
};

// 导出数据
export const exportData = async (settings: ExportSettings): Promise<void> => {
  try {
    const params = new URLSearchParams();
    // 必须参数：用于数据库筛选的年份和年级
    if (settings.year) params.append('year', settings.year.toString());
    if (settings.grade) params.append('grade', settings.grade);
    // 可选参数：用于标题的起始和结束年份
    if (settings.yearStart) params.append('yearStart', settings.yearStart.toString());
    if (settings.yearEnd) params.append('yearEnd', settings.yearEnd.toString());
    // 导出类型和格式
    params.append('format', settings.format === 'xls' ? 'xls' : 'xlsx');

    const response = await fetch(`${API_BASE}/export/${settings.type}?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error(`Export failed with status: ${response.status}`);
    }

    // 创建下载链接
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    // 生成文件名：使用标题年份（如果未提供则使用数据库筛选年份）
    const titleYearStart = settings.yearStart || settings.year;
    const titleYearEnd = settings.yearEnd || settings.year;
    const filename = `${settings.type}_${titleYearStart}-${titleYearEnd}_${settings.grade}.${settings.format}`;
    
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Failed to export data:', error);
    throw error;
  }
};

// 删除数据
export const deleteData = async (type: string, filters: Filters): Promise<void> => {
  try {
    const { year, grade, class: className } = filters;
    const params = new URLSearchParams();
    if (year) params.append('year', year.toString());
    if (grade) params.append('grade', grade);
    if (className) params.append('class_name', className);

    const response = await fetch(`${API_BASE}/data/${type}?${params.toString()}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Delete failed with status: ${response.status}`);
    }

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Delete failed');
    }
  } catch (error) {
    console.error('Failed to delete data:', error);
    throw error;
  }
};

// 获取分析数据
export const fetchAnalysis = async (filters: Filters): Promise<any> => {
  try {
    const { year, grade, class: className } = filters;
    
    // 并行请求分析数据
    const [courseStats, classStats, studentsWithoutCourses] = await Promise.all([
      // 课程统计
      (async () => {
        const params = new URLSearchParams();
        if (year) params.append('year', year.toString());
        if (grade) params.append('grade', grade);
        if (className) params.append('class_name', className);
        
        const response = await fetch(`${API_BASE}/analysis/course-stats?${params.toString()}`);
        if (!response.ok) return null;
        const result = await response.json();
        return result.success ? result : null;
      })(),
      
      // 班级统计
      (async () => {
        const params = new URLSearchParams();
        if (year) params.append('year', year.toString());
        if (grade) params.append('grade', grade);
        
        const response = await fetch(`${API_BASE}/analysis/class-stats?${params.toString()}`);
        if (!response.ok) return null;
        const result = await response.json();
        return result.success ? result : null;
      })(),
      
      // 未选课学生
      (async () => {
        const params = new URLSearchParams();
        if (year) params.append('year', year.toString());
        if (grade) params.append('grade', grade);
        
        const response = await fetch(`${API_BASE}/analysis/students-without-courses?${params.toString()}`);
        if (!response.ok) return null;
        const result = await response.json();
        return result.success ? result : null;
      })(),
    ]);

    return {
      courseStats: courseStats?.course_stats || [],
      courseSummary: courseStats?.summary || {},
      classStats: classStats?.class_stats || [],
      studentsWithoutCourses: studentsWithoutCourses?.students || [],
    };
  } catch (error) {
    console.error('Failed to fetch analysis data:', error);
    return {
      courseStats: [],
      courseSummary: {},
      classStats: [],
      studentsWithoutCourses: [],
    };
  }
};

// 健康检查
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) return false;
    const result = await response.json();
    return result.status === 'healthy';
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};
