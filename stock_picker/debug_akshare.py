#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试akshare API
"""

import akshare as ak
import pandas as pd

def test_akshare_api():
    """测试akshare API"""
    print("=" * 50)
    print("测试akshare API")
    print("=" * 50)
    
    try:
        # 测试获取股票列表
        print("1. 测试获取股票列表...")
        stock_list = ak.stock_info_a_code_name()
        print(f"✓ 成功获取股票列表，共 {len(stock_list)} 只股票")
        print(f"列名: {list(stock_list.columns)}")
        print(f"前3行数据:")
        print(stock_list.head(3))
        
        # 测试获取单只股票数据
        print("\n2. 测试获取单只股票数据...")
        test_stock = "000001"  # 平安银行
        print(f"测试股票代码: {test_stock}")
        
        # 测试不同的股票代码格式
        test_codes = [
            test_stock,
            f"sz{test_stock}",
            f"sh{test_stock}"
        ]
        
        for code in test_codes:
            print(f"\n尝试代码: {code}")
            try:
                # 测试不同的日期范围
                date_ranges = [
                    ("2024-01-01", "2024-01-31"),
                    ("2024-12-01", "2024-12-31"),
                    ("2025-01-01", "2025-01-31"),
                    ("2025-07-01", "2025-07-31")
                ]
                
                for start_date, end_date in date_ranges:
                    print(f"  尝试日期范围: {start_date} 到 {end_date}")
                    data = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                             start_date=start_date, end_date=end_date, 
                                             adjust="qfq")
                    print(f"  ✓ 成功获取数据，行数: {len(data)}")
                    if len(data) > 0:
                        print(f"  列名: {list(data.columns)}")
                        print(f"  前3行数据:")
                        print(data.head(3))
                        return
                    else:
                        print(f"  ✗ 数据为空")
                        
            except Exception as e:
                print(f"✗ 失败: {str(e)}")
        
        print("\n" + "=" * 50)
        print("✓ akshare API测试完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_akshare_api()
