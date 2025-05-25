#!/usr/bin/env python3
"""
钉钉通过模式助手应用主程序
"""
import sys
import traceback

from config import AppConfig
from logger import setup_logger
from client_manager import DingTalkStreamManager
from exceptions import ConfigurationError, DingTalkStreamError


def main() -> None:
    """主函数"""
    logger = None
    stream_manager = None
    
    try:
        # 加载配置
        config = AppConfig.from_env()
        config.validate()
        
        # 设置日志
        logger = setup_logger(level=config.log_level)
        logger.info("应用启动中...")
        
        # 创建并启动Stream管理器
        stream_manager = DingTalkStreamManager(config, logger)
        stream_manager.start()
        
    except KeyboardInterrupt:
        if logger:
            logger.info("程序被用户中断")
        else:
            print("程序被用户中断")
    except ConfigurationError as e:
        # 配置错误
        if logger:
            logger.error(f"配置错误: {str(e)}")
        else:
            print(f"配置错误: {str(e)}")
        sys.exit(1)
    except DingTalkStreamError as e:
        # 钉钉Stream相关错误
        if logger:
            logger.error(f"钉钉Stream错误: {str(e)}")
        else:
            print(f"钉钉Stream错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        if logger:
            logger.error(f"应用运行时出错: {str(e)}")
            logger.debug("详细错误信息:", exc_info=True)
        else:
            print(f"应用运行时出错: {str(e)}")
            traceback.print_exc()
        sys.exit(1)
    finally:
        # 清理资源
        if stream_manager:
            try:
                stream_manager.stop()
            except Exception as e:
                if logger:
                    logger.error(f"清理资源时出错: {str(e)}")
                else:
                    print(f"清理资源时出错: {str(e)}")

if __name__ == "__main__":
    main()
