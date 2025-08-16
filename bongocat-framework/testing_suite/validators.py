"""Validators - Validation utilities for testing"""

import re
import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class URLValidator:
    """Validate URLs and web-related data"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def is_http_url(url: str) -> bool:
        """Check if URL uses HTTP/HTTPS scheme"""
        return url.lower().startswith(('http://', 'https://'))
    
    @staticmethod
    def validate_css_selector(selector: str) -> bool:
        """Basic CSS selector validation"""
        if not selector or not isinstance(selector, str):
            return False
        
        # Basic checks for common CSS selector patterns
        invalid_chars = ['<', '>', '{', '}', '"', "'"]
        return not any(char in selector for char in invalid_chars)


class DataValidator:
    """Validate scraped data and parsing results"""
    
    @staticmethod
    def validate_scrape_result(result: Dict[str, Any]) -> List[str]:
        """Validate scrape result structure"""
        errors = []
        
        required_fields = ['url', 'status', 'timestamp']
        for field in required_fields:
            if field not in result:
                errors.append(f"Missing required field: {field}")
        
        if 'status' in result:
            valid_statuses = ['success', 'error', 'timeout']
            if result['status'] not in valid_statuses:
                errors.append(f"Invalid status: {result['status']}")
        
        if result.get('status') == 'success':
            if 'content' not in result and 'data' not in result:
                errors.append("Success result missing content or data")
        
        return errors
    
    @staticmethod
    def validate_parse_result(result: Dict[str, Any]) -> List[str]:
        """Validate parse result structure"""
        errors = []
        
        if 'success' not in result:
            errors.append("Missing success field")
        
        if 'content_type' not in result:
            errors.append("Missing content_type field")
        
        if result.get('success') and 'data' not in result:
            errors.append("Successful parse missing data field")
        
        return errors
    
    @staticmethod
    def validate_json_data(data: str) -> bool:
        """Check if string is valid JSON"""
        try:
            json.loads(data)
            return True
        except:
            return False
    
    @staticmethod
    def validate_html_structure(html: str) -> List[str]:
        """Basic HTML structure validation"""
        issues = []
        
        if not html.strip():
            issues.append("Empty HTML content")
            return issues
        
        # Check for basic HTML structure
        if '<html' not in html.lower():
            issues.append("Missing <html> tag")
        
        if '<head' not in html.lower():
            issues.append("Missing <head> section")
        
        if '<body' not in html.lower():
            issues.append("Missing <body> section")
        
        # Check for unclosed tags (basic check)
        open_tags = re.findall(r'<(\w+)(?:\s|>)', html.lower())
        close_tags = re.findall(r'</(\w+)>', html.lower())
        
        self_closing = {'img', 'br', 'hr', 'input', 'meta', 'link'}
        
        for tag in open_tags:
            if tag not in self_closing and open_tags.count(tag) != close_tags.count(tag):
                issues.append(f"Potentially unclosed tag: {tag}")
        
        return issues


class ConfigValidator:
    """Validate configuration data"""
    
    @staticmethod
    def validate_rate_limit(rate_limit: Any) -> bool:
        """Validate rate limit value"""
        try:
            val = float(rate_limit)
            return val > 0
        except:
            return False
    
    @staticmethod
    def validate_timeout(timeout: Any) -> bool:
        """Validate timeout value"""
        try:
            val = int(timeout)
            return val > 0
        except:
            return False
    
    @staticmethod
    def validate_log_level(log_level: Any) -> bool:
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        return isinstance(log_level, str) and log_level.upper() in valid_levels
    
    @staticmethod
    def validate_proxy_list(proxies: Any) -> bool:
        """Validate proxy list"""
        if not isinstance(proxies, list):
            return False
        
        for proxy in proxies:
            if not isinstance(proxy, str) or not URLValidator.is_valid_url(proxy):
                return False
        
        return True


class ResponseValidator:
    """Validate HTTP responses and web content"""
    
    @staticmethod
    def is_successful_status(status_code: int) -> bool:
        """Check if HTTP status code indicates success"""
        return 200 <= status_code < 300
    
    @staticmethod
    def is_redirect_status(status_code: int) -> bool:
        """Check if HTTP status code indicates redirect"""
        return 300 <= status_code < 400
    
    @staticmethod
    def is_client_error_status(status_code: int) -> bool:
        """Check if HTTP status code indicates client error"""
        return 400 <= status_code < 500
    
    @staticmethod
    def is_server_error_status(status_code: int) -> bool:
        """Check if HTTP status code indicates server error"""
        return 500 <= status_code < 600
    
    @staticmethod
    def validate_content_type(content_type: str, expected: str) -> bool:
        """Validate content type matches expected"""
        if not content_type:
            return False
        
        # Basic content type matching (ignore charset, boundary, etc.)
        main_type = content_type.split(';')[0].strip().lower()
        return main_type == expected.lower()
    
    @staticmethod
    def validate_response_headers(headers: Dict[str, str]) -> List[str]:
        """Validate response headers"""
        issues = []
        
        # Check for common security headers
        security_headers = [
            'x-frame-options',
            'x-content-type-options',
            'x-xss-protection'
        ]
        
        for header in security_headers:
            if header.lower() not in [h.lower() for h in headers.keys()]:
                issues.append(f"Missing security header: {header}")
        
        return issues


class Validators:
    """Main validator class combining all validation utilities"""
    
    def __init__(self):
        self.url_validator = URLValidator()
        self.data_validator = DataValidator()
        self.config_validator = ConfigValidator()
        self.response_validator = ResponseValidator()
    
    def validate_all(self, data_type: str, data: Any) -> Dict[str, Any]:
        """Run all relevant validations for data type"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            if data_type == 'url':
                if not self.url_validator.is_valid_url(data):
                    results['errors'].append("Invalid URL format")
                    results['valid'] = False
            
            elif data_type == 'scrape_result':
                errors = self.data_validator.validate_scrape_result(data)
                results['errors'].extend(errors)
                if errors:
                    results['valid'] = False
            
            elif data_type == 'parse_result':
                errors = self.data_validator.validate_parse_result(data)
                results['errors'].extend(errors)
                if errors:
                    results['valid'] = False
            
            elif data_type == 'config':
                for key, value in data.items():
                    if key == 'rate_limit' and not self.config_validator.validate_rate_limit(value):
                        results['errors'].append("Invalid rate_limit value")
                        results['valid'] = False
                    elif key == 'timeout' and not self.config_validator.validate_timeout(value):
                        results['errors'].append("Invalid timeout value")
                        results['valid'] = False
            
        except Exception as e:
            results['errors'].append(f"Validation error: {str(e)}")
            results['valid'] = False
        
        return results