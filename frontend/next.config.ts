import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 禁用开发指示器
  devIndicators: false,
  // 启用外部目录支持
  experimental: {
    externalDir: true,
  },
  reactStrictMode: false,
  // 配置API代理 - 使用环境变量
  async rewrites() {
    // 从环境变量获取API地址，默认为容器内部的backend服务
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000';
    
    return [
      {
        source: '/api/xbk/:path*',
        destination: `${apiUrl}/api/xbk/:path*`,
      },
      {
        source: '/api/ai/:path*',
        destination: `${apiUrl}/api/ai/:path*`,
      },
    ];
  },
  // 输出配置 - 适用于独立部署
  output: 'standalone',
};

export default nextConfig;
