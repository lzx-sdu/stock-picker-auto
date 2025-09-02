#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布林带均值回归策略运行器 - 修复版本
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.utils.logger import LoggerMixin
from src.data.stock_data import StockDataManager
from src.strategy.bollinger_mean_reversion_fixed import BollingerMeanReversionStrategyFixed
from src.analysis.report_generator import ReportGenerator


class BollingerStrategyRunnerFixed(LoggerMixin):
    """布林带策略运行器 - 修复版本"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = Config(config_path)
        self.data_manager = StockDataManager(self.config)
        self.strategy = BollingerMeanReversionStrategyFixed(self.config)
        self.report_generator = ReportGenerator(self.config)
        
    def run_strategy(self, date: str = None, max_stocks: int = 50) -> Dict[str, Any]:
        """运行布林带均值回归策略"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        self.log_info(f"开始运行布林带均值回归策略（修复版本），日期: {date}")
        
        try:
            # 获取股票列表
            stock_list = self.data_manager.get_stock_list()
            self.log_info(f"获取到 {len(stock_list)} 只股票")
            
            # 获取股票数据
            stock_data_dict = self._get_stock_data(stock_list, max_stocks)
            self.log_info(f"成功获取 {len(stock_data_dict)} 只股票的历史数据")
            
            # 运行策略筛选
            screened_stocks = self.strategy.screen_stocks(stock_data_dict)
            self.log_info(f"策略筛选出 {len(screened_stocks)} 只符合条件的股票")
            
            # 生成投资组合建议
            portfolio = self.strategy.generate_portfolio_recommendation(screened_stocks)
            
            # 生成报告
            report = self._generate_report(screened_stocks, portfolio, date)
            
            # 保存结果
            self._save_results(screened_stocks, portfolio, report, date)
            
            return {
                'screened_stocks': screened_stocks,
                'portfolio': portfolio,
                'report': report,
                'date': date
            }
            
        except Exception as e:
            self.log_error(f"运行策略时出错: {str(e)}")
            return {}
    
    def _get_stock_data(self, stock_list: pd.DataFrame, max_stocks: int) -> Dict[str, pd.DataFrame]:
        """获取股票历史数据"""
        stock_data_dict = {}
        count = 0
        
        for idx, row in stock_list.iterrows():
            if count >= max_stocks:
                break
                
            stock_code = row['code']
            
            try:
                # 获取最近60天的数据
                data = self.data_manager.get_latest_data(stock_code, days=60)
                
                if not data.empty and len(data) >= 50:
                    stock_data_dict[stock_code] = data
                    count += 1
                
                if count % 10 == 0:
                    self.log_info(f"已获取 {count} 只股票数据")
                    
            except Exception as e:
                self.log_warning(f"获取股票 {stock_code} 数据失败: {str(e)}")
                continue
        
        return stock_data_dict
    
    def _generate_report(self, screened_stocks: List[Dict[str, Any]], 
                        portfolio: Dict[str, Any], date: str) -> Dict[str, Any]:
        """生成策略报告"""
        try:
            # 计算平均风险等级
            avg_risk_level = self._calculate_avg_risk_level(screened_stocks)
            
            # 分析市场分布
            market_analysis = self._analyze_market_distribution(screened_stocks)
            
            # 计算风险指标
            risk_metrics = self._calculate_risk_metrics(screened_stocks)
            
            report_data = {
                'strategy_name': '布林带均值回归策略 - 修复版本',
                'date': date,
                'summary': {
                    'total_screened': len(screened_stocks),
                    'portfolio_positions': portfolio.get('total_positions', 0),
                    'avg_confidence': np.mean([s['composite_score'] for s in screened_stocks]) if screened_stocks else 0,
                    'avg_risk_level': avg_risk_level
                },
                'risk_metrics': risk_metrics,
                'market_analysis': market_analysis,
                'top_picks': screened_stocks[:10],
                'portfolio_allocation': portfolio.get('positions', [])
            }
            
            return report_data
            
        except Exception as e:
            self.log_error(f"生成报告时出错: {str(e)}")
            return {}
    
    def _calculate_avg_risk_level(self, stocks: List[Dict[str, Any]]) -> str:
        """计算平均风险等级"""
        if not stocks:
            return 'medium'
        
        risk_scores = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        
        total_score = 0
        for stock in stocks:
            risk_level = stock.get('trading_advice', {}).get('risk_level', 'medium')
            total_score += risk_scores.get(risk_level, 2)
        
        avg_score = total_score / len(stocks)
        
        if avg_score <= 1.5:
            return 'low'
        elif avg_score <= 2.5:
            return 'medium'
        else:
            return 'high'
    
    def _analyze_market_distribution(self, stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析市场分布"""
        market_dist = {'sh': 0, 'sz': 0}
        
        for stock in stocks:
            code = stock.get('stock_code', '')
            
            # 市场分布
            if code.startswith(('600', '601', '603', '688')):
                market_dist['sh'] += 1
            else:
                market_dist['sz'] += 1
        
        return {
            'market_distribution': market_dist,
            'total_stocks': len(stocks)
        }
    
    def _calculate_risk_metrics(self, stocks: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算风险指标"""
        if not stocks:
            return {'avg_volatility': 0, 'avg_max_drawdown': 0}
        
        volatilities = []
        max_drawdowns = []
        
        for stock in stocks:
            risk_metrics = stock.get('risk_metrics', {})
            if 'volatility' in risk_metrics:
                volatilities.append(risk_metrics['volatility'])
            if 'max_drawdown' in risk_metrics:
                max_drawdowns.append(risk_metrics['max_drawdown'])
        
        return {
            'avg_volatility': np.mean(volatilities) if volatilities else 0,
            'avg_max_drawdown': np.mean(max_drawdowns) if max_drawdowns else 0
        }
    
    def _save_results(self, screened_stocks: List[Dict[str, Any]], 
                     portfolio: Dict[str, Any], report: Dict[str, Any], date: str):
        """保存结果"""
        # 确保输出目录存在
        output_dir = "results/picks"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存筛选结果
        if screened_stocks:
            df_picks = pd.DataFrame(screened_stocks)
            picks_file = f"{output_dir}/bollinger_picks_fixed_{date}.csv"
            df_picks.to_csv(picks_file, index=False, encoding='utf-8')
            self.log_info(f"筛选结果已保存到: {picks_file}")
        
        # 保存投资组合
        if portfolio.get('positions'):
            df_portfolio = pd.DataFrame(portfolio['positions'])
            portfolio_file = f"{output_dir}/bollinger_portfolio_fixed_{date}.csv"
            df_portfolio.to_csv(portfolio_file, index=False, encoding='utf-8')
            self.log_info(f"投资组合已保存到: {portfolio_file}")
        
        # 生成HTML报告
        try:
            html_report = self.report_generator.generate_bollinger_report(report)
            report_file = f"results/reports/bollinger_report_fixed_{date}.html"
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            self.log_info(f"HTML报告已保存到: {report_file}")
            
        except Exception as e:
            self.log_error(f"生成HTML报告失败: {str(e)}")
    
    def analyze_single_stock(self, stock_code: str) -> Dict[str, Any]:
        """分析单只股票"""
        try:
            data = self.data_manager.get_latest_data(stock_code, days=60)
            
            if data.empty:
                self.log_warning(f"股票 {stock_code} 没有数据")
                return {}
            
            analysis = self.strategy.analyze_stock(stock_code, data)
            
            if analysis:
                self.log_info(f"股票 {stock_code} 分析完成，综合评分: {analysis['composite_score']:.3f}")
            
            return analysis
            
        except Exception as e:
            self.log_error(f"分析股票 {stock_code} 时出错: {str(e)}")
            return {}


def main():
    """主函数"""
    print("=" * 60)
    print("布林带均值回归选股策略 - 修复版本")
    print("=" * 60)
    
    # 创建策略运行器
    runner = BollingerStrategyRunnerFixed()
    
    # 运行策略
    results = runner.run_strategy(max_stocks=100)
    
    if results:
        print(f"\n策略运行完成！")
        print(f"筛选出 {len(results['screened_stocks'])} 只股票")
        print(f"投资组合包含 {results['portfolio'].get('total_positions', 0)} 只股票")
        
        # 显示前5只股票
        if results['screened_stocks']:
            print("\n前5只推荐股票:")
            print("-" * 80)
            for i, stock in enumerate(results['screened_stocks'][:5], 1):
                trading_advice = stock['trading_advice']
                print(f"{i}. {stock['stock_code']} - 评分: {stock['composite_score']:.3f} - "
                      f"价格: {stock['current_price']:.2f} - "
                      f"目标: {trading_advice['target_price']:.2f} - "
                      f"止损: {trading_advice['stop_loss']:.2f} - "
                      f"风险等级: {trading_advice['risk_level']}")
    else:
        print("策略运行失败！")


if __name__ == "__main__":
    main()


