"""
Distributed tracing with OpenTelemetry for the RAG chatbot.
"""

import os
from typing import Optional, Dict, Any
from contextlib import contextmanager
from functools import wraps
import time

try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor, ConsoleSpanExporter, OTLPSpanExporter
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCExporter
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    print("Warning: OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-httpx opentelemetry-instrumentation-logging opentelemetry-exporter-jaeger opentelemetry-exporter-otlp-proto-grpc")


class TracingManager:
    """Manages distributed tracing for the RAG chatbot."""
    
    def __init__(self, service_name: str = "rag-chatbot", environment: str = "development"):
        self.service_name = service_name
        self.environment = environment
        self.tracer_provider = None
        self.tracer = None
        
        if OPENTELEMETRY_AVAILABLE:
            self._setup_tracing()
    
    def _setup_tracing(self):
        """Initialize OpenTelemetry tracing."""
        # Create resource
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": "1.0.0",
            "deployment.environment": self.environment
        })
        
        # Create tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        
        # Add span processors
        self._add_span_processors()
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
    
    def _add_span_processors(self):
        """Add span processors for different exporters."""
        # Console exporter for development
        if self.environment == "development":
            console_exporter = ConsoleSpanExporter()
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
        
        # Jaeger exporter
        jaeger_host = os.getenv("JAEGER_HOST", "localhost")
        jaeger_port = int(os.getenv("JAEGER_PORT", "14268"))
        
        try:
            jaeger_exporter = JaegerExporter(
                agent_host_name=jaeger_host,
                agent_port=jaeger_port,
            )
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
        except Exception as e:
            print(f"Warning: Could not setup Jaeger exporter: {e}")
        
        # OTLP exporter (for cloud observability platforms)
        otlp_endpoint = os.getenv("OTLP_ENDPOINT")
        if otlp_endpoint:
            try:
                otlp_exporter = GRPCExporter(endpoint=otlp_endpoint)
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter)
                )
            except Exception as e:
                print(f"Warning: Could not setup OTLP exporter: {e}")
    
    def get_tracer(self):
        """Get the tracer instance."""
        return self.tracer if self.tracer else trace.get_tracer(__name__)
    
    def trace_function(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """Decorator to trace function calls."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not OPENTELEMETRY_AVAILABLE:
                    return await func(*args, **kwargs)
                
                tracer = self.get_tracer()
                with tracer.start_as_current_span(
                    operation_name,
                    attributes=attributes or {}
                ) as span:
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not OPENTELEMETRY_AVAILABLE:
                    return func(*args, **kwargs)
                
                tracer = self.get_tracer()
                with tracer.start_as_current_span(
                    operation_name,
                    attributes=attributes or {}
                ) as span:
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
            
            return async_wrapper if hasattr(func, '__await__') else sync_wrapper
        return decorator
    
    @contextmanager
    def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """Context manager for tracing operations."""
        if not OPENTELEMETRY_AVAILABLE:
            yield
            return
        
        tracer = self.get_tracer()
        with tracer.start_as_current_span(
            operation_name,
            attributes=attributes or {}
        ) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to the current span."""
        if not OPENTELEMETRY_AVAILABLE:
            return
        
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.add_event(name, attributes or {})
    
    def set_attribute(self, key: str, value: Any):
        """Set an attribute on the current span."""
        if not OPENTELEMETRY_AVAILABLE:
            return
        
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.set_attribute(key, value)
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application."""
        if not OPENTELEMETRY_AVAILABLE:
            return
        
        try:
            FastAPIInstrumentor.instrument_app(app)
            HTTPXClientInstrumentor().instrument()
            LoggingInstrumentor().instrument()
        except Exception as e:
            print(f"Warning: Could not instrument FastAPI: {e}")
    
    def shutdown(self):
        """Shutdown the tracer provider."""
        if self.tracer_provider:
            self.tracer_provider.shutdown()


# Global tracing manager
tracing_manager = TracingManager()


def trace_operation(operation_name: str, attributes: Optional[Dict[str, Any]] = None):
    """Decorator to trace operations."""
    return tracing_manager.trace_function(operation_name, attributes)


def add_trace_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Add an event to the current trace."""
    tracing_manager.add_event(name, attributes)


def set_trace_attribute(key: str, value: Any):
    """Set an attribute on the current trace."""
    tracing_manager.set_attribute(key, value)


class TraceContext:
    """Context manager for tracing operations with automatic timing."""
    
    def __init__(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        self.operation_name = operation_name
        self.attributes = attributes or {}
        self.start_time = None
        self.span = None
    
    def __enter__(self):
        self.start_time = time.time()
        if OPENTELEMETRY_AVAILABLE:
            self.span = tracing_manager.get_tracer().start_as_current_span(
                self.operation_name,
                attributes=self.attributes
            ).__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if OPENTELEMETRY_AVAILABLE and self.span:
            self.span.set_attribute("duration_seconds", duration)
            if exc_type:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                self.span.record_exception(exc_val)
            else:
                self.span.set_status(Status(StatusCode.OK))
            self.span.__exit__(exc_type, exc_val, exc_tb)
        
        return False  # Don't suppress exceptions


# Convenience functions for common tracing patterns
def trace_llm_call(provider: str, model: str):
    """Trace LLM calls with provider and model information."""
    return trace_operation(
        "llm_call",
        {"provider": provider, "model": model}
    )


def trace_embedding_call(provider: str, model: str):
    """Trace embedding calls with provider and model information."""
    return trace_operation(
        "embedding_call",
        {"provider": provider, "model": model}
    )


def trace_vector_db_operation(operation: str):
    """Trace vector database operations."""
    return trace_operation(
        "vector_db_operation",
        {"operation": operation}
    )


def trace_rag_query(query_length: int):
    """Trace RAG queries with query information."""
    return trace_operation(
        "rag_query",
        {"query_length": query_length}
    )


def trace_file_processing(file_type: str, file_size: int):
    """Trace file processing operations."""
    return trace_operation(
        "file_processing",
        {"file_type": file_type, "file_size": file_size}
    ) 