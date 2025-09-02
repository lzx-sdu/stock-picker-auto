# 📊 A股布林带均值回归选股系统

## 项目简介

这是一个基于布林带（Bollinger Bands）均值回归策略的A股选股系统。通过分析股票价格相对于布林带的位置，识别可能回归均值的投资机会。

## 核心策略

### 布林带均值回归原理
- **布林带上轨**：20日移动平均线 + 2倍标准差
- **布林带中轨**：20日移动平均线
- **布林带下轨**：20日移动平均线 - 2倍标准差

### 选股条件
1. **超跌反弹机会**：股价触及或跌破布林带下轨
2. **回归均值机会**：股价从下轨开始反弹，但尚未达到中轨
3. **成交量确认**：反弹时成交量放大
4. **技术指标确认**：RSI、MACD等指标支持反弹

## 项目结构

```
stock_picker/
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── stock_data.py      # 股票数据获取
│   │   └── market_data.py     # 市场数据接口
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── bollinger_bands.py # 布林带计算
│   │   ├── technical_indicators.py # 技术指标
│   │   └── stock_screener.py  # 股票筛选器
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── mean_reversion.py  # 均值回归策略
│   │   └── risk_management.py # 风险管理
│   └── utils/
│       ├── __init__.py
│       ├── config.py          # 配置文件
│       └── logger.py          # 日志工具
├── tests/
│   └── test_bollinger_bands.py
├── data/
│   ├── stock_list.csv         # A股股票列表
│   └── historical_data/       # 历史数据存储
├── results/
│   ├── picks/                 # 选股结果
│   └── reports/               # 分析报告
├── requirements.txt
├── config.yaml
└── main.py
```

## 安装依赖

```bash
pip install -r requirements.txt


```

## 使用方法
# 完整流程：获取数据 → 选股 → 生成报告
python main.py --mode data --update-stock-list
python main.py --mode screen --strategy bollinger
python main.py --mode report

### 1. 获取股票数据
```python
python main.py --mode data --update-stock-list
```

### 2. 运行选股分析
```python
python main.py --mode screen --strategy bollinger
```

### 3. 生成选股报告
```python
python main.py --mode report --date 2024-01-15
```

## 配置说明

在 `config.yaml` 中可以配置：
- 布林带参数（周期、标准差倍数）
- 选股条件阈值
- 数据源设置
- 风险控制参数

## 风险提示

- 本系统仅用于技术分析，不构成投资建议
- 股市有风险，投资需谨慎
- 建议结合基本面分析和其他技术指标
- 历史表现不代表未来收益

## 开发计划

- [x] 项目基础架构
- [ ] 数据获取模块
- [ ] 布林带计算模块
- [ ] 选股策略实现
- [ ] 风险管理系统
- [ ] 回测框架
- [ ] 可视化界面 