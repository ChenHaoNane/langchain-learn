"""
大纲智能体模块 - 负责创建写作的整体结构和大纲
"""

from langchain_core.messages import AIMessage, HumanMessage

from multi_agent_system.core.state import AgentState, copy_state
from multi_agent_system.utils.llm_utils import safe_llm_call
from multi_agent_system.utils.batch_processor import batch_processor
from multi_agent_system.config.settings import MAX_TOPIC_LENGTH, DEFAULT_TOPIC, PRIORITY_MODE

def outline_agent(state: AgentState) -> AgentState:
    """
    大纲策划智能体：创建写作的整体结构和大纲
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    # 创建状态的副本
    new_state = copy_state(state)
    messages = new_state["messages"]
    workspace = new_state["workspace"]
    
    # 获取工作流优化配置
    optimization = workspace.get("optimization", batch_processor.optimize_workflow(state))
    is_speed_mode = PRIORITY_MODE == "speed"
    
    # 如果工作空间没有主题，从消息中提取
    if "topic" not in workspace:
        prompt = """请从以下用户消息中提取写作主题：
        
        用户消息：
        {}
        
        请只返回一个简短的主题（不超过30个字符），不要包含任何解释或额外信息。
        例如：'人工智能'、'教育改革'、'气候变化'等。
        """.format('\n'.join([msg.content for msg in messages if isinstance(msg, HumanMessage)]))
        
        print("🔍 正在提取主题...")
        topic_extraction = safe_llm_call(prompt)
        
        # 清理主题文本，使其适合用作文件名
        extracted_topic = topic_extraction.content.strip()
        # 如果提取的主题过长或包含特殊字符，使用一个默认主题
        if len(extracted_topic) > MAX_TOPIC_LENGTH or any(c in extracted_topic for c in '\\/:"*?<>|'):
            simplified_topic = "".join([c for c in extracted_topic if c.isalnum() or c in ' -_'])[:MAX_TOPIC_LENGTH].strip()
            if not simplified_topic:
                simplified_topic = DEFAULT_TOPIC
            workspace["topic"] = simplified_topic
        else:
            workspace["topic"] = extracted_topic
            
        print(f"✅ 提取到主题: {workspace['topic']}")
    
    # 创建大纲 - 根据优化模式调整提示
    if is_speed_mode:
        outline_prompt = f"""
        你是一位高效的大纲策划师。请为以下主题创建一个简洁的写作大纲：
        主题：{workspace.get('topic', '通用主题')}
        
        大纲应包括：
        1. 文章标题
        2. 引言要点
        3. 3个主要章节（每个章节列出要点）
        4. 结论要点
        
        注意：请保持简洁，限制在500字以内。
        """
    else:
        outline_prompt = f"""
        你是一位专业的大纲策划师。请为以下主题创建一个详细的写作大纲：
        主题：{workspace.get('topic', '通用主题')}
        
        大纲应包括：
        1. 文章标题
        2. 引言部分
        3. 3-5个主要章节（每个章节包含2-3个子部分）
        4. 结论部分
        
        请以清晰的层次结构输出大纲。
        """
    
    print("📝 正在创建大纲...")
    outline_response = safe_llm_call(outline_prompt)
    workspace["outline"] = outline_response.content
    workspace["optimization"] = optimization  # 保存优化配置供其他智能体使用
    print("✅ 大纲创建完成")
    
    messages.append(AIMessage(content=f"我已经为主题「{workspace.get('topic')}」创建了大纲：\n\n{workspace['outline']}"))
    
    return new_state 