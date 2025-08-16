"""Dashboard - Main dashboard logic and data aggregation"""

from typing import Dict, Any, List
import time
import psutil
import os


class Dashboard:
    def __init__(self):
        self.start_time = time.time()
        self.scraper_stats = {
            'total_scraped': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'active_scrapers': 0
        }
        self.parser_stats = {
            'total_parsed': 0,
            'html_parsed': 0,
            'json_parsed': 0,
            'xml_parsed': 0,
            'csv_parsed': 0
        }
        self.export_stats = {
            'total_exports': 0,
            'json_exports': 0,
            'csv_exports': 0,
            'xml_exports': 0,
            'html_exports': 0
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system resource statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'disk_usage': disk.percent,
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except Exception:
            return {
                'cpu_usage': 0,
                'memory_usage': 0,
                'memory_total_gb': 0,
                'memory_used_gb': 0,
                'disk_usage': 0,
                'disk_total_gb': 0,
                'disk_used_gb': 0,
                'load_average': [0, 0, 0]
            }
    
    def get_application_stats(self) -> Dict[str, Any]:
        """Get application statistics"""
        uptime_seconds = time.time() - self.start_time
        uptime_hours = uptime_seconds / 3600
        
        return {
            'uptime_seconds': uptime_seconds,
            'uptime_hours': round(uptime_hours, 2),
            'uptime_days': round(uptime_hours / 24, 1),
            'scraper_stats': self.scraper_stats.copy(),
            'parser_stats': self.parser_stats.copy(),
            'export_stats': self.export_stats.copy()
        }
    
    def get_component_status(self) -> Dict[str, str]:
        """Get status of all components"""
        return {
            'core_scraper': 'active',
            'data_parser': 'active',
            'config_manager': 'active',
            'output_handler': 'active',
            'error_logger': 'active',
            'web_interface': 'active',
            'testing_suite': 'ready'
        }
    
    def get_recent_activities(self) -> List[Dict[str, Any]]:
        """Get recent activities (mock data for now)"""
        return [
            {
                'timestamp': time.time() - 300,
                'type': 'scrape',
                'description': 'Scraped https://example.com successfully',
                'status': 'success'
            },
            {
                'timestamp': time.time() - 600,
                'type': 'export',
                'description': 'Exported data to JSON format',
                'status': 'success'
            },
            {
                'timestamp': time.time() - 900,
                'type': 'parse',
                'description': 'Parsed HTML content (1.2MB)',
                'status': 'success'
            },
            {
                'timestamp': time.time() - 1200,
                'type': 'error',
                'description': 'Rate limit exceeded on scraper',
                'status': 'warning'
            }
        ]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            'system_stats': self.get_system_stats(),
            'app_stats': self.get_application_stats(),
            'component_status': self.get_component_status(),
            'recent_activities': self.get_recent_activities(),
            'timestamp': time.time()
        }
    
    def update_scraper_stats(self, success: bool = True, active_change: int = 0):
        """Update scraper statistics"""
        self.scraper_stats['total_scraped'] += 1
        if success:
            self.scraper_stats['successful_scrapes'] += 1
        else:
            self.scraper_stats['failed_scrapes'] += 1
        
        self.scraper_stats['active_scrapers'] += active_change
        self.scraper_stats['active_scrapers'] = max(0, self.scraper_stats['active_scrapers'])
    
    def update_parser_stats(self, content_type: str = 'unknown'):
        """Update parser statistics"""
        self.parser_stats['total_parsed'] += 1
        
        type_key = f"{content_type}_parsed"
        if type_key in self.parser_stats:
            self.parser_stats[type_key] += 1
    
    def update_export_stats(self, format_type: str = 'unknown'):
        """Update export statistics"""
        self.export_stats['total_exports'] += 1
        
        format_key = f"{format_type}_exports"
        if format_key in self.export_stats:
            self.export_stats[format_key] += 1
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        app_stats = self.get_application_stats()
        system_stats = self.get_system_stats()
        
        # Calculate success rates
        total_scrapes = self.scraper_stats['total_scraped']
        success_rate = (self.scraper_stats['successful_scrapes'] / max(total_scrapes, 1)) * 100
        
        # Calculate throughput
        uptime_hours = app_stats['uptime_hours']
        scrapes_per_hour = total_scrapes / max(uptime_hours, 1)
        
        return {
            'success_rate': round(success_rate, 1),
            'scrapes_per_hour': round(scrapes_per_hour, 1),
            'avg_cpu_usage': system_stats['cpu_usage'],
            'avg_memory_usage': system_stats['memory_usage'],
            'total_operations': (
                self.scraper_stats['total_scraped'] +
                self.parser_stats['total_parsed'] +
                self.export_stats['total_exports']
            )
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.start_time = time.time()
        
        for key in self.scraper_stats:
            self.scraper_stats[key] = 0
        
        for key in self.parser_stats:
            self.parser_stats[key] = 0
        
        for key in self.export_stats:
            self.export_stats[key] = 0