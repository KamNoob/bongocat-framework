"""Benchmark Suite - Performance benchmarking for BongoCat components"""

import time
import psutil
import gc
from typing import Dict, Any, List, Callable
from contextlib import contextmanager


class BenchmarkSuite:
    """Performance benchmarking utilities"""
    
    def __init__(self):
        self.results = {}
        self.baseline_results = {}
    
    @contextmanager
    def measure_performance(self, test_name: str):
        """Context manager to measure performance metrics"""
        # Record initial state
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        initial_cpu_times = process.cpu_times()
        start_time = time.perf_counter()
        
        # Force garbage collection before test
        gc.collect()
        
        try:
            yield
        finally:
            # Record final state
            end_time = time.perf_counter()
            final_memory = process.memory_info().rss
            final_cpu_times = process.cpu_times()
            
            # Calculate metrics
            duration = end_time - start_time
            memory_delta = final_memory - initial_memory
            cpu_time = (final_cpu_times.user - initial_cpu_times.user) + \
                      (final_cpu_times.system - initial_cpu_times.system)
            
            self.results[test_name] = {
                'duration': duration,
                'memory_delta_bytes': memory_delta,
                'memory_delta_mb': memory_delta / (1024 * 1024),
                'cpu_time': cpu_time,
                'peak_memory_mb': process.memory_info().rss / (1024 * 1024),
                'timestamp': time.time()
            }
    
    def benchmark_scraper_performance(self, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark scraper performance"""
        from ..testing_suite.mocks import MockScraper
        
        results = []
        scraper = MockScraper()
        
        for i in range(iterations):
            with self.measure_performance(f'scrape_{i}'):
                scraper.scrape(f'http://example.com/page_{i}')
            
            results.append(self.results[f'scrape_{i}'])
        
        # Calculate statistics
        durations = [r['duration'] for r in results]
        memory_deltas = [r['memory_delta_bytes'] for r in results]
        
        return {
            'iterations': iterations,
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'avg_memory_delta_mb': sum(memory_deltas) / len(memory_deltas) / (1024 * 1024),
            'total_duration': sum(durations),
            'operations_per_second': iterations / sum(durations)
        }
    
    def benchmark_parser_performance(self, content_sizes: List[int] = None) -> Dict[str, Any]:
        """Benchmark parser performance with different content sizes"""
        from ..testing_suite.mocks import MockDataParser
        from ..testing_suite.fixtures import TestFixtures
        
        if content_sizes is None:
            content_sizes = [1000, 5000, 10000, 50000, 100000]  # bytes
        
        parser = MockDataParser()
        results = {}
        
        for size in content_sizes:
            # Create content of specified size
            base_content = TestFixtures.get_sample_html()
            content = base_content * (size // len(base_content) + 1)
            content = content[:size]
            
            with self.measure_performance(f'parse_size_{size}'):
                for _ in range(5):  # Parse 5 times for averaging
                    parser.parse(content, 'html')
            
            results[f'size_{size}'] = self.results[f'parse_size_{size}']
        
        return {
            'content_sizes': content_sizes,
            'results': results,
            'performance_scaling': self._analyze_scaling(results)
        }
    
    def benchmark_export_performance(self, data_sizes: List[int] = None) -> Dict[str, Any]:
        """Benchmark export performance"""
        from ..testing_suite.mocks import MockOutputHandler
        
        if data_sizes is None:
            data_sizes = [100, 500, 1000, 5000, 10000]  # number of records
        
        handler = MockOutputHandler()
        results = {}
        
        for size in data_sizes:
            # Create test data of specified size
            test_data = [{'id': i, 'name': f'Item {i}', 'value': i * 10} for i in range(size)]
            
            with self.measure_performance(f'export_size_{size}'):
                for format_type in ['json', 'csv']:
                    handler.export(test_data, format_type, f'test_{size}.{format_type}')
            
            results[f'size_{size}'] = self.results[f'export_size_{size}']
        
        return {
            'data_sizes': data_sizes,
            'results': results
        }
    
    def benchmark_rate_limiter(self, rates: List[float] = None) -> Dict[str, Any]:
        """Benchmark rate limiter accuracy"""
        from ..core_scraper.rate_limiter import RateLimiter
        
        if rates is None:
            rates = [1.0, 2.0, 5.0, 10.0]  # requests per second
        
        results = {}
        
        for rate in rates:
            limiter = RateLimiter(requests_per_second=rate)
            expected_interval = 1.0 / rate
            
            # Measure actual intervals
            intervals = []
            start_time = time.perf_counter()
            
            for i in range(10):
                limiter.wait()
                current_time = time.perf_counter()
                if i > 0:  # Skip first measurement
                    intervals.append(current_time - last_time)
                last_time = current_time
            
            avg_interval = sum(intervals) / len(intervals)
            accuracy = (1.0 - abs(avg_interval - expected_interval) / expected_interval) * 100
            
            results[f'rate_{rate}'] = {
                'expected_interval': expected_interval,
                'actual_interval': avg_interval,
                'accuracy_percent': accuracy,
                'variance': max(intervals) - min(intervals)
            }
        
        return results
    
    def _analyze_scaling(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance scaling characteristics"""
        sizes = []
        durations = []
        
        for key, result in results.items():
            size = int(key.split('_')[1])
            sizes.append(size)
            durations.append(result['duration'])
        
        # Simple linear regression to analyze scaling
        if len(sizes) > 1:
            # Calculate correlation between size and duration
            n = len(sizes)
            sum_x = sum(sizes)
            sum_y = sum(durations)
            sum_xy = sum(x * y for x, y in zip(sizes, durations))
            sum_x2 = sum(x * x for x in sizes)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            scaling_factor = slope * 1000  # Scale factor per 1000 units
            
            return {
                'scaling_type': 'linear' if slope > 0 else 'constant',
                'slope': slope,
                'scaling_factor_per_1000': scaling_factor,
                'correlation': 'strong' if abs(slope) > 0.1 else 'weak'
            }
        
        return {'scaling_type': 'unknown', 'reason': 'insufficient_data'}
    
    def run_full_benchmark_suite(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        print("Running BongoCat Performance Benchmark Suite...")
        
        suite_start = time.perf_counter()
        
        # Run all benchmarks
        scraper_results = self.benchmark_scraper_performance(5)
        parser_results = self.benchmark_parser_performance([1000, 5000, 10000])
        export_results = self.benchmark_export_performance([100, 500, 1000])
        rate_limiter_results = self.benchmark_rate_limiter([1.0, 2.0, 5.0])
        
        suite_duration = time.perf_counter() - suite_start
        
        return {
            'suite_duration': suite_duration,
            'scraper_benchmark': scraper_results,
            'parser_benchmark': parser_results,
            'export_benchmark': export_results,
            'rate_limiter_benchmark': rate_limiter_results,
            'system_info': self._get_system_info(),
            'timestamp': time.time()
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmark context"""
        import platform
        
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'memory_available_gb': psutil.virtual_memory().available / (1024**3)
        }
    
    def compare_with_baseline(self, current_results: Dict[str, Any], baseline_file: str = None):
        """Compare current results with baseline"""
        # This would implement baseline comparison logic
        # For now, just store results
        if baseline_file:
            try:
                import json
                with open(baseline_file, 'w') as f:
                    json.dump(current_results, f, indent=2, default=str)
            except:
                pass  # Ignore file errors in tests
        
        return {
            'comparison': 'baseline_saved',
            'baseline_file': baseline_file
        }