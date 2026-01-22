import { useState, useEffect, useCallback } from 'react';
import { message } from 'antd';
import { Filters, DataSet, ImportSettings, ExportSettings } from '../types/data.types';
import { fetchData, importData as apiImportData, exportData as apiExportData, deleteData as apiDeleteData } from '../utils/api';

export const useData = (filters: Filters) => {
  const [data, setData] = useState<DataSet>({
    courseCatalog: [],
    studentInfo: [],
    courseSelection: [],
    mergedData: [],
  });
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await fetchData(filters);
      setData(result);
    } catch (error) {
      message.error('加载数据失败');
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const refreshData = () => {
    return loadData();
  };

  const importData = async (files: File[], settings: ImportSettings) => {
    try {
      setImporting(true);
      await apiImportData(files, settings);
      // 导入成功后重新加载数据
      await loadData();
      return Promise.resolve();
    } catch (error) {
      message.error('导入数据失败');
      console.error('Failed to import data:', error);
      return Promise.reject(error);
    } finally {
      setImporting(false);
    }
  };

  const exportData = async (settings: ExportSettings) => {
    try {
      setExporting(true);
      await apiExportData(settings);
      return Promise.resolve();
    } catch (error) {
      message.error('导出数据失败');
      console.error('Failed to export data:', error);
      return Promise.reject(error);
    } finally {
      setExporting(false);
    }
  };

  const deleteData = async (type: string, deleteFilters: Filters) => {
    try {
      setDeleting(true);
      await apiDeleteData(type, deleteFilters);
      // 删除成功后重新加载数据
      await loadData();
      return Promise.resolve();
    } catch (error) {
      message.error('删除数据失败');
      console.error('Failed to delete data:', error);
      return Promise.reject(error);
    } finally {
      setDeleting(false);
    }
  };

  return {
    data,
    loading: loading || importing || exporting || deleting,
    refreshData,
    importData,
    exportData,
    deleteData,
  };
};
