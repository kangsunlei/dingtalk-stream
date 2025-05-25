#!/usr/bin/env python3
"""
钉钉通用消息处理器模块
"""
import logging
from typing import Dict, Any, Tuple, Optional
import json
import time
from datetime import datetime

from dingtalk_stream import AckMessage, CallbackMessage, GraphRequest, GraphResponse
import dingtalk_stream

from exceptions import HandlerError


class UniversalMessageHandler(dingtalk_stream.GraphHandler):
    """通用消息处理器 - 详细记录所有请求信息"""
    
    def __init__(self, logger: logging.Logger = None):
        super(dingtalk_stream.GraphHandler, self).__init__()
        self.logger = logger or logging.getLogger(__name__)
        self.request_counter = 0
        
        # 内置模拟天气数据
        self._weather_data = {
            '杭州': {
                'text': '晴天',
                'temperature': 22,
                'humidity': 65,
                'wind_direction': '东南风'
            },
            '北京': {
                'text': '多云',
                'temperature': 18,
                'humidity': 45,
                'wind_direction': '北风'
            },
            '上海': {
                'text': '小雨',
                'temperature': 20,
                'humidity': 78,
                'wind_direction': '东风'
            }
        }

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
        """根据请求内容创建适当的响应"""
        self.logger.info(f"[{request_id}] 开始创建响应...")
        
        # 分析请求内容，决定响应类型
        response_data = None
        
        # 检查是否为天气查询
        if self._is_weather_request(request):
            self.logger.info(f"[{request_id}] 检测到天气查询请求")
            response_data = self._get_weather_data()
        else:
            # 默认响应：回显请求信息
            self.logger.info(f"[{request_id}] 使用默认响应模式")
            response_data = self._create_echo_response(request, request_id)
        
        # 创建HTTP响应
        response = GraphResponse()
        response.status_line.code = 200
        response.status_line.reason_phrase = 'OK'
        response.headers['Content-Type'] = 'application/json'
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Processed-At'] = datetime.now().isoformat()
        response.body = json.dumps(response_data, ensure_ascii=False, indent=2)
        
        self.logger.info(f"[{request_id}] 响应创建完成")
        return response

    def _get_weather_data(self, location: str = '杭州') -> Dict[str, Any]:
        """
        获取天气数据
        
        Args:
            location: 地点名称
            
        Returns:
            天气信息字典
        """
        weather = self._weather_data.get(location, self._weather_data['杭州'])
        
        return {
            'type': 'weather_response',
            'location': location,
            'dateStr': datetime.now().strftime('%Y-%m-%d'),
            'text': weather['text'],
            'temperature': weather['temperature'],
            'humidity': weather['humidity'],
            'wind_direction': weather['wind_direction'],
            'timestamp': datetime.now().isoformat()
        }

    def _is_weather_request(self, request: GraphRequest) -> bool:
        """判断是否为天气查询请求"""
        weather_keywords = ['天气', '气温', '温度', 'weather', '气候', '下雨', '晴天', '阴天']
        
        # 检查URI
        if hasattr(request, 'request_line') and request.request_line:
            uri = getattr(request.request_line, 'uri', '')
            if any(keyword in uri.lower() for keyword in weather_keywords):
                return True
        
        # 检查请求体
        if hasattr(request, 'body') and request.body:
            try:
                if isinstance(request.body, str):
                    body_text = request.body.lower()
                    if any(keyword in body_text for keyword in weather_keywords):
                        return True
                    
                    # 尝试解析JSON中的文本字段
                    try:
                        body_data = json.loads(request.body)
                        text_fields = ['query', 'text', 'message', 'content', 'input']
                        for field in text_fields:
                            if field in body_data and isinstance(body_data[field], str):
                                if any(keyword in body_data[field].lower() for keyword in weather_keywords):
                                    return True
                    except:
                        pass
            except:
                pass
        
        return False

    def _create_echo_response(self, request: GraphRequest, request_id: str) -> Dict[str, Any]:
        """创建回显响应，包含请求的详细信息"""
        echo_data = {
            'type': 'echo_response',
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'message': '收到您的消息，以下是详细的请求信息分析',
            'request_analysis': {}
        }
        
        # 添加请求行信息
        if hasattr(request, 'request_line') and request.request_line:
            echo_data['request_analysis']['request_line'] = {
                'method': getattr(request.request_line, 'method', None),
                'uri': getattr(request.request_line, 'uri', None),
                'version': getattr(request.request_line, 'version', None)
            }
        
        # 添加请求头信息
        if hasattr(request, 'headers') and request.headers:
            echo_data['request_analysis']['headers'] = dict(request.headers)
        
        # 添加请求体信息
        if hasattr(request, 'body') and request.body:
            try:
                if isinstance(request.body, str):
                    try:
                        echo_data['request_analysis']['body'] = json.loads(request.body)
                    except json.JSONDecodeError:
                        echo_data['request_analysis']['body'] = request.body
                else:
                    echo_data['request_analysis']['body'] = request.body
            except Exception as e:
                echo_data['request_analysis']['body_error'] = str(e)
        
        return echo_data

    def _create_error_response(self, error_message: str, request_id: str = "unknown") -> GraphResponse:
        """
        创建错误响应
        
        Args:
            error_message: 错误信息
            request_id: 请求ID
            
        Returns:
            图响应对象
        """
        response = GraphResponse()
        response.status_line.code = 500
        response.status_line.reason_phrase = 'Internal Server Error'
        response.headers['Content-Type'] = 'application/json'
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Error-At'] = datetime.now().isoformat()
        response.body = json.dumps({
            'error': True,
            'request_id': request_id,
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
        
        return response

