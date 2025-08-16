"""Log Rotator - Handle log file rotation"""

import os
import gzip
import time
from typing import Optional


class LogRotator:
    def __init__(self, max_size_mb: int = 10, max_files: int = 5):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_files = max_files
    
    def should_rotate(self, filepath: str) -> bool:
        """Check if log file should be rotated"""
        if not os.path.exists(filepath):
            return False
        
        return os.path.getsize(filepath) >= self.max_size_bytes
    
    def rotate_file(self, filepath: str):
        """Rotate log file"""
        if not os.path.exists(filepath):
            return
        
        # Remove oldest backup if at limit
        oldest_backup = f"{filepath}.{self.max_files}.gz"
        if os.path.exists(oldest_backup):
            os.remove(oldest_backup)
        
        # Shift existing backups
        for i in range(self.max_files - 1, 0, -1):
            old_backup = f"{filepath}.{i}.gz"
            new_backup = f"{filepath}.{i + 1}.gz"
            if os.path.exists(old_backup):
                os.rename(old_backup, new_backup)
        
        # Compress current log file
        with open(filepath, 'rb') as f_in:
            with gzip.open(f"{filepath}.1.gz", 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Clear current log file
        open(filepath, 'w').close()
    
    def cleanup_old_logs(self, log_dir: str, max_age_days: int = 30):
        """Remove log files older than max_age_days"""
        if not os.path.exists(log_dir):
            return
        
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            if filename.endswith('.log') or filename.endswith('.gz'):
                if os.path.getmtime(filepath) < cutoff_time:
                    os.remove(filepath)