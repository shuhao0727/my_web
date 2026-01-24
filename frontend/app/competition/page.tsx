'use client';

import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Spin, Alert, Card, Tree, Input, Tabs, Space } from 'antd';
import { 
  FolderOutlined, 
  FileTextOutlined, 
  SearchOutlined, 
  FileImageOutlined,
  ReloadOutlined,
  CodeOutlined,
  EyeOutlined
} from '@ant-design/icons';
import * as typstApi from '../../lib/typstApi';
import TypstRenderer from '../../components/TypstRenderer';

const { Text, Title, Paragraph } = Typography;
const { Sider, Content } = Layout;
const { Search } = Input;

interface ChapterTreeNode {
  id: string;
  title: string;
  path: string;
  type: 'directory' | 'file';
  level: number;
  children?: ChapterTreeNode[];
  is_typst?: boolean;
}

export default function CompetitionPage() {
  const [loading, setLoading] = useState(true);
  const [structure, setStructure] = useState<typstApi.TypstStructureResponse | null>(null);
  const [chapterTree, setChapterTree] = useState<ChapterTreeNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [selectedFilePath, setSelectedFilePath] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState('view');
  const [lastSyncTime, setLastSyncTime] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'success' | 'error'>('idle');

  // 初始化加载
  useEffect(() => {
    loadData();
    // 24小时同步检查
    const syncInterval = setInterval(() => {
      checkAndSync();
    }, 24 * 60 * 60 * 1000); // 24小时

    // 启动时立即检查一次同步
    setTimeout(() => {
      checkAndSync();
    }, 3000);

    return () => clearInterval(syncInterval);
  }, []);

  // 加载数据
  const loadData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadStructure(),
        loadChapterTree()
      ]);
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载仓库结构
  const loadStructure = async () => {
    try {
      const structureData = await typstApi.getTypstStructure();
      setStructure(structureData);
    } catch (error) {
      console.error('加载仓库结构失败:', error);
    }
  };

  // 加载章节树
  const loadChapterTree = async () => {
    try {
      const tree = await typstApi.buildChapterTree();
      setChapterTree(tree);
      
      // 默认选择第一个Typst文件
      if (tree.length > 0) {
        const firstFile = findFirstTypstFile(tree);
        if (firstFile) {
          handleFileSelect(firstFile);
        }
      }
    } catch (error) {
      console.error('加载章节树失败:', error);
    }
  };

  // 查找第一个Typst文件
  const findFirstTypstFile = (nodes: ChapterTreeNode[]): ChapterTreeNode | null => {
    for (const node of nodes) {
      if (node.type === 'file' && node.is_typst) {
        return node;
      }
      if (node.children && node.children.length > 0) {
        const found = findFirstTypstFile(node.children);
        if (found) return found;
      }
    }
    return null;
  };

  // 处理文件选择
  const handleFileSelect = async (node: ChapterTreeNode) => {
    if (node.type === 'file' && node.is_typst) {
      setSelectedFilePath(node.path);
      setSelectedFile(node.title);
      try {
        const content = await typstApi.getTypstContent(node.path);
        setFileContent(content.content);
      } catch (error) {
        console.error('加载文件内容失败:', error);
        setFileContent('加载文件失败');
      }
    }
  };

  // 检查并同步仓库
  const checkAndSync = async () => {
    try {
      setSyncStatus('syncing');
      // 这里可以调用后端的同步API
      // 暂时模拟同步成功
      setTimeout(() => {
        setSyncStatus('success');
        setLastSyncTime(new Date().toLocaleString());
        // 重新加载数据
        loadData();
      }, 2000);
    } catch (error) {
      console.error('同步失败:', error);
      setSyncStatus('error');
    }
  };

  // 手动触发同步
  const handleManualSync = async () => {
    await checkAndSync();
  };

  // 构建树形数据
  const buildTreeData = (nodes: ChapterTreeNode[]): any[] => {
    return nodes.map(node => ({
      key: node.id,
      title: (
        <div className="flex items-center w-full overflow-hidden">
          <span className="mr-2 flex-shrink-0">
            {node.type === 'directory' ? <FolderOutlined /> : 
             node.is_typst ? <FileTextOutlined /> : <FileImageOutlined />}
          </span>
          <Text ellipsis className="max-w-[280px] overflow-hidden whitespace-nowrap text-ellipsis">
            {node.title}
          </Text>
        </div>
      ),
      isLeaf: node.type === 'file',
      children: node.children ? buildTreeData(node.children) : undefined,
    }));
  };

  // 搜索处理
  const handleSearch = async (value: string) => {
    setSearchQuery(value);
    if (value.trim()) {
      try {
        const results = await typstApi.searchTypstFiles(value);
        // 这里可以显示搜索结果，暂时先忽略
        console.log('搜索结果:', results);
      } catch (error) {
        console.error('搜索失败:', error);
      }
    }
  };

  // 辅助函数：根据ID查找节点
  const findNodeById = (nodes: ChapterTreeNode[], id: string): ChapterTreeNode | null => {
    for (const node of nodes) {
      if (node.id === id) return node;
      if (node.children) {
        const found = findNodeById(node.children, id);
        if (found) return found;
      }
    }
    return null;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <Spin size="large" />
        <Text className="mt-4">正在加载文档库...</Text>
      </div>
    );
  }

  return (
    <Layout className="min-h-screen bg-white overflow-x-hidden">
      {/* 同步状态栏 */}
      <div className="bg-gray-50 border-b border-gray-200 px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <div className={`w-2 h-2 rounded-full mr-2 ${
                syncStatus === 'idle' ? 'bg-gray-400' :
                syncStatus === 'syncing' ? 'bg-yellow-500 animate-pulse' :
                syncStatus === 'success' ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <Text className="text-sm text-gray-600">
                {syncStatus === 'idle' ? '就绪' :
                 syncStatus === 'syncing' ? '同步中...' :
                 syncStatus === 'success' ? '同步成功' : '同步失败'}
              </Text>
            </div>
            {lastSyncTime && (
              <Text className="text-sm text-gray-500">
                最后同步: {lastSyncTime}
              </Text>
            )}
          </div>
          <Space>
            <button
              onClick={handleManualSync}
              className={`px-3 py-1 rounded text-sm flex items-center ${
                syncStatus === 'syncing' 
                  ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
                  : 'bg-blue-100 text-blue-600 hover:bg-blue-200'
              }`}
              disabled={syncStatus === 'syncing'}
            >
              <ReloadOutlined className={`mr-1 ${syncStatus === 'syncing' ? 'animate-spin' : ''}`} />
              {syncStatus === 'syncing' ? '同步中...' : '立即同步'}
            </button>
          </Space>
        </div>
      </div>

      <div className="w-full bg-gray-50 overflow-x-hidden flex justify-center px-12">
        <div className="w-full max-w-[1440px] bg-white rounded-lg shadow-sm overflow-hidden">
          <Layout className="w-full flex-shrink-0 overflow-hidden gap-[50px] justify-center">
            <Sider
              width={340}
              collapsedWidth={80}
              collapsible
              collapsed={siderCollapsed}
              onCollapse={setSiderCollapsed}
              className="border-r border-gray-200 bg-white"
              theme="light"
              style={{ 
                height: 'calc(100vh - 64px)', 
                position: 'sticky', 
                top: 0, 
                left: 0 
              }}
            >
              {!siderCollapsed && (
                <div className="p-4 border-b">
                  <div className="mb-2">
                    <Title level={5} className="mb-2">章节目录</Title>
                  </div>
                  
                  <Search
                    placeholder="搜索章节..."
                    allowClear
                    enterButton={<SearchOutlined />}
                    onSearch={handleSearch}
                    className="mb-4"
                  />
                </div>
              )}

              <div className="h-[calc(100%-180px)]">
                {chapterTree.length > 0 ? (
                  <div className="h-full overflow-y-auto">
                    <Tree
                      showLine
                      showIcon={false}
                      defaultExpandAll
                      selectedKeys={selectedFilePath ? [selectedFilePath] : []}
                      onSelect={(keys, { node }) => {
                        const selectedNode = findNodeById(chapterTree, keys[0] as string);
                        if (selectedNode) {
                          handleFileSelect(selectedNode);
                        }
                      }}
                      treeData={buildTreeData(chapterTree)}
                      className="pl-2 pr-1 w-full"
                    />
                  </div>
                ) : (
                  <div className="p-4 text-center text-gray-400">
                    <FileTextOutlined className="text-2xl mb-2" />
                    <Text>暂无文档</Text>
                  </div>
                )}
              </div>
            </Sider>

            <Content className="bg-gray-50">
              <div className="h-full p-6">
                {selectedFilePath ? (
                  <div className="h-full flex flex-col w-full max-w-[1000px] mx-auto">
                    <div className="mb-4">
                      <Title level={4} className="mb-2">{selectedFile}</Title>
                      <div className="flex items-center text-gray-600 text-sm">
                        <CodeOutlined className="mr-1" />
                        <Text className="truncate">{selectedFilePath}</Text>
                      </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm border h-[800px] overflow-y-scroll">
                      <TypstRenderer 
                        content={fileContent}
                        filePath={selectedFilePath}
                      />
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col justify-center items-center h-full text-gray-400">
                    <FileTextOutlined className="text-4xl mb-4" />
                    <Title level={4} className="mb-2">选择文档</Title>
                    <Text>请从左侧选择您想要查看的文档</Text>
                  </div>
                )}
              </div>
            </Content>
          </Layout>
        </div>
      </div>
    </Layout>
  );
}