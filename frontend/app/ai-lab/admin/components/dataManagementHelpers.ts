import * as XLSX from 'xlsx';
import { message } from 'antd';
import aiApi from '@/lib/aiApi';
import type { 
  Conversation, 
  Student, 
  Agent, 
  ConversationDetail 
} from './types';

/**
 * 批量导出对话为Excel文件
 * @param selectedRowKeys 选中的行键数组
 * @param conversations 对话列表
 * @param setBatchExporting 设置批量导出状态的函数
 * @param setExportProgress 设置导出进度的函数
 * @param setExportTotal 设置导出总数的函数
 * @param setProgressModalVisible 设置进度模态框可见性的函数
 * @param setSelectedRowKeys 设置选中行键的函数
 */
export const handleBatchExport = async (
  selectedRowKeys: React.Key[],
  conversations: Conversation[],
  setBatchExporting: (loading: boolean) => void,
  setExportProgress: (progress: number) => void,
  setExportTotal: (total: number) => void,
  setProgressModalVisible: (visible: boolean) => void,
  setSelectedRowKeys: (keys: React.Key[]) => void
): Promise<void> => {
  if (selectedRowKeys.length === 0) {
    message.warning('请先选择要导出的对话记录');
    return;
  }
  
  // 限制一次最多导出60个对话，避免请求过多
  if (selectedRowKeys.length > 60) {
    message.warning('一次最多导出60个对话，请减少选择数量');
    return;
  }
  
  setBatchExporting(true);
  
  try {
    message.loading(`正在获取 ${selectedRowKeys.length} 个对话的详细内容...`, 0);
    
    // 获取选中的对话基本信息
    const selectedConversations = conversations.filter(conv => 
      selectedRowKeys.includes(`${conv.user_id}-${conv.id}`)
    );
    
    // 创建工作簿
    const wb = XLSX.utils.book_new();
    
    // 第一个工作表：对话概览
    const overviewHeaders = ['学生', '班级', '对话标题', '智能体', '开始时间', '消息数', 'Token数'];
    const overviewData = [
      overviewHeaders,
      ...selectedConversations.map(conv => [
        conv.student_name || '',
        conv.class_name || '',
        conv.title || '',
        conv.agent_name || '',
        conv.start_time ? new Date(conv.start_time).toLocaleString('zh-CN') : '',
        conv.total_messages?.toString() || '0',
        conv.total_tokens?.toString() || '0'
      ])
    ];
    
    const overviewWs = XLSX.utils.aoa_to_sheet(overviewData);
    XLSX.utils.book_append_sheet(wb, overviewWs, '对话概览');
    
    // 设置概览工作表列宽
    const overviewColWidths = overviewHeaders.map((header, index) => {
      const maxLength = Math.max(
        header.length,
        ...selectedConversations.map(conv => {
          const value = overviewData[selectedConversations.indexOf(conv) + 1][index];
          return String(value).length;
        })
      );
      return { wch: Math.min(maxLength + 2, 50) };
    });
    overviewWs['!cols'] = overviewColWidths;
    
    // 设置进度信息
    setExportTotal(selectedConversations.length);
    setExportProgress(0);
    
    // 显示进度模态框
    setProgressModalVisible(true);
    
    // 为每个对话创建详细内容工作表
    let successCount = 0;
    let failCount = 0;
    
    // 依次获取每个对话的详细信息
    for (let i = 0; i < selectedConversations.length; i++) {
      const conv = selectedConversations[i];
      try {
        // 更新进度
        setExportProgress(i + 1);
        
        const res = await aiApi.data.getConversationDetails(conv.id);
        if (res.success) {
          // 合并对话基本信息和消息
          const conversationDetail: ConversationDetail = {
            ...res.conversation,
            messages: res.messages || []
          };
          
          // 创建对话详情工作表
          const detailHeaders = ['角色', '时间', '内容', 'Token数'];
          const detailData = [
            detailHeaders,
            ...conversationDetail.messages.map((msg: any) => [
              msg.role === 'user' ? '提问者' : 'AI回答',
              msg.created_at ? new Date(msg.created_at).toLocaleString('zh-CN') : '',
              msg.content || '',
              msg.tokens?.toString() || '0'
            ])
          ];
          
          // 添加基本信息行
          detailData.unshift([], ['对话基本信息：']);
          detailData.unshift(['学生', conversationDetail.user?.username || '未知用户']);
          detailData.unshift(['对话标题', conversationDetail.title || '']);
          detailData.unshift(['智能体', conversationDetail.agent?.name || '']);
          detailData.unshift(['开始时间', conversationDetail.start_time ? new Date(conversationDetail.start_time).toLocaleString('zh-CN') : '']);
          detailData.unshift(['消息数', conversationDetail.total_messages?.toString() || '0']);
          detailData.unshift(['Token数', conversationDetail.total_tokens?.toString() || '0']);
          
          const detailWs = XLSX.utils.aoa_to_sheet(detailData);
          
          // 设置工作表名称（限制长度，避免Excel报错）
          let sheetName = conv.title || `对话${conv.id}`;
          // 移除无效字符并限制长度（Excel工作表名称最多31个字符）
          sheetName = sheetName.replace(/[\\/*?:\[\]]/g, '').substring(0, 31);
          // 确保工作表名称不重复
          let finalSheetName = sheetName;
          let counter = 1;
          while (wb.SheetNames.includes(finalSheetName)) {
            finalSheetName = `${sheetName.substring(0, 28)}_${counter}`;
            counter++;
          }
          
          XLSX.utils.book_append_sheet(wb, detailWs, finalSheetName);
          
          // 设置列宽
          const detailColWidths = [
            { wch: 10 }, // 角色列
            { wch: 20 }, // 时间列
            { wch: 80 }, // 内容列（较宽）
            { wch: 10 }  // Token数列
          ];
          detailWs['!cols'] = detailColWidths;
          
          successCount++;
        } else {
          failCount++;
          console.error(`获取对话 ${conv.id} 详情失败:`, res);
        }
      } catch (error) {
        failCount++;
        console.error(`获取对话 ${conv.id} 详情失败:`, error);
      }
    }
    
    // 如果没有成功获取任何对话详情，则不导出
    if (successCount === 0) {
      message.destroy();
      message.error('无法获取任何对话的详细内容，导出取消');
      return;
    }
    
    // 生成Excel文件
    message.loading(`正在生成Excel文件...`, 0);
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `批量对话内容_${new Date().toISOString().slice(0, 10)}.xlsx`;
    link.click();
    URL.revokeObjectURL(url);
    
    message.destroy();
    if (failCount > 0) {
      message.warning(`成功导出 ${successCount} 个对话，${failCount} 个对话获取失败`);
    } else {
      message.success(`成功导出 ${successCount} 个对话的详细内容`);
    }
    
    // 清空选择
    setSelectedRowKeys([]);
  } catch (error) {
    console.error('批量导出失败:', error);
    message.destroy();
    message.error('批量导出失败，请重试');
  } finally {
    setBatchExporting(false);
    setProgressModalVisible(false);
  }
};

/**
 * 加载对话列表
 */
export const loadConversations = async (
  currentPage: number,
  currentPageSize: number,
  students: Student[],
  agents: Agent[],
  selectedStudent: number | undefined,
  selectedClass: string | undefined,
  selectedAgent: number | undefined,
  dateRange: [string, string] | undefined,
  searchText: string,
  setLoading: (loading: boolean) => void,
  setConversations: (conversations: Conversation[]) => void,
  setTotal: (total: number) => void,
  setPage: (page: number) => void,
  setPageSize: (pageSize: number) => void
): Promise<void> => {
  setLoading(true);
  try {
    // 由于现有API限制，我们只能按学生获取对话
    // 这里我们先获取所有学生的对话，然后在前端进行筛选
    let allConversations: Conversation[] = [];
    let totalCount = 0;
    
    // 根据筛选条件确定要获取哪些学生的对话
    let studentsToFetch = students;
    
    // 应用班级筛选
    if (selectedClass) {
      studentsToFetch = studentsToFetch.filter(s => s.class_name === selectedClass);
    }
    
    // 如果选择了特定学生，只获取该学生的对话
    if (selectedStudent) {
      // 确保选中的学生在筛选后的列表中
      const targetStudent = studentsToFetch.find(s => s.id === selectedStudent);
      if (targetStudent) {
        studentsToFetch = [targetStudent];
      } else {
        // 如果选中的学生不在筛选后的列表中（例如选择了某个班级，但选中的学生不在该班级）
        // 则使用空数组，表示没有符合条件的学生
        studentsToFetch = [];
      }
    }
    
    if (studentsToFetch.length === 0) {
      // 没有符合条件的学生
      setConversations([]);
      setTotal(0);
      setPage(currentPage);
      setPageSize(currentPageSize);
      return;
    }
    
    // 限制要获取的学生数量以避免过多API请求
    const limitedStudents = studentsToFetch.slice(0, selectedStudent ? 1 : 10);
    
    const promises = limitedStudents.map(async (student) => {
      try {
        const convRes = await aiApi.data.getStudentConversations(
          student.id,
          dateRange?.[0],
          dateRange?.[1],
          1,
          selectedStudent ? 1000 : 50 // 如果选择了特定学生，获取更多对话
        );
        if (convRes.success) {
          return convRes.conversations.map((conv: any) => ({
            ...conv,
            student_name: student.username,
            student_id: student.student_id,
            class_name: student.class_name,
            user_id: student.id,
          }));
        }
        return [];
      } catch (error) {
        console.error(`获取学生 ${student.username} 的对话失败:`, error);
        return [];
      }
    });
    
    const results = await Promise.all(promises);
    allConversations = results.flat();
    totalCount = allConversations.length;
    
    // 前端筛选：按智能体、搜索文本
    let filtered = allConversations;
    
    if (selectedAgent) {
      // 注意：API返回的agent_name是字符串，我们需要通过名称匹配
      // 先找到智能体名称
      const agent = agents.find(a => a.id === selectedAgent);
      if (agent) {
        filtered = filtered.filter(conv => conv.agent_name === agent.name);
      }
    }
    
    if (searchText) {
      const searchLower = searchText.toLowerCase();
      filtered = filtered.filter(conv =>
        conv.title.toLowerCase().includes(searchLower) ||
        conv.student_name.toLowerCase().includes(searchLower) ||
        conv.agent_name.toLowerCase().includes(searchLower) ||
        (conv.student_id && conv.student_id.toLowerCase().includes(searchLower))
      );
    }
    
    // 排序：按开始时间倒序
    filtered.sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
    
    // 分页
    const start = (currentPage - 1) * currentPageSize;
    const end = start + currentPageSize;
    const paginated = filtered.slice(start, end);
    
    setConversations(paginated);
    setTotal(totalCount);
    setPage(currentPage);
    setPageSize(currentPageSize);
  } catch (error) {
    console.error('加载对话列表失败:', error);
    message.error('加载对话列表失败');
  } finally {
    setLoading(false);
  }
};

/**
 * 查看对话详情
 */
export const handleViewDetail = async (
  conversationId: number,
  setDetailLoading: (loading: boolean) => void,
  setCurrentConversation: (conversation: ConversationDetail | null) => void,
  setDetailVisible: (visible: boolean) => void
): Promise<void> => {
  setDetailLoading(true);
  try {
    const res = await aiApi.data.getConversationDetails(conversationId);
    if (res.success) {
      // API返回的数据结构：res.conversation 和 res.messages 是分开的
      // 我们需要合并为一个对象，以匹配ConversationDetail接口
      const conversationDetail: ConversationDetail = {
        ...res.conversation,
        messages: res.messages || []
      };
      setCurrentConversation(conversationDetail);
      setDetailVisible(true);
    } else {
      message.error('获取对话详情失败');
    }
  } catch (error) {
    console.error('获取对话详情失败:', error);
    message.error('获取对话详情失败');
  } finally {
    setDetailLoading(false);
  }
};

/**
 * 导出单个对话
 */
export const handleExport = async (
  conversationId: number,
  currentConversation: ConversationDetail | null,
  exporting: boolean,
  setExporting: (exporting: boolean) => void
): Promise<void> => {
  // 防止重复点击
  if (exporting) return;
  
  setExporting(true);
  
  try {
    // 获取要导出的对话数据
    let conversationToExport: ConversationDetail | null = null;
    
    // 如果当前打开的对话详情就是要导出的对话，直接使用
    if (currentConversation && currentConversation.id === conversationId) {
      conversationToExport = currentConversation;
    } else {
      // 否则，调用API获取对话详情
      message.loading('正在加载对话数据...', 0);
      try {
        const res = await aiApi.data.getConversationDetails(conversationId);
        if (res.success) {
          // API返回的数据结构：res.conversation 和 res.messages 是分开的
          // 我们需要合并为一个对象，以匹配ConversationDetail接口
          conversationToExport = {
            ...res.conversation,
            messages: res.messages || []
          };
        } else {
          message.destroy();
          message.error('获取对话详情失败，无法导出');
          return;
        }
      } catch (error) {
        console.error('获取对话详情失败:', error);
        message.destroy();
        message.error('获取对话详情失败，请检查网络连接');
        return;
      } finally {
        message.destroy();
      }
    }
    
    if (!conversationToExport) {
      message.warning('没有可导出的对话数据');
      return;
    }
    
    // 安全地构建导出内容，处理可能为空的数据
    const content = `对话标题：${conversationToExport.title || '无标题'}\n` +
                   `学生：${conversationToExport.user?.username || '未知用户'}\n` +
                   `智能体：${conversationToExport.agent?.name || '未知智能体'}\n` +
                   `开始时间：${conversationToExport.start_time ? new Date(conversationToExport.start_time).toLocaleString('zh-CN') : '未知时间'}\n` +
                   `消息数：${conversationToExport.total_messages || 0}\n` +
                   `Token数：${conversationToExport.total_tokens || 0}\n\n` +
                   '对话内容：\n' +
                   (conversationToExport.messages && conversationToExport.messages.length > 0 ? 
                    conversationToExport.messages.map(msg =>
                      `${msg.role === 'user' ? '学生' : 'AI'} (${msg.created_at ? new Date(msg.created_at).toLocaleString('zh-CN') : '未知时间'}):\n${msg.content || '无内容'}\n`
                    ).join('\n') : '无消息内容');
    
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `对话_${conversationId}_${new Date().toISOString().slice(0, 10)}.txt`;
    link.click();
    URL.revokeObjectURL(url);
    
    message.success('导出成功');
  } catch (error) {
    console.error('导出对话失败:', error);
    message.error('导出失败，请重试');
  } finally {
    setExporting(false);
  }
};

/**
 * 删除对话
 */
export const handleDelete = async (
  conversationId: number,
  page: number,
  pageSize: number,
  loadConversationsFunc: () => Promise<void>
): Promise<void> => {
  try {
    // 这里需要实现删除API调用
    // 暂时显示提示
    message.info('删除功能需要后端API支持，当前版本暂不可用');
    // 重新加载列表
    await loadConversationsFunc();
  } catch (error) {
    console.error('删除对话失败:', error);
    message.error('删除对话失败');
  }
};

/**
 * 选择/取消选择所有
 */
export const handleSelectAll = (
  selectedRowKeys: React.Key[],
  conversations: Conversation[],
  setSelectedRowKeys: (keys: React.Key[]) => void
): void => {
  if (selectedRowKeys.length === conversations.length) {
    setSelectedRowKeys([]);
  } else {
    setSelectedRowKeys(conversations.map(conv => `${conv.user_id}-${conv.id}`));
  }
};
