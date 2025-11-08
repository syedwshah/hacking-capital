import streamlit as st
import time
import requests
import os

st.set_page_config(
    page_title="Hacking Capital - Trading Agent Demo",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# Custom CSS for demo styling
st.markdown("""
<style>
    .demo-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .status-running {
        color: #ffc107;
        font-weight: bold;
    }
    .status-completed {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with quick stats
st.sidebar.title("🚀 Hacking Capital Demo")
st.sidebar.markdown("---")

# Quick API health check
try:
    api_base = os.environ.get("API_BASE", "http://localhost:8000")
    response = requests.get(f"{api_base}/api/v1/trade/history?limit=1", timeout=2)
    if response.status_code == 200:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Error")
except:
    st.sidebar.warning("⏳ API Starting...")

st.sidebar.markdown("---")

# Quick navigation
st.sidebar.subheader("📊 Key Features")
nav_options = {
    "Trading History & Live Demo": "7_Trading_History.py",
    "Portfolio Optimization": "6_Portfolio_Optimization.py",
    "Live Paper Trading": "5_Paper_Trade_Live.py",
    "Backtesting": "2_Backtest.py"
}

for name, page in nav_options.items():
    if st.sidebar.button(f"🔗 {name}", key=f"nav_{page}"):
        st.switch_page(f"pages/{page}")

st.sidebar.markdown("---")
st.sidebar.caption("💡 Navigate using the page selector above or use the sidebar menu.")

# Main demo dashboard
st.markdown('<div class="demo-header"><h1>🎯 Hacking Capital</h1><h3>LLM-Free Trading Agent Demo</h3><p>Real-time technical analysis, batch processing, and historical performance tracking</p></div>', unsafe_allow_html=True)

# Demo stats in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🤖 AI Agents</h3>
        <p>9 Technical Indicators</p>
        <p>SMA, RSI, MACD, Bollinger Bands, Stochastic, Williams %R, ATR, CCI, OBV</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>📊 Real-time Data</h3>
        <p>Minute-level granularity</p>
        <p>Synthetic market data with realistic patterns</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>🔄 Batch Processing</h3>
        <p>Multi-symbol analysis</p>
        <p>Background simulation with live progress</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <h3>💾 Full Persistence</h3>
        <p>Decision history</p>
        <p>Trade records & performance analytics</p>
    </div>
    """, unsafe_allow_html=True)

# Quick demo actions
st.subheader("🚀 Quick Demo Actions")

demo_col1, demo_col2, demo_col3 = st.columns(3)

with demo_col1:
    if st.button("🎯 Run Single Decision", type="primary", use_container_width=True):
        try:
            response = requests.post(
                f"{api_base}/api/v1/trade/decide",
                json={"symbol": "AAPL", "granularity": "daily", "cash": 10000},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                st.success(f"Decision: {result['decision']['action']} (Confidence: {result['decision']['confidence']:.1%})")
            else:
                st.error("API call failed")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with demo_col2:
    if st.button("📊 View Recent History", type="secondary", use_container_width=True):
        st.switch_page("pages/7_Trading_History.py")

with demo_col3:
    if st.button("🔄 Start Batch Demo", type="secondary", use_container_width=True):
        st.switch_page("pages/7_Trading_History.py")

# System status
st.subheader("📈 System Status")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    # Check database connectivity
    try:
        response = requests.get(f"{api_base}/api/v1/trade/history?limit=1", timeout=2)
        if response.status_code == 200:
            data = response.json()
            st.metric("Database Status", "✅ Connected", f"{data['stats']['total_decisions']} decisions")
        else:
            st.metric("Database Status", "❌ Error")
    except:
        st.metric("Database Status", "⏳ Connecting...")

with status_col2:
    # Check simulation history
    try:
        response = requests.get(f"{api_base}/api/v1/simulate/history?limit=1", timeout=2)
        if response.status_code == 200:
            data = response.json()
            st.metric("Batch Simulations", f"{data['total_batches']} runs", f"{data['total_decisions']} total decisions")
        else:
            st.metric("Batch Simulations", "❌ Error")
    except:
        st.metric("Batch Simulations", "⏳ Loading...")

with status_col3:
    # Show last activity
    try:
        response = requests.get(f"{api_base}/api/v1/trade/history?limit=1", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data['history']:
                last_ts = data['history'][0]['timestamp']
                st.metric("Last Activity", f"🕐 {last_ts[:16]}")
            else:
                st.metric("Last Activity", "No recent activity")
        else:
            st.metric("Last Activity", "❌ Error")
    except:
        st.metric("Last Activity", "⏳ Checking...")

st.markdown("---")
st.caption("💡 Use the navigation buttons above or the sidebar to explore specific features. All data is persisted and historical runs are tracked.")


