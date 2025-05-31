"""
最终审核智能体模块 - 负责最终审核，确保内容质量
"""

from langchain_core.messages import AIMessage

from multi_agent_system.core.state import AgentState, copy_state
from multi_agent_system.utils.llm_utils import safe_llm_call
from multi_agent_system.utils.style_manager import (
    get_polish_guide,
    get_human_writing_tips
)

def finalization_agent(state: AgentState) -> AgentState:
    """
    最终审核智能体：确保内容质量
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    # 创建状态的副本
    new_state = copy_state(state)
    messages = new_state["messages"]
    workspace = new_state["workspace"]
    
    if "revised_content" not in workspace:
        messages.append(AIMessage(content="我需要修订后的内容才能进行最终审核。请先运行修订智能体。"))
        return new_state
    
    # 获取主题和写作风格
    topic = workspace.get("topic", "通用主题")
    writing_style = workspace.get("writing_style", "平衡多元型")
    
    # 根据风格调整最终润色指南
    polish_guide = get_polish_guide(writing_style)
    
    # 人性化写作技巧提示
    human_writing_tips = get_human_writing_tips()
    
    finalization_prompt = f"""
    你是一位专业的内容审核专家。请对以下修订后的内容进行最终审核与润色：
    
    主题：{topic}
    写作风格：{writing_style}
    内容：
    {workspace["revised_content"]}
    
    {polish_guide}
    
    {human_writing_tips}
    
    请执行两个任务：
    
    任务1: 进行最终内容审核，并在你的回复中提供评分和简短总结。这部分内容会被保存为审核记录，但不会包含在最终文章中。
    
    任务2: 提供最终文章内容。请在保持原文主要内容和结构的基础上，根据上述指南进行适当润色，使文章更加自然、流畅和有人文气息。确保：
    - 不要添加任何修订说明、审核评论或元数据
    - 不要使用"最终版本"、"定稿"等标题
    - 只提供纯文章内容，就像这是准备发布的最终稿
    - 不要在文章内容中包含任何评分、评价或审核痕迹
    - 保持文章风格的一致性，符合之前确定的写作风格
    - 突出文章的个性和人文特色，减少AI痕迹
    
    重要：你提供的最终内容将作为文章的正式发布版本，应当读起来自然流畅，像是由有经验的人类作者精心创作的。
    """
    
    print("📝 正在最终审核...")
    finalization_response = safe_llm_call(finalization_prompt)
    
    # 保存审核记录
    workspace["final_review"] = finalization_response.content
    
    # 尝试从回复中提取文章内容，如果提取失败，则使用修订内容
    try:
        # 提取回复中的文章内容
        # 检查是否包含任务2的分隔符或类似内容
        content_markers = [
            "任务2:", "最终文章内容:", "最终内容:", "文章内容:",
            "以下是最终文章:", "以下是文章的最终版本:", "润色后的内容:"
        ]
        
        final_content = workspace["revised_content"]  # 默认使用修订内容
        response_text = finalization_response.content
        
        # 检查是否有任务分隔
        for marker in content_markers:
            if marker in response_text:
                # 找到分隔符后的内容
                parts = response_text.split(marker, 1)
                if len(parts) > 1:
                    # 只取分隔符后的内容
                    potential_content = parts[1].strip()
                    # 确保内容足够长
                    if len(potential_content) > 100:  # 假设文章至少100字符
                        final_content = potential_content
                        break
        
        # 清理可能的结尾评论
        end_markers = ["总结:", "评分:", "结论:", "我的评价", "任务1:"]
        for marker in end_markers:
            if marker in final_content:
                final_content = final_content.split(marker, 1)[0].strip()
        
        workspace["final_content"] = final_content
    except Exception as e:
        print(f"提取文章内容时出错: {e}")
        # 出错时使用修订内容
        workspace["final_content"] = workspace["revised_content"]
    
    print("✅ 最终审核完成")
    
    messages.append(AIMessage(content=f"我已完成最终审核：\n\n{workspace['final_review']}\n\n最终内容已准备就绪，可以导出。"))
    
    return new_state 