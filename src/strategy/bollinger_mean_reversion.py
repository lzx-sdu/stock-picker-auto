#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布林带均值回归选股策略
基于布林带、RSI、MACD、成交量等多重技术指标的综合选股策略
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from utils.logger import LoggerMixin
from analysis.bollinger_bands import BollingerBands


class BollingerMeanReversionStrategy(LoggerMixin):
    """布林带均值回归选股策略"""
    
    def __init__(self, config):
        self.config = config
        self.bollinger = BollingerBands(config)
        self.strategy_config = self._get_strategy_config()
        
    def _get_strategy_config(self) -> Dict[str, Any]:
        """获取策略配置"""
        return {
            'bb_period': 20,
            'bb_std_dev': 2.0,
            'rsi_period': 14,
            'rsi_oversold': 15,           # 从25降低到15，进一步放宽RSI超卖条件
            'rsi_overbought': 85,         # 从75提高到85，进一步放宽RSI超买条件
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'volume_ma_period': 20,
            'min_volume_ratio': 0.8,      # 从1.2降低到0.8，进一步降低成交量要求
            'min_price': 1.0,             # 从2.0降低到1.0，进一步降低最低股价要求
            'max_price': 500.0,           # 从200.0提高到500.0，进一步扩大价格范围
            'min_market_cap': 200000000,  # 从5亿降低到2亿，进一步降低市值要求
            'max_position_ratio': 0.1,     # 单只股票最大仓位
            'stop_loss': 0.08,             # 止损比例
            'take_profit': 0.20,           # 止盈比例
            'confidence_threshold': 0.5    # 从0.6降低到0.5，进一步降低置信度要求
        }
    
    def analyze_stock(self, stock_code: str, data: pd.DataFrame) -> Dict[str, Any]:
        """分析单个股票的均值回归机会"""
        if data.empty or len(data) < 50:
            return {}
        
        try:
            # 计算技术指标
            data = self._calculate_all_indicators(data)
            
            if data.empty:
                return {}
            
            # 分析信号
            signals = self._analyze_signals(data)
            
            # 计算综合评分
            score = self._calculate_composite_score(signals)
            
            # 生成交易建议
            current_price = data['close'].iloc[-1]
            bb_data = {
                'bb_upper': data['upper_band'].iloc[-1],
                'bb_middle': data['ma'].iloc[-1],
                'bb_lower': data['lower_band'].iloc[-1]
            }
            trading_advice = self._generate_trading_advice(signals, score, current_price, bb_data)
            
            analysis_result = {
                'stock_code': stock_code,
                'current_price': data['close'].iloc[-1],
                'bb_position': data['bb_position'].iloc[-1],
                'rsi': data['rsi'].iloc[-1],
                'macd_signal': data['macd_signal'].iloc[-1],
                'volume_ratio': data['volume_ratio'].iloc[-1],
                'signals': signals,
                'composite_score': score,
                'trading_advice': trading_advice,
                'analysis_date': datetime.now().strftime("%Y-%m-%d"),
                'risk_metrics': self._calculate_risk_metrics(data)
            }
            
            return analysis_result
            
        except Exception as e:
            self.log_error(f"分析股票 {stock_code} 时出错: {str(e)}")
            return {}
    
    def _calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        data = data.copy()
        
        # 计算布林带
        data = self.bollinger.calculate(data)
        
        # 计算RSI
        data['rsi'] = self._calculate_rsi(data['close'], self.strategy_config['rsi_period'])
        
        # 计算MACD
        macd_data = self._calculate_macd(data['close'])
        data['macd'] = macd_data['macd']
        data['macd_signal'] = macd_data['signal']
        data['macd_histogram'] = macd_data['histogram']
        
        # 计算成交量指标
        if 'volume' in data.columns:
            data['volume_ma'] = data['volume'].rolling(window=self.strategy_config['volume_ma_period']).mean()
            data['volume_ratio'] = data['volume'] / data['volume_ma']
        else:
            data['volume_ratio'] = 1.0
        
        # 计算价格动量
        data['price_momentum'] = data['close'].pct_change(5)
        
        # 计算波动率
        data['volatility'] = data['close'].rolling(window=20).std() / data['close'].rolling(window=20).mean()
        
        return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """计算MACD指标"""
        ema_fast = prices.ewm(span=self.strategy_config['macd_fast']).mean()
        ema_slow = prices.ewm(span=self.strategy_config['macd_slow']).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=self.strategy_config['macd_signal']).mean()
        histogram = macd - signal
        
        return {
            'macd': macd,
            'signal': signal,
            'histogram': histogram
        }
    
    def _analyze_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析交易信号"""
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        signals = {
            'bb_signals': [],
            'rsi_signals': [],
            'macd_signals': [],
            'volume_signals': [],
            'momentum_signals': [],
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
        if rsi <= self.strategy_config['rsi_oversold']:
            signals['rsi_signals'].append('RSI超卖')
        elif rsi >= self.strategy_config['rsi_overbought']:
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
        if volume_ratio >= self.strategy_config['min_volume_ratio']:
            signals['volume_signals'].append('成交量放大')
        
        # 动量信号
        momentum = latest['price_momentum']
        if momentum > 0.05:
            signals['momentum_signals'].append('价格动量向上')
        elif momentum < -0.05:
            signals['momentum_signals'].append('价格动量向下')
        
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
    
    def _calculate_composite_score(self, signals: Dict[str, Any]) -> float:
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
        
        # 动量信号权重
        momentum_weight = 0.15
        if '价格动量向上' in signals['momentum_signals']:
            score += momentum_weight
        
        return min(score, 1.0)
    
    def _generate_trading_advice(self, signals: Dict[str, Any], score: float, current_price: float, bb_data: Dict[str, float]) -> Dict[str, Any]:
        """生成交易建议"""
        advice = {
            'action': signals['overall_signal'],
            'confidence': score,
            'target_price': 0.0,
            'stop_loss': 0.0,
            'position_size': 0.0,
            'holding_period': 'medium',
            'risk_level': 'medium',
            'reasoning': []
        }
        
        if signals['overall_signal'] == 'BUY' and score >= self.strategy_config['confidence_threshold']:
            # 计算目标价格和止损
            # 添加布林带位置信息到信号中
            signals_with_bb = signals.copy()
            signals_with_bb['bb_position'] = (current_price - bb_data['bb_lower']) / (bb_data['bb_upper'] - bb_data['bb_lower'])
            signals_with_bb['risk_level'] = self._assess_risk_level(signals)
            
            advice['target_price'] = self._calculate_target_price(signals_with_bb, current_price, bb_data)
            advice['stop_loss'] = self._calculate_stop_loss(signals_with_bb, current_price, bb_data)
            advice['position_size'] = self._calculate_position_size(score)
            advice['holding_period'] = self._estimate_holding_period(signals)
            advice['risk_level'] = signals_with_bb['risk_level']
            
            # 添加理由
            for signal_type, signal_list in signals.items():
                if signal_list and signal_type != 'overall_signal':
                    advice['reasoning'].extend(signal_list)
        
        return advice
    
    def _calculate_target_price(self, signals: Dict[str, Any], current_price: float = None, bb_data: Dict[str, float] = None) -> float:
        """计算目标价格"""
        if current_price is None or bb_data is None:
            return 0.0
            
        # 基于布林带位置和信号计算目标价格
        bb_position = signals.get('bb_position', 0.5)
        
        if bb_position <= 0.2:  # 超跌区域
            # 目标价格为布林带中轨
            return bb_data.get('bb_middle', current_price * 1.05)
        elif bb_position >= 0.8:  # 超买区域
            # 目标价格为布林带中轨
            return bb_data.get('bb_middle', current_price * 0.95)
        else:
            # 中性区域：目标价格为当前价格的1.05倍
            return current_price * 1.05
    
    def _calculate_stop_loss(self, signals: Dict[str, Any], current_price: float = None, bb_data: Dict[str, float] = None) -> float:
        """计算止损价格"""
        if current_price is None or bb_data is None:
            return 0.0
            
        # 基于布林带位置和风险等级计算止损价格
        bb_position = signals.get('bb_position', 0.5)
        risk_level = signals.get('risk_level', 'medium')
        
        # 根据风险等级调整止损比例
        stop_loss_ratios = {
            'low': 0.05,    # 5%止损
            'medium': 0.08, # 8%止损
            'high': 0.12    # 12%止损
        }
        
        stop_loss_ratio = stop_loss_ratios.get(risk_level, 0.08)
        
        if bb_position <= 0.2:  # 超跌区域
            # 止损价格为布林带下轨
            return bb_data.get('bb_lower', current_price * (1 - stop_loss_ratio))
        elif bb_position >= 0.8:  # 超买区域
            # 止损价格为布林带上轨
            return bb_data.get('bb_upper', current_price * (1 + stop_loss_ratio))
        else:
            # 中性区域：止损价格为当前价格的8%
            return current_price * (1 - stop_loss_ratio)
    
    def _calculate_position_size(self, score: float) -> float:
        """计算建议仓位大小"""
        base_size = self.strategy_config['max_position_ratio']
        return base_size * score
    
    def _estimate_holding_period(self, signals: Dict[str, Any]) -> str:
        """估算持有期"""
        if '强烈超跌' in signals['bb_signals']:
            return 'long'
        elif '超跌反弹' in signals['bb_signals']:
            return 'medium'
        else:
            return 'short'
    
    def _assess_risk_level(self, signals: Dict[str, Any]) -> str:
        """评估风险等级"""
        risk_factors = 0
        
        if '成交量放大' in signals['volume_signals']:
            risk_factors += 1
        if 'MACD金叉' in signals['macd_signals']:
            risk_factors += 1
        if '价格动量向上' in signals['momentum_signals']:
            risk_factors += 1
        
        if risk_factors >= 2:
            return 'low'
        elif risk_factors >= 1:
            return 'medium'
        else:
            return 'high'
    
    def _calculate_risk_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """计算风险指标"""
        if data.empty:
            return {}
        
        returns = data['close'].pct_change().dropna()
        
        risk_metrics = {
            'volatility': returns.std() * np.sqrt(252),  # 年化波动率
            'max_drawdown': self._calculate_max_drawdown(data['close']),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'var_95': returns.quantile(0.05),  # 95% VaR
        }
        
        return risk_metrics
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """计算最大回撤"""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown.min()
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        if returns.std() == 0:
            return 0
        return (returns.mean() * 252 - risk_free_rate) / (returns.std() * np.sqrt(252))
    
    def screen_stocks(self, stock_data_dict: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """筛选股票"""
        results = []
        
        for stock_code, data in stock_data_dict.items():
            analysis = self.analyze_stock(stock_code, data)
            
            if analysis and analysis['trading_advice']['action'] == 'BUY':
                if analysis['composite_score'] >= self.strategy_config['confidence_threshold']:
                    results.append(analysis)
        
        # 按综合评分排序
        results.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return results
    
    def generate_portfolio_recommendation(self, screened_stocks: List[Dict[str, Any]], 
                                       max_positions: int = 10) -> Dict[str, Any]:
        """生成投资组合建议"""
        if not screened_stocks:
            return {}
        
        # 选择前N只股票
        selected_stocks = screened_stocks[:max_positions]
        
        # 计算权重分配
        total_score = sum(stock['composite_score'] for stock in selected_stocks)
        
        portfolio = {
            'total_positions': len(selected_stocks),
            'total_score': total_score,
            'positions': [],
            'risk_metrics': {
                'avg_volatility': 0.0,
                'avg_max_drawdown': 0.0,
                'portfolio_sharpe': 0.0
            }
        }
        
        total_volatility = 0
        total_drawdown = 0
        
        for stock in selected_stocks:
            weight = stock['composite_score'] / total_score
            position = {
                'stock_code': stock['stock_code'],
                'current_price': stock['current_price'],
                'weight': weight,
                'position_size': stock['trading_advice']['position_size'],
                'target_price': stock['trading_advice']['target_price'],
                'stop_loss': stock['trading_advice']['stop_loss'],
                'confidence': stock['composite_score'],
                'risk_level': stock['trading_advice']['risk_level'],
                'holding_period': stock['trading_advice']['holding_period']
            }
            portfolio['positions'].append(position)
            
            # 累计风险指标
            risk_metrics = stock['risk_metrics']
            total_volatility += risk_metrics.get('volatility', 0)
            total_drawdown += risk_metrics.get('max_drawdown', 0)
        
        # 计算平均风险指标
        if selected_stocks:
            portfolio['risk_metrics']['avg_volatility'] = total_volatility / len(selected_stocks)
            portfolio['risk_metrics']['avg_max_drawdown'] = total_drawdown / len(selected_stocks)
        
        return portfolio
