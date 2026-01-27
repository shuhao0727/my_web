"""
API响应缓存中间件 - 简化版本
为FastAPI应用提供统一的响应缓存机制
"""
import hashlib
import json
import asyncio
from typing import Any, Callable, Dict, List, Optional
from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from .redis_cache import cache, CachePrefix

logger = logging.getLogger(__name__)


def generate_cache_key(request: Request) -> str:
    """根据请求生成缓存键"""
    key_parts = [request.method, request.url.path]
    
    if request.query_params:
        sorted_params = sorted(request.query_params.items())
        key_parts.append(str(sorted_params))
    
    header_keys = ["accept", "accept-language", "user-agent"]
    headers = []
    for key in header_keys:
        value = request.headers.get(key)
        if value:
            headers.append(f"{key}:{value}")
    
    if headers:
        key_parts.append(str(sorted(headers)))
    
    full_key = ":".join(key_parts)
    cache_key = hashlib.md5(full_key.encode()).hexdigest()
    return f"{CachePrefix.API}:{cache_key}"


class SimpleCacheMiddleware(BaseHTTPMiddleware):
    """简化的缓存中间件"""
    
    def __init__(
        self,
        app: ASGIApp,
        ttl: int = 300,
        excluded_paths: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.ttl = ttl
        self.excluded_paths = excluded_paths or []
        logger.info(f"简易缓存中间件已初始化: ttl={ttl}s")
    
    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        if request.method not in ["GET", "HEAD"]:
            return await call_next(request)
        
        cache_key = generate_cache_key(request)
        cached_response = cache.get(cache_key)
        
        if cached_response is not None:
            logger.debug(f"缓存命中: {request.method} {request.url.path}")
            try:
                cached_data = json.loads(cached_response)
                return Response(
                    content=cached_data["content"],
                    status_code=cached_data["status_code"],
                    headers=cached_data["headers"],
                )
            except Exception as e:
                logger.error(f"解析缓存失败: {e}")
        
        response = await call_next(request)
        
        if 200 <= response.status_code < 300:
            try:
                # 获取响应体
                body = b""
                # 使用更安全的方法获取响应体
                if hasattr(response, 'body') and response.body:
                    body = response.body
                else:
                    # 使用备用方法：通过响应迭代器获取
                    try:
                        # 检查是否有body_iterator属性
                        if hasattr(response, 'body_iterator'):
                            async for chunk in response.body_iterator:  # type: ignore
                                if isinstance(chunk, bytes):
                                    body += chunk
                                else:
                                    body += str(chunk).encode('utf-8')
                        else:
                            # 如果没有body_iterator，则无法缓存
                            return response
                    except Exception as e:
                        logger.warning(f"无法读取响应体: {e}")
                        return response
                
                # 重新创建响应（如果使用了body_iterator）
                if body and not hasattr(response, 'body'):
                    response = Response(
                        content=body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                    )
                
                # 过滤头部
                headers = {}
                for key, value in response.headers.items():
                    if key.lower() not in ["date", "expires", "last-modified", "etag"]:
                        headers[key] = value
                
                # 确保body是字符串类型
                if isinstance(body, bytes):
                    content_str = body.decode('utf-8', errors='ignore')
                else:
                    content_str = str(body)
                
                cache_data = {
                    "content": content_str,
                    "headers": headers,
                    "status_code": response.status_code,
                }
                
                cache.set(cache_key, json.dumps(cache_data), ttl=self.ttl)
                logger.debug(f"缓存设置: {request.method} {request.url.path}")
                
            except Exception as e:
                logger.error(f"设置缓存失败: {e}")
        
        return response


def cache_route(ttl: int = 300):
    """路由缓存装饰器"""
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            key_parts = [func.__module__, func.__name__]
            for param_name, param_value in bound_args.arguments.items():
                key_parts.append(f"{param_name}={param_value}")
            
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            cache_key = f"{CachePrefix.API}:{cache_key}"
            
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            result = await func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl=ttl)
            return result
        
        def sync_wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            key_parts = [func.__module__, func.__name__]
            for param_name, param_value in bound_args.arguments.items():
                key_parts.append(f"{param_name}={param_value}")
            
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            cache_key = f"{CachePrefix.API}:{cache_key}"
            
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl=ttl)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# 默认配置
DEFAULT_EXCLUDED_PATHS = [
    "/admin", "/auth", "/login", "/logout",
    "/api/ai/chat", "/api/ai/stream"
]

def create_cache_middleware(app: ASGIApp, ttl: int = 300) -> SimpleCacheMiddleware:
    """创建缓存中间件的快捷函数"""
    return SimpleCacheMiddleware(
        app=app,
        ttl=ttl,
        excluded_paths=DEFAULT_EXCLUDED_PATHS,
    )