"""
Rate Limiter - Controls request frequency to prevent being blocked
"""

import time
from typing import Dict, Optional
import threading
from collections import deque


class RateLimiter:
    """Manages request rate limiting with various strategies"""
    
    def __init__(self, requests_per_second: float = 1.0, burst_limit: int = 5):
        """Initialize rate limiter"""
        self.requests_per_second = requests_per_second
        self.burst_limit = burst_limit
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        
        self.last_request_time = 0
        self.request_times = deque(maxlen=burst_limit * 2)  # Efficient circular buffer
        self.lock = threading.RLock()  # Reentrant lock for better performance
        
        # Adaptive rate limiting
        self.adaptive_mode = False
        self.current_delay = self.min_interval
        self.success_count = 0
        self.failure_count = 0
    
    def wait(self):
        """Wait appropriate time before making next request"""
        with self.lock:
            current_time = time.time()
            
            if self.adaptive_mode:
                time.sleep(self.current_delay)
            else:
                # Fixed rate limiting
                time_since_last = current_time - self.last_request_time
                
                if time_since_last < self.min_interval:
                    sleep_time = self.min_interval - time_since_last
                    time.sleep(sleep_time)
            
            # Update burst tracking
            self._update_burst_tracking()
            self.last_request_time = time.time()
    
    def _update_burst_tracking(self):
        """Update burst request tracking with O(1) operations"""
        current_time = time.time()
        
        # Clean old entries efficiently
        while self.request_times and current_time - self.request_times[0] >= 1.0:
            self.request_times.popleft()
        
        # Add current request
        self.request_times.append(current_time)
        
        # Check if we're hitting burst limit
        if len(self.request_times) >= self.burst_limit:
            # Add extra delay to prevent bursting
            time.sleep(0.5)
    
    def enable_adaptive_mode(self):
        """Enable adaptive rate limiting based on response patterns"""
        self.adaptive_mode = True
    
    def disable_adaptive_mode(self):
        """Disable adaptive rate limiting"""
        self.adaptive_mode = False
        self.current_delay = self.min_interval
    
    def report_success(self):
        """Report successful request for adaptive limiting"""
        if self.adaptive_mode:
            self.success_count += 1
            
            # Gradually decrease delay on success
            if self.success_count >= 5:
                self.current_delay = max(
                    self.min_interval, 
                    self.current_delay * 0.9
                )
                self.success_count = 0
    
    def report_failure(self, status_code: Optional[int] = None):
        """Report failed request for adaptive limiting"""
        if self.adaptive_mode:
            self.failure_count += 1
            
            # Increase delay on failure, especially for rate limiting errors
            if status_code == 429:  # Too Many Requests
                self.current_delay *= 2.0
            elif status_code in [503, 502, 504]:  # Server errors
                self.current_delay *= 1.5
            else:
                self.current_delay *= 1.2
            
            # Cap maximum delay
            self.current_delay = min(self.current_delay, 30.0)
            
            self.success_count = 0
    
    def set_rate(self, requests_per_second: float):
        """Update rate limiting configuration"""
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        
        if not self.adaptive_mode:
            self.current_delay = self.min_interval
    
    def get_stats(self) -> Dict:
        """Get rate limiting statistics"""
        return {
            'requests_per_second': self.requests_per_second,
            'burst_limit': self.burst_limit,
            'min_interval': self.min_interval,
            'current_delay': self.current_delay,
            'adaptive_mode': self.adaptive_mode,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'recent_requests': len(self.request_times)
        }