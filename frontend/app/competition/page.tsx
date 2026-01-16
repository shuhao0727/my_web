'use client';

import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Spin } from 'antd';
import { FolderOutlined, FileTextOutlined, MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import * as repoApi from '@/lib/repoApi';

const { Text } = Typography;
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

  useEffect(() => {
    loadRepositoryData();
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
    } finally {
      setLoading(false);
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

  return (
    <Layout className="min-h-screen bg-white">
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
