"""
编辑智能体模块 - 负责检查内容，提供修订意见
"""

from langchain_core.messages import AIMessage

from multi_agent_system.core.state import AgentState, copy_state
from multi_agent_system.utils.llm_utils import safe_llm_call

def editing_agent(state: AgentState) -> AgentState:
    """
    编辑智能体：检查内容，提供修订意见
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    # 创建状态的副本
    new_state = copy_state(state)
    messages = new_state["messages"]
    workspace = new_state["workspace"]
    
    if "content" not in workspace:
        messages.append(AIMessage(content="我需要内容才能提供编辑建议。请先运行内容创作智能体。"))
        return new_state
    
    editing_prompt = f"""
    你是一位专业的编辑。请审阅以下内容并提供具体的修订建议：
    
    主题：{workspace.get('topic', '通用主题')}
    内容：
    {workspace["content"]}
    
    请关注：
    1. 句子结构和流畅度
    2. 逻辑连贯性
    3. 信息准确性
    4. 语法和拼写错误
    5. 表达清晰度
    
    提供具体的修订建议，并指出需要改进的部分。
    """
    
    print("📝 正在编辑内容...")
    editing_response = safe_llm_call(editing_prompt)
    workspace["editing_suggestions"] = editing_response.content
    print("✅ 编辑完成")
    
    messages.append(AIMessage(content=f"我已经审阅了内容并提供了修订建议：\n\n{workspace['editing_suggestions']}"))
    
    return new_state 