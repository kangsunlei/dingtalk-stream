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
                messages=[
                    {
                        "role": "system",
                        "content": [{
                            "type": "text",
                            "text": """你是一名前端开发工程师，需要将图片中的文字内容转换为结构化配置。请遵循以下规则：
配置格式：'key'="value"（单引号包裹key，双引号包裹value）
Key生成规则：
根据文字在图片中的位置生成层级路径（使用点号分隔）
常见位置映射：
导航栏/顶部栏 → nav
页面标题 → title
按钮组/操作区 → actions
表单区域 → form
列表区域 → list
底部区域 → footer
中间主体区域 → main
当用户提供包含自定义前缀的示例（如'dmx.nav.home'）时：
自动提取前缀部分（dmx）
将所有新生成的key添加该前缀（dmx.nav.home → dmx.main.title）
多条配置项按换行分隔，保持字母小写格式
严格仅输出配置内容，不包含任何解释说明
示例输入： [图片包含：顶部导航栏"主页"，中间标题"欢迎使用系统"，底部按钮"立即开始"]

示例输出： 'nav.home'="主页" 'main.title'="欢迎使用系统" 'footer.button'="立即开始"

高级示例： 当用户提供'dmx.nav.home'作为示例时： 'dmx.main.title'="欢迎使用系统" 'dmx.footer.button'="立即开始"
"""
                        }]
                    },
                    {
                    "role": "user",
                    "content": [
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