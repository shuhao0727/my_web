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
            # 发送一个简单的测试消息
            test_response = await self.chat("你好")
            return {
                "success": True,
                "message": "DeepSeek API连接成功",
                "test_response": test_response[:100] + "..." if len(test_response) > 100 else test_response
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
