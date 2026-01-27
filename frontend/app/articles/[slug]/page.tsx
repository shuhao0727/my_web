"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface ArticleContent {
  slug: string;
  title: string;
  date: string;
  content: string;
  toc: Array<{
    level: number;
    title: string;
    anchor: string;
  }>;
  raw_content: string;
  file_name: string;
}

export default function ArticleDetailPage() {
  const params = useParams();
  const slug = params.slug as string;

  const [article, setArticle] = useState<ArticleContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeAnchor, setActiveAnchor] = useState<string | null>(null);

  // 获取文章内容
  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/articles/content/${slug}`
        );
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("文章不存在");
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setArticle(data);
      } catch (err) {
        console.error("获取文章内容失败:", err);
        setError(err instanceof Error ? err.message : "未知错误");
      } finally {
        setLoading(false);
      }
    };

    if (slug) {
      fetchArticle();
    }
  }, [slug]);

  // 监听滚动，高亮当前目录项
  useEffect(() => {
    const handleScroll = () => {
      if (!article?.toc || article.toc.length === 0) return;

      const headings = article.toc.map((item) => ({
        id: item.anchor,
        element: document.getElementById(item.anchor),
      }));

      // 找到当前可见的标题
      let currentAnchor = null;
      for (const heading of headings) {
        const rect = heading.element?.getBoundingClientRect();
        if (rect && rect.top >= 0 && rect.top <= window.innerHeight * 0.3) {
          currentAnchor = heading.id;
          break;
        }
      }

      // 如果没有找到，则选择最后一个在视口上方的标题
      if (!currentAnchor) {
        for (let i = headings.length - 1; i >= 0; i--) {
          const rect = headings[i].element?.getBoundingClientRect();
          if (rect && rect.top < 0) {
            currentAnchor = headings[i].id;
            break;
          }
        }
      }

      setActiveAnchor(currentAnchor);
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll(); // 初始调用

    return () => window.removeEventListener("scroll", handleScroll);
  }, [article]);

  const scrollToAnchor = (anchor: string) => {
    const element = document.getElementById(anchor);
    if (element) {
      const offset = 100; // 考虑固定header的偏移
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">正在加载文章...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-red-800 text-lg font-semibold">加载失败</h2>
            <p className="text-red-600 mt-2">
              {error || "文章不存在或加载失败"}
            </p>
            <Link
              href="/articles"
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              返回文章列表
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* 头部 */}
      <header className="border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <Link
                href="/articles"
                className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-2"
              >
                <svg
                  className="h-5 w-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                  />
                </svg>
                返回文章列表
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">
                {article.title}
              </h1>
              <div className="mt-2 flex items-center text-sm text-gray-500">
                <svg
                  className="h-4 w-4 mr-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <time dateTime={article.date}>{article.date}</time>
                <span className="mx-2">•</span>
                <span>文件: {article.file_name}</span>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                文章详情
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* 主体内容 - 三栏布局 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* 左侧栏：文章目录 */}
          <aside className="lg:w-1/4">
            <div className="sticky top-8">
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  文章目录
                </h3>
                {article.toc.length > 0 ? (
                  <nav className="space-y-2">
                    {article.toc.map((item) => (
                      <button
                        key={item.anchor}
                        onClick={() => scrollToAnchor(item.anchor)}
                        className={`block w-full text-left text-sm rounded-md px-3 py-2 transition-colors ${
                          activeAnchor === item.anchor
                            ? "bg-blue-50 text-blue-700 border-l-4 border-blue-600"
                            : "text-gray-600 hover:text-blue-600 hover:bg-gray-50"
                        }`}
                        style={{
                          paddingLeft: `${(item.level - 1) * 1 + 0.75}rem`,
                        }}
                      >
                        {item.title}
                      </button>
                    ))}
                  </nav>
                ) : (
                  <p className="text-sm text-gray-500">
                    本文没有可用的目录结构。
                  </p>
                )}

                <div className="mt-8 pt-6 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-900 mb-3">
                    文章信息
                  </h4>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex justify-between">
                      <span>文件路径:</span>
                      <code className="bg-gray-100 px-2 py-1 rounded text-xs">
                        /wz/{article.file_name}
                      </code>
                    </li>
                    <li className="flex justify-between">
                      <span>更新时间:</span>
                      <span>{article.date}</span>
                    </li>
                    <li className="flex justify-between">
                      <span>文章标识:</span>
                      <span className="font-mono">{article.slug}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </aside>

          {/* 中间栏：文章内容 */}
          <article className="lg:w-2/4">
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8">
              {/* 文章内容 */}
              <div
                className="prose prose-lg max-w-none"
                dangerouslySetInnerHTML={{ __html: article.content }}
              />

              {/* 文章底部信息 */}
              <div className="mt-12 pt-8 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">
                      本文以 Markdown 格式存储，支持自动解析和格式渲染。
                    </p>
                  </div>
                  <Link
                    href="/articles"
                    className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    返回列表
                  </Link>
                </div>
              </div>
            </div>
          </article>

          {/* 右侧栏：相关信息和操作 */}
          <aside className="lg:w-1/4">
            <div className="sticky top-8 space-y-6">
              {/* 操作面板 */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  操作
                </h3>
                <div className="space-y-3">
                  <button
                    onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                    className="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <svg
                      className="h-5 w-5 mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 10l7-7m0 0l7 7m-7-7v18"
                      />
                    </svg>
                    回到顶部
                  </button>
                  <button
                    onClick={() => window.print()}
                    className="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <svg
                      className="h-5 w-5 mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
                      />
                    </svg>
                    打印文章
                  </button>
                </div>
              </div>

              {/* 技术说明 */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                <h3 className="text-lg font-medium text-blue-900 mb-3">
                  技术说明
                </h3>
                <ul className="space-y-2 text-sm text-blue-700">
                  <li className="flex items-start">
                    <svg
                      className="h-5 w-5 mr-2 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    文章支持代码高亮、数学公式、表格等丰富格式
                  </li>
                  <li className="flex items-start">
                    <svg
                      className="h-5 w-5 mr-2 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    目录自动生成，支持点击跳转和滚动高亮
                  </li>
                  <li className="flex items-start">
                    <svg
                      className="h-5 w-5 mr-2 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    文章存储在服务器文件系统，便于维护和更新
                  </li>
                </ul>
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <p className="text-xs text-blue-600">
                    更新文章只需在服务器上修改 Markdown 文件即可，无需重启服务。
                  </p>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}