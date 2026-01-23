"""
Dify API客户端
"""
import json
import logging
from typing import Dict, Any, Optional, AsyncGenerator
import httpx
from .api_client import ApiClient, ApiCallRecorder
from datetime import datetime

logger = logging.getLogger(__name__)


class DifyClient(ApiClient):
    """Dify API客户端"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://wangsh.cn:6606/v1",
        app_id: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        初始化Dify客户端
        
        Args:
            api_key: Dify API密钥
            base_url: API基础URL，默认为用户提供的地址
            app_id: 应用ID（可选，通常包含在api_key中）
            timeout: 请求超时时间
            **kwargs: 传递给父类的其他参数
        """
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout, **kwargs)
        
        # Dify API使用特殊的认证头
        self.client.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
        # 如果提供了app_id，更新api_key（有些Dify版本需要app_id）
        self.app_id = app_id
    
    async def chat_messages(
        self,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        response_mode: str = "blocking",
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送聊天消息到Dify
        
        Args:
            query: 用户查询
            user: 用户标识
            conversation_id: 对话ID（可选，必须是有效的UUID格式）
            inputs: 输入参数（可选，默认为空字典）
            response_mode: 响应模式（blocking, streaming）
            **kwargs: 其他API参数
            
        Returns:
            API响应
        """
        endpoint = "/chat-messages"
        
        data = {
            "query": query,
            "user": user,
            "response_mode": response_mode,
            "inputs": inputs if inputs is not None else {}  # 确保inputs字段始终存在
        }
        
        if conversation_id:
            data["conversation_id"] = conversation_id
        
        # 添加其他参数
        data.update(kwargs)
        
        return await self._make_request("POST", endpoint, data=data)
    
    async def chat(
        self,
        user_message: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        简化的聊天接口
        
        Args:
            user_message: 用户消息
            user_id: 用户ID
            conversation_id: 对话ID（可选，必须是有效的UUID格式）
            **kwargs: 其他参数传递给chat_messages
            
        Returns:
            AI回复文本
        """
        try:
            # 确保传入inputs参数，如果kwargs中没有则使用空字典
            if 'inputs' not in kwargs:
                kwargs['inputs'] = {}
                
            response = await self.chat_messages(
                query=user_message,
                user=user_id,
                conversation_id=conversation_id,
                **kwargs
            )
            
            # 解析Dify响应
            if response.get("answer"):
                return response["answer"]
            elif response.get("message"):
                return response["message"]
            else:
                # 尝试其他可能的字段
                return str(response)
                
        except Exception as e:
            logger.error(f"Dify聊天失败: {e}")
            raise
    
    async def stream_chat(
        self,
        user_message: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天接口
        
        Args:
            user_message: 用户消息
            user_id: 用户ID
            conversation_id: 对话ID（可选，必须是有效的UUID格式）
            **kwargs: 其他参数传递给chat_messages
            
        Yields:
            AI回复的文本块
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/chat-messages"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                }
                
                data = {
                    "query": user_message,
                    "user": user_id,
                    "response_mode": "streaming",
                    "inputs": kwargs.get('inputs', {})  # 确保包含inputs字段
                }
                
                if conversation_id:
                    data["conversation_id"] = conversation_id
                
                # 移除已经处理的inputs，避免重复
                kwargs_without_inputs = {k: v for k, v in kwargs.items() if k != 'inputs'}
                data.update(kwargs_without_inputs)
                
                async with client.stream("POST", url, json=data, headers=headers) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_line = line[6:].strip()
                            if data_line == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_line)
                                if "answer" in chunk:
                                    yield chunk["answer"]
                                elif "message" in chunk:
                                    yield chunk["message"]
                                elif "content" in chunk:
                                    yield chunk["content"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Dify流式聊天失败: {e}")
            raise
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        测试Dify API连接
        
        Returns:
            连接测试结果
        """
        try:
            # 首先测试API基础连接
            try:
                response = await self.client.get(self.base_url)
                if response.status_code != 200:
                    # Dify API可能返回其他状态码，但端点可访问
                    if response.status_code >= 400 and response.status_code < 500:
                        return {
                            "success": False,
                            "error": f"API端点不可达或配置错误: HTTP {response.status_code}",
                            "message": "Dify API连接失败"
                        }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"无法连接到API端点: {str(e)}",
                    "message": "Dify API连接失败"
                }
            
            # 然后测试API密钥有效性 - 发送一个极简的测试消息
            try:
                endpoint = "/chat-messages"
                test_data = {
                    "query": "Hello",
                    "user": "test_user",
                    "response_mode": "blocking",
                    "inputs": {}
                }
                
                response = await self.client.post(
                    f"{self.base_url}{endpoint}",
                    json=test_data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                
                # 分析响应
                if response.status_code == 401:
                    return {
                        "success": False,
                        "error": "API密钥无效或已过期",
                        "message": "Dify API密钥验证失败"
                    }
                elif response.status_code == 403:
                    return {
                        "success": False,
                        "error": "API密钥权限不足",
                        "message": "Dify API权限验证失败"
                    }
                elif response.status_code == 404:
                    return {
                        "success": False,
                        "error": "应用不存在或API端点错误",
                        "message": "Dify API配置错误"
                    }
                elif response.status_code >= 400 and response.status_code < 500:
                    # 尝试解析错误信息
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', error_data.get('error', f"HTTP {response.status_code}"))
                        return {
                            "success": False,
                            "error": f"Dify API客户端错误: {error_msg}",
                            "message": "Dify API连接失败"
                        }
                    except:
                        return {
                            "success": False,
                            "error": f"API客户端错误: HTTP {response.status_code}",
                            "message": "Dify API连接失败"
                        }
                elif response.status_code >= 500:
                    return {
                        "success": False,
                        "error": f"API服务器错误: HTTP {response.status_code}",
                        "message": "Dify API服务器错误"
                    }
                elif response.status_code == 200:
                    try:
                        result = response.json()
                        # Dify返回的数据结构检查
                        if "answer" in result or "message" in result:
                            return {
                                "success": True,
                                "message": "Dify API连接成功且API密钥有效",
                                "test_response": "API验证通过"
                            }
                        else:
                            return {
                                "success": True,
                                "message": "Dify API连接成功",
                                "test_response": f"HTTP {response.status_code} 响应正常"
                            }
                    except:
                        return {
                            "success": True,
                            "message": "Dify API连接成功",
                            "test_response": f"HTTP {response.status_code} 响应正常"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"未知响应: HTTP {response.status_code}",
                        "message": "Dify API连接异常"
                    }
                    
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "error": "API请求超时",
                    "message": "Dify API连接超时"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Dify API连接测试异常"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Dify API连接失败"
            }


# 配置示例
DIFY_CONFIG_EXAMPLE = {
    "api_type": "dify",
    "api_key": "app-QefYe18fzOhwjGh70uFWl2sP",
    "base_url": "http://wangsh.cn:6606/v1",
    "app_id": "QefYe18fzOhwjGh70uFWl2sP",
    "timeout": 30,
    "max_retries": 3
}
