#!/usr/bin/env python3
"""
钉钉通用消息处理器模块
"""
import logging
from typing import Dict, Any, Tuple, Optional
import json
import time
import re

from dingtalk_stream import AckMessage, CallbackMessage, GraphRequest, GraphResponse
import dingtalk_stream

from exceptions import HandlerError
from services.image_service import ImageService


class UniversalMessageHandler(dingtalk_stream.GraphHandler):
    """通用消息处理器 - 详细记录所有请求信息"""
    
    def __init__(self, logger: logging.Logger = None, image_service: Optional[ImageService] = None):
        super(dingtalk_stream.GraphHandler, self).__init__()
        self.logger = logger or logging.getLogger(__name__)
        self.image_service = image_service
        self.request_counter = 0
        

    async def process(self, callback: CallbackMessage) -> Tuple[str, Dict[str, Any]]:
        """
        处理钉钉通过模式消息 - 详细记录所有请求信息
        
        Args:
            callback: 回调消息
            
        Returns:
            处理结果元组 (状态, 响应数据)
        """
        start_time = time.time()
        self.request_counter += 1
        request_id = f"req_{self.request_counter}_{int(start_time)}"
        
        try:
            self.logger.info(f"[{request_id}] ========== 新的钉钉请求开始 ==========")
            
            # 记录原始回调数据
            self._log_callback_details(callback, request_id)
            
            # 解析请求
            request = GraphRequest.from_dict(callback.data)
            
            # 记录解析后的请求详情
            self._log_request_details(request, request_id)
            
            # 尝试解析请求体中的业务数据
            self._log_business_data(request, request_id)
            
            # 创建响应
            response = self._create_response_based_on_request(request, request_id)
            
            processing_time = time.time() - start_time
            self.logger.info(f'[{request_id}] 请求处理完成，耗时: {processing_time:.3f}s')
            self.logger.info(f"[{request_id}] ========== 请求处理结束 ==========")
            
            return AckMessage.STATUS_OK, response.to_dict()
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f'[{request_id}] 处理请求时发生错误，耗时: {processing_time:.3f}s, 错误: {str(e)}')
            self.logger.error(f'[{request_id}] 错误详情:', exc_info=True)
            
            error_response = self._create_error_response(f"处理请求时发生错误: {str(e)}", request_id)
            self.logger.info(f"[{request_id}] ========== 请求处理结束(错误) ==========")
            return AckMessage.STATUS_SYSTEM_EXCEPTION, error_response.to_dict()

    def _log_callback_details(self, callback: CallbackMessage, request_id: str) -> None:
        """记录回调消息的详细信息"""
        self.logger.info(f"[{request_id}] 原始回调消息详情:")
        self.logger.info(f"[{request_id}]   - 消息类型: {type(callback).__name__}")
        self.logger.info(f"[{request_id}]   - 消息ID: {getattr(callback, 'message_id', 'N/A')}")
        self.logger.info(f"[{request_id}]   - 时间戳: {getattr(callback, 'timestamp', 'N/A')}")
        
        # 记录完整的原始数据
        if hasattr(callback, 'data') and callback.data:
            try:
                data_str = json.dumps(callback.data, indent=2, ensure_ascii=False)
                self.logger.info(f"[{request_id}] 原始数据内容:\n{data_str}")
            except Exception as e:
                self.logger.warning(f"[{request_id}] 无法序列化原始数据: {str(e)}")
                self.logger.info(f"[{request_id}] 原始数据(repr): {repr(callback.data)}")

    def _log_request_details(self, request: GraphRequest, request_id: str) -> None:
        """记录解析后的请求详情"""
        self.logger.info(f"[{request_id}] GraphRequest 解析结果:")
        
        # 请求行信息
        if hasattr(request, 'request_line') and request.request_line:
            self.logger.info(f"[{request_id}] 请求行信息:")
            self.logger.info(f"[{request_id}]   - 方法: {getattr(request.request_line, 'method', 'N/A')}")
            self.logger.info(f"[{request_id}]   - URI: {getattr(request.request_line, 'uri', 'N/A')}")
            self.logger.info(f"[{request_id}]   - 版本: {getattr(request.request_line, 'version', 'N/A')}")
        
        # 请求头信息
        if hasattr(request, 'headers') and request.headers:
            self.logger.info(f"[{request_id}] 请求头信息:")
            for key, value in request.headers.items():
                self.logger.info(f"[{request_id}]   - {key}: {value}")
        
        # 请求体信息
        if hasattr(request, 'body') and request.body:
            self.logger.info(f"[{request_id}] 请求体信息:")
            try:
                if isinstance(request.body, str):
                    # 尝试解析为JSON
                    try:
                        body_json = json.loads(request.body)
                        body_str = json.dumps(body_json, indent=2, ensure_ascii=False)
                        self.logger.info(f"[{request_id}] 请求体(JSON格式):\n{body_str}")
                    except json.JSONDecodeError:
                        self.logger.info(f"[{request_id}] 请求体(文本格式): {request.body}")
                else:
                    self.logger.info(f"[{request_id}] 请求体(原始格式): {repr(request.body)}")
            except Exception as e:
                self.logger.warning(f"[{request_id}] 无法解析请求体: {str(e)}")

    def _log_business_data(self, request: GraphRequest, request_id: str) -> None:
        """尝试解析并记录业务相关数据"""
        self.logger.info(f"[{request_id}] 业务数据分析:")
        
        # 分析URI路径
        if hasattr(request, 'request_line') and request.request_line and hasattr(request.request_line, 'uri'):
            uri = request.request_line.uri
            self.logger.info(f"[{request_id}] URI路径分析: {uri}")
            
            # 解析查询参数
            if '?' in uri:
                path, query_string = uri.split('?', 1)
                self.logger.info(f"[{request_id}]   - 路径: {path}")
                self.logger.info(f"[{request_id}]   - 查询字符串: {query_string}")
                
                # 解析查询参数
                try:
                    from urllib.parse import parse_qs
                    params = parse_qs(query_string)
                    self.logger.info(f"[{request_id}]   - 解析后的参数:")
                    for key, values in params.items():
                        self.logger.info(f"[{request_id}]     {key}: {values}")
                except Exception as e:
                    self.logger.warning(f"[{request_id}] 解析查询参数失败: {str(e)}")
        
        # 分析请求体中的用户输入
        if hasattr(request, 'body') and request.body:
            try:
                if isinstance(request.body, str):
                    body_data = json.loads(request.body)
                elif isinstance(request.body, dict):
                    body_data = request.body
                else:
                    body_data = None
                
                if body_data:
                    # 查找可能的用户输入字段
                    user_input_fields = ['query', 'text', 'message', 'content', 'input', 'question']
                    for field in user_input_fields:
                        if field in body_data:
                            self.logger.info(f"[{request_id}] 发现用户输入字段 '{field}': {body_data[field]}")
                    
                    # 查找用户信息
                    user_fields = ['user_id', 'user', 'sender', 'from']
                    for field in user_fields:
                        if field in body_data:
                            self.logger.info(f"[{request_id}] 发现用户信息字段 '{field}': {body_data[field]}")
                    
                    # 查找对话上下文
                    context_fields = ['context', 'conversation', 'chat_id', 'session_id']
                    for field in context_fields:
                        if field in body_data:
                            self.logger.info(f"[{request_id}] 发现上下文字段 '{field}': {body_data[field]}")
                            
            except Exception as e:
                self.logger.warning(f"[{request_id}] 分析业务数据时出错: {str(e)}")

    def _create_response_based_on_request(self, request: GraphRequest, request_id: str) -> GraphResponse:
        """根据请求内容创建响应"""
        try:
            self.logger.info(f"[{request_id}] 创建响应基于请求")
            
            # 获取请求内容
            if isinstance(request.body, str):
                body_data = json.loads(request.body)
            elif isinstance(request.body, dict):
                body_data = request.body
            else:
                return self._create_echo_response(request, request_id)
                
            content = body_data.get('input', '')
            
            # 提取所有图片URL
            if self.image_service:
                image_urls = self.image_service.extract_image_urls(content)
                if image_urls:
                    # 处理所有图片
                    results = []
                    for url in image_urls:
                        try:
                            text = self.image_service.recognize_text(url)
                            results.append(f"图片 {url} 中的文字：\n{text}")
                        except Exception as e:
                            results.append(f"处理图片 {url} 时出错：{str(e)}")

                    self.logger.info(f"[{results}] 处理图片URL完成")
                    
                    if results:
                        return self._create_text_response("\n\n".join(results), request_id)
            
            # 默认返回回显响应
            return self._create_echo_response(request, request_id)
            
        except Exception as e:
            self.logger.error(f"[{request_id}] 创建响应时出错: {str(e)}")
            raise HandlerError(f"创建响应时出错: {str(e)}")

    def _create_text_response(self, text: str, request_id: str) -> GraphResponse:
        """创建文本响应"""
        response = GraphResponse()
        response.body = {
            'text': text,
        }
        self.logger.info(f"[{request_id}] 创建文本响应: {text}")
        return response

    def _create_echo_response(self, request: GraphRequest, request_id: str) -> GraphResponse:
        """创建回显响应"""
        response = GraphResponse()
        response.body = {
            'text': f"收到消息: {request.body}",
        }
        self.logger.info(f"[{request_id}] 创建回显响应")
        return response

    def _create_error_response(self, error_message: str, request_id: str = "unknown") -> GraphResponse:
        """创建错误响应"""
        response = GraphResponse()
        response.body = {
            'text': f"处理消息时出错: {error_message}",
        }
        self.logger.error(f"[{request_id}] 创建错误响应: {error_message}")
        return response

