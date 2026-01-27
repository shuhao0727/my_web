"use client";

import { useEffect } from "react";

/**
 * 预加载关键资源的组件
 * 这个组件在客户端运行，用于预加载非关键资源
 */
export function PreloadResources() {
  useEffect(() => {
    // 预加载非关键资源
    const preloadResources = () => {
      // 预加载可能需要的字体
      const fontLink = document.createElement("link");
      fontLink.rel = "preload";
      fontLink.as = "font";
      fontLink.href = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap";
      fontLink.crossOrigin = "anonymous";
      document.head.appendChild(fontLink);

      // 预加载可能需要的图片（首屏外但重要的图片）
      const importantImages: string[] = [
        // 可以添加重要的图片路径
      ];

      importantImages.forEach((src) => {
        const img = new Image();
        img.src = src;
      });

      // 预加载下一页可能需要的JS模块（如果使用预测导航）
      if (typeof window !== "undefined" && "requestIdleCallback" in window) {
        (window as any).requestIdleCallback(() => {
          // 在空闲时间预加载可能需要的模块
          const modules: string[] = [
            // 可以添加动态导入的模块
          ];
          
          modules.forEach((modulePath) => {
            const link = document.createElement("link");
            link.rel = "modulepreload";
            link.href = modulePath;
            document.head.appendChild(link);
          });
        });
      }
    };

    // 使用requestIdleCallback在空闲时间预加载资源
    if (typeof window !== "undefined" && "requestIdleCallback" in window) {
      (window as any).requestIdleCallback(preloadResources, { timeout: 2000 });
    } else {
      // 如果不支持requestIdleCallback，使用setTimeout延迟执行
      setTimeout(preloadResources, 1000);
    }

    // 监听页面可见性变化，当页面切换到可见时预加载资源
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        preloadResources();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  // 这个组件不渲染任何内容
  return null;
}