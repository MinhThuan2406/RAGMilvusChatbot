"""
Monitoring and metrics API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from app.core.metrics import metrics_collector, system_metrics_collector
from app.core.tracing import tracing_manager
from app.core.alerting import alert_manager, AlertSeverity, AlertChannel, get_active_alerts
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics."""
    try:
        metrics = metrics_collector.get_metrics()
        return Response(content=metrics, media_type="text/plain")
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get("/health")
async def health_check():
    """Comprehensive health check."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {}
    }
    
    # Check system metrics
    try:
        import psutil
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent()
        
        health_status["components"]["system"] = {
            "status": "healthy",
            "memory_usage_percent": memory.percent,
            "cpu_usage_percent": cpu_percent,
            "memory_available_gb": round(memory.available / (1024**3), 2)
        }
    except Exception as e:
        health_status["components"]["system"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check if any component is unhealthy
    if any(comp.get("status") == "unhealthy" for comp in health_status["components"].values()):
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    component: Optional[str] = None,
    limit: int = 50
):
    """Get alerts with optional filtering."""
    try:
        # Convert severity string to enum
        severity_enum = None
        if severity:
            try:
                severity_enum = AlertSeverity(severity.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        alerts = alert_manager.get_alerts(severity_enum, component, limit)
        
        # Convert to serializable format
        alert_data = []
        for alert in alerts:
            alert_data.append({
                "id": alert.id,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity.value,
                "component": alert.component,
                "timestamp": alert.timestamp.isoformat(),
                "acknowledged": alert.acknowledged,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "metadata": alert.metadata
            })
        
        return {
            "alerts": alert_data,
            "total": len(alert_data),
            "active": len([a for a in alerts if not a.acknowledged])
        }
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, acknowledged_by: str = "system"):
    """Acknowledge an alert."""
    try:
        alert_manager.acknowledge_alert(alert_id, acknowledged_by)
        return {"message": "Alert acknowledged successfully"}
    except Exception as e:
        logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge alert")


@router.post("/alerts/test")
async def test_alert(
    title: str = "Test Alert",
    message: str = "This is a test alert",
    severity: str = "info",
    component: str = "test",
    channels: Optional[List[str]] = None
):
    """Send a test alert."""
    try:
        # Convert severity string to enum
        try:
            severity_enum = AlertSeverity(severity.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        # Convert channel strings to enums
        channel_enums = []
        if channels:
            for channel in channels:
                try:
                    channel_enums.append(AlertChannel(channel.lower()))
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid channel: {channel}")
        
        # Send test alert
        alert = alert_manager.create_alert(
            title=title,
            message=message,
            severity=severity_enum,
            component=component,
            metadata={"test": True}
        )
        
        await alert_manager.send_alert(alert, channel_enums)
        
        return {
            "message": "Test alert sent successfully",
            "alert_id": alert.id
        }
    except Exception as e:
        logger.error(f"Failed to send test alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test alert")


@router.get("/dashboard")
async def get_dashboard_data():
    """Get dashboard data for monitoring UI."""
    try:
        # Get system metrics
        import psutil
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent()
        
        # Get recent alerts
        recent_alerts = alert_manager.get_alerts(limit=10)
        active_alerts = [a for a in recent_alerts if not a.acknowledged]
        
        # Calculate alert statistics
        alert_stats = {
            "total": len(recent_alerts),
            "active": len(active_alerts),
            "by_severity": {},
            "by_component": {}
        }
        
        for alert in recent_alerts:
            # Count by severity
            severity = alert.severity.value
            alert_stats["by_severity"][severity] = alert_stats["by_severity"].get(severity, 0) + 1
            
            # Count by component
            component = alert.component
            alert_stats["by_component"][component] = alert_stats["by_component"].get(component, 0) + 1
        
        # Get metrics summary (this would integrate with actual metrics)
        metrics_summary = {
            "requests_per_minute": 0,  # Would be calculated from metrics
            "average_response_time": 0,  # Would be calculated from metrics
            "error_rate": 0,  # Would be calculated from metrics
            "llm_requests": 0,  # Would be calculated from metrics
            "embedding_requests": 0,  # Would be calculated from metrics
            "vector_db_operations": 0  # Would be calculated from metrics
        }
        
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2)
            },
            "alerts": alert_stats,
            "metrics": metrics_summary,
            "status": "healthy" if len(active_alerts) == 0 else "warning"
        }
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")


@router.get("/traces")
async def get_trace_info():
    """Get tracing information."""
    try:
        trace_info = {
            "enabled": tracing_manager.tracer is not None,
            "service_name": tracing_manager.service_name,
            "environment": tracing_manager.environment,
            "exporters": []
        }
        
        # Add exporter information if available
        if tracing_manager.tracer_provider:
            # This would provide more detailed exporter info
            trace_info["exporters"] = ["console", "jaeger"]  # Simplified
        
        return trace_info
    except Exception as e:
        logger.error(f"Failed to get trace info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trace information")


@router.post("/metrics/system/start")
async def start_system_metrics():
    """Start collecting system metrics."""
    try:
        system_metrics_collector.start()
        return {"message": "System metrics collection started"}
    except Exception as e:
        logger.error(f"Failed to start system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to start system metrics")


@router.post("/metrics/system/stop")
async def stop_system_metrics():
    """Stop collecting system metrics."""
    try:
        system_metrics_collector.stop()
        return {"message": "System metrics collection stopped"}
    except Exception as e:
        logger.error(f"Failed to stop system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop system metrics")


@router.get("/metrics/system/status")
async def get_system_metrics_status():
    """Get system metrics collection status."""
    try:
        return {
            "running": system_metrics_collector._running,
            "thread_alive": system_metrics_collector._thread.is_alive() if system_metrics_collector._thread else False
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics status")


@router.delete("/alerts/clear")
async def clear_old_alerts(days: int = 30):
    """Clear alerts older than specified days."""
    try:
        old_count = len(alert_manager.alerts)
        alert_manager.clear_old_alerts(days)
        new_count = len(alert_manager.alerts)
        cleared_count = old_count - new_count
        
        return {
            "message": f"Cleared {cleared_count} alerts older than {days} days",
            "cleared_count": cleared_count,
            "remaining_count": new_count
        }
    except Exception as e:
        logger.error(f"Failed to clear old alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear old alerts") 