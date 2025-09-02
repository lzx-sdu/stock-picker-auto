#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的布林带策略测试
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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

def calculate_bollinger_bands(data, period=20, std_dev=2.0):
    """计算布林带"""
    data = data.copy()
    
    # 计算移动平均线
    data['ma'] = data['close'].rolling(window=period).mean()
    
    # 计算标准差
    data['std'] = data['close'].rolling(window=period).std()
    
    # 计算布林带
    data['upper_band'] = data['ma'] + (std_dev * data['std'])
    data['lower_band'] = data['ma'] - (std_dev * data['std'])
    
    # 计算布林带位置
    data['bb_position'] = (data['close'] - data['lower_band']) / (data['upper_band'] - data['lower_band'])
    
    return data

def calculate_rsi(prices, period=14):
    """计算RSI指标"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    histogram = macd - signal_line
    
    return {
        'macd': macd,
        'signal': signal_line,
        'histogram': histogram
    }

def analyze_signals(data):
    """分析交易信号"""
    latest = data.iloc[-1]
    prev = data.iloc[-2] if len(data) > 1 else latest
    
    signals = {
        'bb_signals': [],
        'rsi_signals': [],
        'macd_signals': [],
        'volume_signals': [],
        'overall_signal': 'HOLD'
    }
    
    # 布林带信号
    bb_position = latest['bb_position']
    if bb_position <= 0.1:
        signals['bb_signals'].append('强烈超跌')
    elif bb_position <= 0.2:
        signals['bb_signals'].append('超跌反弹')
    elif bb_position >= 0.9:
        signals['bb_signals'].append('强烈超买')
    elif bb_position >= 0.8:
        signals['bb_signals'].append('超买回调')
    
    # RSI信号
    rsi = latest['rsi']
    if rsi <= 30:
        signals['rsi_signals'].append('RSI超卖')
    elif rsi >= 70:
        signals['rsi_signals'].append('RSI超买')
    
    # MACD信号
    if (latest['macd'] > latest['macd_signal'] and 
        prev['macd'] <= prev['macd_signal']):
        signals['macd_signals'].append('MACD金叉')
    elif (latest['macd'] < latest['macd_signal'] and 
          prev['macd'] >= prev['macd_signal']):
        signals['macd_signals'].append('MACD死叉')
    
    # 成交量信号
    volume_ratio = latest['volume_ratio']
    if volume_ratio >= 1.5:
        signals['volume_signals'].append('成交量放大')
    
    # 综合信号判断
    buy_signals = len(signals['bb_signals']) + len(signals['rsi_signals']) + len(signals['macd_signals'])
    sell_signals = 0
    
    if '强烈超买' in signals['bb_signals'] or 'RSI超买' in signals['rsi_signals']:
        sell_signals += 1
    
    if buy_signals > sell_signals:
        signals['overall_signal'] = 'BUY'
    elif sell_signals > buy_signals:
        signals['overall_signal'] = 'SELL'
    
    return signals

def calculate_composite_score(signals):
    """计算综合评分"""
    score = 0.5  # 基础分
    
    # 布林带信号权重
    bb_weight = 0.3
    if '强烈超跌' in signals['bb_signals']:
        score += bb_weight
    elif '超跌反弹' in signals['bb_signals']:
        score += bb_weight * 0.7
    
    # RSI信号权重
    rsi_weight = 0.2
    if 'RSI超卖' in signals['rsi_signals']:
        score += rsi_weight
    
    # MACD信号权重
    macd_weight = 0.2
    if 'MACD金叉' in signals['macd_signals']:
        score += macd_weight
    
    # 成交量信号权重
    volume_weight = 0.15
    if '成交量放大' in signals['volume_signals']:
        score += volume_weight
    
    return min(score, 1.0)

def main():
    """主函数"""
    print("=" * 60)
    print("布林带均值回归策略测试")
    print("=" * 60)
    
    # 创建示例数据
    sample_data = create_sample_data()
    print(f"创建示例数据: {len(sample_data)} 天")
    print(f"价格范围: {sample_data['close'].min():.2f} - {sample_data['close'].max():.2f}")
    
    # 计算技术指标
    data = calculate_bollinger_bands(sample_data)
    data['rsi'] = calculate_rsi(data['close'])
    
    macd_data = calculate_macd(data['close'])
    data['macd'] = macd_data['macd']
    data['macd_signal'] = macd_data['signal']
    data['macd_histogram'] = macd_data['histogram']
    
    # 计算成交量指标
    data['volume_ma'] = data['volume'].rolling(window=20).mean()
    data['volume_ratio'] = data['volume'] / data['volume_ma']
    
    # 分析信号
    signals = analyze_signals(data)
    
    # 计算综合评分
    score = calculate_composite_score(signals)
    
    # 显示结果
    latest = data.iloc[-1]
    print(f"\n📊 技术指标:")
    print(f"  当前价格: ¥{latest['close']:.2f}")
    print(f"  布林带位置: {latest['bb_position']:.3f}")
    print(f"  RSI: {latest['rsi']:.1f}")
    print(f"  MACD: {latest['macd']:.4f}")
    print(f"  成交量比率: {latest['volume_ratio']:.2f}")
    
    print(f"\n🎯 交易信号:")
    for signal_type, signal_list in signals.items():
        if signal_list and signal_type != 'overall_signal':
            print(f"  {signal_type}: {', '.join(signal_list)}")
    
    print(f"\n📈 综合评分: {score:.3f}")
    print(f"交易建议: {signals['overall_signal']}")
    
    if signals['overall_signal'] == 'BUY' and score >= 0.7:
        print("✅ 符合买入条件！")
    else:
        print("❌ 不符合买入条件")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()


