"""
路由决策模块 - 用于确定工作流的下一步
"""

from langchain_core.messages import HumanMessage

# 尝试导入END常量
try:
    from langgraph.graph import END
except ImportError:
    try:
        from langgraph.graph.graph import END
    except ImportError:
        # 如果无法导入，使用字符串
        END = "END"

from multi_agent_system.core.state import AgentState, get_latest_user_message

def decide_next_step(state: AgentState) -> str:
    """
    决策函数：根据当前状态确定下一步
    
    Args:
        state: 当前状态
        
    Returns:
        下一步的节点名称
    """
    workspace = state.get("workspace", {})
    messages = state.get("messages", [])
    
    # 检查最新的用户消息是否有特定指令
    latest_user_message = get_latest_user_message(state)
    if latest_user_message:
        user_message_lower = latest_user_message.lower()
        
        # 用户请求重新生成大纲
        if any(keyword in user_message_lower for keyword in ["重新生成大纲", "修改大纲", "新大纲"]):
            return "outline_agent"
        
        # 用户请求重新生成内容
        if any(keyword in user_message_lower for keyword in ["重新生成内容", "修改内容", "新内容"]):
            return "content_agent"
        
        # 用户请求重新编辑
        if any(keyword in user_message_lower for keyword in ["重新编辑", "再次编辑", "新编辑"]):
            return "editing_agent"
        
        # 用户请求重新修订
        if any(keyword in user_message_lower for keyword in ["重新修订", "再次修订", "新修订"]):
            return "revision_agent"
        
        # 用户请求最终审核
        if any(keyword in user_message_lower for keyword in ["最终审核", "定稿", "完成"]):
            return "finalization_agent"
    
    # 根据工作流程自动决定下一步
    if "final_content" in workspace:
        # 所有步骤都已完成
        return END
    elif "revised_content" in workspace:
        # 已有修订内容，下一步是最终审核
        return "finalization_agent"
    elif "editing_suggestions" in workspace:
        # 已有编辑建议，下一步是修订
        return "revision_agent"
    elif "content" in workspace:
        # 已有内容，下一步是编辑
        return "editing_agent"
    elif "outline" in workspace:
        # 已有大纲，下一步是创建内容
        return "content_agent"
    else:
        # 没有大纲，从头开始
        return "outline_agent" 