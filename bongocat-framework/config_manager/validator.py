"""Configuration Validator"""

from typing import Dict, Any


class ConfigValidator:
    def validate(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure and values"""
        required_keys = ['rate_limit', 'timeout', 'log_level']
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")
        
        # Validate types and ranges
        if not isinstance(config['rate_limit'], (int, float)) or config['rate_limit'] <= 0:
            raise ValueError("rate_limit must be positive number")
        
        if not isinstance(config['timeout'], int) or config['timeout'] <= 0:
            raise ValueError("timeout must be positive integer")
        
        return True