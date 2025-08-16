"""Environment Variable Handler"""

import os
from typing import Dict, Any


class EnvHandler:
    def get_env_config(self) -> Dict[str, Any]:
        """Extract configuration from environment variables"""
        config = {}
        
        # Map environment variables to config keys
        env_mapping = {
            'BONGOCAT_RATE_LIMIT': ('rate_limit', float),
            'BONGOCAT_TIMEOUT': ('timeout', int),
            'BONGOCAT_LOG_LEVEL': ('log_level', str),
            'BONGOCAT_MAX_RETRIES': ('max_retries', int),
            'BONGOCAT_OUTPUT_FORMAT': ('output_format', str)
        }
        
        for env_key, (config_key, type_converter) in env_mapping.items():
            env_value = os.environ.get(env_key)
            if env_value is not None:
                try:
                    config[config_key] = type_converter(env_value)
                except ValueError:
                    pass  # Skip invalid values
        
        # Handle proxy list from environment
        proxy_env = os.environ.get('BONGOCAT_PROXIES')
        if proxy_env:
            config['proxies'] = [p.strip() for p in proxy_env.split(',') if p.strip()]
        
        return config