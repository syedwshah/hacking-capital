import streamlit as st
from ui.api_client import decide

st.title("Paper Trade (Live)")

symbol = st.text_input("Symbol", value="AAPL")
col1, col2, col3 = st.columns(3)
with col1:
    primary_w = st.slider("Primary agent weight", 0.0, 1.0, 0.5, 0.05)
with col2:
    investor_w = st.slider("Investor patterns weight", 0.0, 1.0, 0.25, 0.05)
with col3:
    tailwinds_w = st.slider("Sentiment/tailwinds weight", 0.0, 1.0, 0.25, 0.05)

st.write("Deterministic-only fallback:", st.toggle("Enable", value=False, key="det_only"))

cash = st.number_input("Cash (USD)", value=1000.0, step=100.0)
granularity = st.selectbox("Granularity", ["1m", "daily"], index=0)

if st.button("Decide now"):
    try:
        result = decide(symbol, granularity, cash)
        st.success(result["decision"])
        with st.expander("Per-agent contributions"):
            st.json(result.get("explain", []))
    except Exception as e:
        st.error(f"Decision error: {e}")

st.caption("This page will later stream simulated trades and show agent contributions over time.")


