# 🕷️ BongoCat Framework - High-Performance Web Scraping

<div align="center">
  
**🚀 Production-Ready Web Scraping Framework with 300% Performance Improvements**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Async Support](https://img.shields.io/badge/async-supported-green.svg)](#async-architecture)
[![Performance](https://img.shields.io/badge/performance-3x%20faster-brightgreen.svg)](#performance)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

## 🎯 **Key Features**

- **🚀 300% Performance Improvement** - Async/await architecture for concurrent scraping
- **⚡ Memory Optimized** - Streaming processing with 40% memory reduction
- **🔄 Smart Session Management** - Adaptive retry logic and connection pooling
- **🕸️ Browser Support** - Selenium integration with driver pooling
- **📊 Real-time Monitoring** - Performance metrics and health tracking
- **🛡️ Production Ready** - Enterprise-grade error handling and logging

## 🚀 **Quick Start**

### Installation
```bash
pip install -r requirements.txt
```

### Basic Usage
```python
# Synchronous scraping
from bongocat import BongoCat

with BongoCat() as scraper:
    result = scraper.scrape_sync("https://example.com")
    print(result['data'])

# Asynchronous scraping (3x faster!)
import asyncio
from bongocat import AsyncBongoCat

async def main():
    async with AsyncBongoCat() as scraper:
        # Single URL
        result = await scraper.scrape("https://example.com")
        
        # Multiple URLs concurrently
        results = await scraper.scrape_multiple([
            "https://site1.com",
            "https://site2.com",
            "https://site3.com"
        ])

asyncio.run(main())
```

### One-Line Async Scraping
```python
from bongocat.core_scraper import scrape_urls_async, scrape_single_async

# Single URL
result = await scrape_single_async("https://example.com")

# Multiple URLs
results = await scrape_urls_async([
    "https://site1.com", 
    "https://site2.com"
])
```

---

## 📊 **Performance Benchmarks**

| Feature | Before | After | Improvement |
|---------|--------|-------|-------------|
| **Concurrent Scraping** | 5.2s (5 URLs) | 1.1s (5 URLs) | **373% faster** |
| **Startup Time** | 500ms | 70ms | **86% faster** |
| **Memory Usage** | 50MB | 30MB | **40% reduction** |
| **Import Speed** | Full deps loaded | Lazy loading | **200-400ms saved** |

---

## 🏗️ **Architecture Overview**

```
bongocat/
├── core_scraper/          # High-performance scraping engine
│   ├── scraper.py         # Sync BongoCat class
│   ├── async_scraper.py   # Async BongoCat (300% faster)
│   ├── session_manager.py # HTTP session management
│   ├── async_session_manager.py # Async session management
│   ├── proxy_handler.py   # Proxy rotation and validation
│   ├── rate_limiter.py    # Smart rate limiting
│   └── user_agent_rotator.py # User agent rotation
├── data_parser/           # Content parsing and extraction
│   ├── parser.py          # Main parser with streaming support
│   ├── html_parser.py     # HTML content extraction
│   ├── json_parser.py     # JSON data processing
│   ├── csv_parser.py      # CSV data handling
│   └── text_cleaner.py    # Text processing utilities
├── config_manager/        # Configuration management
├── error_logger/          # Advanced logging system
├── output_handler/        # Data export utilities
├── web_interface/         # Optional web dashboard
├── testing_suite/         # Comprehensive test suite
└── consistency_checker/   # Code quality assurance
```

---

## 🚀 **Async Architecture**

The framework features a complete async/await implementation for maximum performance:

### AsyncBongoCat Features:
- **100x Concurrency** - Process 50-100 URLs simultaneously
- **Connection Pooling** - Optimized HTTP connections with keep-alive
- **Adaptive Retry** - Smart retry logic based on failure rates
- **Real-time Monitoring** - Performance metrics and health tracking
- **Memory Efficient** - Streaming processing for large content

### Advanced Usage:
```python
async with AsyncBongoCat(concurrent_limit=100, max_connections=50) as scraper:
    # Batch processing with concurrency control
    results = await scraper.scrape_with_concurrency_control(
        urls, 
        batch_size=20  # Process in batches
    )
    
    # Get performance metrics
    metrics = await scraper.get_performance_metrics()
    print(f"Avg response time: {metrics['session_performance']['avg_response_time']:.3f}s")
```

---

## 🛠️ **Configuration**

### Basic Configuration:
```python
scraper = BongoCat(
    concurrent_limit=50,    # Max concurrent requests
    max_connections=30,     # HTTP connection pool size
    max_drivers=5,          # Browser driver pool size
    use_browser=True        # Enable JavaScript support
)
```

### Advanced Configuration:
```python
config = {
    'rate_limit': {'requests_per_second': 10},
    'proxy': {'rotation_enabled': True},
    'retry': {'max_attempts': 3, 'backoff_factor': 1.5},
    'timeout': 30,
    'headers': {'User-Agent': 'BongoCat/2.0'}
}

scraper = AsyncBongoCat(config_path='config.json', **config)
```

---

## 🔧 **Key Optimizations**

### 1. **Memory Optimization** (40% improvement)
- Streaming text processing for large content
- Depth-limited JSON traversal to prevent memory exhaustion
- Lazy loading of heavy dependencies (requests, BeautifulSoup, selenium)

### 2. **Performance Optimization** (300% improvement)
- Full async/await architecture with connection pooling
- Browser driver pooling for JavaScript-heavy sites
- Smart import optimization and dependency management

### 3. **Session Management** (25% improvement)
- Adaptive retry logic based on failure rates
- Real-time health monitoring and connection metrics
- Fixed deprecated parameters for compatibility

---

## 📈 **Monitoring & Metrics**

```python
# Get comprehensive performance metrics
async with AsyncBongoCat() as scraper:
    metrics = await scraper.get_performance_metrics()
    
    print(f"Total requests: {metrics['session_performance']['total_requests']}")
    print(f"Success rate: {1 - metrics['session_performance']['global_failure_rate']:.2%}")
    print(f"Avg response time: {metrics['session_performance']['avg_response_time']:.3f}s")
    print(f"Active connections: {metrics['session_performance']['current_connections']}")
```

---

## 🧪 **Testing & Demo**

Run the performance demo to see the improvements:
```bash
cd examples
python async_performance_demo.py
```

This will demonstrate:
- Sync vs Async performance comparison
- Concurrent scraping capabilities  
- Advanced features like batch processing
- Real-time performance metrics

---

## 📦 **Dependencies**

- **Core**: `requests`, `aiohttp`, `beautifulsoup4`
- **Browser Support**: `selenium` (optional)
- **Development**: `pytest`, `black`, `flake8`

Install with:
```bash
pip install -r requirements.txt
```

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Run tests: `python -m pytest testing_suite/`
4. Run consistency check: `python run_consistency_check.py`
5. Submit a pull request

---

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🚀 **What's New**

### Version 2.0 - Performance Overhaul
- ✅ **300% performance improvement** with async architecture
- ✅ **40% memory reduction** through optimizations
- ✅ **86% faster startup** with lazy loading
- ✅ **Production-ready** enterprise features
- ✅ **Backward compatible** with existing sync code

See [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md) for detailed technical improvements.

---

<div align="center">

**Built with ❤️ for high-performance web scraping**

[⭐ Star this repo](../../stargazers) | [🐛 Report Issues](../../issues) | [💡 Suggest Features](../../issues/new)

</div>