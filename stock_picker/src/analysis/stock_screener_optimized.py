#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版股票筛选器模块
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta
import concurrent.futures
import time

from ..utils.logger import LoggerMixin
from .bollinger_bands import BollingerBands


class OptimizedStockScreener(LoggerMixin):
    """优化版股票筛选器"""
    
    def __init__(self, config):
        self.config = config
        self.screening_config = config.get_screening_config()
        self.stock_pool_config = config.get_stock_pool_config()
        self.bollinger = BollingerBands(config)
        self.max_workers = 8  # 并发线程数
        self.batch_size = 20  # 批处理大小
    
    def run_screening(self, strategy_name: str = "bollinger", 
                     date: str = None, max_stocks: int = None) -> List[Dict[str, Any]]:
        """
        运行优化版选股筛选
        
        Args:
            strategy_name: 策略名称
            date: 筛选日期
            max_stocks: 最大处理股票数量（用于测试）
            
        Returns:
            筛选结果列表
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        self.log_info(f"开始运行优化版 {strategy_name} 策略选股，日期: {date}")
        
        if strategy_name == "bollinger":
            return self._run_bollinger_screening_optimized(date, max_stocks)
        else:
            self.log_error(f"不支持的策略: {strategy_name}")
            return []
    
    def _run_bollinger_screening_optimized(self, date: str, max_stocks: int = None) -> List[Dict[str, Any]]:
        """运行优化版布林带策略筛选"""
        from ..data.stock_data import StockDataManager
        
        data_manager = StockDataManager(self.config)
        stock_list = data_manager.get_stock_list()
        
        # 限制股票数量（用于测试）
        if max_stocks:
            stock_list = stock_list.head(max_stocks)
        
        total_stocks = len(stock_list)
        self.log_info(f"开始处理 {total_stocks} 只股票")
        
        # 分批处理股票
        picks = []
        batches = [stock_list[i:i+self.batch_size] for i in range(0, len(stock_list), self.batch_size)]
        
        start_time = time.time()
        
        for batch_idx, batch in enumerate(batches):
            self.log_info(f"处理批次 {batch_idx + 1}/{len(batches)} ({len(batch)} 只股票)")
            
            # 并发处理当前批次
            batch_picks = self._process_batch_concurrent(batch, data_manager, date)
            picks.extend(batch_picks)
            
            # 显示进度
            processed = (batch_idx + 1) * self.batch_size
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            eta = (total_stocks - processed) / rate if rate > 0 else 0
            
            self.log_info(f"已处理: {min(processed, total_stocks)}/{total_stocks}, "
                         f"速度: {rate:.1f} 股票/秒, ETA: {eta:.1f} 秒")
        
        total_time = time.time() - start_time
        self.log_info(f"布林带筛选完成，共找到 {len(picks)} 只符合条件的股票，"
                     f"总耗时: {total_time:.2f} 秒，平均速度: {total_stocks/total_time:.1f} 股票/秒")
        
        return picks
    
    def _process_batch_concurrent(self, batch: pd.DataFrame, data_manager, date: str) -> List[Dict[str, Any]]:
        """并发处理一批股票"""
        picks = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_stock = {
                executor.submit(self._process_single_stock, row, data_manager, date): row 
                for _, row in batch.iterrows()
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_stock):
                stock_row = future_to_stock[future]
                try:
                    result = future.result()
                    if result:
                        picks.append(result)
                except Exception as e:
                    stock_code = stock_row['code']
                    self.log_error(f"处理股票 {stock_code} 时出错: {str(e)}")
        
        return picks
    
    def _process_single_stock(self, stock_row: pd.Series, data_manager, date: str) -> Dict[str, Any]:
        """处理单只股票"""
        stock_code = stock_row['code']
        stock_name = stock_row['name']
        
        try:
            # 获取股票数据
            data = data_manager.get_latest_data(stock_code, days=60)
            
            if data.empty:
                return None
            
            # 计算布林带
            data = self.bollinger.calculate(data)
            
            if data.empty:
                return None
            
            # 分析信号
            signals = self.bollinger.analyze_signals(data)
            
            # 应用筛选条件
            if self._apply_screening_conditions_optimized(data, signals):
                return {
                    'code': stock_code,
                    'name': stock_name,
                    'current_price': signals['current_price'],
                    'bb_position': signals['bb_position'],
                    'signals': signals['signals'],
                    'screening_date': date
                }
            
            return None
            
        except Exception as e:
            self.log_error(f"处理股票 {stock_code} 时出错: {str(e)}")
            return None
    
    def _apply_screening_conditions_optimized(self, data: pd.DataFrame, 
                                            signals: Dict[str, Any]) -> bool:
        """优化版筛选条件应用"""
        if not signals or data.empty:
            return False
        
        latest = data.iloc[-1]
        
        # 快速价格检查
        price_conditions = self.screening_config.get('price_conditions', {})
        min_price = price_conditions.get('min_price', 5.0)
        max_price = price_conditions.get('max_price', 100.0)
        
        current_price = latest['close']
        if not (min_price <= current_price <= max_price):
            return False
        
        # 布林带位置检查
        bb_position = signals.get('bb_position', 0.5)
        stock_signals = signals.get('signals', [])
        
        # 快速信号检查
        # 寻找超跌反弹机会
        if '触及下轨' in stock_signals:
            return True
        
        # 寻找回归均值机会
        if 0.1 <= bb_position <= 0.3:
            return True
        
        # 成交量确认（简化版）
        if 'volume' in data.columns and len(data) >= 20:
            volume_ratio = self.screening_config.get('technical_conditions', {}).get('volume_ratio', 1.5)
            recent_volume = data['volume'].tail(5).mean()
            avg_volume = data['volume'].tail(20).mean()
            
            if recent_volume > avg_volume * volume_ratio:
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
            'performance_metrics': {
                'processing_time': 'optimized',
                'concurrent_workers': self.max_workers,
                'batch_size': self.batch_size
            }
        }
        
        return summary
