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
    // 优先使用内部API地址（用于容器间通信），如果未定义则使用外部地址
    const apiUrl = process.env.NEXT_PUBLIC_API_URL_INTERNAL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    return [
      {
        source: '/api/xbk/:path*',
        destination: `${apiUrl}/api/xbk/:path*`,
      },
      {
        source: '/api/ai/:path*',
        destination: `${apiUrl}/api/ai/:path*`,
      },
      {
        source: '/api/repo/:path*',
        destination: `${apiUrl}/api/repo/:path*`,
      },
      {
        source: '/api/health',
        destination: `${apiUrl}/health`,
      },
    ];
  },
  // 输出配置 - 适用于独立部署
  output: 'standalone',
};

export default nextConfig;
