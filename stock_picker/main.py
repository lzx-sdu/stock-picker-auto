#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股布林带均值回归选股系统主程序
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.data.stock_data import StockDataManager
from src.analysis.stock_screener import StockScreener
from src.strategy.mean_reversion import MeanReversionStrategy


def setup_argparse():
    """设置命令行参数解析"""
    parser = argparse.ArgumentParser(
        description="A股布林带均值回归选股系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --mode data --update-stock-list
  python main.py --mode screen --strategy bollinger
  python main.py --mode report --date 2024-01-15
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["data", "screen", "report", "backtest"],
        required=True,
        help="运行模式：data(数据获取), screen(选股), report(报告), backtest(回测)"
    )
    
    parser.add_argument(
        "--strategy",
        choices=["bollinger", "rsi", "macd"],
        default="bollinger",
        help="选股策略"
    )
    
    parser.add_argument(
        "--date",
        type=str,
        help="指定日期 (YYYY-MM-DD格式)"
    )
    
    parser.add_argument(
        "--update-stock-list",
        action="store_true",
        help="更新股票列表"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="输出文件路径"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出模式"
    )
    
    return parser


def run_data_mode(args, config, logger):
    """运行数据获取模式"""
    logger.info("开始数据获取模式")
    
    data_manager = StockDataManager(config)
    
    if args.update_stock_list:
        logger.info("更新股票列表...")
        data_manager.update_stock_list()
    
    # 获取指定日期的数据
    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    logger.info(f"获取 {target_date} 的股票数据...")
    data_manager.update_daily_data(target_date)
    
    logger.info("数据获取完成")


def run_screen_mode(args, config, logger):
    """运行选股模式"""
    logger.info("开始选股分析模式")
    
    screener = StockScreener(config)
    strategy = MeanReversionStrategy(config)
    
    # 执行选股
    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    logger.info(f"执行 {args.strategy} 策略选股，日期: {target_date}")
    
    picks = screener.run_screening(
        strategy_name=args.strategy,
        date=target_date
    )
    
    # 保存结果
    output_file = args.output or f"results/picks/{target_date}_{args.strategy}_picks.csv"
    screener.save_results(picks, output_file)
    
    logger.info(f"选股完成，共找到 {len(picks)} 只股票")
    logger.info(f"结果已保存到: {output_file}")


def run_report_mode(args, config, logger):
    """运行报告生成模式"""
    logger.info("开始生成分析报告")
    
    from src.analysis.report_generator import ReportGenerator
    
    generator = ReportGenerator(config)
    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    
    report_file = args.output or f"results/reports/{target_date}_analysis_report.html"
    generator.generate_report(target_date, report_file)
    
    logger.info(f"报告已生成: {report_file}")


def run_backtest_mode(args, config, logger):
    """运行回测模式"""
    logger.info("开始回测分析")
    
    from src.strategy.backtest import BacktestEngine
    
    engine = BacktestEngine(config)
    start_date = args.date or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    results = engine.run_backtest(
        strategy_name=args.strategy,
        start_date=start_date,
        end_date=end_date
    )
    
    output_file = args.output or f"results/backtest/{args.strategy}_backtest_results.csv"
    engine.save_results(results, output_file)
    
    logger.info(f"回测完成，结果已保存到: {output_file}")


def main():
    """主函数"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # 加载配置
    config = Config(args.config)
    
    # 设置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(config, log_level)
    
    logger.info("=" * 50)
    logger.info("A股布林带均值回归选股系统启动")
    logger.info(f"运行模式: {args.mode}")
    logger.info(f"策略: {args.strategy}")
    logger.info("=" * 50)
    
    try:
        # 根据模式执行相应功能
        if args.mode == "data":
            run_data_mode(args, config, logger)
        elif args.mode == "screen":
            run_screen_mode(args, config, logger)
        elif args.mode == "report":
            run_report_mode(args, config, logger)
        elif args.mode == "backtest":
            run_backtest_mode(args, config, logger)
        
        logger.info("程序执行完成")
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main() 