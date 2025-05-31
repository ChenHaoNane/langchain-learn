#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多智能体写作系统入口文件
"""

import os
import sys
import argparse
import time
from typing import Dict, Any, Optional, Callable
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 尝试导入END常量
try:
    from langgraph.graph import END
except ImportError:
    try:
        from langgraph.graph.graph import END
    except ImportError:
        # 如果无法导入，使用字符串
        END = "END"

# 导入核心组件
from multi_agent_system.core.workflow import workflow_manager
from multi_agent_system.core.state import AgentState
from multi_agent_system.agents import (
    outline_agent,
    content_agent,
    editing_agent,
    revision_agent,
    finalization_agent,
    decide_next_step
)
from multi_agent_system.utils.file_utils import save_to_file, save_content_to_file, generate_timestamped_filename
from multi_agent_system.utils.llm_utils import get_llm_manager
from multi_agent_system.config.settings import DEFAULT_TOPIC, DEFAULT_OUTPUT_DIR
from multi_agent_system.utils.batch_processor import batch_processor

def initialize_system() -> None:
    """
    初始化多智能体写作系统
    """
    print("初始化多智能体写作系统...")
    
    # 创建工作流图
    workflow = workflow_manager.create_workflow(decide_next_step)
    
    # 添加智能体节点
    workflow_manager.add_node("outline_agent", outline_agent)
    workflow_manager.add_node("content_agent", content_agent)
    workflow_manager.add_node("editing_agent", editing_agent)
    workflow_manager.add_node("revision_agent", revision_agent)
    workflow_manager.add_node("finalization_agent", finalization_agent)
    
    # 设置入口节点
    workflow_manager.set_entry_point("outline_agent")
    
    # 添加条件边
    workflow_manager.add_conditional_edges(
        "outline_agent",
        decide_next_step,
        {
            "content_agent": "content_agent",
            "editing_agent": "editing_agent",
            "revision_agent": "revision_agent",
            "finalization_agent": "finalization_agent",
            END: END  # 使用END常量
        }
    )
    
    workflow_manager.add_conditional_edges(
        "content_agent",
        decide_next_step,
        {
            "outline_agent": "outline_agent",
            "editing_agent": "editing_agent",
            "revision_agent": "revision_agent",
            "finalization_agent": "finalization_agent",
            END: END  # 使用END常量
        }
    )
    
    workflow_manager.add_conditional_edges(
        "editing_agent",
        decide_next_step,
        {
            "outline_agent": "outline_agent",
            "content_agent": "content_agent",
            "revision_agent": "revision_agent",
            "finalization_agent": "finalization_agent",
            END: END  # 使用END常量
        }
    )
    
    workflow_manager.add_conditional_edges(
        "revision_agent",
        decide_next_step,
        {
            "outline_agent": "outline_agent",
            "content_agent": "content_agent",
            "editing_agent": "editing_agent",
            "finalization_agent": "finalization_agent",
            END: END  # 使用END常量
        }
    )
    
    workflow_manager.add_conditional_edges(
        "finalization_agent",
        decide_next_step,
        {
            "outline_agent": "outline_agent",
            "content_agent": "content_agent",
            "editing_agent": "editing_agent",
            "revision_agent": "revision_agent",
            END: END  # 使用END常量
        }
    )
    
    # 编译工作流
    return workflow_manager.compile()

def create_initial_state(topic: str, style: Optional[str] = None) -> AgentState:
    """
    创建初始状态
    
    Args:
        topic: 写作主题
        style: 写作风格（可选）
        
    Returns:
        初始状态对象
    """
    from langchain_core.messages import HumanMessage
    
    # 创建初始消息
    if style:
        initial_message = f"请为我写一篇关于 '{topic}' 的文章，使用 '{style}' 风格。"
    else:
        initial_message = f"请为我写一篇关于 '{topic}' 的文章。"
    
    messages = [HumanMessage(content=initial_message)]
    
    # 创建初始工作空间
    workspace = {
        "topic": topic,
        "style": style,
        "status": "initialized"
    }
    
    return {
        "messages": messages,
        "workspace": workspace
    }

def run_writing_system(
    topic: str, 
    style: Optional[str] = None, 
    output_dir: str = DEFAULT_OUTPUT_DIR,
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Dict[str, Any]:
    """
    运行多智能体写作系统
    
    Args:
        topic: 写作主题
        style: 写作风格（可选）
        output_dir: 输出目录
        progress_callback: 进度回调函数，接收进度值(0-1)和状态描述
        
    Returns:
        系统最终状态
    """
    from multi_agent_system.utils.batch_processor import batch_processor
    from multi_agent_system.config.settings import PRIORITY_MODE
    
    start_time = time.time()
    print(f"开始为主题 '{topic}' 创作文章...")
    print(f"模式: {'速度优先' if PRIORITY_MODE == 'speed' else '质量优先'}")
    
    # 进度更新
    if progress_callback:
        progress_callback(0.1, "初始化系统...")
    
    # 初始化系统
    app = initialize_system()
    
    # 创建初始状态
    initial_state = create_initial_state(topic, style)
    
    # 优化配置
    optimization_config = batch_processor.optimize_workflow(initial_state)
    parallel_tasks = optimization_config.get("parallel_tasks", False)
    
    # 将优化配置添加到初始状态
    initial_state["workspace"]["optimization"] = optimization_config
    
    # 运行工作流
    print("启动多智能体写作流程...")
    config = {
        "configurable": {
            "thread_id": topic.replace(" ", "_"),
            "optimization": optimization_config
        }
    }
    
    try:
        # 使用带时间统计的执行方式
        process_start = time.time()
        
        # 更新进度 - 开始处理
        if progress_callback:
            progress_callback(0.2, "创建大纲...")
        
        result = app.invoke(initial_state, config)
        
        # 更新进度 - 完成处理
        if progress_callback:
            progress_callback(0.8, "完成工作流...")
        
        process_end = time.time()
        print(f"⏱️ 工作流执行时间: {process_end - process_start:.2f}秒")
        
        # 获取最终结果
        final_state = workflow_manager.get_state(config)
    except Exception as e:
        print(f"运行工作流时出错: {e}")
        if progress_callback:
            progress_callback(1.0, f"错误: {str(e)}")
        return initial_state
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 更新进度 - 保存文件
    if progress_callback:
        progress_callback(0.9, "保存文件...")
    
    # 保存最终内容
    workspace = final_state.get("workspace", {})
    output_path = None
    
    if "final_content" in workspace:
        final_content = workspace["final_content"]
        # 使用时间戳文件名
        filename = generate_timestamped_filename(topic)
        output_path = os.path.join(output_dir, filename)
        try:
            save_to_file(final_content, output_path, title=topic)
            # 将文件路径保存到工作空间
            workspace["output_file"] = output_path
            
            end_time = time.time()
            duration = end_time - start_time
            print(f"✅ 成功创建文章！保存至：{output_path}")
            print(f"⏱️ 总耗时: {duration:.2f}秒")
        except Exception as e:
            print(f"❌ 保存文件时出错: {e}")
    else:
        print("⚠️ 警告：未能生成最终内容")
        # 尝试保存最后一个可用的内容版本
        for content_key in ["revised_content", "content", "outline"]:
            if content_key in workspace:
                fallback_content = workspace[content_key]
                fallback_filename = generate_timestamped_filename(topic, stage=content_key)
                fallback_path = os.path.join(output_dir, fallback_filename)
                try:
                    save_to_file(fallback_content, fallback_path, title=f"{topic} ({content_key})")
                    # 将文件路径保存到工作空间
                    workspace["output_file"] = fallback_path
                    print(f"✅ 已保存{content_key}版本到：{fallback_path}")
                    break
                except Exception:
                    continue
    
    # 更新进度 - 完成
    if progress_callback:
        progress_callback(1.0, "完成!")
    
    return final_state

def interactive_mode() -> None:
    """
    交互模式运行系统
    """
    try:
        # 获取LLM管理器以确保API密钥已设置
        llm_manager = get_llm_manager()
        
        print("=== 多智能体写作系统 ===")
        print("请输入写作主题和风格(可选)")
        
        topic = input("写作主题: ").strip() or DEFAULT_TOPIC
        style = input("写作风格 (可选，按回车跳过): ").strip() or None
        
        # 运行系统
        final_state = run_writing_system(topic, style)
        
        # 打印状态摘要
        workspace = final_state.get("workspace", {})
        print("\n--- 写作流程完成 ---")
        print(f"大纲: {'✅ 已生成' if 'outline' in workspace else '❌ 未生成'}")
        print(f"初始内容: {'✅ 已生成' if 'content' in workspace else '❌ 未生成'}")
        print(f"编辑建议: {'✅ 已生成' if 'editing_suggestions' in workspace else '❌ 未生成'}")
        print(f"修订内容: {'✅ 已生成' if 'revised_content' in workspace else '❌ 未生成'}")
        print(f"最终内容: {'✅ 已生成' if 'final_content' in workspace else '❌ 未生成'}")
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        sys.exit(1)

def main() -> None:
    """
    主函数
    """
    try:
        parser = argparse.ArgumentParser(description='多智能体写作系统')
        parser.add_argument('--topic', type=str, default=None, help='写作主题')
        parser.add_argument('--style', type=str, default=None, help='写作风格')
        parser.add_argument('--output-dir', type=str, default=DEFAULT_OUTPUT_DIR, help='输出目录')
        parser.add_argument('--interactive', action='store_true', help='交互模式')
        parser.add_argument('--visualize', action='store_true', help='生成工作流程图')
        
        # 性能优化参数
        performance_group = parser.add_argument_group('性能优化')
        performance_group.add_argument('--enable-cache', action='store_true', help='启用LLM响应缓存')
        performance_group.add_argument('--disable-cache', action='store_true', help='禁用LLM响应缓存')
        performance_group.add_argument('--parallel', type=int, default=None, help='并行处理的任务数')
        performance_group.add_argument('--priority', choices=['speed', 'quality'], default=None, 
                                      help='处理优先级：speed（速度）或quality（质量）')
        
        args = parser.parse_args()
        
        # 处理性能优化设置
        from multi_agent_system.config.settings import ENABLE_CACHING, MAX_PARALLEL_CALLS, PRIORITY_MODE
        import multi_agent_system.config.settings as settings
        
        if args.enable_cache and not args.disable_cache:
            settings.ENABLE_CACHING = True
            print("✅ 已启用LLM响应缓存")
        elif args.disable_cache and not args.enable_cache:
            settings.ENABLE_CACHING = False
            print("⚠️ 已禁用LLM响应缓存")
            
        if args.parallel is not None and args.parallel > 0:
            settings.MAX_PARALLEL_CALLS = args.parallel
            print(f"✅ 并行任务数设置为: {args.parallel}")
            
        if args.priority:
            settings.PRIORITY_MODE = args.priority
            mode_str = "速度优先" if args.priority == "speed" else "质量优先"
            print(f"✅ 优先模式设置为: {mode_str}")
        
        if args.visualize:
            # 初始化系统并生成可视化
            initialize_system()
            workflow_manager.visualize("writing_workflow.png")
            print("已生成工作流程图: writing_workflow.png")
            return
        
        if args.interactive or not args.topic:
            interactive_mode()
        else:
            # 确保输出目录存在
            os.makedirs(args.output_dir, exist_ok=True)
            run_writing_system(args.topic, args.style, args.output_dir)
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 