import time
import streamlit as st
from ui.api_client import decide
import pandas as pd

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

st.divider()
st.subheader("10-minute demo (synthetic)")
run_demo = st.button("Run 10-step demo")
placeholder_chart = st.empty()
placeholder_table = st.empty()
if run_demo:
    rows = []
    for i in range(10):
        try:
            result = decide(symbol, "1m", cash)
            d = result["decision"]
            rows.append({"step": i + 1, "action": d["action"], "confidence": d["confidence"], "reason": d["reason"]})
            df = pd.DataFrame(rows)
            placeholder_table.dataframe(df, use_container_width=True)
            placeholder_chart.line_chart(df[["confidence"]])
        except Exception as e:
            st.error(f"Demo error at step {i+1}: {e}")
            break
        time.sleep(0.5)

st.caption("Streaming simulation will replace the loop above in a later iteration.")


