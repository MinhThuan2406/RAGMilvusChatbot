"""
Tests for the monitoring and metrics system.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from app.core.metrics import MetricsCollector, metrics_collector, system_metrics_collector
from app.core.tracing import TracingManager, tracing_manager
from app.core.alerting import AlertManager, AlertSeverity, AlertChannel, alert_manager
from app.presentation.api.monitoring import router


class TestMetricsCollector:
    """Test the metrics collector."""
    
    def test_metrics_collector_initialization(self):
        """Test metrics collector initialization."""
        collector = MetricsCollector()
        assert collector.registry is not None
        assert collector.request_total is not None
        assert collector.llm_requests_total is not None
        assert collector.embedding_requests_total is not None
    
    def test_record_request(self):
        """Test recording request metrics."""
        collector = MetricsCollector()
        collector.record_request("GET", "/api/chat", 200, 1.5)
        
        # Check that metrics were recorded
        metrics = collector.get_metrics()
        assert "rag_requests_total" in metrics
        assert "rag_request_duration_seconds" in metrics
    
    def test_record_llm_request(self):
        """Test recording LLM request metrics."""
        collector = MetricsCollector()
        tokens_used = {"input": 100, "output": 50}
        collector.record_llm_request("openai", "gpt-4", "success", 2.0, tokens_used)
        
        metrics = collector.get_metrics()
        assert "llm_requests_total" in metrics
        assert "llm_response_time_seconds" in metrics
        assert "llm_tokens_used_total" in metrics
    
    def test_record_embedding_request(self):
        """Test recording embedding request metrics."""
        collector = MetricsCollector()
        collector.record_embedding_request("openai", "text-embedding-ada-002", "success", 0.5)
        
        metrics = collector.get_metrics()
        assert "embedding_requests_total" in metrics
        assert "embedding_response_time_seconds" in metrics
    
    def test_record_vector_db_operation(self):
        """Test recording vector database operation metrics."""
        collector = MetricsCollector()
        collector.record_vector_db_operation("search", "success", 0.1)
        
        metrics = collector.get_metrics()
        assert "vector_db_operations_total" in metrics
        assert "vector_db_operation_duration_seconds" in metrics
    
    def test_record_rag_metrics(self):
        """Test recording RAG-specific metrics."""
        collector = MetricsCollector()
        collector.record_rag_metrics(1000, [0.8, 0.7, 0.6], 3, "default")
        
        metrics = collector.get_metrics()
        assert "rag_context_length_chars" in metrics
        assert "rag_similarity_score" in metrics
        assert "rag_documents_retrieved_count" in metrics
    
    def test_record_error(self):
        """Test recording error metrics."""
        collector = MetricsCollector()
        collector.record_error("api_error", "chat_controller")
        
        metrics = collector.get_metrics()
        assert "errors_total" in metrics
    
    def test_record_circuit_breaker(self):
        """Test recording circuit breaker metrics."""
        collector = MetricsCollector()
        collector.record_circuit_breaker("openai", 1, 5)
        
        metrics = collector.get_metrics()
        assert "circuit_breaker_state" in metrics
        assert "circuit_breaker_failures_total" in metrics
    
    def test_update_system_metrics(self):
        """Test updating system metrics."""
        collector = MetricsCollector()
        collector.update_system_metrics(
            active_connections={"http": 10, "websocket": 5},
            memory_usage={"total": 8589934592, "used": 4294967296},
            cpu_usage=25.5
        )
        
        metrics = collector.get_metrics()
        assert "active_connections" in metrics
        assert "memory_usage_bytes" in metrics
        assert "cpu_usage_percent" in metrics


class TestTracingManager:
    """Test the tracing manager."""
    
    def test_tracing_manager_initialization(self):
        """Test tracing manager initialization."""
        manager = TracingManager("test-service", "test")
        assert manager.service_name == "test-service"
        assert manager.environment == "test"
    
    @pytest.mark.asyncio
    async def test_trace_function_decorator(self):
        """Test the trace function decorator."""
        manager = TracingManager()
        
        @manager.trace_function("test_operation")
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
    
    def test_trace_operation_context_manager(self):
        """Test the trace operation context manager."""
        manager = TracingManager()
        
        with manager.trace_operation("test_operation") as span:
            assert span is not None
    
    def test_add_event(self):
        """Test adding events to traces."""
        manager = TracingManager()
        
        with manager.trace_operation("test_operation") as span:
            manager.add_event("test_event", {"key": "value"})
            # In a real scenario, this would add an event to the span
    
    def test_set_attribute(self):
        """Test setting attributes on traces."""
        manager = TracingManager()
        
        with manager.trace_operation("test_operation") as span:
            manager.set_attribute("test_key", "test_value")
            # In a real scenario, this would set an attribute on the span


class TestAlertManager:
    """Test the alert manager."""
    
    def test_alert_manager_initialization(self):
        """Test alert manager initialization."""
        manager = AlertManager()
        assert len(manager.alerts) == 0
        assert len(manager.rules) > 0  # Should have default rules
        assert len(manager.notifiers) > 0  # Should have default notifiers
    
    def test_create_alert(self):
        """Test creating an alert."""
        manager = AlertManager()
        alert = manager.create_alert(
            "Test Alert",
            "This is a test alert",
            AlertSeverity.WARNING,
            "test_component"
        )
        
        assert alert.title == "Test Alert"
        assert alert.message == "This is a test alert"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.component == "test_component"
        assert alert.acknowledged == False
        assert len(manager.alerts) == 1
    
    @pytest.mark.asyncio
    async def test_send_alert(self):
        """Test sending an alert."""
        manager = AlertManager()
        alert = manager.create_alert(
            "Test Alert",
            "This is a test alert",
            AlertSeverity.INFO,
            "test_component"
        )
        
        # Mock the notifier to avoid actual sending
        mock_notifier = AsyncMock()
        manager.notifiers[AlertChannel.LOG] = mock_notifier
        
        await manager.send_alert(alert, [AlertChannel.LOG])
        
        mock_notifier.assert_called_once_with(alert)
    
    def test_get_alerts_with_filtering(self):
        """Test getting alerts with filtering."""
        manager = AlertManager()
        
        # Create test alerts
        alert1 = manager.create_alert("Alert 1", "Message 1", AlertSeverity.ERROR, "component1")
        alert2 = manager.create_alert("Alert 2", "Message 2", AlertSeverity.WARNING, "component2")
        alert3 = manager.create_alert("Alert 3", "Message 3", AlertSeverity.ERROR, "component1")
        
        # Test filtering by severity
        error_alerts = manager.get_alerts(severity=AlertSeverity.ERROR)
        assert len(error_alerts) == 2
        
        # Test filtering by component
        component1_alerts = manager.get_alerts(component="component1")
        assert len(component1_alerts) == 2
        
        # Test filtering by both
        filtered_alerts = manager.get_alerts(severity=AlertSeverity.ERROR, component="component1")
        assert len(filtered_alerts) == 2
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        manager = AlertManager()
        alert = manager.create_alert("Test Alert", "Message", AlertSeverity.WARNING, "test")
        
        assert alert.acknowledged == False
        
        manager.acknowledge_alert(alert.id, "test_user")
        
        assert alert.acknowledged == True
        assert alert.acknowledged_by == "test_user"
        assert alert.acknowledged_at is not None
    
    def test_clear_old_alerts(self):
        """Test clearing old alerts."""
        manager = AlertManager()
        
        # Create an old alert (simulate by setting timestamp)
        alert = manager.create_alert("Old Alert", "Message", AlertSeverity.WARNING, "test")
        alert.timestamp = datetime.now() - timedelta(days=31)  # 31 days old
        
        # Create a recent alert
        recent_alert = manager.create_alert("Recent Alert", "Message", AlertSeverity.WARNING, "test")
        
        initial_count = len(manager.alerts)
        manager.clear_old_alerts(days=30)
        final_count = len(manager.alerts)
        
        assert final_count == 1  # Only recent alert should remain
        assert initial_count - final_count == 1
    
    @pytest.mark.asyncio
    async def test_check_rules(self):
        """Test checking alert rules."""
        manager = AlertManager()
        
        # Mock a rule condition to return True
        mock_rule = Mock()
        mock_rule.name = "test_rule"
        mock_rule.condition = Mock(return_value=True)
        mock_rule.severity = AlertSeverity.WARNING
        mock_rule.channels = [AlertChannel.LOG]
        mock_rule.cooldown_minutes = 5
        mock_rule.should_trigger = Mock(return_value=True)
        mock_rule.last_triggered = None
        
        manager.rules = [mock_rule]
        
        # Mock the send_alert method
        with patch.object(manager, 'send_alert', new_callable=AsyncMock) as mock_send:
            await manager.check_rules()
            
            mock_send.assert_called_once()
            assert mock_rule.last_triggered is not None


class TestMonitoringAPI:
    """Test the monitoring API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, client):
        """Test getting metrics endpoint."""
        response = await client.get("/api/monitoring/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/api/monitoring/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "components" in data
    
    @pytest.mark.asyncio
    async def test_get_alerts(self, client):
        """Test getting alerts endpoint."""
        response = await client.get("/api/monitoring/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        assert "total" in data
        assert "active" in data
    
    @pytest.mark.asyncio
    async def test_get_alerts_with_filters(self, client):
        """Test getting alerts with filters."""
        response = await client.get("/api/monitoring/alerts?severity=warning&limit=10")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, client):
        """Test acknowledging an alert."""
        # First create an alert
        alert = alert_manager.create_alert("Test Alert", "Message", AlertSeverity.WARNING, "test")
        
        response = await client.post(f"/api/monitoring/alerts/{alert.id}/acknowledge")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_test_alert(self, client):
        """Test sending a test alert."""
        response = await client.post(
            "/api/monitoring/alerts/test",
            params={
                "title": "Test Alert",
                "message": "Test message",
                "severity": "info",
                "component": "test"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "alert_id" in data
    
    @pytest.mark.asyncio
    async def test_get_dashboard_data(self, client):
        """Test getting dashboard data."""
        response = await client.get("/api/monitoring/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "system" in data
        assert "alerts" in data
        assert "metrics" in data
        assert "status" in data
    
    @pytest.mark.asyncio
    async def test_get_trace_info(self, client):
        """Test getting trace information."""
        response = await client.get("/api/monitoring/traces")
        assert response.status_code == 200
        
        data = response.json()
        assert "enabled" in data
        assert "service_name" in data
        assert "environment" in data
    
    @pytest.mark.asyncio
    async def test_system_metrics_control(self, client):
        """Test system metrics control endpoints."""
        # Test start
        response = await client.post("/api/monitoring/metrics/system/start")
        assert response.status_code == 200
        
        # Test status
        response = await client.get("/api/monitoring/metrics/system/status")
        assert response.status_code == 200
        
        # Test stop
        response = await client.post("/api/monitoring/metrics/system/stop")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_clear_old_alerts(self, client):
        """Test clearing old alerts."""
        response = await client.delete("/api/monitoring/alerts/clear?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "cleared_count" in data
        assert "remaining_count" in data


class TestSystemMetricsCollector:
    """Test the system metrics collector."""
    
    def test_system_metrics_collector_initialization(self):
        """Test system metrics collector initialization."""
        collector = system_metrics_collector
        assert collector._running == False
        assert collector._thread is None
    
    def test_start_stop_system_metrics(self):
        """Test starting and stopping system metrics collection."""
        collector = system_metrics_collector
        
        # Start collection
        collector.start()
        assert collector._running == True
        assert collector._thread is not None
        assert collector._thread.is_alive()
        
        # Stop collection
        collector.stop()
        assert collector._running == False
        # Give thread time to stop
        time.sleep(0.1)
        assert not collector._thread.is_alive()


# Integration tests
class TestMonitoringIntegration:
    """Integration tests for the monitoring system."""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_workflow(self):
        """Test a complete monitoring workflow."""
        # 1. Create an alert
        alert = alert_manager.create_alert(
            "Integration Test Alert",
            "This is an integration test",
            AlertSeverity.ERROR,
            "integration_test"
        )
        
        # 2. Record some metrics
        metrics_collector.record_request("POST", "/api/chat", 200, 1.5)
        metrics_collector.record_llm_request("openai", "gpt-4", "success", 2.0)
        metrics_collector.record_error("test_error", "integration_test")
        
        # 3. Verify metrics were recorded
        metrics = metrics_collector.get_metrics()
        assert "rag_requests_total" in metrics
        assert "llm_requests_total" in metrics
        assert "errors_total" in metrics
        
        # 4. Verify alert was created
        alerts = alert_manager.get_alerts()
        assert len(alerts) > 0
        assert any(a.title == "Integration Test Alert" for a in alerts)
        
        # 5. Acknowledge the alert
        alert_manager.acknowledge_alert(alert.id, "integration_test")
        assert alert.acknowledged == True
    
    def test_metrics_and_tracing_integration(self):
        """Test integration between metrics and tracing."""
        # This would test how metrics and tracing work together
        # For now, just verify both systems are available
        assert metrics_collector is not None
        assert tracing_manager is not None
        assert alert_manager is not None 