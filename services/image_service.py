#!/usr/bin/env python3
"""
图片处理服务模块
"""
import logging
import requests
import json
import os
from typing import Optional
from openai import OpenAI

from exceptions import HandlerError


class ImageService:
    """图片处理服务类"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.api_key = None
        self.client = None
    
    def set_api_key(self, api_key: str) -> None:
        """
        设置千问API密钥
        
        Args:
            api_key: 千问API密钥
        """
        self.api_key = api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.logger.info("千问API密钥已设置")
    
    def extract_image_urls(self, text: str) -> list[str]:
        """
        使用大模型从文本中提取所有图片URL
        
        Args:
            text: 输入文本
            
        Returns:
            提取到的图片URL列表，如果没有则返回空列表
            
        Raises:
            HandlerError: 当处理失败时抛出
        """
        if not self.api_key or not self.client:
            raise HandlerError("未设置千问API密钥")
            
        try:
            prompt = f'请从以下文本中提取所有图片URL，以JSON数组格式返回，如果没有图片URL则返回空数组[]。注意：只返回URL数组，不要包含其他文字说明：\n{text}'
            
            self.logger.info("开始调用千问API提取图片URL")
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            answer = completion.choices[0].message.content.strip()
            self.logger.info(f"API返回结果: {answer}")
            
            try:
                # 尝试解析JSON数组
                urls = json.loads(answer)
                if isinstance(urls, list):
                    return urls
                return []
            except json.JSONDecodeError:
                self.logger.warning(f"解析图片URL列表失败，返回空列表: {answer}")
                return []
                
        except Exception as e:
            error_msg = f"提取图片URL时出错: {str(e)}"
            self.logger.error(error_msg)
            raise HandlerError(error_msg)

    def recognize_text(self, image_url: str) -> str:
        """
        识别图片中的文字
        
        Args:
            image_url: 图片URL
            
        Returns:
            识别出的文字内容
            
        Raises:
            HandlerError: 当处理失败时抛出
        """
        if not self.api_key or not self.client:
            raise HandlerError("未设置千问API密钥")
            
        try:
            self.logger.info(f"开始识别图片文字: {image_url}")
            
            completion = self.client.chat.completions.create(
                model="qwen-vl-plus",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请识别这张图片中的文字内容"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }]
            )
            
            result = completion.choices[0].message.content.strip()
            self.logger.info(f"图片文字识别成功: {result}")
            return result
                
        except Exception as e:
            error_msg = f"识别图片文字时出错: {str(e)}"
            self.logger.error(error_msg)
            raise HandlerError(error_msg)