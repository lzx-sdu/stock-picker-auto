#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布林带均值回归策略运行器
"""

import os
import sys
import pandas as pd
from datetime import datetime
import yaml

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from strategy.bollinger_mean_reversion import BollingerMeanReversionStrategy
from analysis.stock_screener import StockScreener
from analysis.report_generator import ReportGenerator
from utils.config import Config

class BollingerStrategyRunner:
    """布林带策略运行器"""
    
    def __init__(self):
        """初始化"""
        self.config = Config()
        self.strategy = BollingerMeanReversionStrategy(self.config)
        self.screener = StockScreener()
        self.report_generator = ReportGenerator()
        
    def run_strategy(self, max_stocks=500):
        """运行策略"""
        print("🚀 开始运行布林带均值回归策略...")
        print("=" * 60)
        
        try:
            # 1. 获取股票列表
            print("📊 获取股票列表...")
            stock_list = self.screener.get_stock_list()
            print(f"✅ 获取到 {len(stock_list)} 只股票")
            
            # 2. 筛选股票
            print("🔍 开始筛选股票...")
            screened_stocks = []
            
            for i, stock_code in enumerate(stock_list[:max_stocks]):
                try:
                    print(f"处理进度: {i+1}/{min(len(stock_list), max_stocks)} - {stock_code}")
                    
                    # 分析股票
                    result = self.strategy.analyze_stock(stock_code)
                    
                    if result and result['composite_score'] > 0.5:
                        # 格式化股票代码为6位
                        result['stock_code'] = str(stock_code).zfill(6)
                        screened_stocks.append(result)
                        
                except Exception as e:
                    print(f"处理股票 {stock_code} 时出错: {str(e)}")
                    continue
            
            print(f"✅ 筛选完成，共找到 {len(screened_stocks)} 只符合条件的股票")
            
            # 3. 生成投资组合
            print("💼 生成投资组合...")
            portfolio = self._generate_portfolio(screened_stocks)
            
            # 4. 保存结果
            print("💾 保存结果...")
            self._save_results(screened_stocks, portfolio)
            
            # 5. 生成报告
            print("📄 生成HTML报告...")
            self._generate_report(screened_stocks, portfolio)
            
            print("🎉 策略运行完成！")
            print("=" * 60)
            
            return {
                'screened_stocks': screened_stocks,
                'portfolio': portfolio
            }
            
        except Exception as e:
            print(f"❌ 策略运行失败: {str(e)}")
            return None
    
    def _generate_portfolio(self, screened_stocks):
        """生成投资组合"""
        if not screened_stocks:
            return {'positions': [], 'total_positions': 0}
        
        # 按评分排序，选择前10只
        top_stocks = sorted(screened_stocks, key=lambda x: x['composite_score'], reverse=True)[:10]
        
        positions = []
        for stock in top_stocks:
            position = {
                'stock_code': stock['stock_code'],
                'stock_name': stock.get('stock_name', ''),
                'current_price': stock['current_price'],
                'target_price': stock['trading_advice']['target_price'],
                'stop_loss': stock['trading_advice']['stop_loss'],
                'confidence': stock['composite_score'],
                'risk_level': stock['trading_advice']['risk_level']
            }
            positions.append(position)
        
        return {
            'positions': positions,
            'total_positions': len(positions)
        }
    
    def _save_results(self, screened_stocks, portfolio):
        """保存结果到CSV文件"""
        # 创建结果目录
        os.makedirs('results/picks', exist_ok=True)
        os.makedirs('results/reports', exist_ok=True)
        
        # 保存筛选结果
        date = datetime.now().strftime('%Y-%m-%d')
        
        # 格式化股票代码为6位
        for stock in screened_stocks:
            stock['stock_code'] = str(stock['stock_code']).zfill(6)
        
        picks_df = pd.DataFrame(screened_stocks)
        picks_df.to_csv(f'results/picks/bollinger_picks_{date}.csv', index=False, encoding='utf-8-sig')
        
        # 保存投资组合
        portfolio_df = pd.DataFrame(portfolio['positions'])
        portfolio_df.to_csv(f'results/picks/bollinger_portfolio_{date}.csv', index=False, encoding='utf-8-sig')
        
        print(f"✅ 结果已保存到 results/picks/ 目录")
    
    def _generate_report(self, screened_stocks, portfolio):
        """生成HTML报告"""
        date = datetime.now().strftime('%Y-%m-%d')
        report_path = f'results/reports/bollinger_report_{date}.html'
        
        self.report_generator.generate_report(screened_stocks, portfolio['positions'], report_path)
        
        print(f"✅ HTML报告已生成: {report_path}")

def main():
    """主函数"""
    runner = BollingerStrategyRunner()
    results = runner.run_strategy(max_stocks=500)
    
    if results:
        print(f"\n📊 筛选结果统计:")
        print(f"   - 筛选股票数量: {len(results['screened_stocks'])}")
        print(f"   - 投资组合数量: {results['portfolio']['total_positions']}")
        print(f"   - 平均评分: {sum(s['composite_score'] for s in results['screened_stocks']) / len(results['screened_stocks']):.3f}")
        
        # 打开HTML报告
        date = datetime.now().strftime('%Y-%m-%d')
        report_path = f'results/reports/bollinger_report_{date}.html'
        if os.path.exists(report_path):
            print(f"\n📱 正在打开HTML报告...")
            os.startfile(report_path)

if __name__ == "__main__":
    main()

