#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试选股功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.data.stock_data import StockDataManager
from src.analysis.stock_screener import StockScreener

def test_screening():
    """测试选股功能"""
    print("=" * 50)
    print("测试选股功能")
    print("=" * 50)
    
    try:
        # 初始化配置和数据管理器
        config = Config("config.yaml")
        data_manager = StockDataManager(config)
        screener = StockScreener(config)
        
        print("✓ 配置和组件初始化成功")
        
        # 获取股票列表（限制数量进行测试）
        print("\n1. 获取股票列表...")
        stock_list = data_manager.get_stock_list()
        print(f"✓ 成功获取股票列表，共 {len(stock_list)} 只股票")
        
        # 选择前10只股票进行测试
        test_stocks = stock_list.head(10)
        print(f"选择前 {len(test_stocks)} 只股票进行测试")
        
        # 测试单只股票的数据获取和筛选
        print("\n2. 测试单只股票筛选...")
        success_count = 0
        
        for idx, row in test_stocks.iterrows():
            stock_code = row['code']
            stock_name = row['name']
            print(f"\n处理股票: {stock_code} ({stock_name})")
            
            try:
                # 获取股票数据
                data = data_manager.get_stock_data(stock_code)
                if data.empty:
                    print(f"  ✗ 无法获取数据")
                    continue
                
                print(f"  ✓ 获取数据成功，行数: {len(data)}")
                
                # 测试布林带计算
                from src.analysis.bollinger_bands import BollingerBands
                bb = BollingerBands(config)
                bb_data = bb.calculate(data)
                
                if not bb_data.empty:
                    print(f"  ✓ 布林带计算成功")
                    latest = bb_data.iloc[-1]
                    print(f"    最新价格: {latest['close']:.2f}")
                    print(f"    布林带上轨: {latest['upper_band']:.2f}")
                    print(f"    布林带下轨: {latest['lower_band']:.2f}")
                    print(f"    布林带位置: {latest['bb_position']:.2f}")
                    
                    # 检查是否符合筛选条件
                    if latest['bb_position'] < 0.3:  # 接近下轨
                        print(f"  ✓ 符合筛选条件（接近下轨）")
                        success_count += 1
                    else:
                        print(f"  ✗ 不符合筛选条件")
                else:
                    print(f"  ✗ 布林带计算失败")
                    
            except Exception as e:
                print(f"  ✗ 处理失败: {str(e)}")
        
        print(f"\n" + "=" * 50)
        print(f"测试完成: {success_count}/{len(test_stocks)} 只股票符合条件")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_screening()

