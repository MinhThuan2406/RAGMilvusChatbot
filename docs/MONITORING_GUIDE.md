# 📊 Monitoring & Observability Guide

## Overview

The RAG Chatbot now includes a comprehensive monitoring and observability system that provides:

- **📈 Prometheus Metrics Collection**
- **🔍 Distributed Tracing with OpenTelemetry**
- **🚨 Alerting and Notification System**
- **📊 Performance Dashboards**

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │   Monitoring    │    │   Observability │
│                 │    │   System        │    │   Tools         │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • FastAPI       │    │ • Metrics       │    │ • Prometheus    │
│ • RAG Service   │    │ • Tracing       │    │ • Grafana       │
│ • LLM Clients   │    │ • Alerting      │    │ • Jaeger        │
│ • Vector DB     │    │ • Logging       │    │ • Streamlit     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📈 Metrics Collection

### Prometheus Metrics

The system collects comprehensive metrics in Prometheus format:

#### Request Metrics
- `rag_requests_total` - Total number of requests
- `rag_request_duration_seconds` - Request duration

#### LLM Metrics
- `llm_requests_total` - Total LLM requests
- `llm_response_time_seconds` - LLM response time
- `llm_tokens_used_total` - Token usage

#### Embedding Metrics
- `embedding_requests_total` - Total embedding requests
- `embedding_response_time_seconds` - Embedding response time

#### Vector Database Metrics
- `vector_db_operations_total` - Vector DB operations
- `vector_db_operation_duration_seconds` - Operation duration

#### RAG-Specific Metrics
- `rag_context_length_chars` - Context length
- `rag_similarity_score` - Similarity scores
- `rag_documents_retrieved_count` - Documents retrieved

#### System Metrics
- `active_connections` - Active connections
- `memory_usage_bytes` - Memory usage
- `cpu_usage_percent` - CPU usage

#### Error Metrics
- `errors_total` - Total errors
- `circuit_breaker_state` - Circuit breaker state
- `circuit_breaker_failures_total` - Circuit breaker failures

### Usage Examples

```python
from app.core.metrics import metrics_collector, timed_operation

# Record a request
metrics_collector.record_request("POST", "/api/chat", 200, 1.5)

# Record LLM request with tokens
metrics_collector.record_llm_request(
    "openai", "gpt-4", "success", 2.0, 
    {"input": 100, "output": 50}
)

# Use context manager for timing
with timed_operation("vector_db", operation="search"):
    # Your vector DB operation here
    pass
```

## 🔍 Distributed Tracing

### OpenTelemetry Integration

The system supports distributed tracing using OpenTelemetry:

#### Features
- **Automatic instrumentation** of FastAPI endpoints
- **Custom spans** for business operations
- **Multiple exporters** (Console, Jaeger, OTLP)
- **Correlation IDs** for request tracking

#### Usage Examples

```python
from app.core.tracing import trace_operation, add_trace_event, set_trace_attribute

# Trace a function
@trace_operation("llm_call", provider="openai", model="gpt-4")
async def generate_response(prompt: str):
    add_trace_event("prompt_received", {"length": len(prompt)})
    set_trace_attribute("model", "gpt-4")
    # Your LLM call here
    return response

# Use context manager
with trace_operation("rag_query", query_length=len(query)):
    # Your RAG operation here
    pass
```

#### Configuration

Set these environment variables for tracing:

```bash
# Jaeger tracing
JAEGER_HOST=localhost
JAEGER_PORT=14268

# OTLP tracing (for cloud platforms)
OTLP_ENDPOINT=http://localhost:4317
```

## 🚨 Alerting System

### Alert Types

The system includes several alert types:

#### Severity Levels
- **INFO** - Informational messages
- **WARNING** - Warning conditions
- **ERROR** - Error conditions
- **CRITICAL** - Critical failures

#### Default Alert Rules
- **High Error Rate** - Monitors error frequency
- **High Response Time** - Monitors performance
- **Circuit Breaker Open** - Monitors service health
- **LLM Service Unavailable** - Monitors LLM providers
- **Vector Database Issues** - Monitors vector DB health

### Notification Channels

#### Supported Channels
- **Email** - SMTP-based notifications
- **Webhook** - HTTP POST notifications
- **Slack** - Slack webhook integration
- **Discord** - Discord webhook integration
- **Log** - Application logging

#### Configuration

```bash
# Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=alerts@yourcompany.com

# Webhook notifications
WEBHOOK_URL=https://your-webhook-endpoint.com/alerts

# Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Discord notifications
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK
```

### Usage Examples

```python
from app.core.alerting import send_alert, AlertSeverity, AlertChannel

# Send an alert
await send_alert(
    title="LLM Service Down",
    message="OpenAI API is not responding",
    severity=AlertSeverity.CRITICAL,
    component="llm_service",
    channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
)
```

## 📊 Monitoring Dashboard

### Streamlit Dashboard

A comprehensive monitoring dashboard is available at `streamlit/monitoring_dashboard.py`.

#### Features
- **Real-time metrics** display
- **Alert management** interface
- **System health** monitoring
- **Circuit breaker** status
- **Performance charts** and graphs

#### Running the Dashboard

```bash
# Install Streamlit dependencies
pip install streamlit plotly pandas

# Run the dashboard
cd streamlit
streamlit run monitoring_dashboard.py
```

#### Dashboard Sections

1. **Health Status** - Overall system health
2. **System Metrics** - CPU, memory, performance
3. **Alerts** - Active and historical alerts
4. **Circuit Breakers** - Service health status
5. **Metrics** - Raw Prometheus metrics
6. **Traces** - Distributed tracing information

## 🔧 API Endpoints

### Monitoring Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/monitoring/metrics` | GET | Prometheus metrics |
| `/api/monitoring/health` | GET | Health check |
| `/api/monitoring/alerts` | GET | Get alerts |
| `/api/monitoring/alerts/{id}/acknowledge` | POST | Acknowledge alert |
| `/api/monitoring/alerts/test` | POST | Send test alert |
| `/api/monitoring/dashboard` | GET | Dashboard data |
| `/api/monitoring/traces` | GET | Tracing info |
| `/api/monitoring/metrics/system/start` | POST | Start system metrics |
| `/api/monitoring/metrics/system/stop` | POST | Stop system metrics |
| `/api/monitoring/metrics/system/status` | GET | System metrics status |
| `/api/monitoring/alerts/clear` | DELETE | Clear old alerts |

### Example API Usage

```bash
# Get metrics
curl http://localhost:8000/api/monitoring/metrics

# Get health status
curl http://localhost:8000/api/monitoring/health

# Get alerts
curl http://localhost:8000/api/monitoring/alerts

# Send test alert
curl -X POST "http://localhost:8000/api/monitoring/alerts/test" \
  -d "title=Test Alert&message=Test message&severity=warning&component=test"
```

## 🧪 Testing

### Running Tests

```bash
# Run monitoring tests
pytest backend/tests/test_monitoring.py -v

# Run with coverage
pytest backend/tests/test_monitoring.py --cov=app.core.metrics --cov=app.core.tracing --cov=app.core.alerting
```

### Test Categories

1. **Metrics Tests** - Prometheus metrics collection
2. **Tracing Tests** - OpenTelemetry integration
3. **Alerting Tests** - Alert management
4. **API Tests** - Monitoring endpoints
5. **Integration Tests** - End-to-end workflows

## 🚀 Deployment

### Production Setup

#### 1. Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rag-chatbot'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/monitoring/metrics'
```

#### 2. Grafana Dashboard

Import the provided Grafana dashboard configuration for visualization.

#### 3. Alerting Rules

Configure Prometheus alerting rules:

```yaml
groups:
  - name: rag-chatbot
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
```

#### 4. Jaeger Setup

```yaml
# docker-compose.yml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
```

### Environment Variables

```bash
# Monitoring configuration
ENVIRONMENT=production
SERVICE_NAME=rag-chatbot

# Tracing
JAEGER_HOST=jaeger
JAEGER_PORT=14268

# Alerting
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=alerts@yourcompany.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=alerts@yourcompany.com

# Optional: Cloud observability
OTLP_ENDPOINT=https://your-observability-platform.com:4317
```

## 📋 Best Practices

### 1. Metrics Collection

- **Use meaningful labels** for metrics
- **Avoid high cardinality** labels
- **Set appropriate buckets** for histograms
- **Document your metrics**

### 2. Tracing

- **Add context** to spans
- **Use consistent naming** for operations
- **Correlate traces** with logs
- **Set appropriate sampling** rates

### 3. Alerting

- **Set appropriate thresholds** for alerts
- **Use cooldown periods** to prevent alert storms
- **Acknowledge alerts** promptly
- **Review and tune** alert rules regularly

### 4. Performance

- **Monitor resource usage** (CPU, memory, disk)
- **Track response times** for all endpoints
- **Monitor external dependencies** (LLM, vector DB)
- **Set up capacity planning** based on metrics

## 🔍 Troubleshooting

### Common Issues

#### 1. Metrics Not Appearing

```bash
# Check if metrics endpoint is working
curl http://localhost:8000/api/monitoring/metrics

# Check Prometheus configuration
# Verify scrape interval and targets
```

#### 2. Alerts Not Sending

```bash
# Check alert configuration
# Verify SMTP/webhook settings
# Check logs for alert errors
```

#### 3. Tracing Not Working

```bash
# Check OpenTelemetry installation
pip install opentelemetry-api opentelemetry-sdk

# Verify Jaeger is running
curl http://localhost:16686/api/services
```

#### 4. Dashboard Issues

```bash
# Check Streamlit installation
pip install streamlit plotly pandas

# Verify API connectivity
curl http://localhost:8000/api/monitoring/health
```

### Debug Commands

```bash
# Check system metrics
curl http://localhost:8000/api/monitoring/metrics/system/status

# Test alert system
curl -X POST "http://localhost:8000/api/monitoring/alerts/test" \
  -d "title=Debug Alert&message=Testing alert system&severity=info&component=debug"

# Get trace information
curl http://localhost:8000/api/monitoring/traces
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🤝 Contributing

When adding new monitoring features:

1. **Add metrics** for new functionality
2. **Create tests** for monitoring components
3. **Update documentation** with new features
4. **Follow naming conventions** for consistency
5. **Add appropriate alerts** for critical paths 