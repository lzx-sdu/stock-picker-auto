#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票筛选器模块
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..utils.logger import LoggerMixin
from .bollinger_bands import BollingerBands


class StockScreener(LoggerMixin):
    """股票筛选器"""
    
    def __init__(self, config):
        self.config = config
        self.screening_config = config.get_screening_config()
        self.stock_pool_config = config.get_stock_pool_config()
        self.bollinger = BollingerBands(config)
    
    def run_screening(self, strategy_name: str = "bollinger", 
                     date: str = None) -> List[Dict[str, Any]]:
        """
        运行选股筛选
        
        Args:
            strategy_name: 策略名称
            date: 筛选日期
            
        Returns:
            筛选结果列表
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        self.log_info(f"开始运行 {strategy_name} 策略选股，日期: {date}")
        
        if strategy_name == "bollinger":
            return self._run_bollinger_screening(date)
        else:
            self.log_error(f"不支持的策略: {strategy_name}")
            return []
    
    def _run_bollinger_screening(self, date: str) -> List[Dict[str, Any]]:
        """运行布林带策略筛选"""
        from ..data.stock_data import StockDataManager
        
        data_manager = StockDataManager(self.config)
        stock_list = data_manager.get_stock_list()
        
        picks = []
        total_stocks = len(stock_list)
        
        for idx, row in stock_list.iterrows():
            stock_code = row['code']
            stock_name = row['name']
            
            try:
                # 获取股票数据
                data = data_manager.get_latest_data(stock_code, days=60)
                
                if data.empty:
                    continue
                
                # 计算布林带
                data = self.bollinger.calculate(data)
                
                if data.empty:
                    continue
                
                # 分析信号
                signals = self.bollinger.analyze_signals(data)
                
                # 应用筛选条件
                if self._apply_screening_conditions(data, signals):
                    pick = {
                        'code': stock_code,
                        'name': stock_name,
                        'current_price': signals['current_price'],
                        'bb_position': signals['bb_position'],
                        'signals': signals['signals'],
                        'screening_date': date
                    }
                    picks.append(pick)
                
                if (idx + 1) % 100 == 0:
                    self.log_info(f"已处理 {idx + 1}/{total_stocks} 只股票")
                    
            except Exception as e:
                self.log_error(f"处理股票 {stock_code} 时出错: {str(e)}")
                continue
        
        self.log_info(f"布林带筛选完成，共找到 {len(picks)} 只符合条件的股票")
        return picks
    
    def _apply_screening_conditions(self, data: pd.DataFrame, 
                                  signals: Dict[str, Any]) -> bool:
        """应用筛选条件"""
        if not signals or data.empty:
            return False
        
        latest = data.iloc[-1]
        
        # 价格条件
        price_conditions = self.screening_config.get('price_conditions', {})
        min_price = price_conditions.get('min_price', 5.0)
        max_price = price_conditions.get('max_price', 100.0)
        
        if not (min_price <= latest['close'] <= max_price):
            return False
        
        # 布林带条件
        bb_position = signals.get('bb_position', 0.5)
        
        # 寻找超跌反弹机会
        if '触及下轨' in signals.get('signals', []):
            return True
        
        # 寻找回归均值机会
        if 0.1 <= bb_position <= 0.3:  # 价格在下轨附近但开始反弹
            return True
        
        # 成交量确认（如果有成交量数据）
        if 'volume' in data.columns:
            volume_ratio = self.screening_config.get('technical_conditions', {}).get('volume_ratio', 1.5)
            avg_volume = data['volume'].rolling(window=20).mean().iloc[-1]
            current_volume = latest['volume']
            
            if current_volume > avg_volume * volume_ratio:
                return True
        
        return False
    
    def save_results(self, picks: List[Dict[str, Any]], output_file: str):
        """保存筛选结果"""
        if not picks:
            self.log_warning("没有筛选结果可保存")
            return
        
        # 确保输出目录存在
        import os
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 转换为DataFrame并保存
        df = pd.DataFrame(picks)
        
        if output_file.endswith('.csv'):
            df.to_csv(output_file, index=False, encoding='utf-8')
        elif output_file.endswith('.xlsx'):
            df.to_excel(output_file, index=False)
        else:
            df.to_csv(output_file, index=False, encoding='utf-8')
        
        self.log_info(f"筛选结果已保存到: {output_file}")
    
    def generate_summary_report(self, picks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成筛选结果摘要报告"""
        if not picks:
            return {}
        
        df = pd.DataFrame(picks)
        
        summary = {
            'total_picks': len(picks),
            'avg_price': df['current_price'].mean(),
            'price_range': {
                'min': df['current_price'].min(),
                'max': df['current_price'].max()
            },
            'bb_position_stats': {
                'mean': df['bb_position'].mean(),
                'std': df['bb_position'].std()
            },
            'signal_distribution': df['signals'].explode().value_counts().to_dict(),
            'market_distribution': df['code'].apply(
                lambda x: 'sh' if x.startswith(('600', '601', '603', '688')) else 'sz'
            ).value_counts().to_dict()
        }
        
        return summary 