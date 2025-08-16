"""Configuration Loader - Loads config from various sources"""

import json
import yaml
from typing import Dict, Any


class ConfigLoader:
    def load_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load configuration from file"""
        if filepath.endswith('.json'):
            return self._load_json(filepath)
        elif filepath.endswith(('.yml', '.yaml')):
            return self._load_yaml(filepath)
        else:
            raise ValueError(f"Unsupported config file format: {filepath}")
    
    def _load_json(self, filepath: str) -> Dict[str, Any]:
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _load_yaml(self, filepath: str) -> Dict[str, Any]:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)