"""
Proxy Handler - Manages proxy rotation and validation
"""

import random
import time
from ..types import List, Dict, Optional


class ProxyHandler:
    """Handles proxy rotation and health checking"""
    
    def __init__(self, proxy_list: List[str] = None):
        """Initialize proxy handler"""
        self.proxy_list = proxy_list or []
        self.working_proxies = []
        self.failed_proxies = []
        self.last_validation = 0
        self.validation_interval = 300  # 5 minutes
        
        if self.proxy_list:
            self._validate_proxies()
    
    def add_proxy(self, proxy: str):
        """Add proxy to the list"""
        if proxy not in self.proxy_list:
            self.proxy_list.append(proxy)
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get random working proxy"""
        if not self.working_proxies:
            return None
        
        # Re-validate proxies periodically
        current_time = time.time()
        if current_time - self.last_validation > self.validation_interval:
            self._validate_proxies()
        
        proxy = random.choice(self.working_proxies)
        return {
            'http': proxy,
            'https': proxy
        }
    
    def _validate_proxies(self):
        """Validate proxy list by testing connectivity with lazy import"""
        # Lazy load requests only when validation is needed
        import requests
        
        self.working_proxies = []
        self.failed_proxies = []
        
        test_url = "http://httpbin.org/ip"
        timeout = 10
        
        for proxy in self.proxy_list:
            try:
                proxies = {'http': proxy, 'https': proxy}
                response = requests.get(test_url, proxies=proxies, timeout=timeout)
                
                if response.status_code == 200:
                    self.working_proxies.append(proxy)
                else:
                    self.failed_proxies.append(proxy)
                    
            except (requests.RequestException, Exception):
                self.failed_proxies.append(proxy)
        
        self.last_validation = time.time()
    
    def get_proxy_stats(self) -> Dict:
        """Get proxy statistics"""
        return {
            'total_proxies': len(self.proxy_list),
            'working_proxies': len(self.working_proxies),
            'failed_proxies': len(self.failed_proxies),
            'last_validation': self.last_validation,
            'working_list': self.working_proxies,
            'failed_list': self.failed_proxies
        }
    
    def remove_proxy(self, proxy: str):
        """Remove proxy from all lists"""
        if proxy in self.proxy_list:
            self.proxy_list.remove(proxy)
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
        if proxy in self.failed_proxies:
            self.failed_proxies.remove(proxy)
    
    def force_validation(self):
        """Force immediate proxy validation"""
        self._validate_proxies()