"""Log Filters - Filter log messages based on criteria"""

import logging
import re
from typing import List, Pattern


class LogFilter(logging.Filter):
    def __init__(self, keywords: List[str] = None, exclude_patterns: List[str] = None):
        super().__init__()
        self.keywords = keywords or []
        self.exclude_patterns = [re.compile(pattern) for pattern in (exclude_patterns or [])]
    
    def filter(self, record) -> bool:
        """Filter log records based on keywords and patterns"""
        message = record.getMessage()
        
        # Exclude messages matching exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.search(message):
                return False
        
        # Include if keywords are specified and found
        if self.keywords:
            return any(keyword.lower() in message.lower() for keyword in self.keywords)
        
        return True


class LevelRangeFilter(logging.Filter):
    def __init__(self, min_level: int = logging.DEBUG, max_level: int = logging.CRITICAL):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level
    
    def filter(self, record) -> bool:
        """Filter records based on level range"""
        return self.min_level <= record.levelno <= self.max_level