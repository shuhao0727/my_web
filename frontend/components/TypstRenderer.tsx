'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Alert, Spin } from 'antd';
import { WarningOutlined, FileTextOutlined, CodeOutlined, LockOutlined } from '@ant-design/icons';

interface TypstRendererProps {
  content: string;
  filePath: string;
  width?: number | string;
  height?: number | string;
}

export default function TypstRenderer({ 
  content, 
  filePath,
  width = '100%',
  height = '100%'
}: TypstRendererProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [renderedSvg, setRenderedSvg] = useState<string>('');
  const [renderFailed, setRenderFailed] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  // 添加样式控制Typst页面渲染
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      .typst-rendered-content .typst-page svg {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 0 auto;
        overflow: hidden;
      }
      .typst-rendered-content .typst-page {
        width: 100%;
        margin-bottom: 20px;
        overflow: hidden;
      }
      .typst-rendered-content {
        width: 100%;
        overflow-x: hidden;
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  useEffect(() => {
    // 检查内容是否有效
    if (!content.trim()) {
      setError('文档内容为空');
      setLoading(false);
      return;
    } else {
      setError(null);
    }

    // 调用渲染API
    renderTypstContent();
  }, [content, filePath]);

  // 渲染Typst内容
  const renderTypstContent = async () => {
    try {
      setLoading(true);
      setRenderFailed(false);
      
      // 调用渲染API，请求SVG格式
      const encodedPath = encodeURIComponent(filePath);
      const apiBase = process.env.NEXT_PUBLIC_API_URL || '/api';
      const response = await fetch(`${apiBase}/typst/render/${encodedPath}?output_format=svg`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // 处理多页SVG内容（数组）或单页SVG（字符串）
          if (Array.isArray(data.content)) {
            // 如果是数组，将所有SVG合并，用分页分隔
            const svgPages = data.content.map((svg: string, index: number) => {
              // 为每个SVG添加页面标记和样式
              const pageNumber = index + 1;
              return `<div class="typst-page" data-page="${pageNumber}">${svg}</div>`;
            }).join('');
            setRenderedSvg(svgPages);
          } else {
            // 如果是字符串，直接使用
            setRenderedSvg(data.content);
          }
          setError(null);
        } else {
          throw new Error('渲染失败');
        }
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('渲染Typst文档失败:', error);
      setRenderFailed(true);
      setError('文档渲染失败，正在显示源代码');
    } finally {
      setLoading(false);
    }
  };

  // 防止复制
  useEffect(() => {
    const handleCopy = (e: ClipboardEvent) => {
      e.preventDefault();
      alert('为了保护作者的知识产权，本文档内容禁止复制。');
    };

    const handleSelectStart = (e: Event) => {
      e.preventDefault();
    };

    const contentElement = contentRef.current;
    if (contentElement) {
      contentElement.addEventListener('copy', handleCopy);
      contentElement.addEventListener('selectstart', handleSelectStart);
    }

    return () => {
      if (contentElement) {
        contentElement.removeEventListener('copy', handleCopy);
        contentElement.removeEventListener('selectstart', handleSelectStart);
      }
    };
  }, []);

  // 格式化Typst内容用于显示（带样式）
  const formatTypstContent = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, index) => {
      let className = 'text-gray-800';
      let formattedLine = line;

      // 语法高亮规则
      if (line.includes('#import') || line.includes('#include')) {
        className = 'text-blue-600 font-semibold';
      } else if (line.includes('#set')) {
        className = 'text-purple-600 font-semibold';
      } else if (line.includes('=') && line.includes(':')) {
        className = 'text-green-700';
      } else if (line.trim().startsWith('//')) {
        className = 'text-gray-500 italic';
      } else if (line.trim().startsWith('/*') || line.includes('*/')) {
        className = 'text-gray-500 italic';
      } else if (line.trim().startsWith('#')) {
        className = 'text-indigo-600 font-medium';
      } else if (line.includes('+') || line.includes('-') || line.includes('*') || line.includes('/')) {
        className = 'text-red-600';
      }

      // 处理特殊字符
      formattedLine = formattedLine
        .replace(/&/g, '&')
        .replace(/</g, '<')
        .replace(/>/g, '>')
        .replace(/"/g, '"')
        .replace(/'/g, '&#039;');

      return `<div class="${className} font-mono text-sm leading-7 pl-4" data-line="${index + 1}">${formattedLine}</div>`;
    }).join('');
  };

  const formattedContent = formatTypstContent(content);

  // 如果内容为空
  if (!content.trim()) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-gray-400">
        <WarningOutlined className="text-4xl mb-4" />
        <div className="text-lg font-medium">文档内容为空</div>
        <div className="text-sm">请选择其他文档</div>
      </div>
    );
  }

  return (
    <div 
      className="relative w-full h-full flex flex-col bg-white" 
      style={{ width, height }}
      ref={contentRef}
    >
      {/* 内容区域 */}
      <div className="flex-grow overflow-auto bg-white">
        {loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-white bg-opacity-90 z-10">
            <Spin size="large" />
            <div className="mt-4 text-gray-600">正在渲染文档...</div>
          </div>
        )}

        {error && (
          <div className="p-8">
            <Alert
              type="warning"
              title="文档预览受限"
              description={
                <div className="mt-2">
                  <div className="mb-4">{error}</div>
                  <div className="text-sm text-gray-600">
                    <p>Typst文档当前以源代码形式显示。完整渲染功能需要后端Typst编译支持。</p>
                  </div>
                </div>
              }
              showIcon
            />
          </div>
        )}

        {/* 渲染的SVG内容 */}
        {!loading && renderedSvg && !renderFailed && (
          <div className="w-full h-full">
            <div 
              className="typst-rendered-content w-full h-full overflow-auto p-4"
              style={{ 
                userSelect: 'none',
                WebkitUserSelect: 'none',
                MozUserSelect: 'none',
                msUserSelect: 'none',
                backgroundColor: 'white',
              }}
              dangerouslySetInnerHTML={{ __html: renderedSvg }}
            />
          </div>
        )}

        {/* 回退：显示源代码 */}
        {!loading && renderFailed && (
          <div className="w-full h-full p-6 overflow-auto">
            <div 
              className="font-mono text-sm leading-7 bg-white"
              style={{ 
                userSelect: 'none',
                WebkitUserSelect: 'none',
                MozUserSelect: 'none',
                msUserSelect: 'none'
              }}
              dangerouslySetInnerHTML={{ __html: formattedContent }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

// 辅助组件：用于显示Typst内容的简单预览
export function TypstFallback({ content }: { content: string }) {
  return (
    <div className="p-4 whitespace-pre-wrap font-mono text-sm bg-gray-50 rounded overflow-auto max-h-[70vh]">
      {content}
    </div>
  );
}
