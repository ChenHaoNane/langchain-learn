"""
工作流管理模块 - 处理LangGraph相关功能
"""

import sys
from typing import Dict, Any

# 兼容不同版本的LangGraph导入
try:
    from langgraph.graph import START, END, StateGraph
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_VERSION = "0.2.x"
    END_CONSTANT = END
except ImportError:
    try:
        # 尝试导入更新版本的LangGraph
        from langgraph.graph import StateGraph
        from langgraph.graph.graph import START, END
        from langgraph.checkpoint.memory import MemorySaver
        LANGGRAPH_VERSION = "0.4.x"
        END_CONSTANT = END
    except ImportError:
        print("错误：未找到LangGraph。请安装LangGraph: pip install langgraph")
        sys.exit(1)

from multi_agent_system.core.state import AgentState

class WorkflowManager:
    """工作流管理器，处理LangGraph状态图的创建和执行"""
    
    def __init__(self):
        """初始化工作流管理器"""
        self.memory = MemorySaver()
        self.graph_builder = None
        self.compiled_app = None
        self.version = LANGGRAPH_VERSION
        print(f"使用 LangGraph 版本: {self.version}")
    
    def create_workflow(self, decision_fn):
        """
        创建工作流图
        
        Args:
            decision_fn: 决策函数，用于确定下一步执行的节点
        
        Returns:
            StateGraph: 创建的工作流图
        """
        # 初始化工作流
        self.graph_builder = StateGraph(AgentState)
        return self.graph_builder
    
    def add_node(self, name, function):
        """
        添加节点到工作流图
        
        Args:
            name: 节点名称
            function: 节点函数
        """
        if self.graph_builder:
            self.graph_builder.add_node(name, function)
    
    def set_entry_point(self, node_name):
        """
        设置入口点
        
        Args:
            node_name: 入口节点名称
        """
        if self.graph_builder:
            self.graph_builder.set_entry_point(node_name)
    
    def add_edge(self, start_node, end_node):
        """
        添加边
        
        Args:
            start_node: 起始节点
            end_node: 结束节点
        """
        if self.graph_builder:
            self.graph_builder.add_edge(start_node, end_node)
    
    def add_conditional_edges(self, node, decision_fn, routes):
        """
        添加条件边
        
        Args:
            node: 起始节点
            decision_fn: 决策函数
            routes: 路由字典
        """
        if self.graph_builder:
            # 处理END常量
            if "END" in routes:
                routes[END_CONSTANT] = routes.pop("END")
                
            self.graph_builder.add_conditional_edges(
                node,
                decision_fn,
                routes
            )
    
    def compile(self):
        """
        编译工作流
        
        Returns:
            已编译的工作流应用
        """
        if not self.graph_builder:
            raise ValueError("工作流图尚未创建")
        
        print("编译工作流...")
        self.compiled_app = self.graph_builder.compile(checkpointer=self.memory)
        print("工作流准备就绪!")
        return self.compiled_app
    
    def get_state(self, config):
        """
        安全获取工作流状态
        
        Args:
            config: 配置参数
            
        Returns:
            Dict: 标准化的状态字典
        """
        if not self.compiled_app:
            raise ValueError("工作流尚未编译")
        
        try:
            state = self.compiled_app.get_state(config)
            
            # 处理StateSnapshot对象
            if hasattr(state, 'values'):
                # 新版本返回StateSnapshot对象
                workspace = state.values.get("workspace", {}) if hasattr(state.values, 'get') else {}
                messages = state.values.get("messages", []) if hasattr(state.values, 'get') else []
                
                return {
                    "messages": messages,
                    "workspace": workspace
                }
            elif isinstance(state, dict):
                # 旧版本直接返回字典
                return state
            else:
                # 未知类型，返回空状态
                print(f"警告：未知状态类型 {type(state)}，返回空状态")
                return {"messages": [], "workspace": {}}
        except Exception as e:
            print(f"获取状态时出错: {e}")
            return {"messages": [], "workspace": {}}
    
    def visualize(self, output_file_path="workflow.png"):
        """
        可视化工作流图
        
        Args:
            output_file_path: 输出文件路径
        """
        if not self.compiled_app:
            raise ValueError("工作流尚未编译")
        
        try:
            self.compiled_app.get_graph().draw_mermaid_png(output_file_path=output_file_path)
            print(f"已生成工作流图: {output_file_path}")
        except Exception as e:
            print(f"生成工作流图失败: {e}")

# 创建全局实例
workflow_manager = WorkflowManager() 