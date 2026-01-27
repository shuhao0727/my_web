"use client";

import { useState, useEffect, useRef, ImgHTMLAttributes } from "react";

interface LazyImageProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src'> {
  src: string;
  placeholderSrc?: string;
  threshold?: number;
  rootMargin?: string;
  onLoad?: () => void;
  onError?: () => void;
}

/**
 * 图片懒加载组件
 * 使用Intersection Observer API实现图片懒加载，提高页面加载性能
 */
export function LazyImage({
  src,
  placeholderSrc = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23f0f0f0'/%3E%3C/svg%3E",
  threshold = 0.1,
  rootMargin = "50px",
  onLoad,
  onError,
  alt = "",
  className = "",
  ...props
}: LazyImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    // 如果图片已经在视口中，直接加载
    if (!imgRef.current) return;

    // 创建Intersection Observer
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            // 图片进入视口后，可以取消观察
            if (imgRef.current && observerRef.current) {
              observerRef.current.unobserve(imgRef.current);
            }
          }
        });
      },
      {
        threshold,
        rootMargin,
      }
    );

    observerRef.current = observer;
    observer.observe(imgRef.current);

    return () => {
      if (observerRef.current && imgRef.current) {
        observerRef.current.unobserve(imgRef.current);
      }
    };
  }, [threshold, rootMargin]);

  // 当图片进入视口时开始加载
  useEffect(() => {
    if (isInView && !isLoaded) {
      const img = new Image();
      img.src = src;
      img.onload = () => {
        setIsLoaded(true);
        if (onLoad) onLoad();
      };
      img.onerror = () => {
        if (onError) onError();
      };
    }
  }, [isInView, isLoaded, src, onLoad, onError]);

  // 组合类名，添加过渡效果
  const combinedClassName = `lazy-image ${className} ${isLoaded ? 'loaded' : 'loading'}`.trim();

  return (
    <div className="lazy-image-container" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* 占位符 */}
      {!isLoaded && (
        <img
          ref={imgRef}
          src={placeholderSrc}
          alt={alt}
          className={combinedClassName}
          style={{ width: '100%', height: 'auto' }}
          {...props}
        />
      )}
      {/* 实际图片 */}
      {isLoaded && (
        <img
          ref={imgRef}
          src={src}
          alt={alt}
          className={combinedClassName}
          style={{
            width: '100%',
            height: 'auto',
            opacity: isLoaded ? 1 : 0,
            transition: 'opacity 0.3s ease-in-out',
          }}
          onLoad={() => setIsLoaded(true)}
          {...props}
        />
      )}
      {/* 加载样式 */}
      <style jsx>{`
        .lazy-image.loading {
          filter: blur(5px);
          transition: filter 0.3s ease-in-out;
        }
        .lazy-image.loaded {
          filter: blur(0);
        }
        .lazy-image-container {
          background-color: #f0f0f0;
        }
      `}</style>
    </div>
  );
}