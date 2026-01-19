'use client';

import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Spin, Modal, Alert } from 'antd';
import { FolderOutlined, FileTextOutlined, MenuFoldOutlined, MenuUnfoldOutlined, WarningOutlined } from '@ant-design/icons';
import * as repoApi from '@/lib/repoApi';

const { Text, Paragraph } = Typography;
const { Sider, Content } = Layout;

interface ChapterNode {
  id: string;
  title: string;
  path: string;
  isDirectory: boolean;
  level: number;
  children?: ChapterNode[];
}

export default function CompetitionPage() {
  const [chapterTree, setChapterTree] = useState<ChapterNode[]>([]);
  const [selectedChapterPath, setSelectedChapterPath] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [tokenExpiredModalVisible, setTokenExpiredModalVisible] = useState(false);
  const [repoStatus, setRepoStatus] = useState<repoApi.RepoStatus | null>(null);

  useEffect(() => {
    loadRepositoryData();
    checkTokenStatus();
  }, []);

  useEffect(() => {
    if (selectedChapterPath) {
      loadChapterPdf(selectedChapterPath);
    }
  }, [selectedChapterPath]);

  const loadRepositoryData = async () => {
    try {
      setLoading(true);

      const tree = await repoApi.getChapterTree();
      // 对树进行排序：自然排序
      const sortedTree = sortChapterTree(tree);
      setChapterTree(sortedTree);

      if (sortedTree.length > 0) {
        const firstChapter = findFirstLeafChapter(sortedTree);
        if (firstChapter) {
          setSelectedChapterPath(firstChapter.path);
        }
      }
    } catch (err: any) {
      console.error('加载仓库数据失败:', err);
      // 检查是否是令牌过期错误
      if (err.message?.includes('token') || err.message?.includes('authentication')) {
        checkTokenStatus();
      }
    } finally {
      setLoading(false);
    }
  };

  const checkTokenStatus = async () => {
    try {
      const status = await repoApi.getRepoStatus();
      setRepoStatus(status);
      
      // 如果令牌过期，显示弹窗
      if (status.token_expired || (status.remote_error && status.remote_error.includes('token'))) {
        setTokenExpiredModalVisible(true);
      } else {
        setTokenExpiredModalVisible(false);
      }
    } catch (err: any) {
      console.error('检查令牌状态失败:', err);
    }
  };

  const loadChapterPdf = async (chapterPath: string) => {
    try {
      const url = await repoApi.getChapterPdfUrl(chapterPath);
      setPdfUrl(url);
    } catch (err: any) {
      console.error('加载PDF失败:', err);
      setPdfUrl(null);
    }
  };

  const findFirstLeafChapter = (nodes: ChapterNode[]): ChapterNode | null => {
    for (const node of nodes) {
      if (!node.isDirectory) {
        return node;
      }
      if (node.children && node.children.length > 0) {
        const found = findFirstLeafChapter(node.children);
        if (found) return found;
      }
    }
    return null;
  };

  const buildMenuItems = (nodes: ChapterNode[]): any[] => {
    return nodes.map(node => ({
      key: node.id,
      icon: node.isDirectory ? <FolderOutlined /> : <FileTextOutlined />,
      label: (
        <div className="flex items-center justify-between">
          <Text ellipsis style={{ maxWidth: '200px' }}>{node.title}</Text>
        </div>
      ),
      style: { paddingLeft: `${node.level * 16}px` },
      onClick: () => {
        if (!node.isDirectory) {
          setSelectedChapterPath(node.path);
        }
      },
      children: node.children ? buildMenuItems(node.children) : undefined,
    }));
  };

  const sortChapterTree = (nodes: ChapterNode[]): ChapterNode[] => {
    // 对节点进行自然排序
    const sortedNodes = [...nodes].sort((a, b) => {
      // 首先按是否是目录排序，目录在前
      if (a.isDirectory !== b.isDirectory) {
        return a.isDirectory ? -1 : 1;
      }
      // 然后按标题进行自然排序
      return naturalSort(a.title, b.title);
    });

    // 递归排序子节点
    return sortedNodes.map(node => ({
      ...node,
      children: node.children ? sortChapterTree(node.children) : undefined,
    }));
  };

  const naturalSort = (a: string, b: string): number => {
    // 简单的自然排序实现
    const aParts = a.match(/(\d+|\D+)/g) || [];
    const bParts = b.match(/(\d+|\D+)/g) || [];
    
    for (let i = 0; i < Math.min(aParts.length, bParts.length); i++) {
      const aPart = aParts[i];
      const bPart = bParts[i];
      
      const aNum = parseInt(aPart, 10);
      const bNum = parseInt(bPart, 10);
      
      if (!isNaN(aNum) && !isNaN(bNum)) {
        if (aNum !== bNum) {
          return aNum - bNum;
        }
      } else {
        if (aPart < bPart) return -1;
        if (aPart > bPart) return 1;
      }
    }
    
    return aParts.length - bParts.length;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <Spin size="large" />
        <Text className="mt-4">正在加载文档...</Text>
      </div>
    );
  }

  const menuItems = buildMenuItems(chapterTree);

  // GitHub令牌过期弹窗
  const TokenExpiredModal = () => (
    <Modal
      title={
        <div className="flex items-center">
          <WarningOutlined className="text-yellow-500 mr-2" />
          <span>GitHub访问令牌已过期</span>
        </div>
      }
      open={tokenExpiredModalVisible}
      onCancel={() => setTokenExpiredModalVisible(false)}
      footer={[
        <button
          key="close"
          onClick={() => setTokenExpiredModalVisible(false)}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors"
        >
          稍后处理
        </button>,
      ]}
      width={600}
      closable={false}
      maskClosable={false}
    >
      <div className="space-y-4">
        <Alert
          type="warning"
          showIcon
          title="GitHub访问令牌已过期"
          description="您的GitHub访问令牌可能已过期或失效，这将影响文档的自动同步和PDF更新。"
        />
        
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <Paragraph strong>问题影响：</Paragraph>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>无法从GitHub仓库自动同步最新文档</li>
            <li>无法生成新的PDF文件</li>
            <li>现有PDF文件可能无法更新</li>
            <li>文档目录可能无法加载最新内容</li>
          </ul>
        </div>

        <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
          <Paragraph strong>解决方案：</Paragraph>
          <ol className="list-decimal pl-5 space-y-2 mt-2">
            <li>
              <Paragraph strong>1. 获取新的GitHub访问令牌</Paragraph>
              <ul className="list-disc pl-5 space-y-1 mt-1">
                <li>访问 <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">GitHub Token设置页面</a></li>
                <li>点击 "Generate new token (classic)"</li>
                <li>选择 <code className="bg-gray-100 px-1 rounded">repo</code> 权限</li>
                <li>设置合适的过期时间（建议90天）</li>
                <li>复制生成的令牌</li>
              </ul>
            </li>
            <li>
              <Paragraph strong>2. 更新配置文件</Paragraph>
              <ul className="list-disc pl-5 space-y-1 mt-1">
                <li>打开文件：<code className="bg-gray-100 px-1 rounded">/Volumes/文件/4-实用代码/my_web/backend/.env</code></li>
                <li>找到 <code className="bg-gray-100 px-1 rounded">GITHUB_ACCESS_TOKEN=</code> 行</li>
                <li>将旧令牌替换为新令牌</li>
                <li>保存文件</li>
              </ul>
            </li>
            <li>
              <Paragraph strong>3. 重启后端服务</Paragraph>
              <ul className="list-disc pl-5 space-y-1 mt-1">
                <li>停止当前运行的后端服务（Ctrl+C）</li>
                <li>重新启动：<code className="bg-gray-100 px-1 rounded">python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload</code></li>
              </ul>
            </li>
          </ol>
        </div>

        <div className="p-3 bg-gray-100 rounded-md">
          <Paragraph strong>当前状态：</Paragraph>
          <div className="mt-1 space-y-1">
            {repoStatus?.remote_error && (
              <div className="text-red-600 text-sm">
                <span className="font-medium">错误信息：</span> {repoStatus.remote_error}
              </div>
            )}
            {repoStatus?.last_updated && (
              <div className="text-gray-600 text-sm">
                <span className="font-medium">最后同步：</span> {new Date(repoStatus.last_updated).toLocaleString()}
              </div>
            )}
            {repoStatus?.branch && (
              <div className="text-gray-600 text-sm">
                <span className="font-medium">当前分支：</span> {repoStatus.branch}
              </div>
            )}
          </div>
        </div>

        <div className="text-center text-sm text-gray-500">
          <p>如果您已更新令牌，弹窗将在下次检查时自动关闭。</p>
          <p>您也可以点击"稍后处理"暂时关闭此提醒。</p>
        </div>
      </div>
    </Modal>
  );

  return (
    <Layout className="min-h-screen bg-white">
      {/* GitHub令牌过期弹窗 */}
      <TokenExpiredModal />
      <Sider
        width={320}
        collapsedWidth={60}
        collapsible
        collapsed={leftCollapsed}
        onCollapse={setLeftCollapsed}
        trigger={
          leftCollapsed ? (
            <MenuUnfoldOutlined className="text-lg" />
          ) : (
            <MenuFoldOutlined className="text-lg" />
          )
        }
        className="border-r border-gray-200"
        theme="light"
        style={{ 
          overflow: 'auto', 
          height: '100vh', 
          position: 'sticky', 
          top: 0, 
          left: 0 
        }}
      >
        <div className="h-full flex flex-col">
          {!leftCollapsed && (
            <div className="p-4 border-b flex-shrink-0">
              <div className="text-lg font-semibold">文档目录</div>
              <div className="mt-1 text-xs text-gray-500">
                <Text ellipsis>
                  共 {chapterTree.reduce((count, node) => count + countLeafChapters(node), 0)} 个文档
                </Text>
              </div>
            </div>
          )}
          <div className="flex-grow overflow-y-auto">
            {menuItems.length > 0 ? (
              <Menu
                mode="inline"
                selectedKeys={selectedChapterPath ? [selectedChapterPath] : []}
                items={menuItems}
                className="border-0"
              />
            ) : (
              <div className="p-4 text-center text-gray-400">
                <FileTextOutlined className="text-2xl mb-2" />
                <Text>暂无文档</Text>
              </div>
            )}
          </div>
        </div>
      </Sider>

      <Content className="overflow-auto" style={{ height: '100vh' }}>
        <div className="h-full overflow-y-auto">
          {pdfUrl ? (
            <div className="h-full">
              <div className="border rounded-lg overflow-hidden relative h-full">
                {/* 使用sandbox限制iframe功能，防止下载 */}
                <iframe
                  src={pdfUrl}
                  title="PDF预览"
                  className="w-full h-full"
                  style={{ border: 'none' }}
                  sandbox="allow-same-origin allow-scripts"
                  // 以下属性进一步限制功能
                  onContextMenu={(e) => e.preventDefault()}
                  onKeyDown={(e) => {
                    // 阻止快捷键下载 (Ctrl+S, Ctrl+P等)
                    if (e.ctrlKey && (e.key === 's' || e.key === 'p' || e.key === 'd')) {
                      e.preventDefault();
                    }
                  }}
                />
                {/* 透明覆盖层，防止右键菜单 */}
                <div 
                  className="absolute inset-0 pointer-events-none"
                  onContextMenu={(e) => e.preventDefault()}
                />
              </div>
            </div>
          ) : (
            <div className="flex flex-col justify-center items-center h-full text-gray-400">
              <FileTextOutlined className="text-4xl mb-4" />
              <div className="text-lg font-medium">选择文档以预览</div>
              <Text>请从左侧选择您想要查看的文档</Text>
            </div>
          )}
        </div>
      </Content>
    </Layout>
  );
}

function countLeafChapters(node: ChapterNode): number {
  if (!node.isDirectory) {
    return 1;
  }
  if (!node.children || node.children.length === 0) {
    return 0;
  }
  return node.children.reduce((sum, child) => sum + countLeafChapters(child), 0);
}
