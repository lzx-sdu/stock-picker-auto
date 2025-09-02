#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试akshare API - 替代方法
"""

import akshare as ak
import pandas as pd

def test_akshare_alternative():
    """测试akshare替代API"""
    print("=" * 50)
    print("测试akshare替代API")
    print("=" * 50)
    
    try:
        # 测试不同的股票数据获取方法
        test_stock = "000001"  # 平安银行
        
        print(f"测试股票代码: {test_stock}")
        
        # 方法1: stock_zh_a_hist
        print("\n1. 测试 stock_zh_a_hist...")
        try:
            data1 = ak.stock_zh_a_hist(symbol=test_stock, period="daily", 
                                      start_date="2024-01-01", end_date="2024-01-31", 
                                      adjust="qfq")
            print(f"✓ 成功获取数据，行数: {len(data1)}")
            if len(data1) > 0:
                print(f"列名: {list(data1.columns)}")
        except Exception as e:
            print(f"✗ 失败: {str(e)}")
        
        # 方法2: stock_zh_a_daily
        print("\n2. 测试 stock_zh_a_daily...")
        try:
            data2 = ak.stock_zh_a_daily(symbol=test_stock)
            print(f"✓ 成功获取数据，行数: {len(data2)}")
            if len(data2) > 0:
                print(f"列名: {list(data2.columns)}")
                print(f"最新数据:")
                print(data2.tail(3))
        except Exception as e:
            print(f"✗ 失败: {str(e)}")
        
        # 方法3: stock_zh_a_hist_min_em
        print("\n3. 测试 stock_zh_a_hist_min_em...")
        try:
            data3 = ak.stock_zh_a_hist_min_em(symbol=test_stock, period='daily', 
                                             start_date='2024-01-01', end_date='2024-01-31', 
                                             adjust='qfq')
            print(f"✓ 成功获取数据，行数: {len(data3)}")
            if len(data3) > 0:
                print(f"列名: {list(data3.columns)}")
        except Exception as e:
            print(f"✗ 失败: {str(e)}")
        
        # 方法4: 测试不同的股票代码格式
        print("\n4. 测试不同的股票代码格式...")
        test_codes = ["000001", "sz000001", "sh000001", "000001.SZ"]
        
        for code in test_codes:
            print(f"\n尝试代码: {code}")
            try:
                data = ak.stock_zh_a_daily(symbol=code)
                print(f"✓ 成功获取数据，行数: {len(data)}")
                if len(data) > 0:
                    print(f"列名: {list(data.columns)}")
                    print(f"最新价格: {data['close'].iloc[-1] if 'close' in data.columns else 'N/A'}")
                    break
            except Exception as e:
                print(f"✗ 失败: {str(e)}")
        
        print("\n" + "=" * 50)
        print("✓ akshare替代API测试完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_akshare_alternative()

