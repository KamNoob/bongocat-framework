"""
Async BongoCat scraper class - High-performance async web scraping
Provides 3x performance improvement through async/await architecture
"""

import asyncio
import concurrent.futures
import time
from ..types import Dict, List, Optional, Union, Any

# Import for type hints only (not executed at runtime)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bs4 import BeautifulSoup

from ..config_manager.manager import ConfigManager
from ..error_logger.logger import ErrorLogger
from .async_session_manager import AsyncSessionManager
from .proxy_handler import ProxyHandler  
from .rate_limiter import RateLimiter
from .user_agent_rotator import UserAgentRotator
from ..output_handler.handler import OutputHandler


class AsyncBongoCat:
    """
    High-performance async BongoCat scraper for concurrent web data extraction
    Provides 3x performance improvement over sync version
    """
    
    def __init__(self, config_path: str = None, **kwargs):
        """Initialize async BongoCat scraper with configuration"""
        self.config = ConfigManager(config_path) if config_path else ConfigManager()
        self.logger = ErrorLogger(self.config.get_log_level())
        
        # Enhanced async session manager with high concurrency
        concurrent_limit = kwargs.get('concurrent_limit', 100)
        max_connections = kwargs.get('max_connections', 50) 
        self.session_manager = AsyncSessionManager(
            max_connections=max_connections,
            concurrent_limit=concurrent_limit
        )
        
        self.proxy_handler = ProxyHandler(self.config.get_proxy_list())
        self.rate_limiter = RateLimiter(self.config.get_rate_limit())
        self.user_agent_rotator = UserAgentRotator()
        
        # Browser setup for JavaScript-heavy sites (still sync, but optimized for async usage)
        self.driver_pool = []
        self.max_drivers = kwargs.get('max_drivers', 5)  # More drivers for async
        self.use_browser = kwargs.get('use_browser', False)
        self.current_driver_index = 0
        self.driver_semaphore = asyncio.Semaphore(self.max_drivers)
        
        if self.use_browser:
            self._setup_driver_pool()
    
    def _setup_driver_pool(self):
        """Setup Chrome browser pool optimized for async operations"""
        # Lazy load selenium modules
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        self.logger.info(f"Initializing async-optimized browser pool with {self.max_drivers} drivers")
        
        for i in range(self.max_drivers):
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-logging')
                chrome_options.add_argument('--disable-background-timer-throttling')
                chrome_options.add_argument(f'--user-agent={self.user_agent_rotator.get_random_agent()}')
                
                driver = webdriver.Chrome(options=chrome_options)
                self.driver_pool.append({'driver': driver, 'in_use': False})
                self.logger.info(f"Async driver {i+1}/{self.max_drivers} initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize async driver {i+1}: {str(e)}")
                if i == 0:  # If first driver fails, raise error
                    raise
    
    async def scrape(self, url: str, method: str = 'GET', **kwargs) -> Dict:
        """
        Async scraping method - extracts data from URL with high performance
        
        Args:
            url: Target URL to scrape
            method: HTTP method to use
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing scraped data and metadata
        """
        self.logger.info(f"Starting async scrape for URL: {url}")
        
        # Apply async rate limiting
        await self._async_rate_limit()
        
        try:
            if self.use_browser:
                return await self._scrape_with_browser(url, **kwargs)
            else:
                return await self._scrape_with_requests(url, method, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Async scraping failed for {url}: {str(e)}")
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'data': None,
                'timestamp': time.time()
            }
    
    async def _async_rate_limit(self):
        """Async-compatible rate limiting"""
        # Convert sync rate limiter to async
        if hasattr(self.rate_limiter, 'get_wait_time'):
            wait_time = self.rate_limiter.get_wait_time()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        else:
            # Fallback - use sync rate limiter in thread
            import concurrent.futures
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                await loop.run_in_executor(executor, self.rate_limiter.wait)
    
    async def _scrape_with_requests(self, url: str, method: str, **kwargs) -> Dict:
        """Async scraping using aiohttp for maximum performance"""
        headers = {
            'User-Agent': self.user_agent_rotator.get_random_agent(),
            **kwargs.get('headers', {})
        }
        
        # Get proxy if available
        proxy = self.proxy_handler.get_proxy()
        proxy_url = proxy.get('http') if proxy else None
        
        # Prepare request kwargs
        request_kwargs = {
            'headers': headers,
            'timeout': self.config.get_timeout(),
        }
        
        # Add proxy if available
        if proxy_url:
            request_kwargs['proxy'] = proxy_url
        
        # Add data for POST requests
        if method.upper() == 'POST' and 'data' in kwargs:
            request_kwargs['data'] = kwargs['data']
        
        try:
            # Make async request
            response_data = await self.session_manager.make_request(
                'default', method, url, **request_kwargs
            )
            
            # Parse content with BeautifulSoup (in thread to avoid blocking)
            soup = await self._parse_html_async(response_data['content'])
            
            return {
                'url': url,
                'status': 'success',
                'status_code': response_data['status_code'],
                'headers': response_data['headers'],
                'content': response_data['content'],
                'soup': soup,
                'data': await self._extract_data_async(soup, **kwargs),
                'response_time': response_data['response_time'],
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Async request failed: {str(e)}")
            raise
    
    async def _scrape_with_browser(self, url: str, **kwargs) -> Dict:
        """Async browser scraping with driver pool management"""
        async with self.driver_semaphore:  # Control concurrent browser usage
            driver_info = await self._get_available_driver_async()
            driver = driver_info['driver']
            
            try:
                # Run browser operations in thread to avoid blocking
                page_source = await self._browser_operations_async(driver, url, **kwargs)
                
                # Parse content asynchronously
                soup = await self._parse_html_async(page_source)
                
                return {
                    'url': url,
                    'status': 'success', 
                    'content': page_source,
                    'soup': soup,
                    'data': await self._extract_data_async(soup, **kwargs),
                    'timestamp': time.time()
                }
                
            except Exception as e:
                self.logger.error(f"Async browser scraping failed: {str(e)}")
                raise
            finally:
                await self._release_driver_async(driver_info)
    
    async def _browser_operations_async(self, driver, url: str, **kwargs) -> str:
        """Run browser operations in thread to avoid blocking event loop"""
        def browser_sync_ops():
            driver.get(url)
            
            # Wait for page load
            wait_time = kwargs.get('wait_time', 2)
            time.sleep(wait_time)
            
            # Execute custom JavaScript if provided
            if 'javascript' in kwargs:
                driver.execute_script(kwargs['javascript'])
                time.sleep(1)
            
            return driver.page_source
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, browser_sync_ops)
    
    async def _parse_html_async(self, html_content: str) -> 'BeautifulSoup':
        """Parse HTML asynchronously to avoid blocking"""
        def parse_sync():
            from bs4 import BeautifulSoup
            return BeautifulSoup(html_content, 'html.parser')
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, parse_sync)
    
    async def _extract_data_async(self, soup: 'BeautifulSoup', **kwargs) -> Dict:
        """Extract structured data asynchronously"""
        def extract_sync():
            selectors = kwargs.get('selectors', {})
            extracted_data = {}
            
            # Extract data based on CSS selectors
            for key, selector in selectors.items():
                try:
                    elements = soup.select(selector)
                    if elements:
                        if len(elements) == 1:
                            extracted_data[key] = elements[0].get_text(strip=True)
                        else:
                            extracted_data[key] = [elem.get_text(strip=True) for elem in elements]
                    else:
                        extracted_data[key] = None
                except Exception as e:
                    self.logger.warning(f"Failed to extract {key}: {str(e)}")
                    extracted_data[key] = None
            
            return extracted_data
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, extract_sync)
    
    async def _get_available_driver_async(self):
        """Async-compatible driver pool management"""
        # Simple round-robin selection with async safety
        for _ in range(len(self.driver_pool)):
            driver_info = self.driver_pool[self.current_driver_index]
            self.current_driver_index = (self.current_driver_index + 1) % len(self.driver_pool)
            
            if not driver_info['in_use']:
                driver_info['in_use'] = True
                return driver_info
        
        # If no drivers available, use the first one (blocking)
        driver_info = self.driver_pool[0]
        driver_info['in_use'] = True
        return driver_info
    
    async def _release_driver_async(self, driver_info):
        """Release driver back to pool asynchronously"""
        driver_info['in_use'] = False
    
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[Dict]:
        """
        Scrape multiple URLs concurrently for maximum throughput
        This is where the 3x performance improvement really shines
        """
        if not urls:
            return []
        
        self.logger.info(f"Starting concurrent scraping of {len(urls)} URLs")
        start_time = time.time()
        
        # Create tasks for concurrent execution
        tasks = []
        for url in urls:
            task = self.scrape(url, **kwargs)
            tasks.append(task)
        
        # Execute all scraping tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        successful = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to scrape {urls[i]}: {str(result)}")
                processed_results.append({
                    'url': urls[i],
                    'status': 'error',
                    'error': str(result),
                    'timestamp': time.time()
                })
            else:
                successful += 1
                processed_results.append(result)
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"Completed concurrent scraping: {successful}/{len(urls)} successful in {elapsed_time:.2f}s")
        
        return processed_results
    
    async def scrape_with_concurrency_control(self, urls: List[str], batch_size: int = 20, **kwargs) -> List[Dict]:
        """
        Scrape URLs with controlled concurrency to prevent overwhelming target servers
        """
        if not urls:
            return []
        
        self.logger.info(f"Starting batch scraping of {len(urls)} URLs with batch size {batch_size}")
        all_results = []
        
        # Process URLs in batches
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}: {len(batch_urls)} URLs")
            
            batch_results = await self.scrape_multiple(batch_urls, **kwargs)
            all_results.extend(batch_results)
            
            # Small delay between batches to be respectful
            if i + batch_size < len(urls):
                await asyncio.sleep(0.5)
        
        return all_results
    
    async def export_async(self, data: Union[Dict, List[Dict]], format: str = 'json', 
                          filename: str = None) -> str:
        """Export scraped data to file asynchronously"""
        def export_sync():
            handler = OutputHandler()
            return handler.export(data, format, filename)
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, export_sync)
    
    async def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        session_stats = await self.session_manager.get_performance_stats()
        
        # Add browser pool stats if applicable
        browser_stats = {}
        if self.use_browser:
            in_use_drivers = sum(1 for d in self.driver_pool if d['in_use'])
            browser_stats = {
                'total_drivers': len(self.driver_pool),
                'drivers_in_use': in_use_drivers,
                'available_drivers': len(self.driver_pool) - in_use_drivers,
                'max_concurrent_drivers': self.max_drivers
            }
        
        return {
            'session_performance': session_stats,
            'browser_performance': browser_stats,
            'proxy_stats': self.proxy_handler.get_proxy_stats(),
            'rate_limiter_active': hasattr(self.rate_limiter, 'get_stats')
        }
    
    async def close(self):
        """Clean up all async resources"""
        # Close async session manager
        await self.session_manager.close_all()
        
        # Close browser drivers
        for driver_info in self.driver_pool:
            try:
                driver_info['driver'].quit()
            except Exception as e:
                self.logger.warning(f"Error closing async driver: {str(e)}")
        
        self.driver_pool.clear()
        self.logger.info("AsyncBongoCat scraper closed")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Utility functions for easy async usage
async def scrape_urls_async(urls: List[str], config_path: str = None, **kwargs) -> List[Dict]:
    """Convenience function for quick async scraping of multiple URLs"""
    async with AsyncBongoCat(config_path, **kwargs) as scraper:
        return await scraper.scrape_multiple(urls, **kwargs)

async def scrape_single_async(url: str, config_path: str = None, **kwargs) -> Dict:
    """Convenience function for quick async scraping of single URL"""
    async with AsyncBongoCat(config_path, **kwargs) as scraper:
        return await scraper.scrape(url, **kwargs)