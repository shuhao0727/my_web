"""
DeepSeek API客户端
"""
import json
import logging
from typing import Dict, Any, Optional, AsyncGenerator
import httpx
from .api_client import ApiClient
from datetime import datetime

logger = logging.getLogger(__name__)


class DeepSeekClient(ApiClient):
    """DeepSeek API客户端"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL，默认为官方地址
            model: 模型名称，默认为deepseek-chat
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            **kwargs: 传递给父类的其他参数
        """
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 更新请求头
        self.client.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    async def chat_completion(
        self,
        messages: list,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送聊天补全请求
        
        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "你好"}]
            stream: 是否使用流式响应
            temperature: 温度参数，覆盖默认值
            max_tokens: 最大生成token数，覆盖默认值
            **kwargs: 其他API参数
            
        Returns:
            API响应
        """
        endpoint = "/chat/completions"
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
            "stream": stream
        }
        
        # 添加其他参数
        data.update(kwargs)
        
        return await self._make_request("POST", endpoint, data=data)
    
    async def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[list] = None,
        **kwargs
    ) -> str:
        """
        简化的聊天接口
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            conversation_history: 历史对话列表
            **kwargs: 其他参数传递给chat_completion
            
        Returns:
            AI回复文本
        """
        messages = []
        
        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史对话
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.chat_completion(messages, **kwargs)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek聊天失败: {e}")
            raise
    
    async def stream_chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[list] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天接口
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            conversation_history: 历史对话列表
            **kwargs: 其他参数传递给chat_completion
            
        Yields:
            AI回复的文本块
        """
        messages = []
        
        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史对话
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                }
                
                data = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stream": True
                }
                data.update(kwargs)
                
                async with client.stream("POST", url, json=data, headers=headers) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_line = line[6:].strip()
                            if data_line == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_line)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"DeepSeek流式聊天失败: {e}")
            raise
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        测试DeepSeek API连接
        
        Returns:
            连接测试结果
        """
        try:
            # SiliconFlow等第三方API网关的特殊处理
            is_siliconflow = "siliconflow" in self.base_url.lower()
            
            # 首先测试API基础连接（允许非200状态码，因为某些API根路径可能返回404但接口仍可用）
            try:
                response = await self.client.get(self.base_url, timeout=5)
                if response.status_code != 200:
                    if is_siliconflow:
                        logger.info(f"SiliconFlow API端点GET请求返回HTTP {response.status_code}（正常），继续测试")
                    else:
                        logger.info(f"API端点GET请求返回HTTP {response.status_code}，将继续测试POST请求")
            except Exception as e:
                logger.warning(f"API端点GET请求异常（可能正常）: {str(e)}，将继续测试POST请求")
            
            # 测试API密钥有效性 - 发送一个极简的测试消息
            try:
                endpoint = "/chat/completions"
                test_data = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 1
                }
                
                # 使用单独的客户端，避免继承可能错误的headers
                async with httpx.AsyncClient(timeout=10) as client:
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    response = await client.post(
                        f"{self.base_url}{endpoint}",
                        json=test_data,
                        headers=headers
                    )
                    
                    # 分析响应
                    if response.status_code == 401:
                        # 401明确表示API密钥无效
                        return {
                            "success": False,
                            "error": "API密钥无效或已过期",
                            "message": "DeepSeek API密钥验证失败",
                            "status_code": response.status_code
                        }
                    elif response.status_code == 403:
                        # 403表示权限不足
                        return {
                            "success": False,
                            "error": "API密钥权限不足",
                            "message": "DeepSeek API权限验证失败",
                            "status_code": response.status_code
                        }
                    elif response.status_code == 400:
                        # 400错误需要分析具体原因
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('error', {}).get('message', str(error_data))
                            
                            # 如果是模型不存在错误，API密钥可能是有效的
                            if 'model does not exist' in str(error_msg).lower() or 'model not found' in str(error_msg).lower():
                                return {
                                    "success": True if is_siliconflow else False,
                                    "error": f"模型不存在或配置错误: {error_msg}",
                                    "message": "API连接正常但模型配置错误",
                                    "status_code": response.status_code,
                                    "note": "API密钥可能有效，但需要检查模型名称"
                                }
                            else:
                                return {
                                    "success": False,
                                    "error": f"API请求参数错误: {error_msg}",
                                    "message": "DeepSeek API配置错误",
                                    "status_code": response.status_code
                                }
                        except:
                            return {
                                "success": False,
                                "error": "API请求参数错误",
                                "message": "DeepSeek API配置错误",
                                "status_code": response.status_code
                            }
                    elif response.status_code == 404:
                        # 404表示端点不存在
                        return {
                            "success": False,
                            "error": "API端点不存在或路径错误",
                            "message": "DeepSeek API端点配置错误",
                            "status_code": response.status_code
                        }
                    elif response.status_code >= 400 and response.status_code < 500:
                        # 其他4xx错误
                        error_msg = f"HTTP {response.status_code}"
                        try:
                            error_data = response.json()
                            error_msg = f"HTTP {response.status_code}: {str(error_data)}"
                        except:
                            pass
                        
                        # 对于SiliconFlow，某些4xx错误可能只是配置问题而不是连接问题
                        if is_siliconflow and response.status_code in [402, 429]:
                            return {
                                "success": False,
                                "error": f"SiliconFlow API限制: {error_msg}",
                                "message": "API连接正常但受限制",
                                "status_code": response.status_code
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"API客户端错误: {error_msg}",
                                "message": "DeepSeek API连接失败",
                                "status_code": response.status_code
                            }
                    elif response.status_code >= 500:
                        # 5xx服务器错误
                        return {
                            "success": False,
                            "error": f"API服务器错误: HTTP {response.status_code}",
                            "message": "DeepSeek API服务器错误",
                            "status_code": response.status_code
                        }
                    elif response.status_code == 200:
                        # 200成功响应
                        try:
                            result = response.json()
                            if "choices" in result and len(result["choices"]) > 0:
                                return {
                                    "success": True,
                                    "message": "DeepSeek API连接成功且API密钥有效",
                                    "test_response": "API验证通过",
                                    "status_code": response.status_code
                                }
                            else:
                                # 响应格式异常但HTTP 200
                                return {
                                    "success": True,
                                    "message": "DeepSeek API连接成功（响应格式异常）",
                                    "test_response": f"响应格式: {result.keys() if isinstance(result, dict) else 'unknown'}",
                                    "status_code": response.status_code
                                }
                        except Exception as json_error:
                            # JSON解析失败但HTTP 200
                            return {
                                "success": True,
                                "message": "DeepSeek API连接成功（JSON解析失败）",
                                "test_response": f"HTTP {response.status_code} 响应正常",
                                "status_code": response.status_code,
                                "warning": f"JSON解析错误: {str(json_error)}"
                            }
                    else:
                        # 其他状态码
                        return {
                            "success": False,
                            "error": f"未知响应: HTTP {response.status_code}",
                            "message": "DeepSeek API连接异常",
                            "status_code": response.status_code
                        }
                        
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "error": "API请求超时（10秒）",
                    "message": "DeepSeek API连接超时"
                }
            except httpx.ConnectError as e:
                return {
                    "success": False,
                    "error": f"无法连接到API服务器: {str(e)}",
                    "message": "DeepSeek API连接失败"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "DeepSeek API连接测试异常"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "DeepSeek API连接失败"
            }


# 配置示例
DEEPSEEK_CONFIG_EXAMPLE = {
    "api_type": "deepseek",
    "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 30,
    "max_retries": 3
}
