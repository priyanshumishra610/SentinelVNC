#!/usr/bin/env python3
"""
SentinelVNC Streamlit Dashboard
Real-time monitoring dashboard for VNC data exfiltration detection.
"""

import streamlit as st
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Page config
st.set_page_config(
    page_title="SentinelVNC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=1)
def load_alerts(alerts_file: Path) -> pd.DataFrame:
    """Load alerts from JSONL file."""
    if not alerts_file.exists():
        return pd.DataFrame()
    
    alerts = []
    with open(alerts_file, 'r') as f:
        for line in f:
            try:
                alert = json.loads(line.strip())
                alerts.append(alert)
            except json.JSONDecodeError:
                continue
    
    if not alerts:
        return pd.DataFrame()
    
    df = pd.DataFrame(alerts)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    return df


@st.cache_data(ttl=1)
def load_forensic(forensic_dir: Path) -> list:
    """Load forensic files."""
    if not forensic_dir.exists():
        return []
    
    forensic_files = []
    for f in forensic_dir.glob("*.json"):
        try:
            with open(f, 'r') as f:
                forensic = json.load(f)
                forensic_files.append(forensic)
        except:
            continue
    
    return forensic_files


@st.cache_data(ttl=1)
def load_anchors(anchors_dir: Path) -> list:
    """Load anchor files."""
    if not anchors_dir.exists():
        return []
    
    anchors = []
    for f in anchors_dir.glob("*.json"):
        try:
            with open(f, 'r') as f:
                anchor = json.load(f)
                anchors.append(anchor)
        except:
            continue
    
    return sorted(anchors, key=lambda x: x.get("timestamp", 0), reverse=True)


def main():
    """Main dashboard function."""
    st.markdown('<div class="main-header">🛡️ SentinelVNC Dashboard</div>', 
                unsafe_allow_html=True)
    
    # File paths
    alerts_file = Path("logs/alerts.jsonl")
    forensic_dir = Path("forensic")
    anchors_dir = Path("anchors")
    
    # Sidebar
    with st.sidebar:
        st.header("Controls")
        
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)
        if auto_refresh:
            refresh_interval = st.slider("Refresh interval (seconds)", 1, 10, 5)
        
        st.header("Actions")
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("🛑 Contain Threat"):
            st.warning("Containment action triggered! (Simulated)")
            # In production, this would trigger actual containment
            time.sleep(1)
            st.success("Threat contained successfully")
        
        st.header("Info")
        st.info("""
        **SentinelVNC** monitors VNC sessions for:
        - Clipboard abuse
        - Screenshot scraping
        - File exfiltration
        """)
    
    # Main content
    alerts_df = load_alerts(alerts_file)
    forensic_files = load_forensic(forensic_dir)
    anchors = load_anchors(anchors_dir)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_alerts = len(alerts_df) if not alerts_df.empty else 0
        st.metric("Total Alerts", total_alerts)
    
    with col2:
        high_severity = len(alerts_df[alerts_df['severity'] == 'high']) if not alerts_df.empty else 0
        st.metric("High Severity", high_severity, delta=None)
    
    with col3:
        forensic_count = len(forensic_files)
        st.metric("Forensic Records", forensic_count)
    
    with col4:
        anchor_count = len(anchors)
        st.metric("Blockchain Anchors", anchor_count)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Live Alerts", "Detection Analysis", "Forensic Timeline", "Blockchain Anchors"])
    
    with tab1:
        st.header("🚨 Live Alerts")
        
        if alerts_df.empty:
            st.info("No alerts detected yet. Run the attack simulator to generate events.")
        else:
            # Recent alerts
            recent_alerts = alerts_df.sort_values('timestamp', ascending=False).head(10)
            
            for _, alert in recent_alerts.iterrows():
                severity = alert.get('severity', 'medium')
                alert_class = 'alert-high' if severity == 'high' else 'alert-medium'
                
                with st.container():
                    st.markdown(f'<div class="alert-box {alert_class}">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(f"Alert: {alert.get('alert_id', 'Unknown')}")
                        st.write(f"**Time:** {alert.get('datetime', 'N/A')}")
                        st.write(f"**Event Type:** {alert.get('event', {}).get('event_type', 'N/A')}")
                        st.write(f"**Severity:** {severity.upper()}")
                        
                        reasons = alert.get('reasons', [])
                        if reasons:
                            st.write("**Detection Reasons:**")
                            for reason in reasons:
                                st.write(f"- {reason}")
                        
                        ml_score = alert.get('ml_score', 0)
                        if ml_score > 0:
                            st.write(f"**ML Anomaly Score:** {ml_score:.3f}")
                    
                    with col2:
                        if st.button("Contain", key=f"contain_{alert.get('alert_id')}"):
                            st.success("Containment triggered!")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.divider()
    
    with tab2:
        st.header("📊 Detection Analysis")
        
        if alerts_df.empty:
            st.info("No data available for analysis.")
        else:
            # Detection methods
            detection_methods = []
            for _, alert in alerts_df.iterrows():
                methods = alert.get('detection_methods', [])
                detection_methods.extend(methods)
            
            if detection_methods:
                method_counts = pd.Series(detection_methods).value_counts()
                fig = px.pie(values=method_counts.values, names=method_counts.index,
                           title="Detection Methods Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            # Severity distribution
            if 'severity' in alerts_df.columns:
                severity_counts = alerts_df['severity'].value_counts()
                fig = px.bar(x=severity_counts.index, y=severity_counts.values,
                           title="Alerts by Severity",
                           labels={'x': 'Severity', 'y': 'Count'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Timeline
            if 'datetime' in alerts_df.columns:
                alerts_df['date'] = alerts_df['datetime'].dt.date
                timeline = alerts_df.groupby('date').size().reset_index(name='count')
                fig = px.line(timeline, x='date', y='count', title="Alerts Timeline")
                st.plotly_chart(fig, use_container_width=True)
            
            # ML scores distribution
            if 'ml_score' in alerts_df.columns:
                ml_scores = alerts_df['ml_score'].dropna()
                if len(ml_scores) > 0:
                    fig = px.histogram(x=ml_scores, nbins=20, title="ML Anomaly Score Distribution")
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("🔍 Forensic Timeline")
        
        if not forensic_files:
            st.info("No forensic records available.")
        else:
            # Sort by timestamp
            forensic_files.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            for forensic in forensic_files[:20]:  # Show last 20
                with st.expander(f"Forensic ID: {forensic.get('forensic_id', 'Unknown')} - {forensic.get('datetime', 'N/A')}"):
                    st.json(forensic)
    
    with tab4:
        st.header("⛓️ Blockchain Anchors")
        
        if not anchors:
            st.info("No blockchain anchors created yet.")
        else:
            for anchor in anchors:
                with st.expander(f"Anchor: {anchor.get('anchor_id', 'Unknown')} - {anchor.get('datetime', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Merkle Root:**")
                        st.code(anchor.get('merkle_root', 'N/A'), language=None)
                        st.write(f"**Forensic Files:** {anchor.get('forensic_count', 0)}")
                    
                    with col2:
                        st.write("**Verification:**")
                        st.json(anchor.get('verification', {}))
                        st.write(f"**Signature Hash:**")
                        st.code(anchor.get('signature_hash', 'N/A')[:32] + '...', language=None)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()


