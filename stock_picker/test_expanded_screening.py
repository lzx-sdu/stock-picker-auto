#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试扩大股票筛选范围
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import akshare as ak
import time

from src.strategy.bollinger_mean_reversion import BollingerMeanReversionStrategy
from src.analysis.bollinger_bands import BollingerBands


def test_expanded_screening():
    """测试扩大筛选范围"""
    print("=" * 60)
    print("测试扩大股票筛选范围")
    print("=" * 60)
    
    # 创建策略实例，使用更宽松的配置
    config = {
        'bollinger_bands': {'period': 20, 'std_dev': 2.0},
        'screening': {
            'price_conditions': {'min_price': 1.0, 'max_price': 500.0, 'min_market_cap': 200000000},
            'technical_conditions': {'rsi_oversold': 20, 'rsi_overbought': 80, 'volume_ratio': 1.0}
        }
    }
    strategy = BollingerMeanReversionStrategy(config)
    
    # 手动设置更宽松的筛选条件
    strategy.strategy_config.update({
        'confidence_threshold': 0.5,    # 进一步降低置信度要求
        'rsi_oversold': 20,             # 进一步放宽RSI条件
        'rsi_overbought': 80,
        'min_volume_ratio': 1.0,        # 进一步降低成交量要求
        'min_price': 1.0,               # 进一步降低价格要求
        'max_price': 500.0,             # 进一步扩大价格范围
        'min_market_cap': 200000000,    # 进一步降低市值要求（2亿）
    })
    
    print("当前筛选条件:")
    for key, value in strategy.strategy_config.items():
        print(f"  {key}: {value}")
    
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
            
            # 获取最近60天数据
            data = ak.stock_zh_a_hist(symbol=full_code, period="daily", 
                                     start_date=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                                     end_date=datetime.now().strftime("%Y-%m-%d"),
                                     adjust="qfq")
            
            if data.empty or len(data) < 30:
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
            analysis = strategy.analyze_stock(stock_code, data)
            
            if analysis and analysis.get('composite_score', 0) >= strategy.strategy_config['confidence_threshold']:
                screened_stocks.append(analysis)
                print(f"✓ {stock_code} - 评分: {analysis['composite_score']:.3f} - "
                      f"价格: {analysis['current_price']:.2f}")
            
            time.sleep(0.1)  # 避免请求过快
            
        except Exception as e:
            print(f"✗ {stock_code} - 错误: {str(e)[:50]}")
            continue
    
    print(f"\n筛选结果:")
    print(f"测试股票数量: {test_count}")
    print(f"通过筛选数量: {len(screened_stocks)}")
    print(f"筛选通过率: {len(screened_stocks)/test_count*100:.1f}%")
    
    if screened_stocks:
        print(f"\n前10只推荐股票:")
        print("-" * 80)
        for i, stock in enumerate(screened_stocks[:10], 1):
            print(f"{i}. {stock['stock_code']} - 评分: {stock['composite_score']:.3f} - "
                  f"价格: ¥{stock['current_price']:.2f} - "
                  f"RSI: {stock['rsi']:.1f} - "
                  f"风险等级: {stock['trading_advice']['risk_level']}")
    
    return screened_stocks


if __name__ == "__main__":
    test_expanded_screening()
