#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据管理模块
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import akshare as ak
import time

from utils.logger import LoggerMixin


class StockDataManager(LoggerMixin):
    """股票数据管理器"""
    
    def __init__(self, config):
        self.config = config
        self.data_dir = "data"
        self.historical_dir = os.path.join(self.data_dir, "historical_data")
        self.stock_list_file = os.path.join(self.data_dir, "stock_list.csv")
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [self.data_dir, self.historical_dir]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
    
    def update_stock_list(self) -> pd.DataFrame:
        """更新A股股票列表"""
        self.log_info("开始更新A股股票列表...")
        
        try:
            stock_list = ak.stock_info_a_code_name()
            # 确保股票代码是字符串类型
            stock_list['code'] = stock_list['code'].astype(str)
            stock_list['market'] = stock_list['code'].apply(
                lambda x: 'sh' if x.startswith(('600', '601', '603', '688')) else 'sz'
            )
            
            # 过滤ST股票
            stock_list = stock_list[~stock_list['name'].str.contains('ST|退')]
            
            stock_list.to_csv(self.stock_list_file, index=False, encoding='utf-8')
            self.log_info(f"股票列表更新完成，共 {len(stock_list)} 只股票")
            
            return stock_list
            
        except Exception as e:
            self.log_error(f"更新股票列表失败: {str(e)}")
            raise
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        if os.path.exists(self.stock_list_file):
            stock_list = pd.read_csv(self.stock_list_file, encoding='utf-8')
            # 确保股票代码是字符串类型
            stock_list['code'] = stock_list['code'].astype(str)
            return stock_list
        else:
            return self.update_stock_list()
    
    def get_stock_data(self, stock_code: str, start_date: str = None, 
                      end_date: str = None) -> pd.DataFrame:
        """获取单个股票的历史数据"""
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        try:
            # 确保股票代码是字符串类型并补齐6位
            stock_code = str(stock_code).zfill(6)
            # 添加市场前缀
            if stock_code.startswith(('600', '601', '603', '688')):
                full_code = f"sh{stock_code}"
            else:
                full_code = f"sz{stock_code}"
            
            # 获取历史数据 - 使用更可靠的API
            try:
                data = ak.stock_zh_a_daily(symbol=full_code)
                # 暂时不进行日期过滤，获取所有可用数据
            except Exception as e:
                self.log_error(f"使用stock_zh_a_daily失败，尝试stock_zh_a_hist: {str(e)}")
                data = ak.stock_zh_a_hist(symbol=full_code, period="daily", 
                                         start_date=start_date, end_date=end_date, 
                                         adjust="qfq")
            
            # 检查数据列名并重命名
            if '日期' in data.columns:
                column_mapping = {
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'change_pct',
                    '涨跌额': 'change_amount',
                    '换手率': 'turnover_rate'
                }
                data = data.rename(columns=column_mapping)
            elif 'date' in data.columns:
                # 如果已经是英文列名，直接使用
                pass
            else:
                self.log_error(f"未知的数据列名: {list(data.columns)}")
                return pd.DataFrame()
            
            # 确保日期列存在并设置为索引
            if 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                data = data.set_index('date')
            elif data.index.name == 'date' or isinstance(data.index, pd.DatetimeIndex):
                # 如果已经是日期索引，直接使用
                pass
            else:
                self.log_error(f"找不到日期列，可用列: {list(data.columns)}")
                return pd.DataFrame()
            
            return data
            
        except Exception as e:
            self.log_error(f"获取股票 {stock_code} 数据失败: {str(e)}")
            return pd.DataFrame()
    
    def update_daily_data(self, date: str = None):
        """更新指定日期的股票数据"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        self.log_info(f"开始更新 {date} 的股票数据...")
        
        stock_list = self.get_stock_list()
        success_count = 0
        total_count = len(stock_list)
        
        for idx, row in stock_list.iterrows():
            stock_code = row['code']
            try:
                end_date = date
                start_date = (datetime.strptime(date, "%Y-%m-%d") - 
                            timedelta(days=30)).strftime("%Y-%m-%d")
                
                data = self.get_stock_data(stock_code, start_date, end_date)
                
                if not data.empty:
                    file_path = os.path.join(self.historical_dir, f"{stock_code}.csv")
                    data.to_csv(file_path, encoding='utf-8')
                    success_count += 1
                
                time.sleep(0.1)
                
                if (idx + 1) % 100 == 0:
                    self.log_info(f"已处理 {idx + 1}/{total_count} 只股票")
                    
            except Exception as e:
                self.log_error(f"处理股票 {stock_code} 时出错: {str(e)}")
                continue
        
        self.log_info(f"数据更新完成，成功处理 {success_count}/{total_count} 只股票")
    
    def get_latest_data(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """获取股票最新数据"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        return self.get_stock_data(stock_code, start_date, end_date)
    
    def load_stock_data(self, stock_code: str) -> pd.DataFrame:
        """从本地加载股票数据"""
        file_path = os.path.join(self.historical_dir, f"{stock_code}.csv")
        if os.path.exists(file_path):
            data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            return data
        else:
            self.log_warning(f"本地数据文件不存在: {file_path}")
            return pd.DataFrame() 