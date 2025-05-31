"""
配置文件 - 包含系统设置和常量
"""

# API设置
API_TIMEOUT = 60  # API调用超时时间（秒）
DEFAULT_MODEL = "deepseek-chat"  # 默认使用的模型
DEFAULT_TEMPERATURE = 0.7  # 默认温度系数

# 重试设置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试间隔（秒）

# 性能优化设置
ENABLE_CACHING = True  # 启用缓存
MAX_PARALLEL_CALLS = 4  # 最大并行调用数
STREAMING_MODE = False  # 流式输出模式
PRIORITY_MODE = "speed"  # 优先模式，可选："speed"（速度优先）或"quality"（质量优先）

# 系统路径
OUTPUT_DIR = "multi_agent_system/output"  # 输出目录
DEFAULT_OUTPUT_DIR = "output"  # 默认输出目录

# 主题设置
MAX_TOPIC_LENGTH = 30  # 主题最大长度
DEFAULT_TOPIC = "自动生成的文章"  # 默认主题名称

# 文件名设置
FILENAME_MAX_LENGTH = 50  # 文件名最大长度

# 风格映射
STYLE_CATEGORIES = {
    "技术": ["编程", "软件", "人工智能", "机器学习", "区块链", "云计算", "大数据", "物联网"],
    "科学": ["物理", "化学", "生物", "天文", "地理", "医学", "环境"],
    "人文": ["历史", "哲学", "文学", "艺术", "文化", "宗教", "心理"],
    "社会": ["政治", "经济", "法律", "教育", "社会学", "传媒", "国际关系"],
    "生活": ["健康", "旅游", "美食", "时尚", "体育", "娱乐", "家居"]
}

STYLE_MAP = {
    "技术": "专业解析型",
    "科学": "科普教育型",
    "人文": "深度思考型",
    "社会": "批判分析型",
    "生活": "轻松体验型",
    "通用": "平衡多元型"
} 