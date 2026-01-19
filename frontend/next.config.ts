import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: {
    // 禁用开发指示器中的网络地址
    appIsrStatus: false,
  },
  // 禁用网络地址
  experimental: {
    externalDir: true,
  },
  reactStrictMode: false,
};

export default nextConfig;
