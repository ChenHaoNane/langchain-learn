"""
文件处理工具 - 处理文件名和文件保存等功能
"""

import os
import time
from typing import Optional

from multi_agent_system.config.settings import FILENAME_MAX_LENGTH, OUTPUT_DIR

def safe_filename(text: str, max_length: int = FILENAME_MAX_LENGTH) -> str:
    """
    生成一个安全的文件名
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        安全的文件名字符串
    """
    # 如果text为空，使用默认值
    if not text or not isinstance(text, str):
        return "unnamed_file"
        
    # 删除不安全的字符
    safe_text = "".join([c for c in text if c.isalnum() or c in ' -_'])
    
    # 限制长度
    safe_text = safe_text.strip()[:max_length].strip()
    
    # 确保不为空
    if not safe_text:
        return "unnamed_file"
        
    # 替换空格
    return safe_text.replace(' ', '_')

def ensure_directory(directory: str = OUTPUT_DIR) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"✅ 已创建目录: {directory}")

def save_content_to_file(
    content: str, 
    filename: str, 
    directory: str = OUTPUT_DIR, 
    title: Optional[str] = None
) -> str:
    """
    保存内容到文件
    
    Args:
        content: 要保存的内容
        filename: 文件名（不含路径）
        directory: 保存目录
        title: 文档标题，如果提供则会添加到文件开头
    
    Returns:
        完整的文件路径
    """
    # 确保目录存在
    ensure_directory(directory)
    
    # 构建完整的文件路径
    filepath = os.path.join(directory, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            # 如果提供了标题，添加到文件开头
            if title:
                f.write(f"# {title}\n\n")
            f.write(content)
        print(f"✅ 已保存内容到: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ 保存内容失败: {e}")
        return ""

def generate_timestamped_filename(
    topic: str, 
    stage: str = "final", 
    extension: str = "md"
) -> str:
    """
    生成带时间戳的文件名
    
    Args:
        topic: 主题
        stage: 阶段名称
        extension: 文件扩展名
    
    Returns:
        生成的文件名
    """
    # 生成安全的主题名
    safe_topic = safe_filename(topic)
    
    # 添加时间戳
    timestamp = int(time.time())
    
    return f"{safe_topic}_{stage}_{timestamp}.{extension}"

# 添加别名函数，用于兼容性
def save_to_file(content: str, filepath: str, title: Optional[str] = None) -> str:
    """
    保存内容到指定路径（别名函数）
    
    Args:
        content: 要保存的内容
        filepath: 完整的文件路径
        title: 文档标题，如果提供则会添加到文件开头
    
    Returns:
        完整的文件路径
    """
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    
    return save_content_to_file(content, filename, directory, title) 