#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件检查脚本
"""

import os

def check_files():
    """检查所有必要文件"""
    print("🔍 检查必要文件...")
    print("=" * 50)
    
    # 当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    print()
    
    # 需要检查的文件
    files_to_check = [
        "stock_picker/bollinger_strategy_runner.py",
        "requirements.txt",
        ".github/workflows/daily_stock_screening.yml",
        "deploy_to_github.py"
    ]
    
    all_exist = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - 存在")
        else:
            print(f"❌ {file_path} - 不存在")
            all_exist = False
    
    print()
    
    if all_exist:
        print("🎉 所有文件都存在！可以开始部署。")
        print()
        print("下一步操作:")
        print("1. 运行: python deploy_to_github.py")
        print("2. 按提示输入GitHub仓库URL")
        print("3. 等待部署完成")
    else:
        print("⚠️ 部分文件缺失，请检查文件结构。")
        print()
        print("当前目录文件列表:")
        for item in os.listdir("."):
            if os.path.isfile(item):
                print(f"  📄 {item}")
            elif os.path.isdir(item):
                print(f"  📁 {item}/")
        
        print()
        print("stock_picker目录文件列表:")
        if os.path.exists("stock_picker"):
            for item in os.listdir("stock_picker"):
                if os.path.isfile(os.path.join("stock_picker", item)):
                    print(f"  📄 {item}")
                elif os.path.isdir(os.path.join("stock_picker", item)):
                    print(f"  📁 {item}/")

if __name__ == "__main__":
    check_files()

