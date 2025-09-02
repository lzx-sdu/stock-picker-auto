#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试布林带均值回归策略
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.strategy.bollinger_mean_reversion import BollingerMeanReversionStrategy


def create_sample_data():
    """创建示例股票数据"""
    # 生成60天的模拟数据
    dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
    
    # 模拟价格数据 - 创建一个均值回归的走势
    np.random.seed(42)
    base_price = 20.0
    
    # 前30天：价格下跌到布林带下轨
    prices_1 = [base_price * (1 - 0.02 * i + np.random.normal(0, 0.01)) for i in range(30)]
    
    # 后30天：价格反弹
    prices_2 = [prices_1[-1] * (1 + 0.015 * i + np.random.normal(0, 0.01)) for i in range(30)]
    
    prices = prices_1 + prices_2
    
    # 生成成交量数据
    volumes = [1000000 + np.random.normal(0, 200000) for _ in range(60)]
    
    data = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': volumes
    })
    
    data.set_index('date', inplace=True)
    return data


def test_strategy():
    """测试布林带策略"""
    print("=" * 60)
    print("测试布林带均值回归策略")
    print("=" * 60)
    
    # 创建配置
    config = Config("config.yaml")
    
    # 创建策略
    strategy = BollingerMeanReversionStrategy(config)
    
    # 创建示例数据
    sample_data = create_sample_data()
    print(f"创建示例数据: {len(sample_data)} 天")
    print(f"价格范围: {sample_data['close'].min():.2f} - {sample_data['close'].max():.2f}")
    
    # 分析股票
    stock_code = "000001"
    analysis = strategy.analyze_stock(stock_code, sample_data)
    
    if analysis:
        print(f"\n✅ 股票 {stock_code} 分析完成")
        print(f"当前价格: ¥{analysis['current_price']:.2f}")
        print(f"布林带位置: {analysis['bb_position']:.3f}")
        print(f"RSI: {analysis['rsi']:.1f}")
        print(f"综合评分: {analysis['composite_score']:.3f}")
        print(f"交易建议: {analysis['trading_advice']['action']}")
        print(f"置信度: {analysis['trading_advice']['confidence']:.3f}")
        print(f"风险等级: {analysis['trading_advice']['risk_level']}")
        print(f"持有期: {analysis['trading_advice']['holding_period']}")
        
        # 显示信号
        signals = analysis['signals']
        print(f"\n📊 技术信号:")
        for signal_type, signal_list in signals.items():
            if signal_list and signal_type != 'overall_signal':
                print(f"  {signal_type}: {', '.join(signal_list)}")
        
        # 显示风险指标
        risk_metrics = analysis['risk_metrics']
        print(f"\n⚠️ 风险指标:")
        print(f"  波动率: {risk_metrics.get('volatility', 0):.2%}")
        print(f"  最大回撤: {risk_metrics.get('max_drawdown', 0):.2%}")
        print(f"  夏普比率: {risk_metrics.get('sharpe_ratio', 0):.3f}")
        
    else:
        print(f"❌ 股票 {stock_code} 分析失败")


def test_screening():
    """测试股票筛选"""
    print("\n" + "=" * 60)
    print("测试股票筛选功能")
    print("=" * 60)
    
    # 创建配置
    config = Config("config.yaml")
    
    # 创建策略
    strategy = BollingerMeanReversionStrategy(config)
    
    # 创建多只股票的示例数据
    stock_data_dict = {}
    
    for i in range(5):
        stock_code = f"00000{i+1}"
        data = create_sample_data()
        
        # 调整数据使其符合不同的筛选条件
        if i == 0:  # 强烈超跌
            data['close'] = data['close'] * 0.8
        elif i == 1:  # 超跌反弹
            data['close'] = data['close'] * 0.9
        elif i == 2:  # 正常
            pass
        elif i == 3:  # 超买回调
            data['close'] = data['close'] * 1.1
        elif i == 4:  # 强烈超买
            data['close'] = data['close'] * 1.2
        
        stock_data_dict[stock_code] = data
    
    # 运行筛选
    screened_stocks = strategy.screen_stocks(stock_data_dict)
    
    print(f"筛选结果: {len(screened_stocks)} 只股票")
    
    for stock in screened_stocks:
        print(f"  {stock['stock_code']}: 评分 {stock['composite_score']:.3f}, "
              f"建议 {stock['trading_advice']['action']}, "
              f"风险 {stock['trading_advice']['risk_level']}")


def test_portfolio():
    """测试投资组合生成"""
    print("\n" + "=" * 60)
    print("测试投资组合生成")
    print("=" * 60)
    
    # 创建配置
    config = Config("config.yaml")
    
    # 创建策略
    strategy = BollingerMeanReversionStrategy(config)
    
    # 创建示例筛选结果
    screened_stocks = []
    
    for i in range(3):
        stock_code = f"00000{i+1}"
        screened_stocks.append({
            'stock_code': stock_code,
            'current_price': 20.0 + i * 5,
            'composite_score': 0.8 - i * 0.1,
            'trading_advice': {
                'action': 'BUY',
                'position_size': 0.1,
                'target_price': 25.0 + i * 5,
                'stop_loss': 18.0 + i * 5,
                'risk_level': 'medium',
                'holding_period': 'medium'
            },
            'risk_metrics': {
                'volatility': 0.2,
                'max_drawdown': -0.1,
                'sharpe_ratio': 1.0
            }
        })
    
    # 生成投资组合
    portfolio = strategy.generate_portfolio_recommendation(screened_stocks)
    
    print(f"投资组合包含 {portfolio['total_positions']} 只股票")
    print(f"总评分: {portfolio['total_score']:.3f}")
    
    for position in portfolio['positions']:
        print(f"  {position['stock_code']}: 权重 {position['weight']:.1%}, "
              f"仓位 {position['position_size']:.1%}, "
              f"风险 {position['risk_level']}")


if __name__ == "__main__":
    # 运行所有测试
    test_strategy()
    test_screening()
    test_portfolio()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


