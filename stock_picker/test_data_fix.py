#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据获取修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.data.stock_data import StockDataManager

def test_stock_data_fix():
    """测试股票数据获取修复"""
    print("=" * 50)
    print("测试股票数据获取修复")
    print("=" * 50)
    
    try:
        # 初始化配置和数据管理器
        config = Config("config.yaml")
        data_manager = StockDataManager(config)
        
        print("✓ 配置和数据管理器初始化成功")
        
        # 测试获取股票列表
        print("\n1. 测试获取股票列表...")
        stock_list = data_manager.get_stock_list()
        print(f"✓ 成功获取股票列表，共 {len(stock_list)} 只股票")
        
        # 显示前5只股票的信息
        print("\n前5只股票信息:")
        for idx, row in stock_list.head().iterrows():
            print(f"  代码: {row['code']} (类型: {type(row['code'])})")
            print(f"  名称: {row['name']}")
            print(f"  市场: {row['market']}")
            print()
        
        # 测试获取单只股票数据
        print("2. 测试获取单只股票数据...")
        if len(stock_list) > 0:
            # 使用更标准的股票代码进行测试
            test_stock = "000001"  # 平安银行
            print(f"测试股票代码: {test_stock} (类型: {type(test_stock)})")
            
            data = data_manager.get_stock_data(test_stock)
            if not data.empty:
                print(f"✓ 成功获取股票 {test_stock} 的数据")
                print(f"  数据行数: {len(data)}")
                print(f"  最新价格: {data['close'].iloc[-1]:.2f}")
                print(f"  数据列: {list(data.columns)}")
            else:
                print(f"✗ 获取股票 {test_stock} 数据失败")
        else:
            print("✗ 没有股票列表可测试")
        
        print("\n" + "=" * 50)
        print("✓ 数据获取修复测试完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_data_fix()
