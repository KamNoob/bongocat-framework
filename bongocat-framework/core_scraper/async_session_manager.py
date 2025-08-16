"""
Async Session Manager - Handles HTTP session lifecycle with async/await for high performance
"""

import asyncio
import time
from ..framework_types import Dict, Optional, List
from collections import defaultdict


class AsyncSessionManager:
    """Manages async HTTP sessions with connection pooling and health monitoring for maximum throughput"""
    
    def __init__(self, max_connections: int = 50, max_retries: int = 3, concurrent_limit: int = 100):
        """Initialize async session manager with enhanced concurrency support"""
        self.max_connections = max_connections
        self.max_retries = max_retries
        self.concurrent_limit = concurrent_limit
        self.sessions: Dict[str, object] = {}  # aiohttp ClientSession objects
        self.default_session = None
        
        # Semaphore for controlling concurrent requests
        self.semaphore = asyncio.Semaphore(concurrent_limit)
        
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
        
        # Connection pool reuse
        self._connector_cache = {}
    
    async def get_session(self, session_id: str = 'default'):
        """Get or create an async session with health monitoring"""
        if session_id not in self.sessions:
            self.sessions[session_id] = await self._create_async_session(session_id)
            # Initialize stats for new session
            self.session_stats[session_id]['created_at'] = time.time()
        
        if session_id == 'default':
            self.default_session = self.sessions[session_id]
            
        return self.sessions[session_id]
    
    async def _create_async_session(self, session_id: str = 'default'):
        """Create new async session with optimal configuration"""
        # Lazy load aiohttp
        import aiohttp
        
        # Adaptive retry and connection settings
        adaptive_retries = self._calculate_adaptive_retries()
        
        # Create connector with connection pooling
        connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=min(30, self.max_connections),
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )
        
        # Cache connector for reuse
        self._connector_cache[session_id] = connector
        
        # Create session with timeout and retry configuration
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'BongoCat/2.0 (Async High-Performance Web Scraper)'
            }
        )
        
        return session
    
    async def make_request(self, session_id: str, method: str, url: str, **kwargs):
        """Make async HTTP request with semaphore control and monitoring"""
        async with self.semaphore:  # Control concurrency
            session = await self.get_session(session_id)
            
            start_time = time.time()
            retries = 0
            adaptive_retries = self._calculate_adaptive_retries()
            
            while retries <= adaptive_retries:
                try:
                    # Make the async request
                    async with session.request(method, url, **kwargs) as response:
                        response_time = time.time() - start_time
                        
                        # Update monitoring stats
                        await self._monitor_response(response, session_id, response_time)
                        
                        # Return response data
                        content = await response.text()
                        return {
                            'status_code': response.status,
                            'headers': dict(response.headers),
                            'content': content,
                            'url': str(response.url),
                            'response_time': response_time
                        }
                        
                except asyncio.TimeoutError:
                    retries += 1
                    if retries <= adaptive_retries:
                        # Exponential backoff
                        backoff = (2 ** retries) * self._calculate_adaptive_backoff()
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        raise
                        
                except Exception as e:
                    retries += 1
                    if retries <= adaptive_retries:
                        backoff = (2 ** retries) * self._calculate_adaptive_backoff()
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        # Update failure stats
                        await self._monitor_failure(session_id, str(e))
                        raise
            
            raise Exception(f"Max retries ({adaptive_retries}) exceeded for {url}")
    
    async def make_concurrent_requests(self, requests: List[Dict]) -> List[Dict]:
        """Make multiple requests concurrently for maximum throughput"""
        tasks = []
        
        for req in requests:
            session_id = req.get('session_id', 'default')
            method = req.get('method', 'GET')
            url = req['url']
            kwargs = req.get('kwargs', {})
            
            task = self.make_request(session_id, method, url, **kwargs)
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'url': requests[i]['url'],
                    'status': 'error',
                    'error': str(result),
                    'timestamp': time.time()
                })
            else:
                result['status'] = 'success'
                result['timestamp'] = time.time()
                processed_results.append(result)
        
        return processed_results
    
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
            return 0.3  # Aggressive retry for stable conditions
        elif self.global_failure_rate < 0.3:
            return 0.5  # Standard backoff
        else:
            return 1.0  # Conservative backoff for unstable conditions
    
    async def _monitor_response(self, response, session_id: str, response_time: float):
        """Monitor response for health metrics and adaptive behavior"""
        stats = self.session_stats[session_id]
        stats['requests_made'] += 1
        
        # Update response time with exponential moving average
        if stats['avg_response_time'] == 0:
            stats['avg_response_time'] = response_time
        else:
            stats['avg_response_time'] = 0.7 * stats['avg_response_time'] + 0.3 * response_time
        
        # Track failures
        if response.status >= 400:
            stats['failures'] += 1
            stats['last_failure_time'] = time.time()
            stats['consecutive_failures'] += 1
        else:
            stats['consecutive_failures'] = 0
        
        # Update global failure rate periodically
        if time.time() - self.last_stats_update > 30:  # Update every 30 seconds for async
            await self._update_global_failure_rate()
            self.last_stats_update = time.time()
    
    async def _monitor_failure(self, session_id: str, error: str):
        """Monitor failed requests"""
        stats = self.session_stats[session_id]
        stats['failures'] += 1
        stats['last_failure_time'] = time.time()
        stats['consecutive_failures'] += 1
        
        await self._update_global_failure_rate()
    
    async def _update_global_failure_rate(self):
        """Update global failure rate across all sessions"""
        total_requests = sum(stats['requests_made'] for stats in self.session_stats.values())
        total_failures = sum(stats['failures'] for stats in self.session_stats.values())
        
        if total_requests > 0:
            self.global_failure_rate = total_failures / total_requests
        else:
            self.global_failure_rate = 0
    
    async def get_performance_stats(self) -> Dict:
        """Get detailed performance statistics"""
        await self._update_global_failure_rate()
        
        session_performance = {}
        total_requests = 0
        total_response_time = 0
        
        for session_id, stats in self.session_stats.items():
            failure_rate = stats['failures'] / max(stats['requests_made'], 1)
            is_healthy = (
                failure_rate < 0.3 and
                stats['consecutive_failures'] < 10 and
                stats['avg_response_time'] < 10
            )
            
            session_performance[session_id] = {
                **stats,
                'failure_rate': failure_rate,
                'is_healthy': is_healthy,
                'uptime': time.time() - stats['created_at'],
                'requests_per_second': stats['requests_made'] / max(time.time() - stats['created_at'], 1)
            }
            
            total_requests += stats['requests_made']
            total_response_time += stats['avg_response_time'] * stats['requests_made']
        
        avg_response_time = total_response_time / max(total_requests, 1)
        
        return {
            'global_failure_rate': self.global_failure_rate,
            'active_sessions': len(self.sessions),
            'healthy_sessions': sum(1 for perf in session_performance.values() if perf['is_healthy']),
            'total_requests': total_requests,
            'avg_response_time': avg_response_time,
            'concurrent_limit': self.concurrent_limit,
            'current_connections': sum(
                len(connector._conns) if hasattr(connector, '_conns') else 0 
                for connector in self._connector_cache.values()
            ),
            'session_performance': session_performance
        }
    
    async def close_session(self, session_id: str):
        """Close specific async session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            await session.close()
            del self.sessions[session_id]
            
            # Close associated connector
            if session_id in self._connector_cache:
                await self._connector_cache[session_id].close()
                del self._connector_cache[session_id]
    
    async def close_all(self):
        """Close all async sessions and connections"""
        # Close all sessions
        for session in self.sessions.values():
            try:
                await session.close()
            except Exception:
                pass  # Ignore errors during cleanup
        
        # Close all connectors
        for connector in self._connector_cache.values():
            try:
                await connector.close()
            except Exception:
                pass
        
        self.sessions.clear()
        self._connector_cache.clear()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_all()