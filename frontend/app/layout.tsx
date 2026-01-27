import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/layout/Header";
import { PreloadResources } from "@/components/performance/PreloadResources";

export const metadata: Metadata = {
  title: "AI教育平台 - 高中信息技术教学与竞赛",
  description: "面向高中信息技术老师、信息学竞赛教练和AI爱好者的个人网站，集成Dify AI智能体，提供AI智能体、信息学竞赛资源和教学博客。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning translate="no" className="notranslate">
      <head>
        {/* 预加载关键资源 */}
        <link
          rel="preload"
          href="/_next/static/css/app/layout.css"
          as="style"
          crossOrigin="anonymous"
        />
        {/* 预连接关键域名 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        {/* DNS预取外部域名 */}
        <link rel="dns-prefetch" href="//cdn.example.com" />
        {/* 关键CSS内联（如果需要） */}
        <style>
          {`
            /* 关键CSS - 首屏内容样式 */
            .critical-css {
              opacity: 0;
              transition: opacity 0.3s ease-in;
            }
            .critical-css.loaded {
              opacity: 1;
            }
          `}
        </style>
      </head>
      <body className="font-sans bg-gray-50 critical-css" suppressHydrationWarning translate="no">
        <PreloadResources />
        <Header />
        <main className="min-h-screen">
          {children}
        </main>
        {/* 加载完成后移除loading类 */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              document.addEventListener('DOMContentLoaded', function() {
                document.body.classList.add('loaded');
              });
            `,
          }}
        />
      </body>
    </html>
  );
}
