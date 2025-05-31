# 基于LangGraph的多智能体协作写作系统

这个项目是一个基于LangGraph构建的多智能体协作写作系统，通过多个专业智能体的协作来完成高质量的写作任务。

## 目录结构

```
multi_agent_system/
├── README.md            # 本文件
├── requirements.txt     # 依赖项
├── run.py              # 启动菜单脚本
├── multi_agent_writing.py     # 核心系统实现
├── multi_agent_writing_ui.py  # 命令行界面
├── example.py           # 编程使用示例
└── output/              # 输出文件目录
```

## 功能特点

系统包含以下智能体，每个智能体负责写作流程中的不同阶段：

1. **大纲策划智能体** - 负责创建写作的整体结构和大纲
2. **内容创作智能体** - 负责根据大纲生成具体内容
3. **编辑智能体** - 负责检查内容，提供修订意见
4. **修订智能体** - 负责根据编辑建议修改内容
5. **最终审核智能体** - 负责最终审核，确保内容质量

这些智能体通过LangGraph工作流引擎协同工作，完成从写作规划到最终审核的全流程。

## 启动方式

有两种方式启动系统：

### 1. 从根目录启动

在项目根目录下执行：

```bash
python start_writing_system.py
```

### 2. 直接在系统目录中启动

切换到系统目录并执行：

```bash
cd multi_agent_system
python run.py
```

## 使用方法

### 命令行界面

在启动菜单中选择选项1可以打开交互式命令行界面：

```bash
python multi_agent_writing_ui.py
```

在界面中，您可以使用以下命令：

- `/topic <主题>` - 设置新的写作主题
- `/run` - 自动运行整个写作流程
- `/outline` - 只运行大纲策划智能体
- `/content` - 运行到内容创作智能体
- `/edit` - 运行到编辑智能体
- `/revise` - 运行到修订智能体
- `/finalize` - 运行到最终审核智能体
- `/status` - 显示当前状态
- `/view <项目>` - 查看工作空间中的项目 (如: `/view outline`)
- `/save` - 保存当前文章到文件
- `/clear` - 清除屏幕
- `/reset` - 重置工作空间
- `/help` - 显示帮助信息
- `/exit` - 退出程序

### 直接生成文章

在启动菜单中选择选项2可以直接为指定主题生成文章。

### 特性

1. **中间结果保存** - 系统会自动保存每个阶段的结果到`output`目录
2. **状态跟踪** - 实时显示每个智能体的工作进度和状态
3. **错误处理** - 内置API调用超时和错误恢复机制
4. **版本兼容性** - 支持不同版本的LangGraph API
5. **安全文件命名** - 确保所有生成的文件名有效

## 环境要求

- Python 3.8+
- 依赖库：langchain、langgraph、openai等（详见requirements.txt）
- OpenAI API密钥

## 配置

在系统目录下创建一个`.env`文件，包含您的API密钥：

```
OPENAI_API_KEY=your_api_key_here
```

## 故障排除

如果遇到问题，请检查：

1. API密钥是否正确设置
2. 依赖库是否完整安装
3. 网络连接是否正常
4. 输出目录是否具有写入权限

## 系统架构

- `multi_agent_writing.py` - 核心写作系统实现，包含所有智能体和工作流定义
- `multi_agent_writing_ui.py` - 交互式命令行界面，方便用户与系统交互
- `example.py` - 示例代码，演示如何以编程方式使用写作系统

## 安装方法

1. 克隆代码库：
```bash
git clone https://github.com/yourusername/multi-agent-writing.git
cd multi-agent-writing
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置API密钥：
创建`.env`文件，并添加您的OpenAI API密钥：
```
OPENAI_API_KEY=your_api_key_here
```

## 自定义和扩展

您可以通过修改`multi_agent_writing.py`来自定义智能体的行为或添加新的智能体。系统的核心是基于LangGraph的工作流引擎，您可以根据需要调整工作流图结构。

### 添加新智能体

要添加新智能体，请按照以下步骤操作：

1. 在`multi_agent_writing.py`中定义新的智能体函数
2. 在`create_workflow()`函数中添加新节点
3. 更新`decide_next_step()`函数以包含新节点

## 贡献指南

欢迎提交问题和改进建议！请通过GitHub Issues或Pull Requests贡献您的想法。

## 许可证

MIT
