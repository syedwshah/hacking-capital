import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import generate_summaries, get_health

st.title("📊 Market Summaries")
st.markdown("AI-powered market analysis and insights")

# Check API health
try:
    health = get_health()
    if health.get("status") == "healthy":
        st.success("✅ API Connection Healthy")
    else:
        st.error("❌ API Connection Issue")
        st.stop()
except Exception as e:
    st.error(f"❌ API Connection Failed: {e}")
    st.stop()

# Controls section
st.markdown("---")
st.subheader("🔍 Generate Market Summaries")

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    symbol = st.text_input("Stock Symbol", value="AAPL", placeholder="e.g., AAPL, TSLA, GOOGL")

with col2:
    granularity = st.selectbox(
        "Granularity",
        options=["daily", "weekly", "monthly"],
        index=0,
        help="Time period for analysis"
    )

with col3:
    period_days = st.selectbox(
        "Period (days)",
        options=[7, 14, 30, 60, 90],
        index=2,
        help="Historical data period to analyze"
    )

with col4:
    generate_button = st.button("🚀 Generate Summary", type="primary")

# Generate summaries
if generate_button:
    with st.spinner("🔄 Generating AI-powered market analysis..."):
        try:
            result = generate_summaries(symbol, granularity, period_days)
            summaries = result.get("summaries", [])
            ai_powered = result.get("ai_powered", False)

            if summaries:
                st.success(f"✅ Generated {len(summaries)} {granularity} summaries for {symbol}")

                # Store in session state for display
                st.session_state[f"summaries_{symbol}_{granularity}"] = {
                    "data": summaries,
                    "timestamp": datetime.now(),
                    "ai_powered": ai_powered,
                    "symbol": symbol,
                    "granularity": granularity
                }
            else:
                st.warning("⚠️ No data available for the specified parameters")

        except Exception as e:
            st.error(f"❌ Failed to generate summaries: {e}")

# Display stored summaries
st.markdown("---")
st.subheader("📈 Recent Summaries")

# Check for stored summaries
stored_keys = [k for k in st.session_state.keys() if k.startswith("summaries_")]

if stored_keys:
    # Sort by timestamp (most recent first)
    stored_summaries = []
    for key in stored_keys:
        data = st.session_state[key]
        stored_summaries.append({
            "key": key,
            "symbol": data["symbol"],
            "granularity": data["granularity"],
            "timestamp": data["timestamp"],
            "count": len(data["data"]),
            "ai_powered": data["ai_powered"]
        })

    stored_summaries.sort(key=lambda x: x["timestamp"], reverse=True)

    # Summary selector
    summary_options = [f"{s['symbol']} ({s['granularity']}) - {s['count']} periods - {s['timestamp'].strftime('%H:%M:%S')}"
                      for s in stored_summaries]
    selected_summary = st.selectbox("Select Summary to View:", summary_options)

    if selected_summary:
        # Find the corresponding data
        selected_idx = summary_options.index(selected_summary)
        selected_key = stored_summaries[selected_idx]["key"]
        summary_data = st.session_state[selected_key]

        # Display summary info
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.metric("Symbol", summary_data["symbol"])
        with info_col2:
            st.metric("Granularity", summary_data["granularity"].title())
        with info_col3:
            ai_status = "🤖 AI-Powered" if summary_data["ai_powered"] else "📊 Basic Analysis"
            st.metric("Analysis Type", ai_status)

        # Display each summary period
        summaries = summary_data["data"]

        for i, summary in enumerate(summaries):
            period = summary["period"]
            stats = summary["stats"]

            with st.expander(f"📅 {period} - {summary['symbol']}", expanded=(i==0)):

                # Key metrics in columns
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                with metric_col1:
                    price_change = ((stats["close"] - stats["open"]) / stats["open"]) * 100
                    st.metric("Price Change", f"{price_change:+.2f}%",
                             delta=f"{stats['close']:.2f}", delta_color="normal")
                    st.metric("High/Low", f"{stats['high']:.2f}/{stats['low']:.2f}")

                with metric_col2:
                    st.metric("Mean Return", f"{stats['mean_return']:.4f}")
                    st.metric("Volatility", f"{stats['volatility']:.4f}")

                with metric_col3:
                    st.metric("Total Volume", f"{stats['total_volume']:,.0f}")
                    st.metric("Data Points", stats["count"])

                with metric_col4:
                    st.metric("Price Range", f"{stats['price_range']:.2f}")
                    st.metric("Trend Strength", f"{stats['trend_strength']:.4f}")

                # AI Summary (if available)
                if summary_data["ai_powered"] and summary.get("ai_summary"):
                    st.markdown("### 🤖 AI Analysis")
                    st.info(summary["ai_summary"])
                else:
                    st.markdown("### 📊 Basic Stats")
                    st.write(f"• **Close Price**: ${stats['close']:.2f}")
                    st.write(f"• **Average Price**: ${stats['mean_close']:.2f}")
                    st.write(f"• **Trading Volume**: {stats['total_volume']:,.0f}")

                # Mini chart for the period
                if stats["count"] > 1:
                    st.markdown("### 📈 Price Movement")
                    # Create a simple price chart using available data
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=[f"Day {j+1}" for j in range(stats["count"])],
                        y=[stats["open"], stats["close"]],  # Simplified - just open/close
                        mode='lines+markers',
                        name='Price',
                        line=dict(color='#17BECF', width=2)
                    ))
                    fig.update_layout(
                        title="Price Trend",
                        height=200,
                        margin=dict(l=0, r=0, t=30, b=0),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"summary_chart_{period}_{i}")

        # Export option
        if st.button("💾 Export Summaries to CSV"):
            # Convert to DataFrame for export
            export_data = []
            for summary in summaries:
                row = {
                    "Symbol": summary["symbol"],
                    "Granularity": summary["granularity"],
                    "Period": summary["period"],
                    **summary["stats"]
                }
                if summary.get("ai_summary"):
                    row["AI_Summary"] = summary["ai_summary"]
                export_data.append(row)

            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{summary_data['symbol']}_{summary_data['granularity']}_summaries.csv",
                mime="text/csv"
            )

else:
    st.info("💡 Generate your first market summary above to get started!")

# Footer
st.markdown("---")
st.caption("🎯 **AI-Powered Analysis**: When OpenAI API is available, summaries include intelligent market insights and trend analysis.")


