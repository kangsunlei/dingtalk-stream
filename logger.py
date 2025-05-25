#!/usr/bin/env python3
"""
日志配置模块
"""
import logging
import os
from datetime import datetime
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
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    
    # 创建文件处理器
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    
    # 设置格式化器
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # 设置日志级别
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 记录启动信息
    logger.info(f"日志系统初始化完成，日志文件: {log_file}")
    
    return logger
