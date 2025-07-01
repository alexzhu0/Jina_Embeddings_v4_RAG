#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
硅基流动API客户端
负责与LLM模型交互
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """API响应数据结构"""
    success: bool
    content: str
    usage: Optional[Dict] = None
    error: Optional[str] = None
    response_time: Optional[float] = None

class SiliconFlowClient:
    """硅基流动API客户端"""
    
    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-ai/DeepSeek-R1"):
        """
        初始化API客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })
        
        logger.info(f"🚀 初始化硅基流动API客户端")
        logger.info(f"🔗 Base URL: {base_url}")
        logger.info(f"🤖 模型: {model}")
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       temperature: float = 0.3, 
                       max_tokens: int = 8192,
                       timeout: int = 180) -> APIResponse:
        """
        调用聊天完成API
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            timeout: 请求超时时间
            
        Returns:
            APIResponse: API响应结果
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        start_time = time.time()
        
        try:
            logger.debug(f"📤 发送请求到: {url}")
            logger.debug(f"📝 消息数量: {len(messages)}")
            
            response = self.session.post(
                url, 
                json=payload, 
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            
            # 检查HTTP状态码
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ API请求失败: {error_msg}")
                return APIResponse(
                    success=False,
                    content="",
                    error=error_msg,
                    response_time=response_time
                )
            
            # 解析响应
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                logger.info(f"✅ API调用成功 ({response_time:.2f}s)")
                logger.debug(f"📊 Token使用: {usage}")
                
                return APIResponse(
                    success=True,
                    content=content,
                    usage=usage,
                    response_time=response_time
                )
            else:
                error_msg = "响应格式异常: 缺少choices字段"
                logger.error(f"❌ {error_msg}")
                return APIResponse(
                    success=False,
                    content="",
                    error=error_msg,
                    response_time=response_time
                )
                
        except requests.exceptions.Timeout:
            error_msg = f"请求超时 ({timeout}s)"
            logger.error(f"⏰ {error_msg}")
            return APIResponse(
                success=False,
                content="",
                error=error_msg,
                response_time=time.time() - start_time
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求异常: {str(e)}"
            logger.error(f"🌐 {error_msg}")
            return APIResponse(
                success=False,
                content="",
                error=error_msg,
                response_time=time.time() - start_time
            )
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败: {str(e)}"
            logger.error(f"📄 {error_msg}")
            return APIResponse(
                success=False,
                content="",
                error=error_msg,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.error(f"❓ {error_msg}")
            return APIResponse(
                success=False,
                content="",
                error=error_msg,
                response_time=time.time() - start_time
            )
    
    def simple_chat(self, user_message: str, 
                   system_message: str = None,
                   **kwargs) -> APIResponse:
        """
        简化的聊天接口
        
        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            **kwargs: 其他参数
            
        Returns:
            APIResponse: API响应结果
        """
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user", 
            "content": user_message
        })
        
        return self.chat_completion(messages, **kwargs)
    
    def batch_process(self, 
                     queries: List[str], 
                     system_message: str = None,
                     max_retries: int = 3,
                     delay_between_requests: float = 1.0) -> List[APIResponse]:
        """
        批量处理查询
        
        Args:
            queries: 查询列表
            system_message: 系统消息
            max_retries: 最大重试次数
            delay_between_requests: 请求间延迟（秒）
            
        Returns:
            List[APIResponse]: 响应列表
        """
        results = []
        
        for i, query in enumerate(queries):
            logger.info(f"🔄 处理查询 {i+1}/{len(queries)}")
            
            retry_count = 0
            while retry_count < max_retries:
                response = self.simple_chat(query, system_message)
                
                if response.success:
                    results.append(response)
                    break
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"⚠️ 查询失败，重试 {retry_count}/{max_retries}")
                        time.sleep(delay_between_requests * retry_count)
                    else:
                        logger.error(f"❌ 查询最终失败: {response.error}")
                        results.append(response)
            
            # 请求间延迟
            if i < len(queries) - 1:
                time.sleep(delay_between_requests)
        
        success_count = sum(1 for r in results if r.success)
        logger.info(f"📊 批量处理完成: {success_count}/{len(queries)} 成功")
        
        return results
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            bool: 连接是否成功
        """
        logger.info("🔍 测试API连接...")
        
        response = self.simple_chat(
            "你好，请回复'连接成功'", 
            max_tokens=50,
            timeout=10
        )
        
        if response.success:
            logger.info("✅ API连接测试成功")
            return True
        else:
            logger.error(f"❌ API连接测试失败: {response.error}")
            return False

# 全局客户端实例
_api_client = None

def get_api_client() -> SiliconFlowClient:
    """获取全局API客户端实例"""
    global _api_client
    if _api_client is None:
        from config.config import SILICONFLOW_CONFIG
        _api_client = SiliconFlowClient(
            api_key=SILICONFLOW_CONFIG["api_key"],
            base_url=SILICONFLOW_CONFIG["base_url"],
            model=SILICONFLOW_CONFIG["model"]
        )
    return _api_client

 