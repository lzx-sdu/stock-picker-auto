import os
from datetime import datetime
import pandas as pd
from src.utils.config import Config
from src.data.stock_data import StockDataManager
from src.analysis.bollinger_bands import BollingerBands

def get_lower_band_picks(max_stocks=100):
    config = Config("config.yaml")
    data_manager = StockDataManager(config)
    bollinger = BollingerBands(config)
    stock_list = data_manager.get_stock_list().head(max_stocks)
    picks = []

    for _, row in stock_list.iterrows():
        code, name = row['code'], row['name']
        data = data_manager.get_latest_data(code, days=60)
        if data.empty:
            continue
        data = bollinger.calculate(data)
        if data.empty:
            continue
        signals = bollinger.analyze_signals(data)
        if '触及下轨' in signals.get('signals', []):
            picks.append({
                'code': code,
                'name': name,
                'current_price': signals['current_price'],
                'bb_position': signals.get('bb_position', 0.5),
                'signals': signals['signals']
            })
    return picks

def save_html_report(picks, output_file):
    df = pd.DataFrame(picks)
    avg_price = df['current_price'].mean() if not df.empty else 0
    min_price = df['current_price'].min() if not df.empty else 0
    max_price = df['current_price'].max() if not df.empty else 0
    avg_bb = df['bb_position'].mean() if not df.empty else 0
    all_signals = sum([p['signals'] for p in picks], [])
    signal_counts = pd.Series(all_signals).value_counts().to_dict() if all_signals else {}

    table = ""
    for i, p in enumerate(picks, 1):
        sigs = " ".join([f'<span style="color:#155724;background:#d4edda;padding:2px 6px;border-radius:8px;">{s}</span>' if '触及下轨' in s else f'<span style="color:#856404;background:#fff3cd;padding:2px 6px;border-radius:8px;">{s}</span>' for s in p['signals']])
        table += f"<tr><td>{i}</td><td>{p['code']}</td><td>{p['name']}</td><td>¥{p['current_price']:.2f}</td><td>{p['bb_position']:.3f}</td><td>{sigs or '无'}</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="UTF-8"><title>下轨信号选股报告</title>
<style>
body{{font-family:Arial,sans-serif;background:#f5f5f5;}}
.container{{max-width:1000px;margin:30px auto;background:#fff;padding:30px;border-radius:10px;box-shadow:0 2px 10px #0001;}}
h1{{text-align:center;color:#2c3e50;}}
.section{{margin:20px 0;}}
table{{width:100%;border-collapse:collapse;}}
th,td{{border:1px solid #ddd;padding:8px;text-align:center;}}
th{{background:#3498db;color:#fff;}}
tr:nth-child(even){{background:#f2f2f2;}}
</style>
</head><body>
<div class="container">
<h1>📉 A股布林带“下轨”信号选股报告</h1>
<div class="section"><b>报告时间：</b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
<div class="section"><b>选股数量：</b>{len(picks)} 只 | <b>平均价格：</b>¥{avg_price:.2f} | <b>价格区间：</b>¥{min_price:.2f}-¥{max_price:.2f} | <b>平均BB位置：</b>{avg_bb:.3f}</div>
<div class="section"><b>信号分布：</b>{" ".join([f"{k}:{v}只" for k,v in signal_counts.items()]) or "无"}</div>
<div class="section">
<table>
<thead><tr><th>序号</th><th>股票代码</th><th>名称</th><th>当前价格</th><th>BB位置</th><th>信号</th></tr></thead>
<tbody>{table or '<tr><td colspan=6>无符合条件股票</td></tr>'}</tbody>
</table>
</div>
<div class="section" style="color:#666;font-size:13px;">
⚠️ 本报告仅供技术分析参考，不构成投资建议。股市有风险，投资需谨慎。
</div>
</div></body></html>"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 下轨信号报告已生成: {output_file}")

if __name__ == "__main__":
    picks = get_lower_band_picks(max_stocks=100)  # 可调整数量
    save_html_report(picks, f"results/reports/{datetime.now().strftime('%Y-%m-%d')}_lower_band_report.html")