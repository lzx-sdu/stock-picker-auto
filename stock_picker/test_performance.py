#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本
"""

import sys
import os
import time
import concurrent.futures
from typing import List, Dict, Any
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.data.stock_data import StockDataManager
from src.analysis.bollinger_bands import BollingerBands

def test_original_performance():
    """测试原始版本性能"""
    print("=" * 50)
    print("测试原始版本性能")
    print("=" * 50)
    
    config = Config("config.yaml")
    data_manager = StockDataManager(config)
    bollinger = BollingerBands(config)
    
    # 获取测试股票列表
    stock_list = data_manager.get_stock_list().head(20)  # 只测试20只股票
    
    start_time = time.time()
    picks = []
    
    for idx, row in stock_list.iterrows():
        stock_code = row['code']
        stock_name = row['name']
        
        try:
            # 获取股票数据
            data = data_manager.get_latest_data(stock_code, days=60)
            
            if data.empty:
                continue
            
            # 计算布林带
            data = bollinger.calculate(data)
            
            if data.empty:
                continue
            
            # 分析信号
            signals = bollinger.analyze_signals(data)
            
            # 应用筛选条件
            if apply_screening_conditions(data, signals):
                picks.append({
                    'code': stock_code,
                    'name': stock_name,
                    'current_price': signals['current_price'],
                    'bb_position': signals['bb_position']
                })
            
            print(f"处理: {stock_code} ({stock_name})")
            
        except Exception as e:
            print(f"处理股票 {stock_code} 时出错: {str(e)}")
    
    total_time = time.time() - start_time
    print(f"原始版本结果: {len(picks)} 只股票，耗时: {total_time:.2f} 秒")
    print(f"平均速度: {len(stock_list)/total_time:.2f} 股票/秒")
    
    return picks, total_time

def test_optimized_performance():
    """测试优化版本性能"""
    print("=" * 50)
    print("测试优化版本性能")
    print("=" * 50)
    
    config = Config("config.yaml")
    data_manager = StockDataManager(config)
    bollinger = BollingerBands(config)
    
    # 获取测试股票列表
    stock_list = data_manager.get_stock_list().head(20)  # 只测试20只股票
    
    start_time = time.time()
    picks = []
    
    # 并发处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_stock = {
            executor.submit(process_single_stock_optimized, row, data_manager, bollinger): row 
            for _, row in stock_list.iterrows()
        }
        
        for future in concurrent.futures.as_completed(future_to_stock):
            stock_row = future_to_stock[future]
            try:
                result = future.result()
                if result:
                    picks.append(result)
            except Exception as e:
                stock_code = stock_row['code']
                print(f"处理股票 {stock_code} 时出错: {str(e)}")
    
    total_time = time.time() - start_time
    print(f"优化版本结果: {len(picks)} 只股票，耗时: {total_time:.2f} 秒")
    print(f"平均速度: {len(stock_list)/total_time:.2f} 股票/秒")
    
    return picks, total_time

def process_single_stock_optimized(stock_row, data_manager, bollinger):
    """优化版单只股票处理"""
    stock_code = stock_row['code']
    stock_name = stock_row['name']
    
    try:
        # 获取股票数据
        data = data_manager.get_latest_data(stock_code, days=60)
        
        if data.empty:
            return None
        
        # 计算布林带
        data = bollinger.calculate(data)
        
        if data.empty:
            return None
        
        # 分析信号
        signals = bollinger.analyze_signals(data)
        
        # 应用筛选条件
        if apply_screening_conditions(data, signals):
            return {
                'code': stock_code,
                'name': stock_name,
                'current_price': signals['current_price'],
                'bb_position': signals['bb_position']
            }
        
        return None
        
    except Exception as e:
        print(f"处理股票 {stock_code} 时出错: {str(e)}")
        return None

def apply_screening_conditions(data, signals):
    """应用筛选条件"""
    if not signals or data.empty:
        return False
    
    latest = data.iloc[-1]
    
    # 价格条件
    current_price = latest['close']
    if not (5.0 <= current_price <= 100.0):
        return False
    
    # 布林带条件
    bb_position = signals.get('bb_position', 0.5)
    stock_signals = signals.get('signals', [])
    
    # 寻找超跌反弹机会
    if '触及下轨' in stock_signals:
        return True
    
    # 寻找回归均值机会
    if 0.1 <= bb_position <= 0.3:
        return True
    
    return False

def compare_performance():
    """比较性能"""
    print("=" * 50)
    print("性能对比测试")
    print("=" * 50)
    
    # 测试原始版本
    print("\n1. 测试原始版本...")
    original_picks, original_time = test_original_performance()
    
    # 测试优化版本
    print("\n2. 测试优化版本...")
    optimized_picks, optimized_time = test_optimized_performance()
    
    # 性能对比
    print("\n" + "=" * 50)
    print("性能对比结果")
    print("=" * 50)
    
    speed_improvement = original_time / optimized_time if optimized_time > 0 else 0
    
    print(f"原始版本:")
    print(f"  - 处理时间: {original_time:.2f} 秒")
    print(f"  - 筛选结果: {len(original_picks)} 只股票")
    
    print(f"\n优化版本:")
    print(f"  - 处理时间: {optimized_time:.2f} 秒")
    print(f"  - 筛选结果: {len(optimized_picks)} 只股票")
    
    print(f"\n性能提升:")
    print(f"  - 速度提升: {speed_improvement:.1f} 倍")
    print(f"  - 时间节省: {((original_time - optimized_time) / original_time * 100):.1f}%")
    
    # 显示筛选结果
    if optimized_picks:
        print(f"\n筛选结果 (优化版):")
        for pick in optimized_picks[:5]:  # 显示前5只
            print(f"  {pick['code']} ({pick['name']}) - 价格: {pick['current_price']:.2f}, "
                  f"BB位置: {pick['bb_position']:.2f}")

if __name__ == "__main__":
    compare_performance()

