#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
import yaml
from typing import Any, Dict, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config or {}
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise ValueError(f"读取配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_bollinger_config(self) -> Dict[str, Any]:
        """获取布林带配置"""
        return self.get('bollinger_bands', {})
    
    def get_screening_config(self) -> Dict[str, Any]:
        """获取选股配置"""
        return self.get('screening', {})
    
    def get_data_source_config(self) -> Dict[str, Any]:
        """获取数据源配置"""
        return self.get('data_sources', {})
    
    def get_stock_pool_config(self) -> Dict[str, Any]:
        """获取股票池配置"""
        return self.get('stock_pool', {})
    
    def get_reporting_config(self) -> Dict[str, Any]:
        """获取报告配置"""
        return self.get('reporting', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get('logging', {})
    
    def reload(self):
        """重新加载配置文件"""
        self.config_data = self._load_config()
    
    def save(self, config_data: Optional[Dict[str, Any]] = None):
        """
        保存配置到文件
        
        Args:
            config_data: 要保存的配置数据，如果为None则保存当前配置
        """
        if config_data is not None:
            self.config_data = config_data
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
        except Exception as e:
            raise ValueError(f"保存配置文件失败: {e}")
    
    def validate(self) -> bool:
        """
        验证配置文件的完整性
        
        Returns:
            配置是否有效
        """
        required_sections = [
            'bollinger_bands',
            'screening',
            'data_sources',
            'stock_pool'
        ]
        
        for section in required_sections:
            if not self.get(section):
                return False
        
        return True 