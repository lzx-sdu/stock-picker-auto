#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选股策略性能优化脚本
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

class OptimizedScreener:
    """优化版选股器"""
    
    def __init__(self, config):
        self.config = config
        self.data_manager = StockDataManager(config)
        self.bollinger = BollingerBands(config)
        self.max_workers = 8  # 并发线程数
        self.batch_size = 20  # 批处理大小
    
    def run_optimized_screening(self, max_stocks: int = None) -> List[Dict[str, Any]]:
        """运行优化版选股"""
        print("=" * 50)
        print("优化版选股策略")
        print("=" * 50)
        
        # 获取股票列表
        stock_list = self.data_manager.get_stock_list()
        if max_stocks:
            stock_list = stock_list.head(max_stocks)
        
        total_stocks = len(stock_list)
        print(f"开始处理 {total_stocks} 只股票")
        
        # 分批处理
        picks = []
        batches = [stock_list[i:i+self.batch_size] for i in range(0, len(stock_list), self.batch_size)]
        
        start_time = time.time()
        
        for batch_idx, batch in enumerate(batches):
            print(f"处理批次 {batch_idx + 1}/{len(batches)} ({len(batch)} 只股票)")
            
            # 并发处理当前批次
            batch_picks = self._process_batch_concurrent(batch)
            picks.extend(batch_picks)
            
            # 显示进度
            processed = (batch_idx + 1) * self.batch_size
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            eta = (total_stocks - processed) / rate if rate > 0 else 0
            
            print(f"已处理: {min(processed, total_stocks)}/{total_stocks}, "
                  f"速度: {rate:.1f} 股票/秒, ETA: {eta:.1f} 秒")
        
        total_time = time.time() - start_time
        print(f"选股完成，共找到 {len(picks)} 只符合条件的股票")
        print(f"总耗时: {total_time:.2f} 秒，平均速度: {total_stocks/total_time:.1f} 股票/秒")
        
        return picks
    
    def _process_batch_concurrent(self, batch: pd.DataFrame) -> List[Dict[str, Any]]:
        """并发处理一批股票"""
        picks = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_stock = {
                executor.submit(self._process_single_stock, row): row 
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
                    print(f"处理股票 {stock_code} 时出错: {str(e)}")
        
        return picks
    
    def _process_single_stock(self, stock_row: pd.Series) -> Dict[str, Any]:
        """处理单只股票"""
        stock_code = stock_row['code']
        stock_name = stock_row['name']
        
        try:
            # 获取股票数据
            data = self.data_manager.get_latest_data(stock_code, days=60)
            
            if data.empty:
                return None
            
            # 计算布林带
            data = self.bollinger.calculate(data)
            
            if data.empty:
                return None
            
            # 分析信号
            signals = self.bollinger.analyze_signals(data)
            
            # 应用筛选条件
            if self._apply_screening_conditions(data, signals):
                return {
                    'code': stock_code,
                    'name': stock_name,
                    'current_price': signals['current_price'],
                    'bb_position': signals['bb_position'],
                    'signals': signals['signals']
                }
            
            return None
            
        except Exception as e:
            print(f"处理股票 {stock_code} 时出错: {str(e)}")
            return None
    
    def _apply_screening_conditions(self, data: pd.DataFrame, signals: Dict[str, Any]) -> bool:
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
    
    config = Config("config.yaml")
    
    # 测试优化版
    print("\n1. 测试优化版选股器...")
    optimized_screener = OptimizedScreener(config)
    
    start_time = time.time()
    picks = optimized_screener.run_optimized_screening(max_stocks=50)
    optimized_time = time.time() - start_time
    
    print(f"优化版结果: {len(picks)} 只股票，耗时: {optimized_time:.2f} 秒")
    
    # 显示结果
    if picks:
        print("\n筛选结果:")
        for pick in picks[:10]:  # 显示前10只
            print(f"  {pick['code']} ({pick['name']}) - 价格: {pick['current_price']:.2f}, "
                  f"BB位置: {pick['bb_position']:.2f}")
    
    return picks

if __name__ == "__main__":
    compare_performance()

