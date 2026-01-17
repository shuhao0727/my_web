import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/layout/Header";

export const metadata: Metadata = {
  title: "AI教育平台 - 高中信息技术教学与竞赛",
  description: "面向高中信息技术老师、信息学竞赛教练和AI爱好者的个人网站，集成Dify AI智能体，提供AI智能体实验室、信息学竞赛资源和教学博客。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className="font-sans" suppressHydrationWarning>
        <Header />
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
