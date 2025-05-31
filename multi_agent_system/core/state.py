"""
状态模型 - 定义系统状态类型和处理函数
"""

from typing import Dict, List, Any, TypedDict, Optional

from langchain_core.messages import BaseMessage

# 定义系统状态类型
class AgentState(TypedDict):
    """系统状态，包含所有消息和工作空间"""
    messages: List[BaseMessage]
    workspace: Dict[str, Any]

def get_workspace_value(state: AgentState, key: str, default: Any = None) -> Any:
    """
    安全地从工作空间获取值
    
    Args:
        state: 状态对象
        key: 键名
        default: 默认值
    
    Returns:
        键对应的值，如果不存在则返回默认值
    """
    return state.get("workspace", {}).get(key, default)

def set_workspace_value(state: AgentState, key: str, value: Any) -> AgentState:
    """
    安全地设置工作空间值
    
    Args:
        state: 状态对象
        key: 键名
        value: 值
    
    Returns:
        更新后的状态对象
    """
    messages = state.get("messages", [])
    workspace = state.get("workspace", {}).copy()
    workspace[key] = value
    
    return {
        "messages": messages,
        "workspace": workspace
    }

def get_latest_user_message(state: AgentState) -> Optional[str]:
    """
    获取最新的用户消息内容
    
    Args:
        state: 状态对象
    
    Returns:
        最新的用户消息内容，如果没有则返回None
    """
    from langchain_core.messages import HumanMessage
    
    messages = state.get("messages", [])
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message.content
    return None

def copy_state(state: AgentState) -> AgentState:
    """
    创建状态的深拷贝
    
    Args:
        state: 状态对象
    
    Returns:
        状态的深拷贝
    """
    messages = state.get("messages", []).copy()
    workspace = state.get("workspace", {}).copy()
    
    return {
        "messages": messages,
        "workspace": workspace
    } 