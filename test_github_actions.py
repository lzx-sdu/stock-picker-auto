#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 环境测试脚本
"""

import sys
import os
from datetime import datetime

def test_environment():
    """测试环境"""
    print("🔍 测试GitHub Actions环境...")
    print("=" * 50)
    
    # 测试Python版本
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    # 测试工作目录
    print(f"当前工作目录: {os.getcwd()}")
    print(f"目录内容: {os.listdir('.')}")
    
    # 测试src目录
    if os.path.exists('src'):
        print("✅ src目录存在")
        print(f"src目录内容: {os.listdir('src')}")
        
        # 测试子目录
        for subdir in ['strategy', 'analysis', 'utils']:
            subdir_path = os.path.join('src', subdir)
            if os.path.exists(subdir_path):
                print(f"✅ {subdir}目录存在: {os.listdir(subdir_path)}")
            else:
                print(f"❌ {subdir}目录不存在")
    else:
        print("❌ src目录不存在")
    
    # 测试主程序文件
    if os.path.exists('bollinger_strategy_runner.py'):
        print("✅ 主程序文件存在")
    else:
        print("❌ 主程序文件不存在")
    
    # 测试requirements.txt
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt存在")
    else:
        print("❌ requirements.txt不存在")
    
    # 测试Python路径
    print(f"Python路径: {sys.path}")
    
    # 测试模块导入
    try:
        sys.path.insert(0, 'src')
        from strategy.bollinger_mean_reversion import BollingerMeanReversionStrategy
        from analysis.stock_screener import StockScreener
        from analysis.report_generator import ReportGenerator
        from utils.config import Config
        print("✅ 所有模块导入成功")
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
    
    # 创建测试结果
    test_result = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'files_exist': {
            'src': os.path.exists('src'),
            'main_program': os.path.exists('bollinger_strategy_runner.py'),
            'requirements': os.path.exists('requirements.txt')
        }
    }
    
    # 保存测试结果
    os.makedirs('results', exist_ok=True)
    with open('results/test_result.txt', 'w', encoding='utf-8') as f:
        f.write(str(test_result))
    
    print("=" * 50)
    print("✅ 环境测试完成，结果保存到 results/test_result.txt")
    
    return test_result

if __name__ == "__main__":
    test_environment()
