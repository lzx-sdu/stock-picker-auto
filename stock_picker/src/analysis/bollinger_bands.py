#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布林带计算模块
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from ..utils.logger import LoggerMixin


class BollingerBands(LoggerMixin):
    """布林带计算类"""
    
    def __init__(self, config):
        self.config = config
        bb_config = config.get_bollinger_config()
        self.period = bb_config.get('period', 20)
        self.std_dev = bb_config.get('std_dev', 2.0)
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算布林带指标"""
        if data.empty:
            return data
        
        data = data.sort_index()
        
        # 计算移动平均线
        data['ma'] = data['close'].rolling(window=self.period).mean()
        
        # 计算标准差
        data['std'] = data['close'].rolling(window=self.period).std()
        
        # 计算布林带
        data['upper_band'] = data['ma'] + (self.std_dev * data['std'])
        data['lower_band'] = data['ma'] - (self.std_dev * data['std'])
        
        # 计算布林带位置
        data['bb_position'] = (data['close'] - data['lower_band']) / (data['upper_band'] - data['lower_band'])
        
        return data
    
    def analyze_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析布林带信号"""
        if data.empty:
            return {}
        
        latest = data.iloc[-1]
        
        signals = {
            'current_price': latest['close'],
            'upper_band': latest['upper_band'],
            'lower_band': latest['lower_band'],
            'middle_band': latest['ma'],
            'bb_position': latest['bb_position'],
            'signals': []
        }
        
        # 检查是否触及下轨
        if latest['close'] <= latest['lower_band'] * 1.01:
            signals['signals'].append('触及下轨')
        
        # 检查是否触及上轨
        if latest['close'] >= latest['upper_band'] * 0.99:
            signals['signals'].append('触及上轨')
        
        return signals
    
    def get_mean_reversion_opportunities(self, data: pd.DataFrame) -> pd.DataFrame:
        """识别均值回归机会"""
        if data.empty:
            return pd.DataFrame()
        
        opportunities = []
        
        for i in range(len(data) - 1):
            current = data.iloc[i]
            next_day = data.iloc[i + 1]
            
            # 检查从下轨反弹
            if (current['close'] <= current['lower_band'] and 
                next_day['close'] > next_day['lower_band']):
                
                opportunity = {
                    'date': data.index[i + 1],
                    'type': '反弹机会',
                    'price': next_day['close'],
                    'bb_position': next_day['bb_position']
                }
                opportunities.append(opportunity)
        
        return pd.DataFrame(opportunities) 