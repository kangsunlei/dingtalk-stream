#!/usr/bin/env python3
"""
配置管理模块
"""
import os
import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

from exceptions import ConfigurationError


@dataclass
class AppConfig:
    """应用配置类"""
    client_id: str
    client_secret: str
    log_level: str = "INFO"
    dashscope_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """从环境变量加载配置"""
        # 加载环境变量
        load_dotenv()
        
        client_id = os.environ.get('CLIENT_ID')
        client_secret = os.environ.get('CLIENT_SECRET')
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
        dashscope_api_key = os.environ.get('DASHSCOPE_API_KEY')
        
        if not client_id or not client_secret:
            raise ConfigurationError("请设置环境变量CLIENT_ID和CLIENT_SECRET")
        
        return cls(
            client_id=client_id,
            client_secret=client_secret,
            log_level=log_level,
            dashscope_api_key=dashscope_api_key
        )
    
    def validate(self) -> None:
        """
        验证配置有效性
        
        Raises:
            ConfigurationError: 当配置无效时抛出
        """
        # 验证必填字段
        if not self.client_id:
            raise ConfigurationError("CLIENT_ID不能为空")
        if not self.client_secret:
            raise ConfigurationError("CLIENT_SECRET不能为空")
            
        # 验证字段长度
        if len(self.client_id) < 5:
            raise ConfigurationError("CLIENT_ID长度不能小于5个字符")
        if len(self.client_secret) < 5:
            raise ConfigurationError("CLIENT_SECRET长度不能小于5个字符")
            
        # 验证日志级别
        valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if self.log_level.upper() not in valid_log_levels:
            raise ConfigurationError(f"无效的日志级别: {self.log_level}，有效值为: {', '.join(valid_log_levels)}")
            
        # 验证环境变量文件
        if not os.path.exists('.env'):
            raise ConfigurationError("未找到.env文件，请确保已创建配置文件")
            
        # 验证千问API密钥
        if not self.dashscope_api_key:
            raise ConfigurationError("请设置环境变量DASHSCOPE_API_KEY以启用图片文字识别功能")
