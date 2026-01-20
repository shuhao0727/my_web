import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 禁用开发指示器
  devIndicators: false,
  // 启用外部目录支持
  experimental: {
    externalDir: true,
  },
  reactStrictMode: false,
};

export default nextConfig;
