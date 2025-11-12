#!/usr/bin/env python3
"""
SentinelVNC Streamlit Dashboard
Real-time monitoring dashboard showing live alerts and allowing containment actions.
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import List, Dict
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Page config
st.set_page_config(
    page_title="SentinelVNC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_URL = st.sidebar.text_input(
    "Backend API URL",
    value="http://localhost:8000",
    help="URL of the FastAPI backend"
)

AUTO_REFRESH = st.sidebar.checkbox("Auto-refresh", value=True)
REFRESH_INTERVAL = st.sidebar.slider("Refresh interval (seconds)", 1, 30, 5) if AUTO_REFRESH else 5


@st.cache_data(ttl=2)
def fetch_alerts(api_url: str) -> List[Dict]:
    """Fetch alerts from backend API"""
    try:
        response = requests.get(f"{api_url}/api/v1/alerts", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching alerts: {e}")
        return []


def contain_session(api_url: str, session_id: str) -> bool:
    """Send containment request to backend"""
    try:
        # In production, this would require authentication
        response = requests.post(
            f"{api_url}/api/v1/contain",
            json={"session_id": session_id},
            timeout=5
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error containing session: {e}")
        return False


def main():
    """Main dashboard function"""
    st.title("🛡️ SentinelVNC Dashboard")
    st.markdown("Real-time VNC Security Monitoring")
    
    # Fetch alerts
    alerts = fetch_alerts(API_URL)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_alerts = len(alerts)
        st.metric("Total Alerts", total_alerts)
    
    with col2:
        high_severity = sum(1 for a in alerts if a.get("severity") == "high")
        st.metric("High Severity", high_severity)
    
    with col3:
        contained = sum(1 for a in alerts if a.get("contained", False))
        st.metric("Contained", contained)
    
    with col4:
        open_alerts = sum(1 for a in alerts if a.get("status") == "open")
        st.metric("Open Alerts", open_alerts)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Live Alerts", "Detection Analysis", "Forensic Data"])
    
    with tab1:
        st.header("🚨 Live Alerts")
        
        if not alerts:
            st.info("No alerts detected yet. Run the attack simulator to generate events.")
        else:
            # Recent alerts
            recent_alerts = sorted(alerts, key=lambda x: x.get("timestamp", ""), reverse=True)[:20]
            
            for alert in recent_alerts:
                severity = alert.get("severity", "medium")
                alert_id = alert.get("alert_id", "unknown")
                session_id = alert.get("session_id", "unknown")
                
                with st.expander(f"Alert: {alert_id} - {severity.upper()}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Session ID:** {session_id}")
                        st.write(f"**Event Type:** {alert.get('event_type', 'N/A')}")
                        st.write(f"**Timestamp:** {alert.get('timestamp', 'N/A')}")
                        st.write(f"**Status:** {alert.get('status', 'N/A')}")
                        
                        reasons = alert.get("rule_reasons", [])
                        if reasons:
                            st.write("**Detection Reasons:**")
                            for reason in reasons:
                                st.write(f"- {reason}")
                        
                        ml_score = alert.get("ml_score")
                        if ml_score:
                            st.write(f"**ML Anomaly Score:** {ml_score:.3f}")
                        
                        forensic_hash = alert.get("forensic_hash")
                        if forensic_hash:
                            st.write(f"**Forensic Hash:** `{forensic_hash[:32]}...`")
                        
                        tx_hash = alert.get("blockchain_tx_hash")
                        if tx_hash:
                            st.write(f"**Blockchain TX:** `{tx_hash[:32]}...`")
                    
                    with col2:
                        if not alert.get("contained", False):
                            if st.button("Contain", key=f"contain_{alert_id}"):
                                if contain_session(API_URL, session_id):
                                    st.success("Session contained!")
                                    st.rerun()
                        else:
                            st.success("✅ Contained")
    
    with tab2:
        st.header("📊 Detection Analysis")
        
        if not alerts:
            st.info("No data available for analysis.")
        else:
            df = pd.DataFrame(alerts)
            
            # Convert timestamp if needed
            if "timestamp" in df.columns:
                try:
                    df["datetime"] = pd.to_datetime(df["timestamp"])
                except:
                    pass
            
            # Detection methods distribution
            if "detection_methods" in df.columns:
                all_methods = []
                for methods in df["detection_methods"]:
                    if isinstance(methods, list):
                        all_methods.extend(methods)
                
                if all_methods:
                    method_counts = pd.Series(all_methods).value_counts()
                    fig = px.pie(
                        values=method_counts.values,
                        names=method_counts.index,
                        title="Detection Methods Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Severity distribution
            if "severity" in df.columns:
                severity_counts = df["severity"].value_counts()
                fig = px.bar(
                    x=severity_counts.index,
                    y=severity_counts.values,
                    title="Alerts by Severity",
                    labels={"x": "Severity", "y": "Count"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # ML scores distribution
            if "ml_score" in df.columns:
                ml_scores = df["ml_score"].dropna()
                if len(ml_scores) > 0:
                    fig = px.histogram(
                        x=ml_scores,
                        nbins=20,
                        title="ML Anomaly Score Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Timeline
            if "datetime" in df.columns:
                df["date"] = df["datetime"].dt.date
                timeline = df.groupby("date").size().reset_index(name="count")
                fig = px.line(
                    timeline,
                    x="date",
                    y="count",
                    title="Alerts Timeline"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("🔍 Forensic Data")
        
        if not alerts:
            st.info("No forensic data available.")
        else:
            # Show forensic hashes and blockchain TXs
            forensic_data = []
            for alert in alerts:
                if alert.get("forensic_hash"):
                    forensic_data.append({
                        "Alert ID": alert.get("alert_id"),
                        "Forensic Hash": alert.get("forensic_hash"),
                        "Blockchain TX": alert.get("blockchain_tx_hash", "N/A"),
                        "Severity": alert.get("severity"),
                        "Timestamp": alert.get("timestamp")
                    })
            
            if forensic_data:
                df_forensic = pd.DataFrame(forensic_data)
                st.dataframe(df_forensic, use_container_width=True)
            else:
                st.info("No forensic hashes found in alerts.")
    
    # Auto-refresh
    if AUTO_REFRESH:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()


if __name__ == "__main__":
    main()

