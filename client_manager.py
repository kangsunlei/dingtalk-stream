#!/usr/bin/env python3
"""
钉钉Stream客户端管理模块
"""
import logging
from typing import Optional

import dingtalk_stream
from dingtalk_stream import Credential

from config import AppConfig
from handlers import UniversalMessageHandler
from services.image_service import ImageService


class DingTalkStreamManager:
    """钉钉Stream客户端管理器"""
    
    def __init__(self, config: AppConfig, logger: Optional[logging.Logger] = None):
        self.config: AppConfig = config
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        self._client: Optional[dingtalk_stream.DingTalkStreamClient] = None
        
        # 初始化图片服务
        self.image_service = ImageService(self.logger)
        if self.config.dashscope_api_key:
            self.image_service.set_api_key(self.config.dashscope_api_key)
    
    def initialize_client(self) -> dingtalk_stream.DingTalkStreamClient:
        """
        初始化钉钉Stream客户端
        
        Returns:
            初始化后的客户端实例
        """
        try:
            self.logger.info("正在初始化钉钉Stream客户端...")
            
            # 创建凭证
            credential = Credential(self.config.client_id, self.config.client_secret)
            
            # 创建客户端
            self._client = dingtalk_stream.DingTalkStreamClient(credential)
            
            # 注册处理器
            self._register_handlers()
            
            self.logger.info("钉钉Stream客户端初始化完成")
            return self._client
            
        except Exception as e:
            self.logger.error(f"初始化钉钉Stream客户端失败: {str(e)}")
            raise
    
    def _register_handlers(self) -> None:
        """注册消息处理器"""
        if not self._client:
            raise RuntimeError("客户端尚未初始化")
        
        # 注册通用消息处理器
        universal_handler = UniversalMessageHandler(self.logger, self.image_service)
        self._client.register_callback_handler(
            dingtalk_stream.graph.GraphMessage.TOPIC,
            universal_handler
        )
        
        self.logger.info("通用消息处理器注册完成")
    
    def start(self) -> None:
        """启动客户端"""
        if not self._client:
            self.initialize_client()
        
        try:
            self.logger.info("启动钉钉Stream客户端...")
            self._client.start_forever()
        except Exception as e:
            self.logger.error(f"启动客户端时出错: {str(e)}")
            raise
    
    def stop(self) -> None:
        """
        停止客户端
        
        关闭所有连接并清理资源
        """
        if self._client:
            try:
                self.logger.info("正在停止钉钉Stream客户端...")
                self._client.stop()
                self._client = None
                self.logger.info("钉钉Stream客户端已停止")
            except Exception as e:
                self.logger.error(f"停止客户端时出错: {str(e)}")
                raise
