"""File Watcher - Monitors configuration file changes"""

import os
import time
from typing import Callable, Optional


class FileWatcher:
    def __init__(self, filepath: str, callback: Callable = None):
        self.filepath = filepath
        self.callback = callback
        self.last_modified = 0
        self.is_watching = False
    
    def start_watching(self):
        """Start monitoring file for changes"""
        self.is_watching = True
        if os.path.exists(self.filepath):
            self.last_modified = os.path.getmtime(self.filepath)
    
    def check_for_changes(self) -> bool:
        """Check if file has been modified"""
        if not self.is_watching or not os.path.exists(self.filepath):
            return False
        
        current_modified = os.path.getmtime(self.filepath)
        if current_modified > self.last_modified:
            self.last_modified = current_modified
            if self.callback:
                self.callback(self.filepath)
            return True
        return False
    
    def stop_watching(self):
        """Stop monitoring file"""
        self.is_watching = False