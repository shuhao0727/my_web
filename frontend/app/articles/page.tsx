"use client";

import { useState, useEffect, useMemo, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";

interface Article {
  slug: string;
  title: string;
  date: string;
  description: string;
  file_name: string;
}

interface ArticleDetail extends Article {
  content: string;
}

interface TableOfContentsItem {
  id: string;
  text: string;
  level: number;
}

function ArticlesPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const slug = searchParams.get("slug");

  const [articles, setArticles] = useState<Article[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredArticles, setFilteredArticles] = useState<Article[]>([]);
  const [currentArticle, setCurrentArticle] = useState<ArticleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingArticle, setLoadingArticle] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 获取文章列表
  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/articles/list");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setArticles(data);
        setFilteredArticles(data);
        
        // 如果没有指定slug且有文章，默认选择第一篇文章
        if (!slug && data.length > 0) {
          const params = new URLSearchParams(searchParams.toString());
          params.set("slug", data[0].slug);
          router.push(`/articles?${params.toString()}`, { scroll: false });
        }
      } catch (err) {
        console.error("获取文章列表失败:", err);
        setError("无法加载文章列表，请检查后端服务是否运行");
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  // 根据slug获取文章详情
  useEffect(() => {
    const fetchArticleDetail = async () => {
      if (!slug) {
        setCurrentArticle(null);
        return;
      }

      setLoadingArticle(true);
      try {
        const response = await fetch(`http://localhost:8000/api/articles/content/${slug}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // 使用raw_content（原始markdown）作为内容，如果没有则使用content字段
        setCurrentArticle({
          ...data,
          content: data.raw_content || data.content || ""
        });
      } catch (err) {
        console.error("获取文章详情失败:", err);
        setCurrentArticle(null);
      } finally {
        setLoadingArticle(false);
      }
    };

    fetchArticleDetail();
  }, [slug]);

  // 搜索文章
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredArticles(articles);
      return;
    }

    const searchLower = searchQuery.toLowerCase();
    const filtered = articles.filter(
      (article) =>
        article.title.toLowerCase().includes(searchLower) ||
        article.description.toLowerCase().includes(searchLower)
    );
    setFilteredArticles(filtered);
  }, [searchQuery, articles]);

  // 生成文章目录
  const tableOfContents = useMemo(() => {
    if (!currentArticle?.content) return [];

    const toc: TableOfContentsItem[] = [];
    const lines = currentArticle.content.split("\n");
    const idCount: Record<string, number> = {};
    
    lines.forEach((line) => {
      const headingMatch = line.match(/^(#{1,3})\s+(.+)$/);
      if (headingMatch && headingMatch[1] && headingMatch[2]) {
        const level = headingMatch[1].length;
        const text = headingMatch[2].trim();
        
        // 如果文本为空，跳过这个标题
        if (!text || text === "") {
          return;
        }
        
        // 生成ID：移除特殊字符，用连字符替换空格
        let id = text
          .toLowerCase()
          .replace(/[^\w\s-]/g, "")
          .replace(/\s+/g, "-")
          .replace(/-+/g, "-")
          .replace(/^-+|-+$/g, ""); // 移除开头和结尾的连字符
        
        // 处理空ID的情况
        if (!id || id === "") {
          id = `heading-${toc.length + 1}`;
        }
        
        // 确保ID以字母开头（避免无效的DOM ID）
        if (/^\d/.test(id)) {
          id = `section-${id}`;
        }
        
        // 确保ID不以连字符开头
        if (/^-/.test(id)) {
          id = `section${id}`;
        }
        
        // 检查ID是否已存在，如果存在则添加唯一后缀
        const originalId = id;
        let counter = 1;
        while (idCount[id] !== undefined) {
          counter++;
          id = `${originalId}-${counter}`;
        }
        
        idCount[id] = 1;
        toc.push({ id, text, level });
      }
    });

    return toc;
  }, [currentArticle]);

  // 点击文章列表项
  const handleArticleClick = (articleSlug: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("slug", articleSlug);
    router.push(`/articles?${params.toString()}`, { scroll: false });
  };

  // 点击目录项
  const handleTocClick = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">正在加载文章列表...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md">
          <div className="text-red-500 text-center">
            <svg className="w-16 h-16 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <h2 className="text-xl font-bold mb-2">加载失败</h2>
            <p className="text-gray-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* 左侧文章列表 */}
      <div className="w-80 border-r border-gray-200 bg-white flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-800">文章专栏</h2>
            <p className="text-sm text-gray-500 mt-1">共 {articles.length} 篇文章</p>
          </div>
          
          <div className="relative">
            <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="搜索文章..."
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {filteredArticles.length === 0 ? (
            <div className="p-6 text-center">
              <p className="text-gray-500">没有找到相关文章</p>
            </div>
          ) : (
            <div className="p-2">
              {filteredArticles.map((article) => (
                <div
                  key={article.slug}
                  className={`p-4 rounded-lg cursor-pointer transition-all duration-200 mb-2 ${
                    slug === article.slug
                      ? "bg-blue-50 border border-blue-200"
                      : "hover:bg-gray-50"
                  }`}
                  onClick={() => handleArticleClick(article.slug)}
                >
                  <div className="flex items-start">
                    <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${
                      slug === article.slug ? "bg-blue-500" : "bg-gray-300"
                    }`} />
                    <div className="ml-3 flex-1">
                      <h3 className="font-medium text-gray-900 line-clamp-2">{article.title}</h3>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">{article.description}</p>
                      <div className="flex items-center mt-2 text-xs text-gray-400">
                        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span>{article.date}</span>
                      </div>
                    </div>
                    {slug === article.slug && (
                      <svg className="flex-shrink-0 text-blue-500 ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 中间文章内容 */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-8">
          {loadingArticle ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-2"></div>
              <p className="text-gray-600">正在加载文章...</p>
            </div>
          ) : currentArticle ? (
            <article className="prose prose-lg max-w-none">
              <header className="mb-8 pb-6 border-b border-gray-200">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">{currentArticle.title}</h1>
                <div className="flex items-center text-gray-500">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <time dateTime={currentArticle.date}>{currentArticle.date}</time>
                </div>
              </header>

              <div className="markdown-body">
                <ReactMarkdown
                  components={{
                    h1: ({ node, ...props }) => {
                      const text = props.children?.toString() || "heading-1";
                      const id = text.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "") || "heading-1";
                      return <h1 id={id} {...props} />;
                    },
                    h2: ({ node, ...props }) => {
                      const text = props.children?.toString() || "heading-2";
                      const id = text.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "") || "heading-2";
                      return <h2 id={id} {...props} />;
                    },
                    h3: ({ node, ...props }) => {
                      const text = props.children?.toString() || "heading-3";
                      const id = text.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "") || "heading-3";
                      return <h3 id={id} {...props} />;
                    },
                    code({ node, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || "");
                      return match ? (
                        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                          <code className={className} {...props}>
                            {children}
                          </code>
                        </pre>
                      ) : (
                        <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded" {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {currentArticle.content}
                </ReactMarkdown>
              </div>
            </article>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <svg className="text-6xl text-gray-300 mb-4 w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-xl font-medium text-gray-700 mb-2">选择一篇文章开始阅读</h3>
              <p className="text-gray-500">从左侧列表中选择一篇文章，内容将显示在这里</p>
            </div>
          )}
        </div>
      </div>

      {/* 右侧文章目录 */}
      <div className="w-64 border-l border-gray-200 bg-white">
        <div className="p-6 border-b border-gray-200">
          <h3 className="font-semibold text-gray-800">文章目录</h3>
        </div>
        
        <div className="p-4">
          {tableOfContents.length > 0 ? (
            <nav className="space-y-1">
              {tableOfContents.map((item) => (
                <button
                  key={item.id}
                  className={`block w-full text-left px-3 py-2 rounded-md transition-colors ${
                    item.level === 1
                      ? "text-sm font-medium text-gray-900 hover:bg-gray-100"
                      : item.level === 2
                      ? "text-sm text-gray-700 hover:bg-gray-100 pl-6"
                      : "text-xs text-gray-500 hover:bg-gray-100 pl-10"
                  }`}
                  onClick={() => handleTocClick(item.id)}
                >
                  {item.text}
                </button>
              ))}
            </nav>
          ) : (
            <p className="text-sm text-gray-500 text-center p-4">
              {currentArticle ? "本文暂无目录结构" : "选择一篇文章后显示目录"}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ArticlesPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">正在加载文章列表...</p>
        </div>
      </div>
    }>
      <ArticlesPageContent />
    </Suspense>
  );
}