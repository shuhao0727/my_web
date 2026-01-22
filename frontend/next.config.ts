import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 禁用开发指示器
  devIndicators: false,
  // 启用外部目录支持
  experimental: {
    externalDir: true,
  },
  reactStrictMode: false,
  // 配置API代理
  async rewrites() {
    return [
      {
        source: '/api/xbk/:path*',
        destination: 'http://localhost:8000/api/xbk/:path*',
      },
      {
        source: '/api/ai/:path*',
        destination: 'http://localhost:8000/api/ai/:path*',
      },
    ];
  },
};

export default nextConfig;
