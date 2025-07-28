"""工具模块.

包含各种实用工具函数。
"""

import logging
import sys
from pathlib import Path


def setup_logging(
    level: int = logging.INFO,
    log_file: str | None = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """设置日志记录.

    Args:
        level: 日志级别
        log_file: 日志文件路径，如果为None则只输出到控制台
        log_format: 日志格式

    Returns
    -------
        配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger("espanso-llm-quick-translate")
    logger.setLevel(level)

    # 清除现有的处理器
    logger.handlers.clear()

    # 创建格式化器
    formatter = logging.Formatter(log_format)

    # ! 不添加控制台处理器，因为 espanso 依赖 stdout 输出

    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "espanso-llm-quick-translate") -> logging.Logger:
    """获取日志记录器.

    Args:
        name: 日志记录器名称

    Returns
    -------
        日志记录器
    """
    return logging.getLogger(name)
