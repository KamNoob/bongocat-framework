"""
BongoCat - Advanced Web Scraping Framework
"""

__version__ = "1.0.0"
__author__ = "BongoCat Team"

from .core_scraper.scraper import BongoCat
from .data_parser.parser import DataParser
from .config_manager.manager import ConfigManager
from .output_handler.handler import OutputHandler
from .error_logger.logger import ErrorLogger

__all__ = [
    "BongoCat",
    "DataParser", 
    "ConfigManager",
    "OutputHandler",
    "ErrorLogger"
]