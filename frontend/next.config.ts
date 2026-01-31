import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 禁用开发指示器
  devIndicators: false,
  // 仅启用必要的实验性功能
  experimental: {
    externalDir: true,
  },
  reactStrictMode: false,
  // 配置API代理 - 使用环境变量
  // 输出配置 - 适用于独立部署
  output: 'standalone',
};

export default nextConfig;
