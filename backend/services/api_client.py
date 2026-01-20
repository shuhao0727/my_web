"""
通用API客户端基类
提供HTTP请求、错误处理、重试机制和日志记录功能
"""
import json
import logging
import time
from typing import Dict, Any, Optional, Union
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class ApiClient:
    """通用API客户端基类"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        初始化API客户端
        
        Args:
            api_key: API密钥
            base_url: 基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求，包含重试机制
        
        Args:
            method: HTTP方法（GET, POST, PUT, DELETE）
            endpoint: API端点（不包含基础URL）
            data: 请求体数据
            headers: 额外请求头
            params: 查询参数
            
        Returns:
            API响应数据（字典）
            
        Raises:
            Exception: 请求失败，包括网络错误和API错误
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self.client.headers.copy()
        if headers:
            request_headers.update(headers)
        
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"API请求尝试 {attempt + 1}/{self.max_retries}: {method} {url}")
                
                response = await self.client.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=request_headers,
                    params=params
                )
                
                # 检查HTTP状态码
                response.raise_for_status()
                
                # 解析响应
                result = response.json()
                logger.debug(f"API请求成功: {method} {url}")
                return result
                
            except httpx.HTTPStatusError as e:
                last_exception = e
                status_code = e.response.status_code if e.response else None
                
                # 如果是4xx客户端错误（除了429），不要重试
                if status_code and 400 <= status_code < 500 and status_code != 429:
                    logger.error(f"API客户端错误: {status_code} {e}")
                    raise
                
                logger.warning(f"API请求失败 ({status_code}): {e}, 尝试 {attempt + 1}/{self.max_retries}")
                
            except (httpx.RequestError, json.JSONDecodeError) as e:
                last_exception = e
                logger.warning(f"API请求异常: {e}, 尝试 {attempt + 1}/{self.max_retries}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))  # 指数退避
        
        # 所有重试都失败
        logger.error(f"API请求失败，已达到最大重试次数 {self.max_retries}")
        raise Exception(f"API请求失败: {last_exception}") from last_exception
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        测试API连接
        
        Returns:
            连接测试结果
        """
        try:
            # 发送一个简单的请求来测试连接
            response = await self.client.get(self.base_url)
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "连接成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "连接失败"
            }
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    def __del__(self):
        """析构函数，确保关闭客户端"""
        try:
            import asyncio
            if hasattr(self, 'client') and not self.client.is_closed:
                asyncio.run(self.close())
        except:
            pass


class ApiCallRecorder:
    """API调用记录器"""
    
    @staticmethod
    def record_call(
        api_type: str,
        agent_id: int,
        user_id: int,
        conversation_id: Optional[int],
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        status: str,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        记录API调用详情
        
        Returns:
            API调用记录
        """
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # 估算token使用（简单估算）
        request_text = json.dumps(request_data, ensure_ascii=False)
        response_text = json.dumps(response_data, ensure_ascii=False)
        request_tokens = len(request_text) // 4
        response_tokens = len(response_text) // 4
        
        return {
            "api_type": api_type,
            "agent_id": agent_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "request_timestamp": start_time.isoformat(),
            "response_timestamp": end_time.isoformat(),
            "duration_ms": duration_ms,
            "status": status,
            "error_message": error_message,
            "request_tokens": request_tokens,
            "response_tokens": response_tokens,
            "total_tokens": request_tokens + response_tokens
        }

# 向后兼容：APIClient 是 ApiClient 的别名
APIClient = ApiClient
