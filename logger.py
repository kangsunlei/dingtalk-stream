#!/usr/bin/env python3
"""
日志配置模块
"""
import logging
from typing import Optional


def setup_logger(name: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """
    设置并返回日志记录器
    
    Args:
        name: 日志记录器名称，默认为根记录器
        level: 日志级别，默认为INFO
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建处理器
    handler = logging.StreamHandler()
    
    # 设置格式化器
    formatter = logging.Formatter(
        '%(asctime)s %(name)-8s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(handler)
    
    # 设置日志级别
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    return logger
