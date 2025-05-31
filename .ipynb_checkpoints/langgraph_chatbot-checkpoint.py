from dotenv import load_dotenv
load_dotenv()

from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import pandas as pd
import json
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.checkpoint.memory import MemorySaver

# 定义 Tavily 搜索工具，最大搜索结果数设置为 2
tool = TavilySearchResults(max_results=2)
tools = [tool]


class State(TypedDict):
    messages: Annotated[list, add_messages]


# 定义 BasicToolNode，用于执行工具请求
class BasicToolNode:
    """一个在最后一条 AIMessage 中执行工具请求的节点。
    
    该节点会检查最后一条 AI 消息中的工具调用请求，并依次执行这些工具调用。
    """

    def __init__(self, tools: list) -> None:
        # tools 是一个包含所有可用工具的列表，我们将其转化为字典，
        # 通过工具名称（tool.name）来访问具体的工具
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, state: State) -> State:
        """执行工具调用
        
        参数:
        state: 包含 "messages" 键的字典，"messages" 是对话消息的列表，
              其中最后一条消息可能包含工具调用的请求。
        
        返回:
        更新后的状态，包含所有原始消息和工具调用结果
        """
        messages = state["messages"]
        if not messages:
            raise ValueError("输入中未找到消息")
        
        # 获取最后一条消息（应该是AI消息，包含工具调用）
        last_message = messages[-1]
        
        # 用于保存工具调用的结果
        new_messages = list(messages)  # 复制原始消息列表
        
        # 遍历工具调用请求，执行工具并将结果添加到消息历史
        for tool_call in last_message.tool_calls:
            # 根据工具名称找到相应的工具，并调用工具的 invoke 方法执行工具
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            tool_result = self.tools_by_name[tool_name].invoke(tool_args)
            
            # 将工具调用结果作为 ToolMessage 添加到消息历史
            new_messages.append(
                ToolMessage(
                    content=json.dumps(tool_result),  # 工具调用的结果以 JSON 格式保存
                    name=tool_name,  # 工具的名称
                    tool_call_id=tool_id,  # 工具调用的唯一标识符
                )
            )
        
        # 返回更新后的状态
        return {"messages": new_messages}


# 创建状态图
graph_builder = StateGraph(State)

# 初始化 OpenAI 聊天模型
chat_model = ChatOpenAI(model="deepseek-chat")

# 将工具绑定到聊天模型
llm_with_tools = chat_model.bind_tools(tools)

# 定义聊天机器人节点函数
def chatbot(state: State) -> State:
    """处理消息并生成回复"""
    messages = state["messages"]
    
    # 使用 LLM 处理消息并生成回复
    response = llm_with_tools.invoke(messages)
    
    # 将 AI 回复添加到消息列表
    new_messages = list(messages)
    new_messages.append(response)
    
    return {"messages": new_messages}

# 添加聊天机器人节点
graph_builder.add_node("chatbot", chatbot)

# 创建工具节点实例并添加到图中
tool_node = BasicToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

from typing import Literal

# 定义路由函数，检查工具调用
def route_tools(state: State) -> Literal["tools", "__end__"]:
    """
    使用条件边来检查最后一条消息中是否有工具调用。
    
    参数:
    state: 状态字典，用于存储当前对话的状态和消息。
    
    返回:
    如果最后一条消息包含工具调用，返回 "tools" 节点，表示需要执行工具调用；
    否则返回 "__end__"，表示直接结束流程。
    """
    messages = state["messages"]
    if not messages:
        return "__end__"
    
    # 获取最后一条消息
    last_message = messages[-1]
    
    # 检查最后一条消息是否有工具调用请求
    if (isinstance(last_message, AIMessage) and 
        hasattr(last_message, "tool_calls") and 
        last_message.tool_calls):
        return "tools"  # 如果有工具调用请求，返回 "tools" 节点
    
    return "__end__"  # 否则返回 "__end__"，流程结束

# 构建图的边
graph_builder.add_edge(START, "chatbot")

# 添加条件边，判断是否需要调用工具
graph_builder.add_conditional_edges(
    "chatbot",  # 从聊天机器人节点开始
    route_tools,  # 路由函数，决定下一个节点
    {
        "tools": "tools",  # 如果需要工具调用，转到工具节点
        "__end__": END     # 如果不需要工具调用，结束当前流程
    }
)

# 当工具调用完成后，返回到聊天机器人节点以继续对话
graph_builder.add_edge("tools", "chatbot")

# 创建内存检查点
memory = MemorySaver()

# 编译图
graph = graph_builder.compile(checkpointer=memory)

# 可选：生成可视化图表
graph.get_graph().draw_mermaid_png(output_file_path="chatbot.png")

# 主循环
# while True:
#     # 获取用户输入
#     user_input = input("User: ")
    
#     # 可以随时通过输入 "quit"、"exit" 或 "q" 退出聊天循环
#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")  # 打印告别信息
#         break  # 结束循环，退出聊天

#     # 创建包含用户消息的初始状态
#     human_message = HumanMessage(content=user_input)
#     initial_state = {"messages": [human_message]}
    
#     # 使用 graph.stream 处理用户输入，获取聊天机器人的回复
#     for event in graph.stream(initial_state):
#         for value in event.values():
#             # 获取最新消息
#             messages = value.get("messages", [])
#             if messages and isinstance(messages[-1], AIMessage):
#                 # 打印 AI 消息内容
#                 print("Assistant:", messages[-1].content)

config = {"configurable": {"thread_id": "1"}}

# 用户输入的消息
user_input = "Hi there! My name is Peng."

# 第二个参数 config 用于设置对话线程 ID
# 在这里，"thread_id" 是唯一标识符，用于保存和区分对话线程。
# 每个对话线程的状态将由 MemorySaver 保存下来，因此可以跨多轮对话继续进行。
events = graph.stream(
    {"messages": [HumanMessage(content=user_input)]},  # 第一个参数传入用户的输入消息，消息格式为 ("user", "输入内容")
    config,  # 第二个参数用于指定线程配置，包含线程 ID
    stream_mode="values"  # stream_mode 设置为 "values"，表示返回流式数据的值
)

# 遍历每个事件，并打印最后一条消息的内容
for event in events:
    # 通过 pretty_print 打印最后一条消息的内容
    event["messages"][-1].pretty_print()

user_input = "Remember my name?"

events = graph.stream(
    {"messages": [HumanMessage(content=user_input)]},
    config,
    stream_mode="values"
)

for event in events:
    event["messages"][-1].pretty_print()

snapshot = graph.get_state(config)

messages = snapshot.values['messages']
df = pd.DataFrame([{
    'content': msg.content,
    'message_id': msg.id,
    'type': type(msg).__name__,
    'token_usage': msg.response_metadata.get('token_usage') if hasattr(msg, 'response_metadata') else None
} for msg in messages])

df.to_csv('messages.csv', index=False)