"""
批处理工具 - 用于优化多智能体任务执行
"""

import asyncio
from typing import List, Dict, Any, Callable, Coroutine, Optional, Union

from multi_agent_system.utils.llm_utils import batch_llm_calls, llm_manager
from multi_agent_system.core.state import AgentState, copy_state
from multi_agent_system.config.settings import MAX_PARALLEL_CALLS, PRIORITY_MODE

class BatchProcessor:
    """批处理器，用于并行执行多个智能体任务"""
    
    def __init__(self, max_workers: int = MAX_PARALLEL_CALLS):
        """初始化批处理器
        
        Args:
            max_workers: 最大并行工作线程数
        """
        self.max_workers = max_workers
        self.priority_mode = PRIORITY_MODE
    
    async def run_parallel_tasks(
        self, 
        tasks: List[Callable[..., Coroutine]], 
        args_list: List[tuple] = None
    ) -> List[Any]:
        """并行运行多个异步任务
        
        Args:
            tasks: 异步任务函数列表
            args_list: 参数列表（每个元素对应一个任务的参数元组）
            
        Returns:
            各任务的结果列表
        """
        if args_list is None:
            args_list = [()] * len(tasks)
            
        async_tasks = [task(*args) for task, args in zip(tasks, args_list)]
        return await asyncio.gather(*async_tasks)
    
    def parallel_execute(
        self, 
        agent_functions: List[Callable[[AgentState], AgentState]], 
        states: Union[AgentState, List[AgentState]]
    ) -> List[AgentState]:
        """并行执行多个智能体函数
        
        Args:
            agent_functions: 智能体函数列表
            states: 状态或状态列表（如果是单个状态，会被复制后传给每个函数）
            
        Returns:
            处理后的状态列表
        """
        # 处理单个状态的情况
        if not isinstance(states, list):
            states = [copy_state(states) for _ in range(len(agent_functions))]
            
        # 创建执行函数
        async def execute_agent(agent_fn, state):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, agent_fn, state)
            
        # 创建任务
        tasks = [execute_agent for _ in agent_functions]
        args_list = [(fn, state) for fn, state in zip(agent_functions, states)]
        
        # 获取事件循环
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # 并行执行
        return loop.run_until_complete(self.run_parallel_tasks(tasks, args_list))
    
    def batch_process_prompts(self, prompts: List[str]) -> List[str]:
        """批量处理多个提示文本
        
        Args:
            prompts: 提示文本列表
            
        Returns:
            响应文本列表
        """
        responses = batch_llm_calls(prompts)
        return [response.content for response in responses]
    
    def optimize_workflow(self, state: AgentState) -> Dict[str, Any]:
        """根据状态优化工作流程
        
        Args:
            state: 当前状态
            
        Returns:
            优化配置
        """
        # 根据优先模式调整配置
        if self.priority_mode == "speed":
            return {
                "parallel_tasks": True,
                "max_tokens": 1000,  # 限制token数量以加快生成
                "stream_output": False  # 禁用流式输出以优化速度
            }
        else:  # 质量优先
            return {
                "parallel_tasks": False,
                "max_tokens": 3000,  # 更多token以提高质量
                "stream_output": True  # 启用流式输出
            }

# 创建全局实例
batch_processor = BatchProcessor() 