import streamlit as st

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

st.write("This page will stream simulated trades and show agent contributions (placeholder).")


