import structlog
import logging
import sys
from typing import Any, Dict
# Simple hardcoded settings for demo
LOG_LEVEL = "INFO"
LOG_FORMAT = "console"

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if LOG_FORMAT == "json"
        else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure standard logging
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=getattr(logging, LOG_LEVEL.upper()),
)

logger = structlog.get_logger()


class MetricsCollector:
    """Simple metrics collector for monitoring."""
    
    def __init__(self):
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        if name not in self.counters:
            self.counters[name] = {}
        
        tag_key = str(tags) if tags else "default"
        if tag_key not in self.counters[name]:
            self.counters[name][tag_key] = 0
        
        self.counters[name][tag_key] += value
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        if name not in self.gauges:
            self.gauges[name] = {}
        
        tag_key = str(tags) if tags else "default"
        self.gauges[name][tag_key] = value
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value."""
        if name not in self.histograms:
            self.histograms[name] = {}
        
        tag_key = str(tags) if tags else "default"
        if tag_key not in self.histograms[name]:
            self.histograms[name][tag_key] = []
        
        self.histograms[name][tag_key].append(value)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "counters": self.counters,
            "gauges": self.gauges,
            "histograms": self.histograms
        }


# Global metrics collector
metrics = MetricsCollector()


def log_request(request_id: str, cccd: str, status: str, duration_ms: float = None):
    """Log API request with structured data."""
    log_data = {
        "request_id": request_id,
        "cccd": cccd,
        "status": status,
        "event": "api_request"
    }
    
    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms
    
    logger.info("API request processed", **log_data)
    
    # Update metrics
    metrics.increment_counter("api_requests_total", tags={"status": status})
    if duration_ms is not None:
        metrics.record_histogram("api_request_duration_ms", duration_ms)


def log_scraping_error(request_id: str, cccd: str, error: str):
    """Log scraping error."""
    logger.error("Scraping error", 
                request_id=request_id, 
                cccd=cccd, 
                error=error,
                event="scraping_error")
    
    metrics.increment_counter("scraping_errors_total")


def log_rate_limit_exceeded(api_key_hash: str):
    """Log rate limit exceeded."""
    logger.warning("Rate limit exceeded", 
                  api_key_hash=api_key_hash,
                  event="rate_limit_exceeded")
    
    metrics.increment_counter("rate_limit_exceeded_total")