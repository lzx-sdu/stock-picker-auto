#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
均值回归策略模块
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from ..utils.logger import LoggerMixin
from ..analysis.bollinger_bands import BollingerBands


class MeanReversionStrategy(LoggerMixin):
    """均值回归策略"""
    
    def __init__(self, config):
        self.config = config
        self.bollinger = BollingerBands(config)
    
    def analyze_stock(self, stock_code: str, data: pd.DataFrame) -> Dict[str, Any]:
        """分析单个股票的均值回归机会"""
        if data.empty:
            return {}
        
        # 计算布林带
        data = self.bollinger.calculate(data)
        
        if data.empty:
            return {}
        
        # 分析信号
        signals = self.bollinger.analyze_signals(data)
        
        # 计算技术指标
        technical_indicators = self._calculate_technical_indicators(data)
        
        # 生成交易信号
        trading_signals = self._generate_trading_signals(signals, technical_indicators)
        
        analysis_result = {
            'stock_code': stock_code,
            'current_price': signals.get('current_price', 0),
            'bb_position': signals.get('bb_position', 0.5),
            'signals': signals.get('signals', []),
            'technical_indicators': technical_indicators,
            'trading_signals': trading_signals,
            'analysis_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        return analysis_result
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """计算技术指标"""
        if data.empty:
            return {}
        
        latest = data.iloc[-1]
        indicators = {}
        
        # RSI
        if len(data) >= 14:
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = rsi.iloc[-1]
        
        # 移动平均线
        indicators['ma5'] = data['close'].rolling(window=5).mean().iloc[-1]
        indicators['ma10'] = data['close'].rolling(window=10).mean().iloc[-1]
        indicators['ma20'] = data['close'].rolling(window=20).mean().iloc[-1]
        
        # 成交量指标
        if 'volume' in data.columns:
            indicators['volume_ma'] = data['volume'].rolling(window=20).mean().iloc[-1]
            indicators['volume_ratio'] = latest['volume'] / indicators['volume_ma']
        
        return indicators
    
    def _generate_trading_signals(self, signals: Dict[str, Any],
                                indicators: Dict[str, float]) -> Dict[str, Any]:
        """生成交易信号"""
        trading_signals = {
            'action': 'HOLD',
            'confidence': 0.0,
            'reason': [],
            'target_price': 0.0,
            'stop_loss': 0.0
        }
        
        if not signals or not indicators:
            return trading_signals
        
        bb_position = signals.get('bb_position', 0.5)
        current_price = signals.get('current_price', 0)
        
        # 买入信号
        if '触及下轨' in signals.get('signals', []):
            trading_signals['action'] = 'BUY'
            trading_signals['confidence'] = 0.8
            trading_signals['reason'].append('触及布林带下轨')
            
            # 设置目标价格和止损
            if 'upper_band' in signals:
                trading_signals['target_price'] = signals['upper_band']
            trading_signals['stop_loss'] = current_price * 0.92
        
        # RSI确认
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            trading_signals['confidence'] += 0.1
            trading_signals['reason'].append('RSI超卖')
        
        # 成交量确认
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:
            trading_signals['confidence'] += 0.1
            trading_signals['reason'].append('成交量放大')
        
        # 限制置信度
        trading_signals['confidence'] = min(trading_signals['confidence'], 1.0)
        
        return trading_signals
    
    def get_portfolio_recommendations(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成投资组合建议"""
        if not analysis_results:
            return {}
        
        # 筛选买入信号
        buy_signals = [result for result in analysis_results 
                      if result.get('trading_signals', {}).get('action') == 'BUY']
        
        # 按置信度排序
        buy_signals.sort(key=lambda x: x.get('trading_signals', {}).get('confidence', 0), reverse=True)
        
        portfolio = {
            'total_recommendations': len(buy_signals),
            'top_picks': buy_signals[:10],
            'portfolio_allocation': {}
        }
        
        # 计算仓位分配
        if buy_signals:
            weight = 1.0 / len(buy_signals)
            for signal in buy_signals:
                stock_code = signal['stock_code']
                portfolio['portfolio_allocation'][stock_code] = weight
        
        return portfolio 