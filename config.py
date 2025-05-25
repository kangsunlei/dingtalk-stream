#!/usr/bin/env python3
"""
配置管理模块
"""
import os
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
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """从环境变量加载配置"""
        # 加载环境变量
        load_dotenv()
        
        client_id = os.environ.get('CLIENT_ID')
        client_secret = os.environ.get('CLIENT_SECRET')
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
        
        if not client_id or not client_secret:
            raise ConfigurationError("请设置环境变量CLIENT_ID和CLIENT_SECRET")
        
        return cls(
            client_id=client_id,
            client_secret=client_secret,
            log_level=log_level
        )
    
    def validate(self) -> None:
        """验证配置有效性"""
        if not self.client_id:
            raise ConfigurationError("CLIENT_ID不能为空")
        if not self.client_secret:
            raise ConfigurationError("CLIENT_SECRET不能为空")
