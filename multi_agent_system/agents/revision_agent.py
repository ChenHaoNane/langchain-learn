"""
修订智能体模块 - 负责根据编辑建议修改内容
"""

from langchain_core.messages import AIMessage

from multi_agent_system.core.state import AgentState, copy_state
from multi_agent_system.utils.llm_utils import safe_llm_call
from multi_agent_system.utils.style_manager import (
    detect_style_for_topic,
    get_revision_guide
)

def revision_agent(state: AgentState) -> AgentState:
    """
    修订智能体：根据编辑建议修改内容
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    # 创建状态的副本
    new_state = copy_state(state)
    messages = new_state["messages"]
    workspace = new_state["workspace"]
    
    if "editing_suggestions" not in workspace or "content" not in workspace:
        messages.append(AIMessage(content="我需要内容和编辑建议才能进行修订。请先运行编辑智能体。"))
        return new_state
    
    # 获取之前确定的写作风格，如果没有则确定一个
    topic = workspace.get("topic", "通用主题")
    writing_style = workspace.get("writing_style", "")
    
    if not writing_style:
        # 如果没有预先确定的风格，根据主题推断
        writing_style = detect_style_for_topic(topic)
        workspace["writing_style"] = writing_style
    
    # 根据风格提供个性化修订指南
    style_revision_guide = get_revision_guide(writing_style)
    
    revision_prompt = f"""
    你是一位专业的内容修订者。请根据以下编辑建议修订内容：
    
    主题：{topic}
    写作风格：{writing_style}
    
    原始内容：
    {workspace["content"]}
    
    编辑建议：
    {workspace["editing_suggestions"]}
    
    风格修订指南：
    {style_revision_guide}
    
    人性化写作建议：
    1. 避免过于完美的结构和表达，适当保留一些个性化特点
    2. 减少明显的AI痕迹，如过度平衡的论述和机械化的段落结构
    3. 可以有一定的情感倾向和个人色彩
    4. 使用更自然的过渡和连接，避免公式化的"首先"、"其次"、"总之"等
    5. 句式长短结合，避免所有段落结构过于相似
    6. 适当使用修辞手法，如反问、设问、比喻等增加表现力
    
    请按照以下要求提供修订后的内容：
    1. 直接提供修订后的完整内容，不要包含任何解释、注释或修订说明
    2. 不要添加"修订说明"、"编辑记录"或类似的元数据
    3. 不要使用标题如"### 修订版本"或"## 修订内容"等
    4. 保持原有的整体结构，但风格应更加自然、人性化
    5. 只输出修订后的正文内容
    
    最终输出应该是一篇可以直接发布的、有个性和人文气息的完整文章，读起来像是由有经验的人类作者撰写的。
    """
    
    print("📝 正在修订内容...")
    revision_response = safe_llm_call(revision_prompt)
    workspace["revised_content"] = revision_response.content
    print("✅ 修订完成")
    
    content_preview = workspace['revised_content'][:300] + "..." if len(workspace['revised_content']) > 300 else workspace['revised_content']
    messages.append(AIMessage(content=f"我已经根据编辑建议修订了内容。以下是修订后的内容摘要：\n\n{content_preview}"))
    
    return new_state 