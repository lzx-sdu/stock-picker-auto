#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理模块
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional


def setup_logger(config, level: int = logging.INFO) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        config: 配置对象
        level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    # 获取日志配置
    log_config = config.get_logging_config()
    
    # 创建日志记录器
    logger = logging.getLogger('stock_picker')
    logger.setLevel(level)
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    log_file = log_config.get('file', 'logs/stock_picker.log')
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建轮转文件处理器
        max_size = log_config.get('max_size', '10MB')
        backup_count = log_config.get('backup_count', 5)
        
        # 转换文件大小
        size_map = {'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024}
        if isinstance(max_size, str):
            for unit, multiplier in size_map.items():
                if max_size.upper().endswith(unit):
                    max_size = int(max_size[:-len(unit)]) * multiplier
                    break
            else:
                max_size = 10 * 1024 * 1024  # 默认10MB
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = 'stock_picker') -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器
    """
    return logging.getLogger(name)


class LoggerMixin:
    """日志混入类，为其他类提供日志功能"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取日志记录器"""
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)
    
    def log_debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)
    
    def log_exception(self, message: str):
        """记录异常日志"""
        self.logger.exception(message)


def log_function_call(func):
    """函数调用日志装饰器"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"调用函数: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
            raise
    return wrapper


def log_performance(func):
    """性能日志装饰器"""
    import time
    
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        logger.debug(f"开始执行: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"函数 {func.__name__} 执行完成，耗时: {execution_time:.2f}秒")
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.error(f"函数 {func.__name__} 执行失败，耗时: {execution_time:.2f}秒，错误: {str(e)}")
            raise
    
    return wrapper 