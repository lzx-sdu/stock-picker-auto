#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布林带均值回归策略运行器 - GitHub Actions专用版本
"""

import os
import sys
import pandas as pd
from datetime import datetime
import yaml

# 修复GitHub Actions环境下的Python路径问题
def setup_python_path():
    """设置Python路径"""
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查是否在GitHub Actions环境中
    if os.environ.get('GITHUB_ACTIONS'):
        print("🔍 检测到GitHub Actions环境")
        # GitHub Actions中，代码在 /home/runner/work/仓库名/仓库名/ 目录下
        # 需要添加src目录到Python路径
        src_path = os.path.join(current_dir, 'src')
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)
            print(f"✅ 已添加src路径: {src_path}")
        else:
            print(f"❌ src目录不存在: {src_path}")
            # 尝试其他可能的路径
            possible_paths = [
                'src',
                '../src',
                '../../src',
                os.path.join(os.path.dirname(__file__), 'src')
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    sys.path.insert(0, os.path.abspath(path))
                    print(f"✅ 找到替代路径: {os.path.abspath(path)}")
                    break
    else:
        print("🔍 本地环境")
        # 本地环境中，使用相对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(current_dir, 'src')
        sys.path.insert(0, src_path)
        print(f"✅ 已添加src路径: {src_path}")
    
    print(f"Python路径: {sys.path}")

# 设置Python路径
setup_python_path()

# 尝试导入模块
try:
    from utils.logger import LoggerMixin
    print("✅ 基础模块导入成功")
except ImportError as e:
    print(f"❌ 基础模块导入失败: {e}")
    sys.exit(1)

class SimpleStockRunner:
    """简化的股票筛选运行器 - 用于GitHub Actions测试"""
    
    def __init__(self):
        """初始化"""
        try:
            print("✅ 简化运行器初始化成功")
        except Exception as e:
            print(f"❌ 简化运行器初始化失败: {e}")
            raise
    
    def run_strategy(self, max_stocks=500):
        """运行策略"""
        print("🚀 开始运行简化版布林带策略...")
        print("=" * 60)
        
        try:
            # 创建模拟数据用于测试
            print("📊 创建模拟股票数据...")
            mock_stocks = self._create_mock_stocks(max_stocks)
            print(f"✅ 创建了 {len(mock_stocks)} 只模拟股票")
            
            # 模拟筛选过程
            print("🔍 开始模拟筛选...")
            screened_stocks = self._mock_screening(mock_stocks)
            print(f"✅ 筛选完成，共找到 {len(screened_stocks)} 只符合条件的股票")
            
            # 生成投资组合
            print("💼 生成投资组合...")
            portfolio = self._generate_portfolio(screened_stocks)
            
            # 保存结果
            print("💾 保存结果...")
            self._save_results(screened_stocks, portfolio)
            
            # 生成报告
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
            import traceback
            traceback.print_exc()
            return None
    
    def _create_mock_stocks(self, count):
        """创建模拟股票数据"""
        stocks = []
        for i in range(count):
            stock = {
                'stock_code': f"{i+1:06d}",
                'stock_name': f"模拟股票{i+1}",
                'current_price': round(10 + i * 0.1, 2),
                'bb_position': round(0.3 + (i % 3) * 0.2, 2),
                'rsi': round(30 + (i % 5) * 10, 2),
                'macd_signal': 'golden_cross' if i % 2 == 0 else 'death_cross',
                'volume_ratio': round(0.8 + (i % 3) * 0.3, 2),
                'composite_score': round(0.5 + (i % 5) * 0.1, 2),
                'trading_advice': {
                    'target_price': round(12 + i * 0.15, 2),
                    'stop_loss': round(8 + i * 0.1, 2),
                    'risk_level': 'low' if i % 3 == 0 else 'medium' if i % 3 == 1 else 'high'
                }
            }
            stocks.append(stock)
        return stocks
    
    def _mock_screening(self, stocks):
        """模拟筛选过程"""
        # 筛选评分大于0.6的股票
        screened = [stock for stock in stocks if stock['composite_score'] > 0.6]
        return screened[:20]  # 最多返回20只
    
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
                'stock_name': stock['stock_name'],
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
        picks_file = f'results/picks/bollinger_picks_{date}.csv'
        portfolio_file = f'results/picks/bollinger_portfolio_{date}.csv'
        
        # 转换为DataFrame并保存
        picks_df = pd.DataFrame(screened_stocks)
        picks_df.to_csv(picks_file, index=False, encoding='utf-8-sig')
        print(f"✅ 筛选结果已保存到: {picks_file}")
        
        portfolio_df = pd.DataFrame(portfolio['positions'])
        portfolio_df.to_csv(portfolio_file, index=False, encoding='utf-8-sig')
        print(f"✅ 投资组合已保存到: {portfolio_file}")
    
    def _generate_report(self, screened_stocks, portfolio):
        """生成HTML报告"""
        try:
            from analysis.report_generator import ReportGenerator
            generator = ReportGenerator()
            
            date = datetime.now().strftime('%Y-%m-%d')
            report_file = f'results/reports/bollinger_report_{date}.html'
            
            # 生成报告
            generator.generate_report(
                screened_stocks,
                portfolio['positions'],
                report_file
            )
            
            print(f"✅ HTML报告已生成: {report_file}")
            
        except Exception as e:
            print(f"❌ 生成HTML报告失败: {e}")
            # 创建简单的HTML报告
            self._create_simple_html_report(screened_stocks, portfolio)
    
    def _create_simple_html_report(self, screened_stocks, portfolio):
        """创建简单的HTML报告"""
        date = datetime.now().strftime('%Y-%m-%d')
        report_file = f'results/reports/bollinger_report_{date}.html'
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票筛选报告 - {date}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .summary {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 布林带均值回归策略选股报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
    </div>
    
    <div class="content">
        <div class="summary">
            <h2>📊 筛选摘要</h2>
            <p>筛选股票数量: {len(screened_stocks)}</p>
            <p>投资组合数量: {portfolio['total_positions']}</p>
        </div>
        
        <h2>🎯 筛选结果</h2>
        <table>
            <tr>
                <th>股票代码</th>
                <th>股票名称</th>
                <th>当前价格</th>
                <th>综合评分</th>
                <th>目标价格</th>
                <th>止损价格</th>
                <th>风险等级</th>
            </tr>
"""
        
        for stock in screened_stocks:
            html_content += f"""
            <tr>
                <td>{stock['stock_code']}</td>
                <td>{stock['stock_name']}</td>
                <td>{stock['current_price']}</td>
                <td>{stock['composite_score']}</td>
                <td>{stock['trading_advice']['target_price']}</td>
                <td>{stock['trading_advice']['stop_loss']}</td>
                <td>{stock['trading_advice']['risk_level']}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
</body>
</html>
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 简单HTML报告已生成: {report_file}")

def main():
    """主函数"""
    print("🚀 布林带均值回归策略运行器 - GitHub Actions版本")
    print("=" * 60)
    
    try:
        runner = SimpleStockRunner()
        results = runner.run_strategy(max_stocks=500)
        
        if results:
            print("🎉 策略运行成功！")
            print(f"筛选结果: {len(results['screened_stocks'])} 只股票")
            print(f"投资组合: {results['portfolio']['total_positions']} 个仓位")
        else:
            print("❌ 策略运行失败")
            
    except Exception as e:
        print(f"❌ 程序运行异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

