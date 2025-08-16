"""Main Configuration Manager"""

import os
import json
from typing import Dict, Any, Optional
from .loader import ConfigLoader
from .validator import ConfigValidator
from .env_handler import EnvHandler


class ConfigManager:
    """Central configuration management"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config.json"
        self.loader = ConfigLoader()
        self.validator = ConfigValidator()
        self.env_handler = EnvHandler()
        self._config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file and environment"""
        # Load from file
        if os.path.exists(self.config_path):
            self._config = self.loader.load_from_file(self.config_path)
        else:
            self._config = self.get_default_config()
        
        # Override with environment variables
        env_config = self.env_handler.get_env_config()
        self._config.update(env_config)
        
        # Validate configuration
        self.validator.validate(self._config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def get_rate_limit(self) -> float:
        return self.get('rate_limit', 1.0)
    
    def get_timeout(self) -> int:
        return self.get('timeout', 30)
    
    def get_proxy_list(self) -> list:
        return self.get('proxies', [])
    
    def get_log_level(self) -> str:
        return self.get('log_level', 'INFO')
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'rate_limit': 1.0,
            'timeout': 30,
            'proxies': [],
            'log_level': 'INFO',
            'max_retries': 3,
            'user_agents': [],
            'output_format': 'json'
        }