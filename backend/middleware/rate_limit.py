"""
API速率限制中间件
基于内存存储，适用于单实例部署
"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """API速率限制中间件"""
    
    def __init__(self, app, requests_per_minute: int = 60, 
                 burst_capacity: int = 10, 
                 exempt_paths: list[str] | None = None):
        """
        初始化速率限制中间件
        
        Args:
            app: FastAPI应用
            requests_per_minute: 每分钟请求数限制
            burst_capacity: 突发请求容量（令牌桶容量）
            exempt_paths: 免限制路径列表
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_capacity = burst_capacity
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json", "/"]
        
        # 令牌桶算法：每个IP的令牌桶
        self.token_buckets = defaultdict(lambda: {
            'tokens': burst_capacity,
            'last_refill': time.time()
        })
        
        # 令牌补充速率（每秒补充的令牌数）
        self.refill_rate = requests_per_minute / 60.0
    
    async def dispatch(self, request: Request, call_next):
        # 检查是否在免限制路径中
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await call_next(request)
        
        # 获取客户端IP（支持代理头）
        client_ip = self._get_client_ip(request)
        
        # 检查速率限制
        if not self._allow_request(client_ip):
            logger.warning(f"速率限制触发: IP={client_ip}, Path={path}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "请求过于频繁",
                    "message": f"请稍后再试，每分钟限制{self.requests_per_minute}次请求",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # 继续处理请求
        response = await call_next(request)
        
        # 添加速率限制头
        remaining, reset_time = self._get_rate_limit_info(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP"""
        # 优先从X-Forwarded-For获取（如果经过代理）
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个IP
            return forwarded_for.split(",")[0].strip()
        
        # 从X-Real-IP获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 默认使用客户端地址
        client_host = request.client.host if request.client else "unknown"
        return client_host
    
    def _allow_request(self, client_ip: str) -> bool:
        """检查是否允许请求（令牌桶算法）"""
        now = time.time()
        bucket = self.token_buckets[client_ip]
        
        # 计算应该补充的令牌数
        time_passed = now - bucket['last_refill']
        tokens_to_add = time_passed * self.refill_rate
        
        # 更新令牌数（不超过容量）
        bucket['tokens'] = min(
            self.burst_capacity,
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_refill'] = now
        
        # 检查是否有足够的令牌
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        else:
            return False
    
    def _get_rate_limit_info(self, client_ip: str) -> tuple:
        """获取速率限制信息（剩余令牌数，重置时间）"""
        bucket = self.token_buckets[client_ip]
        remaining_tokens = int(bucket['tokens'])
        
        # 计算重置时间（令牌补充到1个所需的时间）
        if remaining_tokens < 1:
            tokens_needed = 1 - bucket['tokens']
            reset_in_seconds = int(tokens_needed / self.refill_rate)
        else:
            reset_in_seconds = 0
        
        return remaining_tokens, reset_in_seconds