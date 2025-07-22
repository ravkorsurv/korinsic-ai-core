import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = "kor-ai-surveillance", config: Optional[dict] = None
) -> logging.Logger:
    """Setup and configure logger for the surveillance platform"""

    # Try to get configuration from the config module if not provided
    if config is None:
        try:
            from .config import config as global_config

            config = global_config.get_logging_config()
        except ImportError:
            # Fallback to environment variables
            config = {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "format": os.getenv(
                    "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                ),
                "file_rotation": True,
                "max_file_size": "10MB",
                "backup_count": 5,
            }

    # Get configuration values
    level = config.get("level", "INFO")
    log_format = config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_rotation = config.get("file_rotation", True)
    max_file_size = config.get("max_file_size", "10MB")
    backup_count = config.get("backup_count", 5)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (rotating) - only if file rotation is enabled
    if file_rotation:
        log_dir = os.getenv("LOG_DIR", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Parse max file size
        if isinstance(max_file_size, str):
            if max_file_size.endswith("MB"):
                max_bytes = int(max_file_size[:-2]) * 1024 * 1024
            elif max_file_size.endswith("KB"):
                max_bytes = int(max_file_size[:-2]) * 1024
            else:
                max_bytes = int(max_file_size)
        else:
            max_bytes = max_file_size

        log_file = os.path.join(
            log_dir, f'surveillance_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Error file handler
        error_file = os.path.join(
            log_dir, f'surveillance_errors_{datetime.now().strftime("%Y%m%d")}.log'
        )
        error_handler = RotatingFileHandler(
            error_file, maxBytes=max_bytes, backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

    return logger
