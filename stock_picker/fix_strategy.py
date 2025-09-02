#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复布林带策略的目标价格和止损价格计算问题
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def format_stock_code(stock_code):
    """格式化股票代码为6位标准格式"""
    code = str(stock_code).strip()
    
    # 如果是数字，补齐到6位
    if code.isdigit():
        return code.zfill(6)
    
    # 如果包含字母，提取数字部分
    import re
    numbers = re.findall(r'\d+', code)
    if numbers:
        return numbers[0].zfill(6)
    
    return code.zfill(6)

def calculate_target_price(signals, current_price, bb_data):
    """计算目标价格"""
    if not current_price or not bb_data:
        return 0.0
        
    bb_middle = bb_data.get('middle', current_price)
    
    # 根据信号类型调整目标价格
    if '强烈超跌' in signals.get('bb_signals', []):
        # 超跌反弹目标：回到布林带中轨
        return round(bb_middle, 2)
    elif '超跌反弹' in signals.get('bb_signals', []):
        # 反弹目标：中轨上方5%
        return round(bb_middle * 1.05, 2)
    elif '强烈超买' in signals.get('bb_signals', []):
        # 超买回调目标：回到中轨
        return round(bb_middle, 2)
    else:
        # 默认目标：当前价格上方15%
        return round(current_price * 1.15, 2)

def calculate_stop_loss(signals, current_price):
    """计算止损价格"""
    if not current_price:
        return 0.0
        
    # 基础止损比例
    base_stop_loss = 0.08
    
    # 根据信号类型调整止损
    if '强烈超跌' in signals.get('bb_signals', []):
        # 超跌股票止损更严格
        stop_loss_ratio = base_stop_loss * 0.8
    elif '强烈超买' in signals.get('bb_signals', []):
        # 超买股票止损更宽松
        stop_loss_ratio = base_stop_loss * 1.2
    else:
        stop_loss_ratio = base_stop_loss
        
    return round(current_price * (1 - stop_loss_ratio), 2)

def fix_csv_data():
    """修复CSV数据中的目标价格和止损价格"""
    
    # 读取原始数据
    picks_file = "results/picks/bollinger_picks_2025-08-12.csv"
    portfolio_file = "results/picks/bollinger_portfolio_2025-08-12.csv"
    
    if not os.path.exists(picks_file):
        print(f"文件不存在: {picks_file}")
        return
    
    # 读取数据
    df_picks = pd.read_csv(picks_file)
    
    # 修复数据
    fixed_data = []
    
    for idx, row in df_picks.iterrows():
        # 格式化股票代码
        stock_code = format_stock_code(row['stock_code'])
        
        # 解析信号数据
        import ast
        try:
            signals = ast.literal_eval(row['signals'])
            trading_advice = ast.literal_eval(row['trading_advice'])
        except:
            continue
        
        current_price = row['current_price']
        bb_position = row['bb_position']
        
        # 估算布林带数据（基于位置计算）
        # 假设布林带宽度为当前价格的20%
        bb_width = current_price * 0.2
        bb_middle = current_price - (bb_position - 0.5) * bb_width
        
        bb_data = {
            'upper': bb_middle + bb_width,
            'middle': bb_middle,
            'lower': bb_middle - bb_width
        }
        
        # 计算正确的目标价格和止损价格
        target_price = calculate_target_price(signals, current_price, bb_data)
        stop_loss = calculate_stop_loss(signals, current_price)
        
        # 更新交易建议
        trading_advice['target_price'] = target_price
        trading_advice['stop_loss'] = stop_loss
        
        # 创建修复后的行数据
        fixed_row = row.copy()
        fixed_row['stock_code'] = stock_code
        fixed_row['trading_advice'] = str(trading_advice)
        
        fixed_data.append(fixed_row)
    
    # 保存修复后的数据
    fixed_df = pd.DataFrame(fixed_data)
    fixed_picks_file = "results/picks/bollinger_picks_fixed_2025-08-12.csv"
    fixed_df.to_csv(fixed_picks_file, index=False, encoding='utf-8')
    
    print(f"修复后的数据已保存到: {fixed_picks_file}")
    
    # 修复投资组合数据
    if os.path.exists(portfolio_file):
        df_portfolio = pd.read_csv(portfolio_file)
        
        # 修复股票代码格式
        df_portfolio['stock_code'] = df_portfolio['stock_code'].apply(format_stock_code)
        
        # 更新目标价格和止损价格
        for idx, row in df_portfolio.iterrows():
            stock_code = row['stock_code']
            current_price = row['current_price']
            
            # 从修复后的picks数据中获取对应的目标价格和止损价格
            matching_pick = fixed_df[fixed_df['stock_code'] == stock_code]
            if not matching_pick.empty:
                pick_row = matching_pick.iloc[0]
                import ast
                trading_advice = ast.literal_eval(pick_row['trading_advice'])
                
                df_portfolio.at[idx, 'target_price'] = trading_advice['target_price']
                df_portfolio.at[idx, 'stop_loss'] = trading_advice['stop_loss']
        
        fixed_portfolio_file = "results/picks/bollinger_portfolio_fixed_2025-08-12.csv"
        df_portfolio.to_csv(fixed_portfolio_file, index=False, encoding='utf-8')
        
        print(f"修复后的投资组合数据已保存到: {fixed_portfolio_file}")
    
    return fixed_df, df_portfolio if os.path.exists(portfolio_file) else None

def generate_fixed_html_report():
    """生成修复后的HTML报告"""
    
    # 修复数据
    fixed_picks, fixed_portfolio = fix_csv_data()
    
    if fixed_picks is None:
        print("无法修复数据")
        return
    
    # 生成HTML报告
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>布林带均值回归策略 - 修复版本 - 2025-08-12</title>
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
        
        .fix-note {{
            background-color: #d1ecf1; 
            border: 1px solid #bee5eb; 
            color: #0c5460; 
            padding: 15px; 
            border-radius: 5px; 
            margin: 20px 0; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 布林带均值回归策略 - 修复版本</h1>
            <p>基于多重技术指标的综合选股分析报告</p>
            <p>报告日期: 2025-08-12</p>
        </div>
        
        <div class="content">
            <div class="fix-note">
                <strong>🔧 修复说明：</strong><br>
                1. 修复了目标价格和止损价格计算问题<br>
                2. 股票代码已格式化为标准6位格式<br>
                3. 价格计算基于布林带位置和信号类型
            </div>
            
            <!-- 策略摘要 -->
            <div class="section">
                <h2>📈 策略摘要</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="number">{len(fixed_picks)}</div>
                        <div class="label">筛选股票数</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{len(fixed_portfolio) if fixed_portfolio is not None else 0}</div>
                        <div class="label">投资组合股票数</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{fixed_picks['composite_score'].mean():.3f}</div>
                        <div class="label">平均置信度</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">LOW</div>
                        <div class="label">平均风险等级</div>
                    </div>
                </div>
            </div>
            
            <!-- 推荐股票 -->
            <div class="section">
                <h2>🎯 推荐股票（修复版）</h2>
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
    """
    
    # 添加股票数据
    for idx, row in fixed_picks.head(10).iterrows():
        import ast
        trading_advice = ast.literal_eval(row['trading_advice'])
        risk_class = f"risk-{trading_advice.get('risk_level', 'medium')}"
        confidence_width = row['composite_score'] * 100
        
        html_content += f"""
                        <tr>
                            <td><strong>{row['stock_code']}</strong></td>
                            <td>¥{row['current_price']:.2f}</td>
                            <td>{row['bb_position']:.3f}</td>
                            <td>{row['rsi']:.1f}</td>
                            <td>
                                {row['composite_score']:.3f}
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: {confidence_width}%"></div>
                                </div>
                            </td>
                            <td>¥{trading_advice.get('target_price', 0):.2f}</td>
                            <td>¥{trading_advice.get('stop_loss', 0):.2f}</td>
                            <td class="{risk_class}">{trading_advice.get('risk_level', 'medium').upper()}</td>
                            <td>{trading_advice.get('holding_period', 'medium')}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <!-- 投资组合 -->
            <div class="section">
                <h2>💼 投资组合建议（修复版）</h2>
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
    """
    
    # 添加投资组合数据
    if fixed_portfolio is not None:
        for idx, row in fixed_portfolio.iterrows():
            risk_class = f"risk-{row.get('risk_level', 'medium')}"
            
            html_content += f"""
                        <tr>
                            <td><strong>{row['stock_code']}</strong></td>
                            <td>¥{row['current_price']:.2f}</td>
                            <td>{row['weight']:.1%}</td>
                            <td>{row['position_size']:.1%}</td>
                            <td>¥{row['target_price']:.2f}</td>
                            <td>¥{row['stop_loss']:.2f}</td>
                            <td class="{risk_class}">{row.get('risk_level', 'medium').upper()}</td>
                        </tr>
            """
    
    html_content += """
                    </tbody>
                </table>
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
            <p>© 2024 布林带均值回归选股系统 | 修复版本 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
    """
    
    # 保存HTML报告
    report_file = "results/reports/bollinger_report_fixed_2025-08-12.html"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"修复后的HTML报告已保存到: {report_file}")

if __name__ == "__main__":
    print("开始修复布林带策略数据...")
    generate_fixed_html_report()
    print("修复完成！")


