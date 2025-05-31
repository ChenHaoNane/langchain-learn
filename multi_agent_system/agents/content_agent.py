"""
内容智能体模块 - 负责根据大纲创建文章内容
"""

from langchain_core.messages import AIMessage

from multi_agent_system.core.state import AgentState, copy_state
from multi_agent_system.utils.llm_utils import safe_llm_call
from multi_agent_system.utils.style_manager import get_style_for_topic
from multi_agent_system.config.settings import PRIORITY_MODE

def content_agent(state: AgentState) -> AgentState:
    """
    内容生成智能体：根据大纲创建文章内容
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    # 创建状态的副本
    new_state = copy_state(state)
    messages = new_state["messages"]
    workspace = new_state["workspace"]
    
    # 检查是否存在大纲
    if "outline" not in workspace:
        messages.append(AIMessage(content="请先创建大纲，然后我才能生成内容。"))
        return new_state
    
    # 确定写作风格
    if "style" not in workspace or not workspace["style"]:
        topic = workspace.get("topic", "通用主题")
        print("🔍 正在确定写作风格...")
        workspace["style"] = get_style_for_topic(topic)
        print(f"✅ 确定写作风格: {workspace['style']}")
        
    # 根据优化模式调整提示
    is_speed_mode = PRIORITY_MODE == "speed"
    if is_speed_mode:
        # 速度优先模式使用更简洁的提示
        content_prompt = f"""
        你是一位高效的内容写作者。请根据以下大纲和风格要求，快速创建一篇文章内容。

        大纲：
        {workspace['outline']}

        风格：{workspace['style']}

        要求：
        1. 内容要紧扣大纲
        2. 使用简洁明了的语言
        3. 重点突出，信息密度高
        4. 限制在1500字以内

        请直接给出文章内容，不要包含额外的解释。
        """
    else:
        # 质量优先模式使用更详细的提示
        content_prompt = f"""
        你是一位专业的内容创作者。请根据以下大纲和风格要求，创建一篇高质量的文章内容：

        大纲：
        {workspace['outline']}

        风格：{workspace['style']}

        要求：
        1. 内容应该完全覆盖大纲中的所有要点
        2. 使用适合主题的语言和表达方式
        3. 适当添加例子、数据或引用增强文章说服力
        4. 确保文章结构清晰，段落衔接自然
        5. 结论部分应该有意义，不要生硬结束

        请创建一篇完整、连贯的文章内容。
        """
    
    print("📝 正在创建内容...")
    content_response = safe_llm_call(content_prompt)
    workspace["content"] = content_response.content
    print("✅ 内容创建完成")
    
    # 添加消息
    content_summary = workspace["content"][:150] + "..." if len(workspace["content"]) > 150 else workspace["content"]
    messages.append(AIMessage(content=f"我已经根据大纲创建了文章内容。以下是内容摘要：\n\n{content_summary}"))
    
    return new_state 