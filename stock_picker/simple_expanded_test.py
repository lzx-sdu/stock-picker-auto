#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版扩大股票筛选范围测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import akshare as ak
import time

def calculate_bollinger_bands(data, period=20, std_dev=2.0):
    """计算布林带"""
    data = data.copy()
    data['ma'] = data['close'].rolling(window=period).mean()
    data['std'] = data['close'].rolling(window=period).std()
    data['upper_band'] = data['ma'] + (std_dev * data['std'])
    data['lower_band'] = data['ma'] - (std_dev * data['std'])
    data['bb_position'] = (data['close'] - data['lower_band']) / (data['upper_band'] - data['lower_band'])
    return data

def calculate_rsi(prices, period=14):
    """计算RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_stock_simple(stock_code, data):
    """简化版股票分析"""
    if data.empty or len(data) < 20:  # 降低数据要求
        return None
    
    # 计算技术指标
    data = calculate_bollinger_bands(data)
    data['rsi'] = calculate_rsi(data['close'])
    
    if 'volume' in data.columns:
        data['volume_ma'] = data['volume'].rolling(window=20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_ma']
    else:
        data['volume_ratio'] = 1.0
    
    # 获取最新数据
    latest = data.iloc[-1]
    current_price = latest['close']
    
    # 更宽松的筛选条件
    conditions = []
    
    # 价格条件（更宽松）
    if 0.5 <= current_price <= 1000.0:  # 扩大价格范围
        conditions.append(True)
    else:
        conditions.append(False)
    
    # RSI条件（更宽松）
    if 10 <= latest['rsi'] <= 90:  # 扩大RSI范围
        conditions.append(True)
    else:
        conditions.append(False)
    
    # 布林带位置条件（更宽松）
    if 0.05 <= latest['bb_position'] <= 0.95:  # 扩大布林带位置范围
        conditions.append(True)
    else:
        conditions.append(False)
    
    # 成交量条件（更宽松）
    if latest['volume_ratio'] >= 0.5:  # 降低成交量要求
        conditions.append(True)
    else:
        conditions.append(False)
    
    # 计算综合评分
    score = sum(conditions) / len(conditions)
    
    # 如果满足大部分条件，返回分析结果
    if score >= 0.5:  # 进一步降低阈值
        return {
            'stock_code': stock_code,
            'current_price': current_price,
            'bb_position': latest['bb_position'],
            'rsi': latest['rsi'],
            'volume_ratio': latest['volume_ratio'],
            'composite_score': score,
            'risk_level': 'medium' if score >= 0.7 else 'high'
        }
    
    return None

def test_expanded_screening():
    """测试扩大筛选范围"""
    print("=" * 60)
    print("简化版扩大股票筛选范围测试")
    print("=" * 60)
    
    print("筛选条件:")
    print("  价格范围: ¥0.5 - ¥1000.0")
    print("  RSI范围: 10 - 90")
    print("  布林带位置: 0.05 - 0.95")
    print("  成交量比率: >= 0.5")
    print("  综合评分阈值: >= 0.5")
    
    # 获取股票列表
    print("\n获取股票列表...")
    try:
        stock_list = ak.stock_info_a_code_name()
        stock_list['code'] = stock_list['code'].astype(str)
        # 过滤ST股票
        stock_list = stock_list[~stock_list['name'].str.contains('ST|退')]
        print(f"总股票数量: {len(stock_list)}")
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return
    
    # 测试筛选
    screened_stocks = []
    test_count = min(100, len(stock_list))  # 测试前100只股票
    
    print(f"\n开始测试筛选前 {test_count} 只股票...")
    
    for idx, row in stock_list.head(test_count).iterrows():
        stock_code = row['code']
        
        try:
            # 获取股票数据
            stock_code = str(stock_code).zfill(6)
            if stock_code.startswith(('600', '601', '603', '688')):
                full_code = f"sh{stock_code}"
            else:
                full_code = f"sz{stock_code}"
            
            # 尝试不同的数据获取方法
            try:
                # 方法1：使用stock_zh_a_daily
                data = ak.stock_zh_a_daily(symbol=full_code)
            except Exception as e1:
                try:
                    # 方法2：使用stock_zh_a_hist
                    data = ak.stock_zh_a_hist(symbol=full_code, period="daily", 
                                             start_date=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                                             end_date=datetime.now().strftime("%Y-%m-%d"),
                                             adjust="qfq")
                except Exception as e2:
                    # 方法3：尝试不带市场前缀
                    try:
                        data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                                 start_date=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                                                 end_date=datetime.now().strftime("%Y-%m-%d"),
                                                 adjust="qfq")
                    except Exception as e3:
                        data = pd.DataFrame()
            
            if data.empty or len(data) < 20:
                continue
            
            # 重命名列
            if '日期' in data.columns:
                column_mapping = {
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount'
                }
                data = data.rename(columns=column_mapping)
            
            if 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                data = data.set_index('date')
            
            # 分析股票
            analysis = analyze_stock_simple(stock_code, data)
            
            if analysis:
                screened_stocks.append(analysis)
                if len(screened_stocks) <= 20:  # 只显示前20只的详细信息
                    print(f"✓ {stock_code} - 评分: {analysis['composite_score']:.3f} - "
                          f"价格: ¥{analysis['current_price']:.2f} - "
                          f"RSI: {analysis['rsi']:.1f}")
            
            time.sleep(0.05)  # 避免请求过快
            
        except Exception as e:
            continue
    
    print(f"\n筛选结果:")
    print(f"测试股票数量: {test_count}")
    print(f"通过筛选数量: {len(screened_stocks)}")
    print(f"筛选通过率: {len(screened_stocks)/test_count*100:.1f}%")
    
    if screened_stocks:
        print(f"\n前15只推荐股票:")
        print("-" * 100)
        for i, stock in enumerate(screened_stocks[:15], 1):
            print(f"{i:2d}. {stock['stock_code']} - 评分: {stock['composite_score']:.3f} - "
                  f"价格: ¥{stock['current_price']:6.2f} - "
                  f"RSI: {stock['rsi']:5.1f} - "
                  f"布林带位置: {stock['bb_position']:.3f} - "
                  f"风险等级: {stock['risk_level']}")
    
    return screened_stocks

if __name__ == "__main__":
    test_expanded_screening()
