#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多智能体写作系统 - 启动界面
"""

import os
import sys
from pathlib import Path

def main():
    """主函数，用于启动多智能体写作系统界面"""
    # 获取当前脚本目录
    script_dir = Path(__file__).resolve().parent
    
    # 检查界面文件是否存在
    ui_file = script_dir / "multi_agent_writing_ui.py"
    if not ui_file.exists():
        print(f"错误: 找不到界面文件 {ui_file}")
        sys.exit(1)
    
    # 打印版本信息
    try:
        import gradio
        print(f"Gradio版本: {gradio.__version__}")
        if gradio.__version__.startswith("4."):
            print("✅ 已启用实时进度显示功能")
        else:
            print("⚠️ 当前Gradio版本不支持实时进度显示，建议升级")
    except ImportError:
        print("⚠️ 未检测到Gradio库，请安装: pip install --upgrade gradio")
    
    # 启动界面
    print("\n正在启动多智能体写作系统界面...")
    print("系统准备就绪后，请在浏览器中访问: http://127.0.0.1:7860")
    print("启动过程可能需要几秒钟，请耐心等待...\n")
    os.system(f"python {ui_file}")

if __name__ == "__main__":
    main() 