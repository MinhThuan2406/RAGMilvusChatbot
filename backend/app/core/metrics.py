"""
Prometheus metrics collection for the RAG chatbot.
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess
)
import time
from functools import wraps
from typing import Dict, Any, Optional
import threading
from contextlib import contextmanager


class MetricsCollector:
    """Centralized metrics collection for the RAG chatbot."""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Initialize all metrics."""
        
        # Request metrics
        self.request_total = Counter(
            'rag_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'rag_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # LLM metrics
        self.llm_requests_total = Counter(
            'llm_requests_total',
            'Total number of LLM requests',
            ['provider', 'model', 'status'],
            registry=self.registry
        )
        
        self.llm_response_time = Histogram(
            'llm_response_time_seconds',
            'LLM response time in seconds',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.llm_tokens_used = Counter(
            'llm_tokens_used_total',
            'Total tokens used by LLM',
            ['provider', 'model', 'token_type'],
            registry=self.registry
        )
        
        # Embedding metrics
        self.embedding_requests_total = Counter(
            'embedding_requests_total',
            'Total number of embedding requests',
            ['provider', 'model', 'status'],
            registry=self.registry
        )
        
        self.embedding_response_time = Histogram(
            'embedding_response_time_seconds',
            'Embedding response time in seconds',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # Vector database metrics
        self.vector_db_operations_total = Counter(
            'vector_db_operations_total',
            'Total number of vector database operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.vector_db_operation_duration = Histogram(
            'vector_db_operation_duration_seconds',
            'Vector database operation duration in seconds',
            ['operation'],
            registry=self.registry
        )
        
        # RAG-specific metrics
        self.rag_context_length = Histogram(
            'rag_context_length_chars',
            'Length of RAG context in characters',
            ['source'],
            registry=self.registry
        )
        
        self.rag_similarity_score = Histogram(
            'rag_similarity_score',
            'Similarity scores for retrieved documents',
            ['source'],
            registry=self.registry
        )
        
        self.rag_documents_retrieved = Histogram(
            'rag_documents_retrieved_count',
            'Number of documents retrieved per query',
            ['source'],
            registry=self.registry
        )
        
        # System metrics
        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections',
            ['type'],
            registry=self.registry
        )
        
        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['type'],
            registry=self.registry
        )
        
        self.cpu_usage_percent = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total number of errors',
            ['type', 'component'],
            registry=self.registry
        )
        
        # Circuit breaker metrics
        self.circuit_breaker_state = Gauge(
            'circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['service'],
            registry=self.registry
        )
        
        self.circuit_breaker_failures = Counter(
            'circuit_breaker_failures_total',
            'Total circuit breaker failures',
            ['service'],
            registry=self.registry
        )
        
        # File processing metrics
        self.files_processed_total = Counter(
            'files_processed_total',
            'Total number of files processed',
            ['file_type', 'status'],
            registry=self.registry
        )
        
        self.file_processing_duration = Histogram(
            'file_processing_duration_seconds',
            'File processing duration in seconds',
            ['file_type'],
            registry=self.registry
        )
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics."""
        self.request_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_llm_request(self, provider: str, model: str, status: str, duration: float, 
                          tokens_used: Optional[Dict[str, int]] = None):
        """Record LLM request metrics."""
        self.llm_requests_total.labels(provider=provider, model=model, status=status).inc()
        self.llm_response_time.labels(provider=provider, model=model).observe(duration)
        
        if tokens_used:
            for token_type, count in tokens_used.items():
                self.llm_tokens_used.labels(
                    provider=provider, model=model, token_type=token_type
                ).inc(count)
    
    def record_embedding_request(self, provider: str, model: str, status: str, duration: float):
        """Record embedding request metrics."""
        self.embedding_requests_total.labels(provider=provider, model=model, status=status).inc()
        self.embedding_response_time.labels(provider=provider, model=model).observe(duration)
    
    def record_vector_db_operation(self, operation: str, status: str, duration: float):
        """Record vector database operation metrics."""
        self.vector_db_operations_total.labels(operation=operation, status=status).inc()
        self.vector_db_operation_duration.labels(operation=operation).observe(duration)
    
    def record_rag_metrics(self, context_length: int, similarity_scores: list, 
                          documents_retrieved: int, source: str = "default"):
        """Record RAG-specific metrics."""
        self.rag_context_length.labels(source=source).observe(context_length)
        self.rag_documents_retrieved.labels(source=source).observe(documents_retrieved)
        
        for score in similarity_scores:
            self.rag_similarity_score.labels(source=source).observe(score)
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics."""
        self.errors_total.labels(type=error_type, component=component).inc()
    
    def record_circuit_breaker(self, service: str, state: int, failures: int = 0):
        """Record circuit breaker metrics."""
        self.circuit_breaker_state.labels(service=service).set(state)
        if failures > 0:
            self.circuit_breaker_failures.labels(service=service).inc(failures)
    
    def record_file_processing(self, file_type: str, status: str, duration: float):
        """Record file processing metrics."""
        self.files_processed_total.labels(file_type=file_type, status=status).inc()
        self.file_processing_duration.labels(file_type=file_type).observe(duration)
    
    def update_system_metrics(self, active_connections: Dict[str, int] = None,
                            memory_usage: Dict[str, float] = None,
                            cpu_usage: float = None):
        """Update system metrics."""
        if active_connections:
            for conn_type, count in active_connections.items():
                self.active_connections.labels(type=conn_type).set(count)
        
        if memory_usage:
            for mem_type, usage in memory_usage.items():
                self.memory_usage_bytes.labels(type=mem_type).set(usage)
        
        if cpu_usage is not None:
            self.cpu_usage_percent.set(cpu_usage)
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry)


# Global metrics collector instance
metrics_collector = MetricsCollector()


def metrics_middleware(func):
    """Decorator to automatically record metrics for API endpoints."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        method = "GET"  # Default, should be overridden
        endpoint = func.__name__
        
        try:
            result = await func(*args, **kwargs)
            status = 200
            return result
        except Exception as e:
            status = 500
            metrics_collector.record_error("api_error", endpoint)
            raise
        finally:
            duration = time.time() - start_time
            metrics_collector.record_request(method, endpoint, status, duration)
    
    return wrapper


@contextmanager
def timed_operation(operation: str, **labels):
    """Context manager for timing operations."""
    start_time = time.time()
    try:
        yield
        status = "success"
    except Exception as e:
        status = "error"
        raise
    finally:
        duration = time.time() - start_time
        if operation == "vector_db":
            metrics_collector.record_vector_db_operation(operation, status, duration)
        elif operation == "llm":
            provider = labels.get("provider", "unknown")
            model = labels.get("model", "unknown")
            metrics_collector.record_llm_request(provider, model, status, duration)
        elif operation == "embedding":
            provider = labels.get("provider", "unknown")
            model = labels.get("model", "unknown")
            metrics_collector.record_embedding_request(provider, model, status, duration)
        elif operation == "file_processing":
            file_type = labels.get("file_type", "unknown")
            metrics_collector.record_file_processing(file_type, status, duration)


class SystemMetricsCollector:
    """Collect system-level metrics."""
    
    def __init__(self):
        self._running = False
        self._thread = None
    
    def start(self):
        """Start collecting system metrics."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._collect_metrics, daemon=True)
            self._thread.start()
    
    def stop(self):
        """Stop collecting system metrics."""
        self._running = False
        if self._thread:
            self._thread.join()
    
    def _collect_metrics(self):
        """Collect system metrics in background."""
        import psutil
        
        while self._running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                
                # Update metrics
                metrics_collector.update_system_metrics(
                    memory_usage={
                        "total": memory.total,
                        "available": memory.available,
                        "used": memory.used,
                        "percent": memory.percent
                    },
                    cpu_usage=cpu_percent
                )
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                metrics_collector.record_error("system_metrics_error", "system_collector")
                time.sleep(60)  # Wait longer on error


# Global system metrics collector
system_metrics_collector = SystemMetricsCollector() 