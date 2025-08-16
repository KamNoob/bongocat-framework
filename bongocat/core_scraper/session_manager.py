"""
Session Manager - Handles HTTP session lifecycle and connection pooling
"""

import time
from ..types import Dict, Optional, List
from collections import defaultdict

# Lazy load heavy network dependencies
def _get_requests_modules():
    """Lazy load requests and related modules"""
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    return requests, HTTPAdapter, Retry


class SessionManager:
    """Manages HTTP sessions with connection pooling, adaptive retry logic, and health monitoring"""
    
    def __init__(self, max_connections: int = 10, max_retries: int = 3):
        """Initialize session manager with monitoring capabilities"""
        self.max_connections = max_connections
        self.max_retries = max_retries
        self.sessions: Dict[str, requests.Session] = {}
        self.default_session = None
        
        # Health monitoring and adaptive retry state
        self.session_stats = defaultdict(lambda: {
            'requests_made': 0,
            'failures': 0,
            'avg_response_time': 0,
            'last_failure_time': None,
            'consecutive_failures': 0,
            'created_at': time.time()
        })
        self.global_failure_rate = 0
        self.last_stats_update = time.time()
    
    def get_session(self, session_id: str = 'default'):
        """Get or create a session with health monitoring"""
        if session_id not in self.sessions:
            self.sessions[session_id] = self._create_session(session_id)
            # Initialize stats for new session
            self.session_stats[session_id]['created_at'] = time.time()
        
        if session_id == 'default':
            self.default_session = self.sessions[session_id]
            
        return self.sessions[session_id]
    
    def _create_session(self, session_id: str = 'default'):
        """Create new session with adaptive retry configuration using lazy loading"""
        requests, HTTPAdapter, Retry = _get_requests_modules()
        session = requests.Session()
        
        # Adaptive retry strategy based on global failure rate
        adaptive_retries = self._calculate_adaptive_retries()
        adaptive_backoff = self._calculate_adaptive_backoff()
        
        # Configure retry strategy with updated parameter names
        retry_strategy = Retry(
            total=adaptive_retries,
            status_forcelist=[429, 500, 502, 503, 504, 408],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],  # Updated from deprecated method_whitelist
            backoff_factor=adaptive_backoff,
            respect_retry_after_header=True
        )
        
        # Configure adapter with connection pooling and monitoring  
        adapter = HTTPAdapter(
            pool_connections=self.max_connections,
            pool_maxsize=self.max_connections,
            max_retries=retry_strategy
        )
        
        # Add request/response monitoring hooks
        session.hooks['response'].append(lambda r, *args, **kwargs: self._monitor_response(r, session_id))
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def close_session(self, session_id: str):
        """Close specific session"""
        if session_id in self.sessions:
            self.sessions[session_id].close()
            del self.sessions[session_id]
    
    def close_all(self):
        """Close all sessions"""
        for session in self.sessions.values():
            session.close()
        self.sessions.clear()
        
    def _calculate_adaptive_retries(self) -> int:
        """Calculate adaptive retry count based on global failure rate"""
        if self.global_failure_rate < 0.1:  # Low failure rate
            return max(1, self.max_retries - 1)
        elif self.global_failure_rate < 0.3:  # Medium failure rate
            return self.max_retries
        else:  # High failure rate
            return min(self.max_retries + 2, 10)
    
    def _calculate_adaptive_backoff(self) -> float:
        """Calculate adaptive backoff factor based on conditions"""
        if self.global_failure_rate < 0.1:
            return 0.5  # Aggressive retry for stable conditions
        elif self.global_failure_rate < 0.3:
            return 1.0  # Standard backoff
        else:
            return 2.0  # Conservative backoff for unstable conditions
    
    def _monitor_response(self, response, session_id: str):
        """Monitor response for health metrics and adaptive behavior"""
        stats = self.session_stats[session_id]
        stats['requests_made'] += 1
        
        # Calculate response time if available
        if hasattr(response, 'elapsed'):
            response_time = response.elapsed.total_seconds()
            if stats['avg_response_time'] == 0:
                stats['avg_response_time'] = response_time
            else:
                # Exponential moving average
                stats['avg_response_time'] = 0.7 * stats['avg_response_time'] + 0.3 * response_time
        
        # Track failures
        if response.status_code >= 400:
            stats['failures'] += 1
            stats['last_failure_time'] = time.time()
            stats['consecutive_failures'] += 1
        else:
            stats['consecutive_failures'] = 0
        
        # Update global failure rate periodically
        if time.time() - self.last_stats_update > 60:  # Update every minute
            self._update_global_failure_rate()
            self.last_stats_update = time.time()
    
    def _update_global_failure_rate(self):
        """Update global failure rate across all sessions"""
        total_requests = sum(stats['requests_made'] for stats in self.session_stats.values())
        total_failures = sum(stats['failures'] for stats in self.session_stats.values())
        
        if total_requests > 0:
            self.global_failure_rate = total_failures / total_requests
        else:
            self.global_failure_rate = 0
    
    def get_health_status(self) -> Dict:
        """Get detailed health status of all sessions"""
        self._update_global_failure_rate()
        
        session_health = {}
        for session_id, stats in self.session_stats.items():
            failure_rate = stats['failures'] / max(stats['requests_made'], 1)
            is_healthy = (
                failure_rate < 0.5 and
                stats['consecutive_failures'] < 5 and
                stats['avg_response_time'] < 30
            )
            
            session_health[session_id] = {
                **stats,
                'failure_rate': failure_rate,
                'is_healthy': is_healthy,
                'uptime': time.time() - stats['created_at']
            }
        
        return {
            'global_failure_rate': self.global_failure_rate,
            'active_sessions': len(self.sessions),
            'healthy_sessions': sum(1 for h in session_health.values() if h['is_healthy']),
            'session_details': session_health
        }
    
    def get_session_stats(self) -> Dict:
        """Get basic session statistics with enhanced monitoring"""
        health_status = self.get_health_status()
        
        return {
            'active_sessions': len(self.sessions),
            'session_ids': list(self.sessions.keys()),
            'max_connections': self.max_connections,
            'max_retries': self.max_retries,
            'global_failure_rate': self.global_failure_rate,
            'healthy_sessions': health_status['healthy_sessions'],
            'total_requests': sum(stats['requests_made'] for stats in self.session_stats.values()),
            'total_failures': sum(stats['failures'] for stats in self.session_stats.values())
        }