#!/usr/bin/env python3
"""
自定义异常类模块
"""


class DingTalkStreamError(Exception):
    """钉钉Stream相关异常的基类"""
    pass


class ConfigurationError(DingTalkStreamError):
    """配置错误异常"""
    pass


class HandlerError(DingTalkStreamError):
    """处理器错误异常"""
    pass


class ServiceError(DingTalkStreamError):
    """服务错误异常"""
    pass


class WeatherServiceError(ServiceError):
    """天气服务错误异常"""
    pass
