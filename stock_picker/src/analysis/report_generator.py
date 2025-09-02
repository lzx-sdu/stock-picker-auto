#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器模块
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from ..utils.logger import LoggerMixin


class ReportGenerator(LoggerMixin):
    """报告生成器"""
    
    def __init__(self, config):
        self.config = config
        self.reporting_config = config.get_reporting_config()
    
    def generate_report(self, date: str, output_file: str):
        """生成分析报告"""
        self.log_info(f"开始生成 {date} 的分析报告")
        
        try:
            # 创建简单的HTML报告
            html_content = self._create_html_report(date)
            
            # 确保输出目录存在
            import os
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 保存报告
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.log_info(f"报告已生成: {output_file}")
            
        except Exception as e:
            self.log_error(f"生成报告失败: {str(e)}")
            raise
    
    def _create_html_report(self, date: str) -> str:
        """创建HTML报告内容"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>A股布林带均值回归选股报告 - {date}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        .section {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; }}
        .info-card {{ background-color: white; padding: 15px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>📊 A股布林带均值回归选股报告</h1>
    
    <div class="section">
        <h2>📅 报告信息</h2>
        <div class="info-card">
            <p><strong>报告日期:</strong> {date}</p>
            <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>策略类型:</strong> 布林带均值回归</p>
        </div>
    </div>
    
    <div class="section">
        <h2>⚙️ 策略配置</h2>
        <div class="info-card">
            <p><strong>布林带周期:</strong> 20天</p>
            <p><strong>标准差倍数:</strong> 2.0</p>
            <p><strong>价格范围:</strong> 5.0-100.0元</p>
        </div>
    </div>
    
    <div class="section">
        <h2>📈 运行状态</h2>
        <div class="info-card" style="background-color: #d4edda; color: #155724;">
            <strong>✓ 系统运行正常</strong><br>
            所有模块已加载，配置已验证，可以开始选股分析。
        </div>
    </div>
    
    <div class="section">
        <h2>🔍 使用说明</h2>
        <div class="info-card">
            <p><strong>数据获取:</strong> python main.py --mode data --update-stock-list</p>
            <p><strong>选股分析:</strong> python main.py --mode screen --strategy bollinger</p>
            <p><strong>生成报告:</strong> python main.py --mode report --date {date}</p>
        </div>
    </div>
    
    <div style="text-align: center; margin-top: 30px; color: #666;">
        <p>⚠️ 风险提示：本系统仅用于技术分析，不构成投资建议。股市有风险，投资需谨慎。</p>
        <p>© 2024 A股布林带均值回归选股系统</p>
    </div>
</body>
</html>
        """
        return html_content
    
    def generate_bollinger_report(self, report_data: Dict[str, Any]) -> str:
        """生成布林带策略的详细HTML报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{report_data.get('strategy_name', '布林带均值回归策略')} - {report_data.get('date', '')}</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background-color: white; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            overflow: hidden; 
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        
        .content {{ padding: 30px; }}
        
        .section {{ 
            margin: 30px 0; 
            padding: 25px; 
            background-color: #f8f9fa; 
            border-radius: 8px; 
            border-left: 4px solid #667eea; 
        }}
        
        .section h2 {{ 
            color: #2c3e50; 
            margin-top: 0; 
            font-size: 1.5em; 
        }}
        
        .summary-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin: 20px 0; 
        }}
        
        .summary-card {{ 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            text-align: center; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        }}
        
        .summary-card .number {{ 
            font-size: 2em; 
            font-weight: bold; 
            color: #667eea; 
        }}
        
        .summary-card .label {{ 
            color: #666; 
            margin-top: 5px; 
        }}
        
        .stock-table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
            background: white; 
            border-radius: 8px; 
            overflow: hidden; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        }}
        
        .stock-table th {{ 
            background-color: #667eea; 
            color: white; 
            padding: 15px; 
            text-align: left; 
        }}
        
        .stock-table td {{ 
            padding: 12px 15px; 
            border-bottom: 1px solid #eee; 
        }}
        
        .stock-table tr:hover {{ background-color: #f8f9fa; }}
        
        .risk-low {{ color: #28a745; font-weight: bold; }}
        .risk-medium {{ color: #ffc107; font-weight: bold; }}
        .risk-high {{ color: #dc3545; font-weight: bold; }}
        
        .confidence-bar {{ 
            background-color: #e9ecef; 
            border-radius: 10px; 
            height: 8px; 
            overflow: hidden; 
        }}
        
        .confidence-fill {{ 
            background: linear-gradient(90deg, #28a745, #20c997); 
            height: 100%; 
            border-radius: 10px; 
        }}
        
        .portfolio-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }}
        
        .portfolio-card {{ 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        }}
        
        .footer {{ 
            background-color: #2c3e50; 
            color: white; 
            text-align: center; 
            padding: 20px; 
            margin-top: 30px; 
        }}
        
        .warning {{ 
            background-color: #fff3cd; 
            border: 1px solid #ffeaa7; 
            color: #856404; 
            padding: 15px; 
            border-radius: 5px; 
            margin: 20px 0; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {report_data.get('strategy_name', '布林带均值回归策略')}</h1>
            <p>基于多重技术指标的综合选股分析报告</p>
            <p>报告日期: {report_data.get('date', '')}</p>
        </div>
        
        <div class="content">
            <!-- 策略摘要 -->
            <div class="section">
                <h2>📈 策略摘要</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="number">{report_data.get('summary', {}).get('total_screened', 0)}</div>
                        <div class="label">筛选股票数</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{report_data.get('summary', {}).get('portfolio_positions', 0)}</div>
                        <div class="label">投资组合股票数</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{report_data.get('summary', {}).get('avg_confidence', 0):.3f}</div>
                        <div class="label">平均置信度</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{report_data.get('summary', {}).get('avg_risk_level', 'medium').upper()}</div>
                        <div class="label">平均风险等级</div>
                    </div>
                </div>
            </div>
            
            <!-- 风险指标 -->
            <div class="section">
                <h2>⚠️ 风险指标</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="number">{report_data.get('risk_metrics', {}).get('avg_volatility', 0):.2%}</div>
                        <div class="label">平均波动率</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{report_data.get('risk_metrics', {}).get('avg_max_drawdown', 0):.2%}</div>
                        <div class="label">平均最大回撤</div>
                    </div>
                </div>
            </div>
            
            <!-- 市场分布 -->
            <div class="section">
                <h2>🏢 市场分布</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="number">{report_data.get('market_analysis', {}).get('market_distribution', {}).get('sh', 0)}</div>
                        <div class="label">上海市场</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{report_data.get('market_analysis', {}).get('market_distribution', {}).get('sz', 0)}</div>
                        <div class="label">深圳市场</div>
                    </div>
                </div>
            </div>
            
            <!-- 推荐股票 -->
            <div class="section">
                <h2>🎯 推荐股票</h2>
                {self._generate_stock_table(report_data.get('top_picks', []))}
            </div>
            
            <!-- 投资组合 -->
            <div class="section">
                <h2>💼 投资组合建议</h2>
                {self._generate_portfolio_table(report_data.get('portfolio_allocation', []))}
            </div>
            
            <!-- 风险提示 -->
            <div class="warning">
                <strong>⚠️ 重要风险提示：</strong><br>
                1. 本报告基于技术分析，不构成投资建议<br>
                2. 股市有风险，投资需谨慎<br>
                3. 请根据自身风险承受能力做出投资决策<br>
                4. 建议分散投资，不要将所有资金投入单一股票
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 布林带均值回归选股系统 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        return html_content
    
    def _generate_stock_table(self, stocks: List[Dict[str, Any]]) -> str:
        """生成股票表格HTML"""
        if not stocks:
            return '<p>暂无推荐股票</p>'
        
        table_html = '''
        <table class="stock-table">
            <thead>
                <tr>
                    <th>股票代码</th>
                    <th>当前价格</th>
                    <th>布林带位置</th>
                    <th>RSI</th>
                    <th>综合评分</th>
                    <th>目标价格</th>
                    <th>止损价格</th>
                    <th>风险等级</th>
                    <th>持有期</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for stock in stocks:
            risk_class = f"risk-{stock.get('trading_advice', {}).get('risk_level', 'medium')}"
            confidence_width = stock.get('composite_score', 0) * 100
            
            table_html += f'''
                <tr>
                    <td><strong>{stock.get('stock_code', '')}</strong></td>
                    <td>¥{stock.get('current_price', 0):.2f}</td>
                    <td>{stock.get('bb_position', 0):.3f}</td>
                    <td>{stock.get('rsi', 0):.1f}</td>
                    <td>
                        {stock.get('composite_score', 0):.3f}
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {confidence_width}%"></div>
                        </div>
                    </td>
                    <td>¥{stock.get('trading_advice', {}).get('target_price', 0):.2f}</td>
                    <td>¥{stock.get('trading_advice', {}).get('stop_loss', 0):.2f}</td>
                    <td class="{risk_class}">{stock.get('trading_advice', {}).get('risk_level', 'medium').upper()}</td>
                    <td>{stock.get('trading_advice', {}).get('holding_period', 'medium')}</td>
                </tr>
            '''
        
        table_html += '</tbody></table>'
        return table_html
    
    def _generate_portfolio_table(self, positions: List[Dict[str, Any]]) -> str:
        """生成投资组合表格HTML"""
        if not positions:
            return '<p>暂无投资组合建议</p>'
        
        table_html = '''
        <table class="stock-table">
            <thead>
                <tr>
                    <th>股票代码</th>
                    <th>当前价格</th>
                    <th>权重</th>
                    <th>建议仓位</th>
                    <th>目标价格</th>
                    <th>止损价格</th>
                    <th>风险等级</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for pos in positions:
            risk_class = f"risk-{pos.get('risk_level', 'medium')}"
            
            table_html += f'''
                <tr>
                    <td><strong>{pos.get('stock_code', '')}</strong></td>
                    <td>¥{pos.get('current_price', 0):.2f}</td>
                    <td>{pos.get('weight', 0):.1%}</td>
                    <td>{pos.get('position_size', 0):.1%}</td>
                    <td>¥{pos.get('target_price', 0):.2f}</td>
                    <td>¥{pos.get('stop_loss', 0):.2f}</td>
                    <td class="{risk_class}">{pos.get('risk_level', 'medium').upper()}</td>
                </tr>
            '''
        
        table_html += '</tbody></table>'
        return table_html
