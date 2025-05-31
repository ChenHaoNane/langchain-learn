"""
LLM工具类 - 包含LLM初始化和调用相关功能
"""

import time
import sys
import os
import asyncio
from typing import Any, Dict, Optional, List, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from multi_agent_system.config.settings import (
    API_TIMEOUT, 
    DEFAULT_MODEL, 
    DEFAULT_TEMPERATURE,
    MAX_RETRIES,
    RETRY_DELAY,
    ENABLE_CACHING,
    MAX_PARALLEL_CALLS
)

class LLMManager:
    """LLM管理器，处理模型初始化和调用"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(LLMManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化LLM管理器"""
        if not self.initialized:
            self.response_cache = {}  # 简单的响应缓存
            self.executor = ThreadPoolExecutor(max_workers=MAX_PARALLEL_CALLS)  # 线程池
            self.initialize_llm()
            self.initialized = True
    
    def initialize_llm(self, model: str = DEFAULT_MODEL, temperature: float = DEFAULT_TEMPERATURE) -> None:
        """初始化大语言模型
        
        Args:
            model: 模型名称
            temperature: 温度系数
        """
        try:
            # 添加缓存支持
            cache_options = {}
            if ENABLE_CACHING:
                try:
                    from langchain.globals import set_llm_cache
                    from langchain.cache import InMemoryCache
                    set_llm_cache(InMemoryCache())
                    print("✅ 已启用LLM响应缓存")
                except ImportError:
                    print("⚠️ 无法导入缓存模块，将禁用缓存")
            
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                request_timeout=API_TIMEOUT,
                **cache_options
            )
            print(f"✅ 成功初始化模型: {model}")
        except Exception as e:
            print(f"❌ 初始化模型时出错: {e}")
            print("请确保您已经设置了正确的API密钥和模型名称。")
            sys.exit(1)
    
    def safe_call(self, prompt: str, retries: int = MAX_RETRIES, delay: int = RETRY_DELAY) -> AIMessage:
        """安全调用LLM，带有重试机制和缓存
        
        Args:
            prompt: 提示文本
            retries: 最大重试次数
            delay: 重试间隔(秒)
        
        Returns:
            AI响应消息
        """
        # 检查缓存
        if ENABLE_CACHING and prompt in self.response_cache:
            print("🔄 使用缓存的响应...")
            return self.response_cache[prompt]
            
        for attempt in range(retries):
            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                
                # 添加到缓存
                if ENABLE_CACHING:
                    self.response_cache[prompt] = response
                    
                return response
            except Exception as e:
                if attempt < retries - 1:
                    print(f"API调用失败，正在重试 ({attempt+1}/{retries}): {e}")
                    time.sleep(delay)  # 等待一段时间后重试
                else:
                    print(f"API调用失败，达到最大重试次数: {e}")
                    # 返回一个模拟的回应
                    return AIMessage(content="API调用失败，无法获取回应。请稍后再试。")
    
    async def async_call(self, prompt: str, retries: int = MAX_RETRIES, delay: int = RETRY_DELAY) -> AIMessage:
        """异步调用LLM
        
        Args:
            prompt: 提示文本
            retries: 最大重试次数
            delay: 重试间隔(秒)
            
        Returns:
            AI响应消息
        """
        # 创建一个可以在事件循环中运行的函数
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            lambda: self.safe_call(prompt, retries, delay)
        )
    
    async def parallel_calls(self, prompts: List[str]) -> List[AIMessage]:
        """并行调用LLM处理多个提示
        
        Args:
            prompts: 提示文本列表
            
        Returns:
            AI响应消息列表
        """
        tasks = [self.async_call(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
        
    def batch_process(self, prompts: List[str]) -> List[AIMessage]:
        """批量处理多个提示（同步接口）
        
        Args:
            prompts: 提示文本列表
            
        Returns:
            AI响应消息列表
        """
        # 为没有事件循环的环境创建一个新的事件循环
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(self.parallel_calls(prompts))
    
    def change_model(self, model: str, temperature: Optional[float] = None) -> None:
        """更改使用的模型
        
        Args:
            model: 新的模型名称
            temperature: 新的温度系数，如果为None则保持不变
        """
        try:
            temp = temperature if temperature is not None else self.llm.temperature
            self.initialize_llm(model=model, temperature=temp)
        except Exception as e:
            print(f"更改模型失败: {e}")

# 创建全局实例
llm_manager = LLMManager()

# 导出便捷函数
def safe_llm_call(prompt: str, retries: int = MAX_RETRIES, delay: int = RETRY_DELAY) -> AIMessage:
    """安全调用LLM的便捷函数
    
    Args:
        prompt: 提示文本
        retries: 最大重试次数
        delay: 重试间隔(秒)
    
    Returns:
        AI响应消息
    """
    return llm_manager.safe_call(prompt, retries, delay)

def batch_llm_calls(prompts: List[str]) -> List[AIMessage]:
    """批量并行调用LLM的便捷函数
    
    Args:
        prompts: 提示文本列表
    
    Returns:
        AI响应消息列表
    """
    return llm_manager.batch_process(prompts)

def get_llm_manager() -> LLMManager:
    """
    获取LLM管理器实例
    
    Returns:
        LLMManager: LLM管理器实例
    """
    return llm_manager 