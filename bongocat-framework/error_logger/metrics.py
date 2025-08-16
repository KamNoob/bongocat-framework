"""Log Metrics - Track logging statistics"""

from collections import defaultdict
from typing import Dict, Any
import time


class LogMetrics:
    def __init__(self):
        self.counts = defaultdict(int)
        self.start_time = time.time()
        self.last_error_time = None
        
    def increment(self, level: str):
        """Increment count for log level"""
        self.counts[level] += 1
        if level in ['ERROR', 'CRITICAL']:
            self.last_error_time = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'log_counts': dict(self.counts),
            'total_logs': sum(self.counts.values()),
            'error_rate': (self.counts['ERROR'] + self.counts['CRITICAL']) / max(sum(self.counts.values()), 1),
            'last_error_time': self.last_error_time,
            'logs_per_minute': sum(self.counts.values()) / max(uptime / 60, 1)
        }
    
    def reset(self):
        """Reset all metrics"""
        self.counts.clear()
        self.start_time = time.time()
        self.last_error_time = None