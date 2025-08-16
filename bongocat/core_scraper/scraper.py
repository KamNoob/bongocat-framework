"""
Main BongoCat scraper class - handles web scraping operations
"""

import asyncio
import time
from ..types import Dict, List, Optional, Union, Any

# Import for type hints only (not executed at runtime)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bs4 import BeautifulSoup

# Move import to module level for performance
from ..output_handler.handler import OutputHandler

from ..config_manager.manager import ConfigManager
from ..error_logger.logger import ErrorLogger
from .session_manager import SessionManager
from .proxy_handler import ProxyHandler  
from .rate_limiter import RateLimiter
from .user_agent_rotator import UserAgentRotator


class BongoCat:
    """
    Main BongoCat scraper class for web data extraction
    """
    
    def __init__(self, config_path: str = None, **kwargs):
        """Initialize BongoCat scraper with configuration"""
        self.config = ConfigManager(config_path) if config_path else ConfigManager()
        self.logger = ErrorLogger(self.config.get_log_level())
        self.session_manager = SessionManager()
        self.proxy_handler = ProxyHandler(self.config.get_proxy_list())
        self.rate_limiter = RateLimiter(self.config.get_rate_limit())
        self.user_agent_rotator = UserAgentRotator()
        
        # Browser setup for JavaScript-heavy sites with pooling
        self.driver_pool = []
        self.max_drivers = kwargs.get('max_drivers', 3)
        self.use_browser = kwargs.get('use_browser', False)
        self.current_driver_index = 0
        
        if self.use_browser:
            self._setup_driver_pool()
    
    def _setup_driver_pool(self):
        """Setup Chrome browser pool for JavaScript rendering with driver reuse"""
        # Lazy load selenium modules
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        self.logger.info(f"Initializing browser pool with {self.max_drivers} drivers")
        
        for i in range(self.max_drivers):
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument(f'--user-agent={self.user_agent_rotator.get_random_agent()}')
                
                driver = webdriver.Chrome(options=chrome_options)
                self.driver_pool.append({'driver': driver, 'in_use': False})
                self.logger.info(f"Driver {i+1}/{self.max_drivers} initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize driver {i+1}: {str(e)}")
                if i == 0:  # If first driver fails, raise error
                    raise
    
    def _get_available_driver(self):
        """Get available driver from pool or wait for one"""
        # Simple round-robin selection
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
    
    def _release_driver(self, driver_info):
        """Release driver back to pool"""
        driver_info['in_use'] = False
    
    async def scrape(self, url: str, method: str = 'GET', **kwargs) -> Dict:
        """
        Main scraping method - extracts data from URL
        
        Args:
            url: Target URL to scrape
            method: HTTP method to use
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing scraped data and metadata
        """
        self.logger.info(f"Starting scrape for URL: {url}")
        
        # Apply rate limiting
        self.rate_limiter.wait()
        
        try:
            if self.use_browser:
                return await self._scrape_with_browser(url, **kwargs)
            else:
                return self._scrape_with_requests(url, method, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Scraping failed for {url}: {str(e)}")
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'data': None,
                'timestamp': time.time()
            }
    
    def _scrape_with_requests(self, url: str, method: str, **kwargs) -> Dict:
        """Scrape using requests library with lazy loading"""
        # Lazy load requests and BeautifulSoup
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': self.user_agent_rotator.get_random_agent(),
            **kwargs.get('headers', {})
        }
        
        session = self.session_manager.get_session()
        
        # Apply proxy if available  
        proxies = self.proxy_handler.get_proxy()
        
        try:
            if method.upper() == 'GET':
                response = session.get(url, headers=headers, proxies=proxies, 
                                     timeout=self.config.get_timeout())
            elif method.upper() == 'POST':
                response = session.post(url, headers=headers, proxies=proxies,
                                      data=kwargs.get('data'), 
                                      timeout=self.config.get_timeout())
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Parse content with BeautifulSoup (already imported above)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                'url': url,
                'status': 'success',
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'soup': soup,
                'data': self._extract_data(soup, **kwargs),
                'timestamp': time.time()
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise
    
    async def _scrape_with_browser(self, url: str, **kwargs) -> Dict:
        """Scrape using Selenium browser with async waits"""
        # Lazy load BeautifulSoup for browser scraping
        from bs4 import BeautifulSoup
        
        driver_info = self._get_available_driver()
        driver = driver_info['driver']
        
        try:
            driver.get(url)
            
            # Use async sleep for better performance
            wait_time = kwargs.get('wait_time', 2)
            await asyncio.sleep(wait_time)
            
            # Execute custom JavaScript if provided
            if 'javascript' in kwargs:
                driver.execute_script(kwargs['javascript'])
                await asyncio.sleep(1)  # Async sleep for JS execution
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            return {
                'url': url,
                'status': 'success', 
                'content': page_source,
                'soup': soup,
                'data': self._extract_data(soup, **kwargs),
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Browser scraping failed: {str(e)}")
            raise
        finally:
            self._release_driver(driver_info)
    
    def _extract_data(self, soup: 'BeautifulSoup', **kwargs) -> Dict:
        """Extract structured data from parsed HTML"""
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
    
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[Dict]:
        """Scrape multiple URLs with async support for better performance"""
        results = []
        
        for url in urls:
            try:
                result = await self.scrape(url, **kwargs)
                results.append(result)
                self.logger.info(f"Successfully scraped: {url}")
            except Exception as e:
                self.logger.error(f"Failed to scrape {url}: {str(e)}")
                results.append({
                    'url': url,
                    'status': 'error', 
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        return results
    
    def scrape_sync(self, url: str, method: str = 'GET', **kwargs) -> Dict:
        """Synchronous version of scrape for backward compatibility"""
        if self.use_browser:
            # Run async method in event loop for browser-based scraping
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(self.scrape(url, method, **kwargs))
            except RuntimeError:
                # Create new event loop if none exists
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.scrape(url, method, **kwargs))
                finally:
                    loop.close()
        else:
            # For requests-based scraping, use sync version directly
            self.logger.info(f"Starting sync scrape for URL: {url}")
            self.rate_limiter.wait()
            
            try:
                return self._scrape_with_requests(url, method, **kwargs)
            except Exception as e:
                self.logger.error(f"Scraping failed for {url}: {str(e)}")
                return {
                    'url': url,
                    'status': 'error',
                    'error': str(e),
                    'data': None,
                    'timestamp': time.time()
                }
    
    def export(self, data: Union[Dict, List[Dict]], format: str = 'json', 
               filename: str = None) -> str:
        """Export scraped data to file"""
        # Use module-level import for better performance
        handler = OutputHandler()
        return handler.export(data, format, filename)
    
    def close(self):
        """Clean up resources"""
        # Close all drivers in pool
        for driver_info in self.driver_pool:
            try:
                driver_info['driver'].quit()
            except Exception as e:
                self.logger.warning(f"Error closing driver: {str(e)}")
        
        self.driver_pool.clear()
        self.session_manager.close_all()
        self.logger.info("BongoCat scraper closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()