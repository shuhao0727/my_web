'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import '../../app/globals.css';

interface FileInfo {
  name: string;
  path: string;
  type: string;
  size: number;
  extension: string;
  is_markdown: boolean;
}

interface ArticleStructure {
  success: boolean;
  structure: {
    categories: {
      exists: boolean;
      count: number;
      subdirectories: string[];
      category_list: Array<{
        name: string;
        file_count: number;
        files: string[];
      }>;
    };
    markdown_files: {
      total: number;
      files: string[];
    };
  };
  articles_path: string;
}

interface TreeData {
  success: boolean;
  path: string;
  files: FileInfo[];
  count: number;
  articles_path: string;
}

interface ArticleContent {
  success: boolean;
  path: string;
  content: string;
  html_content: string;
  size: number;
  encoding: string;
}

export default function ArticlesPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [treeData, setTreeData] = useState<TreeData | null>(null);
  const [currentPath, setCurrentPath] = useState('');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<ArticleContent | null>(null);
  const [structure, setStructure] = useState<ArticleStructure | null>(null);

  // 加载文章树结构和处理URL参数
  useEffect(() => {
    // 从URL参数中获取路径
    const urlParams = new URLSearchParams(window.location.search);
    const pathParam = urlParams.get('path');
    
    if (pathParam) {
      // 如果URL中有path参数，表示要直接加载特定文件
      const decodedPath = decodeURIComponent(pathParam);
      if (decodedPath.endsWith('.md')) {
        // 如果是文件路径，直接加载文件内容
        loadFileContent(decodedPath);
      } else {
        // 如果是目录路径，切换到该目录
        setCurrentPath(decodedPath);
        loadTree(decodedPath);
      }
    } else {
      // 默认加载根目录
      loadTree(currentPath);
    }
    loadStructure();
  }, []);

  const loadTree = async (path: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const url = path ? 
        `/api/md/articles/tree?path=${encodeURIComponent(path)}` : 
        '/api/md/articles/tree';
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`加载文件树失败: ${response.status}`);
      }
      
      const data = await response.json();
      setTreeData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  };

  const loadStructure = async () => {
    try {
      const response = await fetch('/api/md/articles/structure');
      if (!response.ok) {
        throw new Error(`加载结构失败: ${response.status}`);
      }
      const data = await response.json();
      setStructure(data);
    } catch (err) {
      console.error('加载结构失败:', err);
    }
  };

  const loadFileContent = async (filePath: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/md/articles/content/${filePath}`);
      
      if (!response.ok) {
        throw new Error(`加载文件内容失败: ${response.status}`);
      }
      
      const data = await response.json();
      setFileContent(data);
      setSelectedFile(filePath);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  };

  const handleNavigate = (path: string) => {
    setCurrentPath(path);
    setSelectedFile(null);
    setFileContent(null);
    loadTree(path); // 立即重新加载当前路径的树结构
  };

  const handleFileSelect = (filePath: string) => {
    loadFileContent(filePath);
  };

  const goBack = () => {
    if (currentPath) {
      const parentPath = currentPath.split('/').slice(0, -1).join('/');
      handleNavigate(parentPath || '');
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h1 className="text-2xl font-bold text-red-600 mb-4">错误</h1>
            <p className="text-red-600">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              重试
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-[1440px] mx-auto px-12">
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-[50px]">
          {/* 侧边栏 - 文件树 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-4 sticky top-4">
              <h2 className="text-lg font-semibold mb-4">文章目录</h2>
              
              {currentPath && (
                <button
                  onClick={goBack}
                  className="flex items-center mb-2 text-blue-600 hover:text-blue-800 text-sm"
                >
                  ← 返回上级
                </button>
              )}
              
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                </div>
              ) : treeData ? (
                <div className="space-y-1">
                  {treeData.files.map((file) => (
                    <div
                      key={file.path}
                      className={`flex items-center p-2 rounded cursor-pointer hover:bg-gray-100 ${
                        selectedFile === file.path ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                      }`}
                      onClick={() => {
                        if (file.type === 'directory') {
                          handleNavigate(file.path);
                        } else if (file.type === 'file' && file.is_markdown) {
                          handleFileSelect(file.path);
                        }
                      }}
                    >
                      <span className="mr-2">
                        {file.type === 'directory' ? '📁' : '📄'}
                      </span>
                      <span className="text-sm truncate">{file.name}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">暂无文件</p>
              )}
              
              {/* 文章分类统计 */}
              {structure && (
                <div className="mt-4 pt-4 border-t">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">统计信息</h3>
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>总文件数: {structure.structure.markdown_files.total}</div>
                    <div>分类数: {structure.structure.categories.subdirectories.length}</div>
                    <div>总大小: {structure.structure.categories.count} 个目录</div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* 主内容区 */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-md p-6">
              {loading && !fileContent ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p>加载中...</p>
                </div>
              ) : fileContent ? (
                <div>
                  <div className="flex justify-between items-center mb-6 pb-4 border-b">
                    <h2 className="text-xl font-semibold text-gray-800">
                      {selectedFile?.split('/').pop()?.replace('.md', '')}
                    </h2>
                    <button
                      onClick={() => setFileContent(null)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      × 关闭
                    </button>
                  </div>
                  
                  <div className="prose max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code({node, className, children, ...props}) {
                          const match = /language-(\w+)/.exec(className || '')
                          return match ? (
                            <pre className={className}>
                              <code {...props}>{children}</code>
                            </pre>
                          ) : (
                            <code className={className} {...props}>{children}</code>
                          )
                        }
                      }}
                    >
                      {fileContent.content}
                    </ReactMarkdown>
                  </div>
                  
                  <div className="mt-6 pt-6 border-t text-sm text-gray-600">
                    <div>文件大小: {fileContent.size} 字节</div>
                    <div>路径: {fileContent.path}</div>
                  </div>
                </div>
              ) : (
                <div>
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">欢迎来到文章板块</h2>
                  <p className="text-gray-600">
                    这里展示了您的Markdown文章。点击左侧目录浏览和选择文章。
                  </p>
                  
                  {structure && structure.structure.categories.category_list.length > 0 && (
                    <div className="mt-6">
                      <h3 className="text-lg font-medium text-gray-700 mb-3">文章分类</h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {structure.structure.categories.category_list.map((category) => (
                          <div 
                            key={category.name}
                            className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                            onClick={() => handleNavigate(category.name)}
                          >
                            <h4 className="font-medium text-gray-800">{category.name}</h4>
                            <p className="text-sm text-gray-600 mt-1">
                              {category.file_count} 个文件
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
