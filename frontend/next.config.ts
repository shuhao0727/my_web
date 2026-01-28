import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 禁用开发指示器
  devIndicators: false,
  // 启用外部目录支持
  experimental: {
    externalDir: true,
  },
  // Turbopack配置 - 解决Next.js 16默认启用Turbopack的问题
  turbopack: {},
  reactStrictMode: false,
  // 重定向配置 - 将旧路由重定向到新路由
  async redirects() {
    return [
      {
        source: '/blog',
        destination: '/articles',
        permanent: true, // 301永久重定向
      },
      {
        source: '/blog/:slug*',
        destination: '/articles/:slug*',
        permanent: true,
      },
    ];
  },
  // 配置API代理 - 优先使用环境变量，开发环境使用localhost
  async rewrites() {
    // 开发环境使用localhost，生产环境使用backend容器地址
    const isProduction = process.env.NODE_ENV === 'production';
    const apiUrl = isProduction 
      ? 'http://backend:8000' 
      : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    console.log('API Proxy URL:', apiUrl, '(Environment:', process.env.NODE_ENV, ')');
    
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
        source: '/api/typst/:path*',
        destination: `${apiUrl}/api/typst/:path*`,
      },
      {
        source: '/api/health',
        destination: `${apiUrl}/health`,
      },
    ];
  },
  // 输出配置 - 适用于独立部署
  output: 'standalone',
  // 图片优化配置
  images: {
    domains: [], // 可添加CDN域名
    formats: ['image/webp', 'image/avif'], // 支持现代图片格式
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840], // 设备尺寸
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384], // 图片尺寸
  },
  // 压缩配置
  compress: true,
  // 生产环境优化
  poweredByHeader: false,
  generateEtags: true,
  // 编译器优化
  compiler: {
    // 移除生产环境的console.log
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
    // 启用styled-components的优化（如果使用）
    styledComponents: true,
  },
  // 跨域配置
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },
  // 构建优化
  webpack: (config, { isServer, dev }) => {
    // 仅在生产环境启用优化
    if (!dev && !isServer) {
      // 启用代码分割优化
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          minSize: 20000,
          maxSize: 70000,
          minChunks: 1,
          maxAsyncRequests: 30,
          maxInitialRequests: 30,
          cacheGroups: {
            defaultVendors: {
              test: /[\\/]node_modules[\\/]/,
              priority: -10,
              reuseExistingChunk: true,
              name: 'vendors',
            },
            default: {
              minChunks: 2,
              priority: -20,
              reuseExistingChunk: true,
            },
            // 单独打包antd
            antd: {
              test: /[\\/]node_modules[\\/]antd[\\/]/,
              name: 'antd',
              priority: 0,
            },
          },
        },
      };
    }
    return config;
  },
};

export default nextConfig;
