#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    try:
        from src.utils.config import Config
        print("✓ Config模块导入成功")
        
        from src.utils.logger import setup_logger
        print("✓ Logger模块导入成功")
        
        from src.data.stock_data import StockDataManager
        print("✓ StockDataManager模块导入成功")
        
        from src.analysis.bollinger_bands import BollingerBands
        print("✓ BollingerBands模块导入成功")
        
        from src.analysis.stock_screener import StockScreener
        print("✓ StockScreener模块导入成功")
        
        from src.strategy.mean_reversion import MeanReversionStrategy
        print("✓ MeanReversionStrategy模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 模块导入失败: {str(e)}")
        return False

def test_config():
    """测试配置加载"""
    try:
        from src.utils.config import Config
        config = Config("config.yaml")
        print("✓ 配置文件加载成功")
        
        # 测试配置获取
        bb_config = config.get_bollinger_config()
        screening_config = config.get_screening_config()
        
        print(f"✓ 布林带配置: {bb_config}")
        print(f"✓ 筛选配置: {screening_config}")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置加载失败: {str(e)}")
        return False

def test_bollinger_calculation():
    """测试布林带计算"""
    try:
        import pandas as pd
        import numpy as np
        from src.utils.config import Config
        from src.analysis.bollinger_bands import BollingerBands
        
        # 创建测试数据
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        prices = np.random.randn(30).cumsum() + 100  # 模拟价格数据
        
        data = pd.DataFrame({
            'close': prices,
            'open': prices * 0.99,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'volume': np.random.randint(1000000, 10000000, 30)
        }, index=dates)
        
        # 测试布林带计算
        config = Config("config.yaml")
        bb = BollingerBands(config)
        
        result = bb.calculate(data)
        
        if not result.empty and 'upper_band' in result.columns:
            print("✓ 布林带计算成功")
            print(f"  最新价格: {result['close'].iloc[-1]:.2f}")
            print(f"  上轨: {result['upper_band'].iloc[-1]:.2f}")
            print(f"  下轨: {result['lower_band'].iloc[-1]:.2f}")
            return True
        else:
            print("✗ 布林带计算失败")
            return False
            
    except Exception as e:
        print(f"✗ 布林带计算测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("A股布林带均值回归选股系统 - 简单测试")
    print("=" * 50)
    
    tests = [
        ("模块导入测试", test_imports),
        ("配置加载测试", test_config),
        ("布林带计算测试", test_bollinger_calculation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  {test_name}失败")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！项目可以正常运行。")
    else:
        print("✗ 部分测试失败，请检查错误信息。")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 