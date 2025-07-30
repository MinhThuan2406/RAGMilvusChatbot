"""
Alerting and notification system for the RAG chatbot.
"""

import asyncio
import smtplib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
import os


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert notification channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    LOG = "log"


@dataclass
class Alert:
    """Alert data structure."""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    component: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class AlertRule:
    """Rule for triggering alerts based on conditions."""
    
    def __init__(self, name: str, condition: Callable, severity: AlertSeverity,
                 channels: List[AlertChannel], cooldown_minutes: int = 5):
        self.name = name
        self.condition = condition
        self.severity = severity
        self.channels = channels
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None
    
    def should_trigger(self) -> bool:
        """Check if alert should be triggered based on cooldown."""
        if self.last_triggered is None:
            return True
        
        cooldown_delta = timedelta(minutes=self.cooldown_minutes)
        return datetime.now() - self.last_triggered > cooldown_delta


class AlertManager:
    """Manages alerting and notifications."""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.rules: List[AlertRule] = []
        self.notifiers: Dict[AlertChannel, Callable] = {}
        self._setup_default_rules()
        self._setup_default_notifiers()
    
    def _setup_default_rules(self):
        """Setup default alert rules."""
        # High error rate
        self.add_rule(AlertRule(
            name="high_error_rate",
            condition=self._check_high_error_rate,
            severity=AlertSeverity.WARNING,
            channels=[AlertChannel.EMAIL, AlertChannel.LOG],
            cooldown_minutes=10
        ))
        
        # High response time
        self.add_rule(AlertRule(
            name="high_response_time",
            condition=self._check_high_response_time,
            severity=AlertSeverity.WARNING,
            channels=[AlertChannel.EMAIL, AlertChannel.LOG],
            cooldown_minutes=5
        ))
        
        # Circuit breaker open
        self.add_rule(AlertRule(
            name="circuit_breaker_open",
            condition=self._check_circuit_breaker_open,
            severity=AlertSeverity.ERROR,
            channels=[AlertChannel.EMAIL, AlertChannel.WEBHOOK, AlertChannel.LOG],
            cooldown_minutes=2
        ))
        
        # LLM service unavailable
        self.add_rule(AlertRule(
            name="llm_service_unavailable",
            condition=self._check_llm_service_unavailable,
            severity=AlertSeverity.CRITICAL,
            channels=[AlertChannel.EMAIL, AlertChannel.WEBHOOK, AlertChannel.SLACK],
            cooldown_minutes=1
        ))
        
        # Vector database issues
        self.add_rule(AlertRule(
            name="vector_db_issues",
            condition=self._check_vector_db_issues,
            severity=AlertSeverity.ERROR,
            channels=[AlertChannel.EMAIL, AlertChannel.LOG],
            cooldown_minutes=5
        ))
    
    def _setup_default_notifiers(self):
        """Setup default notification channels."""
        self.register_notifier(AlertChannel.EMAIL, self._send_email)
        self.register_notifier(AlertChannel.WEBHOOK, self._send_webhook)
        self.register_notifier(AlertChannel.LOG, self._log_alert)
        self.register_notifier(AlertChannel.SLACK, self._send_slack)
        self.register_notifier(AlertChannel.DISCORD, self._send_discord)
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.rules.append(rule)
    
    def register_notifier(self, channel: AlertChannel, notifier: Callable):
        """Register a notification function for a channel."""
        self.notifiers[channel] = notifier
    
    def create_alert(self, title: str, message: str, severity: AlertSeverity,
                    component: str, metadata: Optional[Dict[str, Any]] = None) -> Alert:
        """Create a new alert."""
        alert = Alert(
            id=f"alert_{int(time.time())}_{len(self.alerts)}",
            title=title,
            message=message,
            severity=severity,
            component=component,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        return alert
    
    async def send_alert(self, alert: Alert, channels: Optional[List[AlertChannel]] = None):
        """Send an alert through specified channels."""
        if channels is None:
            channels = [AlertChannel.LOG]  # Default to logging
        
        for channel in channels:
            if channel in self.notifiers:
                try:
                    await self.notifiers[channel](alert)
                except Exception as e:
                    logging.error(f"Failed to send alert via {channel}: {e}")
    
    async def check_rules(self):
        """Check all alert rules and trigger alerts if needed."""
        for rule in self.rules:
            if rule.should_trigger() and rule.condition():
                alert = self.create_alert(
                    title=f"Alert: {rule.name}",
                    message=f"Alert condition '{rule.name}' was triggered",
                    severity=rule.severity,
                    component="alert_manager",
                    metadata={"rule_name": rule.name}
                )
                
                await self.send_alert(alert, rule.channels)
                rule.last_triggered = datetime.now()
    
    # Default alert conditions
    def _check_high_error_rate(self) -> bool:
        """Check if error rate is high."""
        # This would integrate with metrics collector
        # For now, return False
        return False
    
    def _check_high_response_time(self) -> bool:
        """Check if response time is high."""
        # This would integrate with metrics collector
        # For now, return False
        return False
    
    def _check_circuit_breaker_open(self) -> bool:
        """Check if any circuit breakers are open."""
        # This would integrate with circuit breaker manager
        # For now, return False
        return False
    
    def _check_llm_service_unavailable(self) -> bool:
        """Check if LLM service is unavailable."""
        # This would integrate with LLM health checks
        # For now, return False
        return False
    
    def _check_vector_db_issues(self) -> bool:
        """Check if vector database has issues."""
        # This would integrate with vector DB health checks
        # For now, return False
        return False
    
    # Default notifiers
    async def _send_email(self, alert: Alert):
        """Send alert via email."""
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        alert_email = os.getenv("ALERT_EMAIL")
        
        if not all([smtp_server, smtp_username, smtp_password, alert_email]):
            logging.warning("Email notification not configured")
            return
        
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = alert_email
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
        
        body = f"""
        Alert Details:
        --------------
        Title: {alert.title}
        Message: {alert.message}
        Severity: {alert.severity.value}
        Component: {alert.component}
        Timestamp: {alert.timestamp}
        
        Metadata: {json.dumps(alert.metadata, indent=2) if alert.metadata else 'None'}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")
    
    async def _send_webhook(self, alert: Alert):
        """Send alert via webhook."""
        webhook_url = os.getenv("WEBHOOK_URL")
        if not webhook_url:
            logging.warning("Webhook URL not configured")
            return
        
        payload = {
            "alert": asdict(alert),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed to send webhook alert: {e}")
    
    async def _send_slack(self, alert: Alert):
        """Send alert via Slack."""
        slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not slack_webhook_url:
            logging.warning("Slack webhook URL not configured")
            return
        
        color_map = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9500",
            AlertSeverity.ERROR: "#ff0000",
            AlertSeverity.CRITICAL: "#8b0000"
        }
        
        payload = {
            "attachments": [{
                "color": color_map.get(alert.severity, "#000000"),
                "title": alert.title,
                "text": alert.message,
                "fields": [
                    {"title": "Severity", "value": alert.severity.value, "short": True},
                    {"title": "Component", "value": alert.component, "short": True},
                    {"title": "Timestamp", "value": alert.timestamp.isoformat(), "short": False}
                ],
                "footer": "RAG Chatbot Alert System"
            }]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(slack_webhook_url, json=payload)
                response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {e}")
    
    async def _send_discord(self, alert: Alert):
        """Send alert via Discord."""
        discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not discord_webhook_url:
            logging.warning("Discord webhook URL not configured")
            return
        
        color_map = {
            AlertSeverity.INFO: 0x36a64f,
            AlertSeverity.WARNING: 0xff9500,
            AlertSeverity.ERROR: 0xff0000,
            AlertSeverity.CRITICAL: 0x8b0000
        }
        
        payload = {
            "embeds": [{
                "color": color_map.get(alert.severity, 0x000000),
                "title": alert.title,
                "description": alert.message,
                "fields": [
                    {"name": "Severity", "value": alert.severity.value, "inline": True},
                    {"name": "Component", "value": alert.component, "inline": True},
                    {"name": "Timestamp", "value": alert.timestamp.isoformat(), "inline": False}
                ],
                "footer": {"text": "RAG Chatbot Alert System"}
            }]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(discord_webhook_url, json=payload)
                response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed to send Discord alert: {e}")
    
    def _log_alert(self, alert: Alert):
        """Log alert to application logs."""
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)
        
        logging.log(log_level, f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.message}")
    
    def get_alerts(self, severity: Optional[AlertSeverity] = None, 
                   component: Optional[str] = None, limit: int = 100) -> List[Alert]:
        """Get alerts with optional filtering."""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if component:
            alerts = [a for a in alerts if a.component == component]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                break
    
    def clear_old_alerts(self, days: int = 30):
        """Clear alerts older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff_date]


# Global alert manager
alert_manager = AlertManager()


# Convenience functions
async def send_alert(title: str, message: str, severity: AlertSeverity,
                    component: str, channels: Optional[List[AlertChannel]] = None,
                    metadata: Optional[Dict[str, Any]] = None):
    """Send an alert."""
    alert = alert_manager.create_alert(title, message, severity, component, metadata)
    await alert_manager.send_alert(alert, channels)


async def check_alerts():
    """Check all alert rules."""
    await alert_manager.check_rules()


def get_active_alerts(severity: Optional[AlertSeverity] = None,
                     component: Optional[str] = None) -> List[Alert]:
    """Get active (unacknowledged) alerts."""
    alerts = alert_manager.get_alerts(severity, component)
    return [a for a in alerts if not a.acknowledged] 