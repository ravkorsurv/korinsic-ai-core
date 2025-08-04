"""Simplified logger utility for testing"""

import logging
import sys

def setup_logger(name=None, level=logging.INFO):
    """Setup a basic logger"""
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger
