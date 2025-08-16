"""Log Handlers"""

import logging
import os
from typing import Optional


class FileHandler(logging.FileHandler):
    def __init__(self, filename: str, mode: str = 'a'):
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, mode, encoding='utf-8')


class ConsoleHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream)
        
    def format(self, record):
        # Add color coding for different log levels
        color_codes = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green  
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m'  # Magenta
        }
        
        reset_code = '\033[0m'
        color = color_codes.get(record.levelname, '')
        
        formatted = super().format(record)
        return f"{color}{formatted}{reset_code}"