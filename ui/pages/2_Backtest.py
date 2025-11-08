import streamlit as st
import pandas as pd
import time
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.state import job_manager
from ui.api_client import fetch_data

st.title("🧪 Background Backtest")
st.write("Run deterministic backtests in the background while navigating the app.")

# Input section
st.header("⚙️ Backtest Configuration")
symbol = st.text_input("Symbol", value="AAPL", key="backtest_symbol")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", value=pd.to_datetime("2020-01-01"), key="backtest_start")
with col2:
    end_date = st.date_input("End date", value=pd.to_datetime("2020-02-01"), key="backtest_end")
initial_cash = st.number_input("Initial cash", value=1000.0, step=100.0, key="backtest_cash")

# Start background job
if st.button("🚀 Start Background Backtest", type="primary", use_container_width=True):
    job_id = job_manager.start_backtest_job(
        symbol=symbol,
        start_date=str(start_date),
        end_date=str(end_date),
        initial_cash=initial_cash
    )
    st.success(f"✅ Backtest started! Job ID: `{job_id[:8]}...`")
    st.info("🔄 You can navigate to other pages while the backtest runs in the background.")
    time.sleep(1)  # Brief pause to show message
    st.rerun()

# Active jobs section
active_jobs = job_manager.get_active_jobs()
if active_jobs:
    st.header("🔄 Active Backtests")
    st.info(f"📊 {len(active_jobs)} backtest(s) currently running in the background.")

    for job_id in active_jobs:
        job = job_manager.get_job_status(job_id)
        if job:
            with st.expander(f"🕐 {job['symbol']} - {job['start_date']} to {job['end_date']} (ID: {job_id[:8]}...)", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", job["status"].title())
                with col2:
                    st.metric("Progress", f"{job['progress']}%")
                with col3:
                    created_at = datetime.fromisoformat(job["created_at"])
                    st.metric("Started", created_at.strftime("%H:%M:%S"))

                # Progress bar
                st.progress(job["progress"] / 100)

                # Show progress message if available
                if job.get("progress_message"):
                    st.info(f"📊 {job['progress_message']}")
                elif job["progress"] < 100:
                    st.info("🔄 Processing data points...")

                if st.button(f"🔄 Refresh Status", key=f"refresh_{job_id}"):
                    st.rerun()

# Completed jobs section
all_jobs = job_manager.get_jobs()
completed_jobs = {jid: job for jid, job in all_jobs.items() if job["status"] in ["completed", "failed"]}

if completed_jobs:
    st.header("📚 Backtest History")

    # Sort by completion time (most recent first)
    sorted_jobs = sorted(
        completed_jobs.items(),
        key=lambda x: x[1].get("completed_at", x[1]["created_at"]),
        reverse=True
    )

    for job_id, job in sorted_jobs[:10]:  # Show last 10 jobs
        status_icon = "✅" if job["status"] == "completed" else "❌"
        symbol = job["symbol"]
        date_range = f"{job['start_date']} to {job['end_date']}"

        with st.expander(f"{status_icon} {symbol} - {date_range} ({job_id[:8]}...)", expanded=False):
            col1, col2, col3, col4 = st.columns(4)

            # Job metadata
            created_at = datetime.fromisoformat(job["created_at"])
            with col1:
                st.metric("Status", job["status"].title())
                st.caption(f"Started: {created_at.strftime('%m/%d %H:%M')}")

            if job["status"] == "completed":
                result = job["result"]

                # Key metrics
                with col2:
                    st.metric("Final Equity", f"${result.get('final_equity', 0):,.2f}")
                with col3:
                    st.metric("Strategy Return", f"{result.get('strategy_return', 0):.1%}")
                with col4:
                    st.metric("Max Drawdown", f"{result.get('max_drawdown', 0):.1%}")

                # Performance summary
        st.success(result.get("summary", ""))

                # Equity curve with buy-and-hold comparison
        snapshots = result.get("snapshots", [])
        if snapshots:
                    st.subheader("📈 Performance Comparison")

                    # Fetch price data for buy-and-hold calculation
                    try:
                        price_data = fetch_data(symbol, job["start_date"], job["end_date"], "daily")
                        price_df = pd.DataFrame(price_data["rows"])
                        price_df["ts"] = pd.to_datetime(price_df["ts"])

                        # Calculate buy-and-hold: buy at first price, hold throughout
                        if not price_df.empty:
                            initial_price = price_df.iloc[0]["close"]
                            shares = job["initial_cash"] / initial_price
                            price_df["buy_hold_value"] = shares * price_df["close"]

                            # Merge with snapshots
                            snapshot_df = pd.DataFrame(snapshots)
                            snapshot_df["ts"] = pd.to_datetime(snapshot_df["ts"])

                            merged_df = pd.merge(snapshot_df, price_df[["ts", "buy_hold_value"]], on="ts", how="left")
                            merged_df = merged_df.set_index("ts")

                            st.line_chart(merged_df[["equity", "buy_hold_value"]], use_container_width=True)
                        else:
                            # Fallback to just strategy equity
                            df = pd.DataFrame(snapshots)
                            df["ts"] = pd.to_datetime(df["ts"])
                            df = df.set_index("ts")
                            st.line_chart(df[["equity"]], use_container_width=True)
                    except Exception:
                        # Fallback if price fetch fails
            df = pd.DataFrame(snapshots)
            df["ts"] = pd.to_datetime(df["ts"])
            df = df.set_index("ts")
                        st.line_chart(df[["equity"]], use_container_width=True)

                # Buy-and-hold comparison
                buy_hold_return = result.get('buy_hold_return', 0)
                strategy_return = result.get('strategy_return', 0)
                if buy_hold_return != 0:
                    beat_market = strategy_return > buy_hold_return
                    color = "green" if beat_market else "red"
                    st.metric(
                        "vs Buy & Hold",
                        f"{buy_hold_return:.1%}",
                        f"{'+' if strategy_return - buy_hold_return > 0 else ''}{(strategy_return - buy_hold_return):.1%}",
                        color
                    )

                # Trades table
                trades = result.get("trades", [])
                if trades:
                    st.subheader("💼 Trade History")
                    trades_df = pd.DataFrame(trades)

                    # Color code actions
                    def color_trade_action(val):
                        if val == "BUY":
                            return "background-color: #d4edda; color: #155724"
                        elif val == "SELL":
                            return "background-color: #f8d7da; color: #721c24"
                        return ""

                    styled_trades = trades_df.style.apply(
                        lambda x: [color_trade_action(val) if col == "action" else "" for col, val in x.items()],
                        axis=1
                    ).format({
                        "price": "${:.2f}",
                        "quantity": "{:.4f}",
                        "fees": "${:.2f}"
                    })

                    st.dataframe(styled_trades, use_container_width=True)

                    # Trade summary
                    buy_trades = len([t for t in trades if t["action"] == "BUY"])
                    sell_trades = len([t for t in trades if t["action"] == "SELL"])
                    total_fees = sum(t.get("fees", 0) for t in trades)

                    st.caption(f"**Trade Summary**: {buy_trades} buys, {sell_trades} sells, ${total_fees:.2f} in fees")

                # Decision analysis section
                st.subheader("🧠 Decision Analysis")
                st.write("**Why were these decisions made?**")

                # Get trading decisions that would have been made during this period
                try:
                    from ui.api_client import decide

                    # Sample some key decision points (first day of each month)
                    analysis_dates = pd.date_range(start=job["start_date"], end=job["end_date"], freq='MS')[:3]

                    for analysis_date in analysis_dates:
                        try:
                            # Get decision for this date (using first day of month as proxy)
                            decision = decide(symbol, "daily", job["initial_cash"])

                            with st.expander(f"Decision Analysis - {analysis_date.strftime('%Y-%m-%d')}", expanded=False):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    action_color = "🟢" if decision.get("action") == "BUY" else "🔴" if decision.get("action") == "SELL" else "🟡"
                                    st.metric("Action", f"{action_color} {decision.get('action')}")
                                with col2:
                                    st.metric("Confidence", f"{decision.get('confidence', 0):.1%}")
                                with col3:
                                    st.metric("Quantity", f"{decision.get('quantity', 0):.2f}")

                                # Show reasoning
                                reason = decision.get("reason", "")
                                if reason:
                                    st.write("**Reasoning:**")
                                    st.code(reason, language="text")

                                st.caption("*Note: This shows what the agent would decide at this point in time*")

                        except Exception as e:
                            st.warning(f"Could not analyze decisions for {analysis_date.strftime('%Y-%m-%d')}: {e}")

    except Exception as e:
                    st.warning(f"Decision analysis unavailable: {e}")

            elif job["status"] == "failed":
                with col2:
                    st.error("❌ Failed")
                    if job.get("error"):
                        st.caption(f"Error: {job['error']}")

    if len(completed_jobs) > 10:
        st.info(f"Showing 10 most recent jobs. Total completed: {len(completed_jobs)}")

# Cleanup old jobs
if st.button("🧹 Cleanup Old Jobs (24h+)", help="Remove completed jobs older than 24 hours"):
    job_manager.cleanup_old_jobs(24)
    st.success("✅ Old jobs cleaned up!")
    time.sleep(1)
    st.rerun()

# Help section
st.markdown("---")
st.subheader("💡 How Background Backtests Work")
st.markdown("""
**🎯 Headless Execution**: Start a backtest and navigate to other pages while it runs in the background.

**📊 Persistent Results**: Completed backtests remain available until you close the browser or clear old jobs.

**🧠 Decision Analysis**: View detailed reasoning for why specific trading decisions were made during the backtest period.

**📈 Performance Tracking**: Compare strategy performance against buy-and-hold benchmarks with visual equity curves.

**🔄 Real-time Updates**: Active jobs show progress and can be monitored across page navigation.
""")

# Auto-refresh for active jobs
if active_jobs:
    time.sleep(2)  # Auto-refresh every 2 seconds when there are active jobs
    st.rerun()


