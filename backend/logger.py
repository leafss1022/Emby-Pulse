"""
日志配置模块
提供统一的日志配置和管理
"""
import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str = "emby_stats",
    level: str = None,
    log_file: str = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    配置并返回一个日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR)，默认从环境变量读取
        log_file: 日志文件路径，默认输出到 /config/logs/emby-stats.log
        max_bytes: 单个日志文件最大大小
        backup_count: 保留的日志文件数量

    Returns:
        配置好的 Logger 实例
    """
    # 获取日志级别（优先使用参数，其次环境变量，最后默认 INFO）
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()

    # 创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.INFO))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件 handler（可选）
    if log_file:
        try:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to setup file handler: {e}")

    return logger


def get_logger(module_name: str = None) -> logging.Logger:
    """
    获取日志记录器（用于各个模块）

    Args:
        module_name: 模块名称，用于区分日志来源

    Returns:
        Logger 实例
    """
    if module_name:
        return logging.getLogger(f"emby_stats.{module_name}")
    return logging.getLogger("emby_stats")


# 默认日志配置
def init_logging():
    """初始化应用的日志系统"""
    # 检查是否启用文件日志
    enable_file_log = os.getenv("ENABLE_FILE_LOG", "false").lower() == "true"
    log_file = "/config/logs/emby-stats.log" if enable_file_log else None

    return setup_logger(
        name="emby_stats",
        log_file=log_file
    )
