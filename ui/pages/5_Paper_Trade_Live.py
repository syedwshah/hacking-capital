import time
import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.api_client import decide, get_agent_weights, set_agent_weights, simulate_batch, stream_events

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
        decision = result["decision"]

        # Add cache status badge
        cache_hit = decision.get("cache_hit", False)
        cache_badge = "🟢 CACHE HIT" if cache_hit else "🔴 CACHE MISS"

        st.success(f"{decision['action']} - Confidence: {decision['confidence']:.2f} - {cache_badge}")
        st.write(f"Reason: {decision['reason']}")

        with st.expander("Per-agent contributions"):
            st.json(result.get("explain", {}))
    except Exception as e:
        st.error(f"Decision error: {e}")

st.divider()

# Trading Mode Selection
trading_mode = st.radio(
    "🎯 Trading Mode",
    ["Fixed Steps", "Continuous Trading"],
    index=0,
    key="trading_mode",
    help="Fixed Steps: Run for a set number of trades. Continuous: Keep trading indefinitely."
)

if trading_mode == "Fixed Steps":
    st.subheader("Live streaming simulation")
    steps = st.number_input("Steps to simulate", min_value=1, max_value=60, value=10, step=1, key="stream_steps")
    run_stream = st.button("🚀 Start Fixed Simulation")
else:
    st.subheader("🎲 Continuous Live Trading")
    st.info("⚠️ **Continuous Mode**: Trading will run indefinitely until stopped. Perfect for demo!")
    max_trades = st.number_input("Max trades (0 = unlimited)", min_value=0, max_value=1000, value=50, step=10, key="max_trades")
    trade_interval = st.slider("Trade interval (seconds)", min_value=1, max_value=10, value=2, key="trade_interval")
    run_stream = st.button("🚀 Start Continuous Trading", type="primary")

if run_stream:
    # Create placeholders for real-time updates
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Live Trading Decisions")
        placeholder_table = st.empty()
        progress_bar = st.empty()
        status_text = st.empty()
        stop_button_placeholder = st.empty()

    with col2:
        st.subheader("🤖 Agent Analysis")
        agent_analysis_placeholder = st.empty()
        confidence_chart_placeholder = st.empty()

    # Additional placeholders
    reasoning_placeholder = st.empty()
    chart_placeholder = st.empty()

    rows = []
    explains = []
    confidence_history = []
    trading_active = True

    # Stop button for continuous mode
    if trading_mode == "Continuous Trading":
        stop_button = stop_button_placeholder.button("🛑 Stop Continuous Trading", type="secondary", key="stop_trading")

    try:
        status_text.markdown("🔄 Connecting to live trading stream...")
        event_count = 0

        # Determine how many steps to run
        if trading_mode == "Fixed Steps":
            total_steps = steps
            progress_bar.progress(0)  # Show progress bar for fixed steps
        else:
            total_steps = max_trades if max_trades > 0 else float('inf')
            progress_bar.text("🎲 Continuous trading active...")  # No progress bar for continuous

        # Create a generator that can be stopped
        def trading_generator():
            step_count = 0

            while trading_active and (total_steps == float('inf') or step_count < total_steps):
                try:
                    # Check if stop button was pressed (for continuous mode)
                    if trading_mode == "Continuous Trading":
                        try:
                            stop_pressed = st.session_state.get("stop_trading", False)
                            if stop_pressed:
                                trading_active = False
                                break
                        except:
                            pass

                    # Determine how many steps to request at once
                    batch_size = min(10, total_steps - step_count) if total_steps != float('inf') else 1

                    # Simulate trading decisions
                    for event_data in stream_events(symbol, batch_size, cash):
                        step_count += 1
                        yield event_data

                        # For continuous mode, wait between trades
                        if trading_mode == "Continuous Trading" and step_count < total_steps:
                            time.sleep(trade_interval)

                    # If we got here and it's not continuous mode, we've finished
                    if trading_mode != "Continuous Trading":
                        break

                except Exception as e:
                    st.error(f"Trading error: {e}")
                    trading_active = False
                    break

        for event_data in trading_generator():
            event_count += 1

            # Update progress bar differently for each mode
            if trading_mode == "Fixed Steps":
                progress = min(event_count / total_steps, 1.0)
                progress_bar.progress(progress)
            else:
                # For continuous mode, show trade count
                progress_bar.markdown(f"📊 **Trades Made:** {event_count}")

            # Trigger background summarization every 5 trades
            if event_count % 5 == 0:
                try:
                    # Trigger background summarization
                    import requests
                    api_base = os.environ.get("API_BASE", "http://localhost:8000")
                    requests.post(f"{api_base}/api/v1/summaries/generate", json={
                        "symbol": symbol,
                        "period_days": 1,
                        "granularity": "1m"
                    }, timeout=2)
                except:
                    pass  # Silently fail if summarization fails

            # Extract decision data from the event
            event = event_data.get("data", {})
            if isinstance(event, str):
                import json
                event = json.loads(event)

            step = event.get("step", event_count)
            decision = event.get("decision", {})
            price = event.get("price", 0.0)
            ts = event.get("ts", "")
            explain_data = event.get("explain", {})

            # Add cache hit/miss badge
            cache_hit = decision.get("cache_hit", False)
            cache_badge = "🟢 HIT" if cache_hit else "🔴 MISS"

            row = {
                "step": step,
                "timestamp": ts,
                "price": f"${price:.2f}",
                "action": decision.get("action", "HOLD"),
                "confidence": f"{decision.get('confidence', 0.0):.1%}",
                "quantity": decision.get("quantity", 0.0),
                "cache": cache_badge
            }
            rows.append(row)
            explains.append(explain_data)
            confidence_history.append({
                "step": step,
                "confidence": decision.get("confidence", 0.0),
                "price": price
            })

            # Update decisions table
            df = pd.DataFrame(rows)
            placeholder_table.dataframe(df, use_container_width=True)

            # Update agent analysis
            if explain_data:
                agents = explain_data.get("agents", [])

                # Create agent analysis display
                analysis_html = f"""
                <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <h4>🎯 Decision: {decision.get('action', 'HOLD')} ({decision.get('confidence', 0):.1%})</h4>
                    <p><strong>Reason:</strong> {decision.get('reason', 'N/A')}</p>
                    <p><strong>Cache:</strong> {cache_badge}</p>
                </div>

                <div style="margin-top: 10px;">
                    <h5>🤖 Agent Contributions:</h5>
                """

                for agent in agents:
                    score = agent.get('score', 0)
                    weight = agent.get('weight', 0)
                    contribution = score * weight
                    reason = agent.get('reason', '')

                    # Color based on contribution
                    color = "#28a745" if contribution > 0 else "#dc3545" if contribution < 0 else "#6c757d"

                    analysis_html += f"""
                    <div style="background: {color}15; border-left: 3px solid {color}; padding: 8px; margin: 5px 0; border-radius: 3px;">
                        <strong>{agent.get('agent', 'Unknown')}:</strong> {contribution:.3f} (score: {score:.3f}, weight: {weight:.2f})<br>
                        <small style="color: #666;">{reason}</small>
                    </div>
                    """

                analysis_html += "</div>"
                agent_analysis_placeholder.markdown(analysis_html, unsafe_allow_html=True)

            # Update confidence chart
            if len(confidence_history) > 1:
                chart_df = pd.DataFrame(confidence_history)
                chart_df = chart_df.set_index("step")
                confidence_chart_placeholder.line_chart(chart_df[["confidence", "price"]])

            # Update main chart
            if len(confidence_history) > 1:
                chart_df = pd.DataFrame(confidence_history)
                chart_df = chart_df.set_index("step")
                chart_placeholder.line_chart(chart_df)

            # Update status with detailed info
            action_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(decision.get('action', 'HOLD'), "🟡")
            if trading_mode == "Fixed Steps":
                step_display = f"**Step {event_count}/{total_steps}**"
            else:
                step_display = f"**Trade #{event_count}**"
            status_text.markdown(f"{step_display} - {action_emoji} **{decision.get('action', 'HOLD')}** at ${price:.2f} (Confidence: {decision.get('confidence', 0):.1%})")

            # Add a small delay for demo purposes
            time.sleep(0.5)

        # Final status based on trading mode
        if trading_mode == "Fixed Steps":
            progress_bar.progress(1.0)
            status_text.markdown(f"✅ **Fixed Simulation Complete!** Processed {event_count} trading decisions with live agent analysis.")
        else:
            if not trading_active:
                status_text.markdown(f"🛑 **Continuous Trading Stopped!** Processed {event_count} trading decisions total.")
            else:
                status_text.markdown(f"🎯 **Continuous Trading Finished!** Reached target of {max_trades} trades.")

        # Final summary
        if rows:
            buy_count = sum(1 for r in rows if r["action"] == "BUY")
            sell_count = sum(1 for r in rows if r["action"] == "SELL")
            hold_count = sum(1 for r in rows if r["action"] == "HOLD")

            mode_desc = "Fixed" if trading_mode == "Fixed Steps" else "Continuous"
            st.success(f"📊 **{mode_desc} Trading Summary**: {buy_count} BUY, {sell_count} SELL, {hold_count} HOLD decisions made with real-time agent reasoning!")

            # Show trading frequency
            if event_count > 1 and confidence_history:
                avg_confidence = sum(c['confidence'] for c in confidence_history) / len(confidence_history)
                st.info(f"📈 **Trading Stats**: Average confidence {avg_confidence:.1%}, {event_count} total decisions")

    except Exception as e:
        st.error(f"❌ Streaming error: {e}")
        status_text.markdown("❌ **Trading Failed** - Check API connection")

    # Clear stop button after completion
    if trading_mode == "Continuous Trading":
        stop_button_placeholder.empty()

st.divider()
st.subheader("Batch simulation (multi-symbol)")
batch_symbols = st.text_input("Symbols (comma-separated)", value="AAPL,MSFT,SPY")
steps = st.number_input("Steps", min_value=1, max_value=60, value=10, step=1)
if st.button("Run batch"):
    syms = [s.strip().upper() for s in batch_symbols.split(",") if s.strip()]
    try:
        result = simulate_batch(symbols=syms, steps=int(steps), cash=cash)
        st.success("Batch complete")

        # Process results with cache badges
        processed_results = []
        for item in result["results"]:
            cache_hit = item.get("cache_hit", False)
            cache_badge = "🟢 HIT" if cache_hit else "🔴 MISS"
            processed_item = item.copy()
            processed_item["cache_status"] = cache_badge
            processed_results.append(processed_item)

        df = pd.DataFrame(processed_results)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Batch simulation error: {e}")

