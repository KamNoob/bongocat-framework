"""Main Error Logger"""

import logging
import sys
from typing import Dict, Any


class ErrorLogger:
    def __init__(self, level: str = 'INFO'):
        self.logger = logging.getLogger('bongocat')
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Add console handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message"""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message"""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, extra: Dict[str, Any] = None):
        """Log error message"""
        self.logger.error(message, extra=extra)
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Log debug message"""
        self.logger.debug(message, extra=extra)
    
    def critical(self, message: str, extra: Dict[str, Any] = None):
        """Log critical message"""
        self.logger.critical(message, extra=extra)