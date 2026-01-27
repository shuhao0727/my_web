import { useState, useEffect } from 'react';
import { message } from 'antd';
import { Filters, SystemConfig } from '../types/data.types';
import { fetchSystemConfig } from '../utils/api';

export const useFilter = () => {
  const [filters, setFilters] = useState<Filters>({});
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  const [availableGrades, setAvailableGrades] = useState<string[]>([]);
  const [availableSemesters, setAvailableSemesters] = useState<string[]>([]);
  const [availableClasses, setAvailableClasses] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFilterOptions();
  }, []);

  const loadFilterOptions = async () => {
    try {
      setLoading(true);
      const config: SystemConfig = await fetchSystemConfig();
      setAvailableYears(config.availableYears || []);
      setAvailableGrades(config.availableGrades || []);
      setAvailableSemesters(config.availableSemesters || []);
      setAvailableClasses(config.availableClasses || []);

      // 如果有当前配置，则设置默认筛选条件
      if (config.currentYear || config.currentGrade) {
        setFilters({
          year: config.currentYear,
          grade: config.currentGrade,
          semester: config.currentSemester,
        });
      }
    } catch (error) {
      message.error('加载筛选选项失败');
      console.error('Failed to load filter options:', error);
    } finally {
      setLoading(false);
    }
  };

  return {
    filters,
    setFilters,
    availableYears,
    availableGrades,
    availableSemesters,
    availableClasses,
    loading,
  };
};
