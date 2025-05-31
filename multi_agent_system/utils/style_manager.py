"""
风格管理模块 - 处理写作风格相关功能
"""

from typing import Dict, List, Optional

from multi_agent_system.config.settings import STYLE_CATEGORIES, STYLE_MAP, PRIORITY_MODE
from multi_agent_system.utils.llm_utils import safe_llm_call

def get_style_for_topic(topic: str) -> str:
    """
    获取主题的写作风格，根据速度/质量模式选择不同的实现
    
    Args:
        topic: 文章主题
    
    Returns:
        写作风格
    """
    # 速度优先模式使用快速检测
    if PRIORITY_MODE == "speed":
        return detect_style_for_topic(topic)
    # 质量优先模式使用LLM确定
    else:
        return determine_style_for_topic(topic)

def detect_style_for_topic(topic: str) -> str:
    """
    基于主题自动检测合适的写作风格
    
    Args:
        topic: 文章主题
    
    Returns:
        推荐的写作风格
    """
    # 先使用预定义的分类进行快速分类
    topic_lower = topic.lower()
    
    # 尝试从主题关键词判断类别
    detected_category = "通用"
    for category, keywords in STYLE_CATEGORIES.items():
        if any(keyword.lower() in topic_lower for keyword in keywords):
            detected_category = category
            break
    
    # 从类别映射到风格
    style = STYLE_MAP.get(detected_category, "平衡多元型")
    
    return style

def get_style_instructions(writing_style: str) -> str:
    """
    根据写作风格获取具体的写作指南
    
    Args:
        writing_style: 写作风格
    
    Returns:
        写作指南
    """
    # 根据不同风格返回相应的写作指南
    if "学术" in writing_style or "研究" in writing_style:
        return """
        - 使用学术性语言，注重论证和引用
        - 提供具体数据和研究结果支持观点
        - 使用第三人称客观叙述
        - 加入适当的专业术语，但确保解释清晰
        - 结构严谨，逻辑性强
        """
    elif "通俗" in writing_style or "科普" in writing_style:
        return """
        - 使用日常用语，避免艰深晦涩的词汇
        - 多用比喻和例子来解释复杂概念
        - 语气友好亲切，可使用第二人称
        - 短句为主，避免过长的复杂句
        - 增加趣味性和互动性的表达
        """
    elif "故事" in writing_style or "叙述" in writing_style:
        return """
        - 以故事或案例为主线展开论述
        - 塑造具体人物或场景
        - 使用生动的描述和对话
        - 注重情节发展和转折
        - 增加个人色彩和情感元素
        """
    elif "辩论" in writing_style or "说理" in writing_style:
        return """
        - 清晰呈现不同立场和观点
        - 使用反问、设问等修辞手法
        - 论证有力，逐步深入
        - 预设反方观点并有效反驳
        - 结论明确有说服力
        """
    elif "经验" in writing_style or "分享" in writing_style:
        return """
        - 使用第一人称叙述
        - 分享具体案例和个人见解
        - 语气真诚自然
        - 加入实用的建议和技巧
        - 避免过度理论化
        """
    elif "专业" in writing_style or "解析" in writing_style:
        return """
        - 使用行业专业术语，但适当解释复杂概念
        - 提供深入的技术分析和见解
        - 结构清晰，层次分明
        - 引用权威来源和最新研究
        - 保持客观中立的专业语气
        """
    else:
        # 默认多样化写作风格
        return """
        - 避免过于正式和模板化的表达
        - 句式多样，长短句结合
        - 适当使用修辞手法增加表现力
        - 减少重复的句式和词汇
        - 语气自然流畅，像人类作者一样写作
        """

def get_revision_guide(writing_style: str) -> str:
    """
    根据写作风格获取修订指南
    
    Args:
        writing_style: 写作风格
    
    Returns:
        修订指南
    """
    if "专业" in writing_style or "解析" in writing_style:
        return """
        - 增加专业术语的准确性，但避免过度专业化导致难以理解
        - 加强技术细节的清晰度和准确性
        - 确保逻辑推导严密，论证有力
        - 适当引入行业最新发展和趋势
        - 保持客观分析，但可以有明确的专业立场
        """
    elif "科普" in writing_style or "教育" in writing_style:
        return """
        - 将复杂概念转化为通俗易懂的解释
        - 加入生动的比喻和实例
        - 增加与读者日常生活的关联性
        - 保持知识的准确性，同时提高趣味性
        - 设置一些问题和思考点，增加互动性
        """
    elif "深度" in writing_style or "思考" in writing_style:
        return """
        - 增加哲学性思考和开放性问题
        - 深化主题的历史和文化背景
        - 鼓励多角度思考和价值观探讨
        - 语言可以更加优美和富有感染力
        - 适当引用经典著作或名人观点
        """
    elif "批判" in writing_style or "分析" in writing_style:
        return """
        - 强化不同观点的对比和分析
        - 提供更有说服力的数据和案例支持
        - 增加对主流观点的质疑和思考
        - 保持批判性思维，但避免过度偏激
        - 结论部分提出建设性的解决方案
        """
    elif "轻松" in writing_style or "体验" in writing_style:
        return """
        - 增加个人体验和感受的描述
        - 使用更加生动、活泼的语言
        - 加入一些幽默元素和日常用语
        - 减少抽象概念，增加具体场景描述
        - 结构可以更加灵活，叙事性更强
        """
    else:
        return """
        - 平衡专业性和可读性
        - 句式多样化，避免重复的表达模式
        - 增加一些个人观点，但保持整体客观
        - 适当加入生动的例子和场景
        - 确保内容丰富多元，同时结构清晰
        """

def get_polish_guide(writing_style: str) -> str:
    """
    根据写作风格获取润色指南
    
    Args:
        writing_style: 写作风格
    
    Returns:
        润色指南
    """
    if "专业" in writing_style or "学术" in writing_style:
        return """
        最终润色指南：
        - 进一步检查术语使用的准确性和一致性
        - 确保引用和数据有足够支持
        - 保持论证的严密性和连贯性
        - 适当减少形式化的学术语言，增加可读性
        - 保留一些专业见解和独特视角，避免过于教科书化
        """
    elif "通俗" in writing_style or "科普" in writing_style:
        return """
        最终润色指南：
        - 进一步简化复杂概念，确保通俗易懂
        - 增加生活化的例子和场景
        - 加入一些幽默元素或有趣的比喻
        - 检查是否有过于专业的术语需要进一步解释
        - 增强互动性和亲和力，如使用反问句或设问
        """
    elif "故事" in writing_style or "叙述" in writing_style:
        return """
        最终润色指南：
        - 增强故事情节的连贯性和吸引力
        - 丰富人物或场景的细节描写
        - 加强情感元素和共鸣点
        - 保持叙事节奏的变化，制造适当的起伏
        - 故事元素和主题信息应紧密结合，相辅相成
        """
    elif "批判" in writing_style or "辩论" in writing_style:
        return """
        最终润色指南：
        - 确保论点鲜明，立场清晰
        - 加强论证过程中的逻辑性和说服力
        - 预设反对观点并有效回应
        - 平衡批判性与建设性，避免过度消极
        - 结论部分提出有价值的见解或解决方案
        """
    elif "经验" in writing_style or "分享" in writing_style:
        return """
        最终润色指南：
        - 增强个人色彩和真实感
        - 加入更多细节和具体的实例
        - 保持语言的自然流畅和口语化特点
        - 确保建议和经验具有实用价值
        - 适当表达情感和个人反思，增加共鸣
        """
    else:
        return """
        最终润色指南：
        - 确保内容的多样性和平衡性
        - 增加一些个性化表达和独特视角
        - 检查文章的节奏感，避免平铺直叙
        - 适当加入修辞手法，增强表现力
        - 保持专业性的同时增加可读性和亲和力
        """

def determine_style_for_topic(topic: str) -> str:
    """
    使用LLM确定主题的最佳写作风格
    
    Args:
        topic: 文章主题
    
    Returns:
        写作风格
    """
    style_prompt = f"""
    请为主题"{topic}"确定一个合适的写作风格。
    不要解释你的选择过程，只需简洁地返回一种写作风格，例如：
    "学术严谨型"、"通俗易懂型"、"故事叙述型"、"辩论说理型"、"经验分享型"等。
    返回的内容应该只有写作风格，不超过10个字。
    """
    
    print("🔍 正在确定写作风格...")
    style_response = safe_llm_call(style_prompt)
    writing_style = style_response.content.strip()
    print(f"✅ 确定写作风格: {writing_style}")
    
    return writing_style

def get_human_writing_tips() -> str:
    """
    获取通用的人性化写作技巧
    
    Returns:
        人性化写作技巧
    """
    return """
    人性化写作技巧：
    1. 打破完美：加入一些小转折或偶然的思考，避免过于完美的结构
    2. 情感温度：适当表达情感和态度，避免冷冰冰的客观叙述
    3. 语言个性：使用一些个性化的表达和独特的比喻
    4. 有限视角：不必面面俱到，可以有一定的倾向性和局限性
    5. 读者连接：建立与读者的连接，如使用"我们"或提问等方式
    6. 自然过渡：使用自然的过渡，避免机械的"此外"、"最后"等过渡词
    7. 节奏变化：段落长短不一，句式多样，制造阅读节奏的变化
    8. 真实细节：加入一些具体的、生活化的细节增加真实感
    """ 