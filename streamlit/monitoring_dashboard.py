"""
Streamlit monitoring dashboard for the RAG chatbot.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
REFRESH_INTERVAL = 30  # seconds

st.set_page_config(
    page_title="RAG Chatbot Monitoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_api_data(endpoint: str):
    """Get data from API endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch data from {endpoint}: {e}")
        return None

def main():
    st.title("🤖 RAG Chatbot Monitoring Dashboard")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("📊 Dashboard Controls")
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    if auto_refresh:
        st.sidebar.info(f"Auto-refreshing every {REFRESH_INTERVAL} seconds")
    
    # Manual refresh
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    # Health Status
    with col1:
        st.subheader("🏥 Health Status")
        health_data = get_api_data("/api/monitoring/health")
        if health_data:
            status = health_data.get("status", "unknown")
            status_color = "🟢" if status == "healthy" else "🔴"
            st.metric("System Status", f"{status_color} {status.title()}")
            
            if "components" in health_data:
                for component, data in health_data["components"].items():
                    if isinstance(data, dict) and "status" in data:
                        comp_status = data["status"]
                        comp_color = "🟢" if comp_status == "healthy" else "🔴"
                        st.write(f"{comp_color} {component.title()}: {comp_status}")
        else:
            st.error("❌ Unable to fetch health data")
    
    # System Metrics
    with col2:
        st.subheader("💻 System Metrics")
        dashboard_data = get_api_data("/api/monitoring/dashboard")
        if dashboard_data and "system" in dashboard_data:
            system = dashboard_data["system"]
            st.metric("CPU Usage", f"{system.get('cpu_usage_percent', 0):.1f}%")
            st.metric("Memory Usage", f"{system.get('memory_usage_percent', 0):.1f}%")
            st.metric("Available Memory", f"{system.get('memory_available_gb', 0):.1f} GB")
        else:
            st.error("❌ Unable to fetch system metrics")
    
    # Alerts
    with col3:
        st.subheader("🚨 Alerts")
        alerts_data = get_api_data("/api/monitoring/alerts?limit=5")
        if alerts_data:
            total_alerts = alerts_data.get("total", 0)
            active_alerts = alerts_data.get("active", 0)
            st.metric("Total Alerts", total_alerts)
            st.metric("Active Alerts", active_alerts, delta=active_alerts)
            
            if active_alerts > 0:
                st.warning(f"⚠️ {active_alerts} active alerts")
        else:
            st.error("❌ Unable to fetch alerts")
    
    # Circuit Breakers
    with col4:
        st.subheader("⚡ Circuit Breakers")
        cb_data = get_api_data("/api/circuit-breakers/")
        if cb_data:
            total_breakers = len(cb_data)
            open_breakers = sum(1 for cb in cb_data.values() if cb.get("state") == "open")
            st.metric("Total Breakers", total_breakers)
            st.metric("Open Breakers", open_breakers)
            
            if open_breakers > 0:
                st.error(f"🔴 {open_breakers} circuit breakers are open")
        else:
            st.error("❌ Unable to fetch circuit breaker data")
    
    st.markdown("---")
    
    # Detailed Views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Metrics", "🚨 Alerts", "🔍 Traces", "⚙️ System"])
    
    # Metrics Tab
    with tab1:
        st.subheader("📈 Prometheus Metrics")
        
        # Get raw metrics
        try:
            metrics_response = requests.get(f"{API_BASE_URL}/api/monitoring/metrics", timeout=5)
            if metrics_response.status_code == 200:
                metrics_text = metrics_response.text
                st.code(metrics_text, language="text")
            else:
                st.error("Failed to fetch metrics")
        except Exception as e:
            st.error(f"Error fetching metrics: {e}")
    
    # Alerts Tab
    with tab2:
        st.subheader("🚨 Alert Management")
        
        # Alert filters
        col1, col2, col3 = st.columns(3)
        with col1:
            severity_filter = st.selectbox(
                "Filter by Severity",
                ["All", "info", "warning", "error", "critical"]
            )
        with col2:
            component_filter = st.selectbox(
                "Filter by Component",
                ["All", "system", "llm", "vector_db", "rag", "test"]
            )
        with col3:
            limit_filter = st.slider("Limit", 5, 50, 20)
        
        # Get filtered alerts
        params = {"limit": limit_filter}
        if severity_filter != "All":
            params["severity"] = severity_filter
        if component_filter != "All":
            params["component"] = component_filter
        
        alerts_data = get_api_data(f"/api/monitoring/alerts?{requests.compat.urlencode(params)}")
        
        if alerts_data and "alerts" in alerts_data:
            alerts = alerts_data["alerts"]
            
            if alerts:
                # Create DataFrame for better display
                df = pd.DataFrame(alerts)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp', ascending=False)
                
                # Display alerts
                for _, alert in df.iterrows():
                    severity_color = {
                        "info": "🔵",
                        "warning": "🟡", 
                        "error": "🔴",
                        "critical": "💀"
                    }.get(alert['severity'], "⚪")
                    
                    with st.expander(f"{severity_color} {alert['title']} ({alert['timestamp']})"):
                        st.write(f"**Message:** {alert['message']}")
                        st.write(f"**Component:** {alert['component']}")
                        st.write(f"**Severity:** {alert['severity']}")
                        st.write(f"**Acknowledged:** {alert['acknowledged']}")
                        
                        if alert['metadata']:
                            st.write("**Metadata:**")
                            st.json(alert['metadata'])
                        
                        # Acknowledge button
                        if not alert['acknowledged']:
                            if st.button(f"Acknowledge Alert {alert['id']}", key=alert['id']):
                                try:
                                    response = requests.post(
                                        f"{API_BASE_URL}/api/monitoring/alerts/{alert['id']}/acknowledge"
                                    )
                                    if response.status_code == 200:
                                        st.success("Alert acknowledged!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to acknowledge alert")
                                except Exception as e:
                                    st.error(f"Error acknowledging alert: {e}")
            else:
                st.info("No alerts found with current filters")
        else:
            st.error("Unable to fetch alerts")
        
        # Test alert section
        st.markdown("---")
        st.subheader("🧪 Test Alert")
        
        with st.form("test_alert"):
            test_title = st.text_input("Alert Title", "Test Alert")
            test_message = st.text_area("Alert Message", "This is a test alert from the dashboard")
            test_severity = st.selectbox("Severity", ["info", "warning", "error", "critical"])
            test_component = st.text_input("Component", "test")
            
            if st.form_submit_button("Send Test Alert"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/monitoring/alerts/test",
                        params={
                            "title": test_title,
                            "message": test_message,
                            "severity": test_severity,
                            "component": test_component
                        }
                    )
                    if response.status_code == 200:
                        st.success("Test alert sent successfully!")
                    else:
                        st.error("Failed to send test alert")
                except Exception as e:
                    st.error(f"Error sending test alert: {e}")
    
    # Traces Tab
    with tab3:
        st.subheader("🔍 Tracing Information")
        
        trace_data = get_api_data("/api/monitoring/traces")
        if trace_data:
            st.json(trace_data)
        else:
            st.error("Unable to fetch trace information")
    
    # System Tab
    with tab4:
        st.subheader("⚙️ System Information")
        
        # System metrics status
        metrics_status = get_api_data("/api/monitoring/metrics/system/status")
        if metrics_status:
            st.write("**System Metrics Collection:**")
            st.write(f"Running: {metrics_status.get('running', False)}")
            st.write(f"Thread Alive: {metrics_status.get('thread_alive', False)}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Start System Metrics"):
                    try:
                        response = requests.post(f"{API_BASE_URL}/api/monitoring/metrics/system/start")
                        if response.status_code == 200:
                            st.success("System metrics started!")
                        else:
                            st.error("Failed to start system metrics")
                    except Exception as e:
                        st.error(f"Error starting system metrics: {e}")
            
            with col2:
                if st.button("Stop System Metrics"):
                    try:
                        response = requests.post(f"{API_BASE_URL}/api/monitoring/metrics/system/stop")
                        if response.status_code == 200:
                            st.success("System metrics stopped!")
                        else:
                            st.error("Failed to stop system metrics")
                    except Exception as e:
                        st.error(f"Error stopping system metrics: {e}")
        
        # Clear old alerts
        st.markdown("---")
        st.subheader("🧹 Maintenance")
        
        days_to_clear = st.slider("Clear alerts older than (days)", 1, 90, 30)
        if st.button("Clear Old Alerts"):
            try:
                response = requests.delete(f"{API_BASE_URL}/api/monitoring/alerts/clear?days={days_to_clear}")
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Cleared {result.get('cleared_count', 0)} alerts")
                else:
                    st.error("Failed to clear old alerts")
            except Exception as e:
                st.error(f"Error clearing old alerts: {e}")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

if __name__ == "__main__":
    main() 