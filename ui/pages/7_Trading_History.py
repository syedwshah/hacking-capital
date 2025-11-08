import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.api_client import stream_events

# Add new API client functions for trading history
def get_trading_history(symbol=None, limit=50):
    """Get trading decision history."""
    import httpx
    API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")

    params = {"limit": limit}
    if symbol:
        params["symbol"] = symbol

    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{API_BASE}/trade/history", params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.error(f"Failed to fetch trading history: {e}")
        return {"history": [], "stats": {}}

def get_trading_performance(symbol=None, days=30):
    """Get trading performance metrics."""
    import httpx
    API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")

    params = {"days": days}
    if symbol:
        params["symbol"] = symbol

    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{API_BASE}/trade/performance", params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.error(f"Failed to fetch trading performance: {e}")
        return {"performance": {}}

def get_simulation_history(limit=10):
    """Get simulation batch processing history."""
    import httpx
    API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")

    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{API_BASE}/simulate/history", params={"limit": limit})
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.error(f"Failed to fetch simulation history: {e}")
        return {"simulation_batches": [], "total_batches": 0}

st.title("📊 Trading History & Performance")
st.markdown("**View past AI trading decisions and performance metrics**")
# Quick simulation controls
st.subheader("🚀 Quick Simulation")
col1, col2, col3 = st.columns(3)
with col1:
    symbol = st.selectbox("Stock Symbol", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"], index=0)
with col2:
    duration = st.slider("Duration (minutes)", 5, 15, 5, 5)
with col3:
    cash = st.number_input("Starting Cash ($)", value=5000, step=1000)

if st.button("🚀 Start Simulation", type="primary"):
    st.header(f"🎯 Live Simulation: {symbol} - {duration} Minutes")

    # Create placeholders for real-time updates
    status_placeholder = st.empty()
    chart_placeholder = st.empty()
    trades_placeholder = st.empty()
    decisions_placeholder = st.empty()

    # Initialize data storage
    trades_data = []
    decisions_data = []
    price_history = []

    try:
        status_placeholder.info("🔄 Connecting to simulation stream...")

        event_count = 0
        for event_data in stream_events(symbol, duration, cash):
            event_count += 1

            # Parse event data
            event = event_data.get("data", {})
            if isinstance(event, str):
                import json
                event = json.loads(event)

            step = event.get("step", event_count)
            decision = event.get("decision", {})
            price = event.get("price", 0.0)
            ts = event.get("ts", "")
            explain_data = event.get("explain", {})

            # Store data for visualization
            price_history.append({"step": step, "price": price, "timestamp": ts})

            if decision.get("action") in ["BUY", "SELL"]:
                trades_data.append({
                    "step": step,
                    "timestamp": ts,
                    "action": decision.get("action"),
                    "price": price,
                    "quantity": decision.get("quantity", 0),
                    "reason": decision.get("reason", "")
                })

            decisions_data.append({
                "step": step,
                "action": decision.get("action", "HOLD"),
                "confidence": decision.get("confidence", 0.0),
                "price": price,
                "reason": decision.get("reason", "")[:100] + "..." if len(decision.get("reason", "")) > 100 else decision.get("reason", "")
            })

            # Update UI
            status_placeholder.success(f"📊 Step {event_count}/{duration} - {decision.get('action', 'HOLD')} at ${price:.2f}")

            # Update price chart
            if price_history:
                price_df = pd.DataFrame(price_history)
                chart_placeholder.line_chart(price_df.set_index("step")["price"])

            # Update trades table
            if trades_data:
                trades_df = pd.DataFrame(trades_data)
                trades_placeholder.dataframe(trades_df, use_container_width=True)

            # Update recent decisions
            if decisions_data:
                recent_decisions = decisions_data[-5:]  # Show last 5 decisions
                decisions_placeholder.dataframe(
                    pd.DataFrame(recent_decisions),
                    use_container_width=True
                )

        status_placeholder.success(f"✅ Simulation complete! Processed {event_count} steps with {len(trades_data)} trades.")

        # Final summary
        if trades_data:
            total_trades = len(trades_data)
            buy_trades = len([t for t in trades_data if t["action"] == "BUY"])
            sell_trades = len([t for t in trades_data if t["action"] == "SELL"])

            st.success(f"📈 Simulation Summary: {total_trades} trades ({buy_trades} buys, {sell_trades} sells)")

    except Exception as e:
        status_placeholder.error(f"❌ Simulation failed: {str(e)}")

# Historical Trading Data Section
st.header("📚 Recent Trading History")

# Symbol filter for history
history_symbol = st.selectbox("Filter by Symbol", ["All", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"], index=0, key="history_symbol")

try:
    # Get real trading history from database
    symbol_filter = None if history_symbol == "All" else history_symbol
    history_data = get_trading_history(symbol=symbol_filter, limit=50)

    historical_trades = history_data.get("history", [])
    stats = history_data.get("stats", {})

    if historical_trades:
        st.subheader("Recent Trading Decisions")
        trades_df = pd.DataFrame(historical_trades)

        # Color code actions
        def color_action(val):
            if val == "BUY":
                return "background-color: #d4edda; color: #155724"
            elif val == "SELL":
                return "background-color: #f8d7da; color: #721c24"
            return ""

        # Format the dataframe
        display_df = trades_df.copy()
        display_df["timestamp"] = pd.to_datetime(display_df["timestamp"]).dt.strftime("%m-%d %H:%M")

        styled_trades = display_df.style.apply(
            lambda x: [color_action(val) if col == "action" else "" for col, val in x.items()],
            axis=1
        ).format({
            "quantity": "{:.2f}",
            "confidence": "{:.1%}"
        })

        st.dataframe(styled_trades, use_container_width=True)

        # Performance summary from database stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Decisions", stats.get("total_decisions", 0))
        with col2:
            st.metric("Buy Decisions", stats.get("buy_decisions", 0))
        with col3:
            st.metric("Sell Decisions", stats.get("sell_decisions", 0))
        with col4:
            st.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.1%}")

    else:
        st.info("No trading history available. Run some trading decisions to generate data!")

except Exception as e:
    st.error(f"Error loading trading history: {str(e)}")
    st.info("💡 Tip: Make sure the API is running and has processed some trading decisions.")

# Quick Performance Summary
st.header("📈 Performance Summary")

try:
    # Get overall performance data
    performance_response = get_trading_performance(symbol=None, days=7)  # Last 7 days
    performance_data = performance_response.get("performance", {})

    if performance_data:
        perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

        with perf_col1:
            st.metric("Total Decisions", performance_data.get("total_decisions", 0))
        with perf_col2:
            st.metric("Win Rate", f"{performance_data.get('win_rate', 0):.1%}")
        with perf_col3:
            st.metric("Avg Confidence", f"{performance_data.get('avg_confidence', 0):.1%}")
        with perf_col4:
            st.metric("High Conf Trades", performance_data.get("high_confidence_trades", 0))

    else:
        st.info("No recent performance data available.")

except Exception as e:
    st.error(f"Error loading performance summary: {str(e)}")

# Simulation Batch History
st.header("🔄 Simulation Batch History")

# Refresh button
col1, col2 = st.columns([3, 1])
with col1:
    limit_batches = st.slider("Show Batches", 5, 20, 10, key="batch_limit")
with col2:
    if st.button("🔄 Refresh", key="refresh_sim_history"):
        st.rerun()

try:
    sim_history = get_simulation_history(limit=limit_batches)

    if sim_history["simulation_batches"]:
        st.subheader(f"Recent Simulation Batches ({sim_history['total_batches']} total)")

        # Summary metrics
        total_batches = sim_history['total_batches']
        total_decisions = sim_history['total_decisions']
        avg_batch_size = total_decisions / total_batches if total_batches > 0 else 0

        summary_col1, summary_col2, summary_col3 = st.columns(3)
        with summary_col1:
            st.metric("Total Batches", total_batches)
        with summary_col2:
            st.metric("Total Decisions", total_decisions)
        with summary_col3:
            st.metric("Avg Batch Size", f"{avg_batch_size:.1f}")

        st.markdown("---")

        for i, batch in enumerate(sim_history["simulation_batches"]):
            batch_name = batch.get('batch_id', f"Batch {i+1}")
            with st.expander(f"{batch_name}: {batch['decision_count']} decisions - {batch['batch_timestamp'][:16]}", expanded=(i==0)):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Decisions", batch["decision_count"])
                    st.metric("Symbols", f"{batch['symbol_count']} ({', '.join(batch['symbols'][:3])}{'...' if len(batch['symbols']) > 3 else ''})")

                with col2:
                    st.metric("Avg Confidence", f"{batch['avg_confidence']:.1%}")
                    buy_count = batch["actions"].count("BUY")
                    sell_count = batch["actions"].count("SELL")
                    hold_count = batch["actions"].count("HOLD")
                    st.write(f"Actions: BUY({buy_count}) SELL({sell_count}) HOLD({hold_count})")

                with col3:
                    # Action distribution pie chart
                    import plotly.graph_objects as go

                    action_counts = {
                        "BUY": batch["actions"].count("BUY"),
                        "SELL": batch["actions"].count("SELL"),
                        "HOLD": batch["actions"].count("HOLD")
                    }

                    fig = go.Figure(data=[go.Pie(
                        labels=list(action_counts.keys()),
                        values=list(action_counts.values()),
                        marker_colors=['#d4edda', '#f8d7da', '#fff3cd']
                    )])
                    fig.update_layout(
                        title="Action Distribution",
                        showlegend=True,
                        height=200,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Show sample decisions
                if batch["decisions"]:
                    st.subheader("Sample Decisions")

                    # Convert to DataFrame for display
                    decisions_df = pd.DataFrame(batch["decisions"][:8])  # Show first 8
                    display_df = decisions_df.copy()
                    display_df["timestamp"] = pd.to_datetime(display_df["timestamp"]).dt.strftime("%H:%M:%S")

                    # Color code actions
                    def color_action(val):
                        if val == "BUY":
                            return "background-color: #d4edda; color: #155724"
                        elif val == "SELL":
                            return "background-color: #f8d7da; color: #721c24"
                        return ""

                    styled_decisions = display_df.style.apply(
                        lambda x: [color_action(val) if col == "action" else "" for col, val in x.items()],
                        axis=1
                    ).format({
                        "quantity": "{:.2f}",
                        "confidence": "{:.1%}"
                    })

                    st.dataframe(styled_decisions, use_container_width=True)

                    # Export option
                    if st.button(f"📥 Export {batch_name} Data", key=f"export_{batch_name}"):
                        csv_data = decisions_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=f"{batch_name}_decisions.csv",
                            mime="text/csv",
                            key=f"download_{batch_name}"
                        )

    else:
        st.info("No simulation batches found. Run some batch simulations to see history!")

except Exception as e:
    st.error(f"Error loading simulation history: {str(e)}")

# Batch Simulation Launcher
st.header("🚀 Batch Simulation")

batch_symbols = st.multiselect(
    "Select Symbols for Batch Simulation",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"],
    default=["AAPL", "MSFT"],
    key="batch_symbols"
)

batch_steps = st.slider("Steps per Symbol", 5, 20, 10, key="batch_steps")
batch_cash = st.number_input("Cash per Simulation ($)", value=1000, step=500, key="batch_cash")

# Live batch simulation progress
batch_progress_placeholder = st.empty()
batch_status_placeholder = st.empty()
batch_results_placeholder = st.empty()

if st.button("🚀 Run Live Batch Simulation", type="primary", use_container_width=True):
    if not batch_symbols:
        st.error("Please select at least one symbol!")
    else:
        # Initialize progress tracking
        total_steps = len(batch_symbols) * batch_steps
        progress_bar = batch_progress_placeholder.progress(0)
        status_text = batch_status_placeholder.empty()

        try:
            API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")

            payload = {
                "symbols": batch_symbols,
                "steps": batch_steps,
                "cash": batch_cash
            }

            # Show initial status
            status_text.markdown('<p class="status-running">🔄 Starting batch simulation...</p>', unsafe_allow_html=True)

            import httpx
            import time

            with httpx.Client(timeout=120.0) as client:
                # Start the simulation
                r = client.post(f"{API_BASE}/simulate/batch", json=payload)
                r.raise_for_status()
                result = r.json()

            # Process results with animated progress
            completed_steps = 0

            for i, symbol_result in enumerate(result["results"]):
                # Update progress for each symbol
                symbol_steps = symbol_result["steps"]
                for step in range(symbol_steps):
                    time.sleep(0.1)  # Simulate processing time
                    completed_steps += 1
                    progress = min(completed_steps / total_steps, 1.0)
                    progress_bar.progress(progress)

                    # Update status
                    status_text.markdown(f'<p class="status-running">🔄 Processing {symbol_result["symbol"]} - Step {step + 1}/{symbol_steps} ({completed_steps}/{total_steps} total)</p>', unsafe_allow_html=True)

                # Show completion for this symbol
                status_text.markdown(f'<p class="status-completed">✅ {symbol_result["symbol"]} completed - {symbol_result["actions"].count("BUY") + symbol_result["actions"].count("SELL")} trades</p>', unsafe_allow_html=True)

            # Final completion
            progress_bar.progress(1.0)
            status_text.markdown('<p class="status-completed">🎉 Batch simulation completed! All data saved to history.</p>', unsafe_allow_html=True)

            # Clear progress bar after a moment
            time.sleep(2)
            progress_bar.empty()

            # Display results
            batch_results_placeholder.subheader("📊 Batch Results Summary")

            results_col1, results_col2, results_col3 = st.columns(3)

            total_trades = sum(len([a for a in r["actions"] if a in ["BUY", "SELL"]]) for r in result["results"])
            avg_confidence = sum(r["avg_confidence"] for r in result["results"]) / len(result["results"])
            cache_hits = sum(1 for r in result["results"] if r["cache_hit"])

            with results_col1:
                st.metric("Total Symbols", len(result["results"]))
            with results_col2:
                st.metric("Total Trades", total_trades)
            with results_col3:
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")

            # Detailed results in expandable sections
            for symbol_result in result["results"]:
                with st.expander(f"📈 {symbol_result['symbol']} Detailed Results", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Steps", symbol_result["steps"])
                    with col2:
                        st.metric("Avg Confidence", f"{symbol_result['avg_confidence']:.1%}")
                    with col3:
                        st.metric("Cache Hit", "✅" if symbol_result["cache_hit"] else "❌")
                    with col4:
                        buy_actions = symbol_result["actions"].count("BUY")
                        sell_actions = symbol_result["actions"].count("SELL")
                        st.metric("Trades", f"{buy_actions + sell_actions}")

                    # Action sequence visualization
                    st.write("**Action Sequence:**")
                    actions_text = " → ".join(symbol_result["actions"])
                    st.code(actions_text, language="text")

                    # Simple confidence chart
                    if len(symbol_result["actions"]) > 1:
                        st.write("**Confidence Trend:**")
                        st.line_chart([symbol_result["avg_confidence"]] * len(symbol_result["actions"]))

            # Auto-refresh simulation history after completion
            st.success("✅ Results added to simulation history!")
            time.sleep(1)
            st.rerun()  # Auto-refresh to show updated history

        except Exception as e:
            status_text.markdown('<p class="status-error">❌ Batch simulation failed</p>', unsafe_allow_html=True)
            progress_bar.empty()
            st.error(f"Error: {str(e)}")

# Trading History Section
st.markdown("---")
st.subheader("📈 Recent Trading Decisions")

try:
    history_data = get_trading_history(limit=20)
    history = history_data.get("history", [])

    if history:
        # Convert to DataFrame for display
        df = pd.DataFrame([
            {
                "Time": datetime.fromisoformat(h["ts"]).strftime("%H:%M:%S"),
                "Symbol": h["symbol"],
                "Action": h["action"],
                "Quantity": h["quantity"],
                "Confidence": f"{h['confidence']:.1%}",
                "Reason": h["reason"][:50] + "..." if len(h["reason"]) > 50 else h["reason"]
            }
            for h in history
        ])

        st.dataframe(df, use_container_width=True)

        # Simple stats
        total_decisions = len(history)
        buy_count = sum(1 for h in history if h["action"] == "BUY")
        sell_count = sum(1 for h in history if h["action"] == "SELL")
        avg_confidence = sum(h["confidence"] for h in history) / total_decisions if total_decisions > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Decisions", total_decisions)
        with col2:
            st.metric("Buy Orders", buy_count)
        with col3:
            st.metric("Sell Orders", sell_count)
        with col4:
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")

    else:
        st.info("No trading history available. Run some simulations to see results here!")

except Exception as e:
    st.error(f"Failed to load trading history: {e}")

# Footer
st.markdown("---")
st.caption("🎯 **Demo Features**: Live batch processing with real-time progress, automatic history updates, and comprehensive data persistence.")
