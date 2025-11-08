import time
import streamlit as st
import pandas as pd
from ui.api_client import decide, get_agent_weights, set_agent_weights, simulate_batch

st.title("Paper Trade (Live)")

if "primary_weight" not in st.session_state:
    st.session_state["primary_weight"] = 0.5
if "investor_weight" not in st.session_state:
    st.session_state["investor_weight"] = 0.25
if "tailwinds_weight" not in st.session_state:
    st.session_state["tailwinds_weight"] = 0.25

symbol = st.text_input("Symbol", value="AAPL")
col1, col2, col3 = st.columns(3)
with col1:
    st.session_state["primary_weight"] = st.slider(
        "Primary agent weight", 0.0, 1.0, st.session_state["primary_weight"], 0.05, key="primary_weight_slider"
    )
with col2:
    st.session_state["investor_weight"] = st.slider(
        "Investor patterns weight", 0.0, 1.0, st.session_state["investor_weight"], 0.05, key="investor_weight_slider"
    )
with col3:
    st.session_state["tailwinds_weight"] = st.slider(
        "Sentiment/tailwinds weight", 0.0, 1.0, st.session_state["tailwinds_weight"], 0.05, key="tailwinds_weight_slider"
    )

st.write("Deterministic-only fallback:", st.toggle("Enable", value=False, key="det_only"))

cash = st.number_input("Cash (USD)", value=1000.0, step=100.0)
granularity = st.selectbox("Granularity", ["1m", "daily"], index=0)

col_load, col_save = st.columns(2)
with col_load:
    if st.button("Load weights", use_container_width=True):
        data = get_agent_weights()
        weights = {item["agent"]: item["weight"] for item in data.get("weights", [])}
        st.session_state["primary_weight"] = weights.get("primary", 0.5)
        st.session_state["investor_weight"] = weights.get("investor_patterns", 0.25)
        st.session_state["tailwinds_weight"] = weights.get("sentiment_tailwinds", 0.25)
        st.success("Loaded weights from API")
        st.experimental_rerun()
with col_save:
    if st.button("Save weights", use_container_width=True):
        payload = [
            {"agent": "primary", "weight": st.session_state["primary_weight"]},
            {"agent": "investor_patterns", "weight": st.session_state["investor_weight"]},
            {"agent": "sentiment_tailwinds", "weight": st.session_state["tailwinds_weight"]},
        ]
        set_agent_weights(payload)
        st.success("Weights saved (normalized server-side)")

if st.button("Decide now"):
    try:
        result = decide(symbol, granularity, cash)
        st.success(result["decision"])
        with st.expander("Per-agent contributions"):
            st.json(result.get("explain", {}))
    except Exception as e:
        st.error(f"Decision error: {e}")

st.divider()
st.subheader("10-minute demo (synthetic)")
run_demo = st.button("Run 10-step demo")
placeholder_chart = st.empty()
placeholder_table = st.empty()
explain_placeholder = st.empty()
if run_demo:
    rows = []
    explains = []
    for i in range(10):
        try:
            result = decide(symbol, "1m", cash)
            d = result["decision"]
            rows.append({"step": i + 1, "action": d["action"], "confidence": d["confidence"], "reason": d["reason"]})
            explains.append(result.get("explain", {}))
            df = pd.DataFrame(rows)
            placeholder_table.dataframe(df, use_container_width=True)
            placeholder_chart.line_chart(df[["confidence"]])
            explain_placeholder.json(explains[-1])
        except Exception as e:
            st.error(f"Demo error at step {i+1}: {e}")
            break
        time.sleep(0.5)

st.caption("Streaming simulation will replace the loop above in a later iteration.")

st.divider()
st.subheader("Batch simulation (multi-symbol)")
batch_symbols = st.text_input("Symbols (comma-separated)", value="AAPL,MSFT,SPY")
steps = st.number_input("Steps", min_value=1, max_value=60, value=10, step=1)
if st.button("Run batch"):
    syms = [s.strip().upper() for s in batch_symbols.split(",") if s.strip()]
    try:
        result = simulate_batch(symbols=syms, steps=int(steps), cash=cash)
        st.success("Batch complete")
        df = pd.DataFrame(result["results"])
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Batch simulation error: {e}")

