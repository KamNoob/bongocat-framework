"""Mock Objects - Mock implementations for testing"""

from unittest.mock import Mock, MagicMock
import time
from typing import Dict, Any, List


class MockScraper:
    """Mock scraper for testing"""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.closed = False
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Mock scrape method"""
        if self.should_fail:
            return {
                'url': url,
                'status': 'error',
                'error': 'Mock error for testing',
                'timestamp': time.time()
            }
        
        return {
            'url': url,
            'status': 'success',
            'status_code': 200,
            'content': '<html><title>Mock Page</title></html>',
            'data': {'title': 'Mock Page'},
            'timestamp': time.time()
        }
    
    def close(self):
        """Mock close method"""
        self.closed = True


class MockDataParser:
    """Mock data parser for testing"""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
    
    def parse(self, content: str, content_type: str = 'auto', **kwargs) -> Dict[str, Any]:
        """Mock parse method"""
        if self.should_fail:
            return {
                'success': False,
                'error': 'Mock parsing error',
                'content_type': content_type
            }
        
        return {
            'success': True,
            'content_type': content_type,
            'data': {'mock': 'parsed data'},
            'cleaned_text': content.strip() if isinstance(content, str) else str(content)
        }


class MockOutputHandler:
    """Mock output handler for testing"""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.exported_files = []
    
    def export(self, data: Any, format_type: str, filename: str = None) -> str:
        """Mock export method"""
        if self.should_fail:
            raise Exception("Mock export error")
        
        filepath = filename or f"mock_output.{format_type}"
        self.exported_files.append(filepath)
        return filepath


class MockConfigManager:
    """Mock configuration manager for testing"""
    
    def __init__(self, config_data: Dict[str, Any] = None):
        self.config_data = config_data or {
            'rate_limit': 1.0,
            'timeout': 30,
            'log_level': 'INFO',
            'proxies': [],
            'max_retries': 3
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Mock get method"""
        return self.config_data.get(key, default)
    
    def get_rate_limit(self) -> float:
        return self.get('rate_limit', 1.0)
    
    def get_timeout(self) -> int:
        return self.get('timeout', 30)
    
    def get_proxy_list(self) -> List[str]:
        return self.get('proxies', [])
    
    def get_log_level(self) -> str:
        return self.get('log_level', 'INFO')


class MockErrorLogger:
    """Mock error logger for testing"""
    
    def __init__(self):
        self.logged_messages = {
            'info': [],
            'warning': [],
            'error': [],
            'debug': [],
            'critical': []
        }
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        self.logged_messages['info'].append({'message': message, 'extra': extra})
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        self.logged_messages['warning'].append({'message': message, 'extra': extra})
    
    def error(self, message: str, extra: Dict[str, Any] = None):
        self.logged_messages['error'].append({'message': message, 'extra': extra})
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        self.logged_messages['debug'].append({'message': message, 'extra': extra})
    
    def critical(self, message: str, extra: Dict[str, Any] = None):
        self.logged_messages['critical'].append({'message': message, 'extra': extra})


class MockWebSocketHandler:
    """Mock WebSocket handler for testing"""
    
    def __init__(self):
        self.connected_clients = {}
        self.broadcasted_messages = []
    
    def broadcast_scraper_update(self, scraper_id: str, update_data: Dict[str, Any]):
        self.broadcasted_messages.append({
            'type': 'scraper_update',
            'scraper_id': scraper_id,
            'data': update_data
        })
    
    def broadcast_status_update(self, status_data: Dict[str, Any]):
        self.broadcasted_messages.append({
            'type': 'status_update',
            'data': status_data
        })
    
    def get_connected_clients_count(self) -> int:
        return len(self.connected_clients)


class MockObjects:
    """Factory for creating mock objects"""
    
    @staticmethod
    def create_mock_request_response(status_code: int = 200, content: str = None):
        """Create mock HTTP response"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = content or '<html><title>Mock</title></html>'
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.raise_for_status = Mock()
        return mock_response
    
    @staticmethod
    def create_mock_beautiful_soup():
        """Create mock BeautifulSoup object"""
        mock_soup = Mock()
        mock_soup.find.return_value = Mock()
        mock_soup.find_all.return_value = []
        mock_soup.select.return_value = []
        mock_soup.get_text.return_value = "Mock text content"
        return mock_soup
    
    @staticmethod
    def create_mock_selenium_driver():
        """Create mock Selenium WebDriver"""
        mock_driver = Mock()
        mock_driver.get = Mock()
        mock_driver.page_source = '<html><title>Mock Selenium</title></html>'
        mock_driver.execute_script = Mock()
        mock_driver.quit = Mock()
        return mock_driver
    
    @staticmethod
    def create_mock_flask_app():
        """Create mock Flask application"""
        mock_app = Mock()
        mock_app.config = {}
        mock_app.test_client = Mock()
        return mock_app
    
    @staticmethod
    def create_mock_socketio():
        """Create mock SocketIO instance"""
        mock_socketio = Mock()
        mock_socketio.emit = Mock()
        mock_socketio.on = Mock()
        return mock_socketio