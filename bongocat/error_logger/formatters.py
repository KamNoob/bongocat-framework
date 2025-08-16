"""Log Formatters"""

import logging
import json
from datetime import datetime


class LogFormatter(logging.Formatter):
    def format(self, record):
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class SimpleFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )