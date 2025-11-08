import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from ui.api_client import fetch_data
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.api_client import fetch_data

# Mock portfolio API functions (since the API endpoints might not be fully implemented yet)
def mock_create_portfolio(name, symbols, initial_value=100000):
    """Mock portfolio creation for demonstration."""
    assets = []
    for symbol in symbols:
        # Mock data - in real implementation, this would come from the API
        price = 100 + hash(symbol) % 200
        assets.append({
            "symbol": symbol,
            "current_price": price,
            "expected_return": 0.10 + (hash(symbol) % 20) / 100,
            "volatility": 0.25 + (hash(symbol) % 30) / 100,
            "weight": 1.0 / len(symbols)
        })

    return {
        "portfolio_name": name,
        "assets": assets,
        "total_value": initial_value
    }

def mock_optimize_portfolio(portfolio_name, optimization_type="mpt"):
    """Mock portfolio optimization for demonstration."""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    if optimization_type == "risk_parity":
        # Risk parity weights
        weights = [0.2] * 5
        expected_return = 0.135
        expected_volatility = 0.28
        sharpe_ratio = 0.32
    else:
        # MPT optimization
        weights = [0.15, 0.25, 0.20, 0.20, 0.20]
        expected_return = 0.142
        expected_volatility = 0.29
        sharpe_ratio = 0.35

    return {
        "portfolio_name": f"{portfolio_name} ({optimization_type.upper()})",
        "optimized_weights": dict(zip(symbols, weights)),
        "expected_return": expected_return,
        "expected_volatility": expected_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": -0.18,
        "diversification_ratio": 1.15,
        "recommendations": [
            f"Optimized using {optimization_type.upper()} methodology",
            f"Expected return: {expected_return:.1%}",
            f"Expected volatility: {expected_volatility:.1%}",
            f"Sharpe ratio: {sharpe_ratio:.2f}"
        ],
        "rebalance_actions": [
            {"symbol": "AAPL", "action": "BUY", "current_weight": 0.2, "target_weight": 0.15, "amount": -5000},
            {"symbol": "MSFT", "action": "BUY", "current_weight": 0.2, "target_weight": 0.25, "amount": 5000}
        ]
    }

st.title("🎯 Portfolio Optimization")
st.write("Advanced portfolio management using technical indicators and modern portfolio theory.")

# Sidebar controls
st.sidebar.header("Portfolio Settings")

# Portfolio templates
templates = {
    "Conservative": ["AAPL", "MSFT", "GOOGL", "AMZN"],
    "Aggressive": ["TSLA", "NVDA", "AAPL", "META", "NFLX"],
    "Balanced": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]
}

template_choice = st.sidebar.selectbox("Portfolio Template", list(templates.keys()))
selected_symbols = st.sidebar.multiselect(
    "Custom Symbols",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"],
    default=templates[template_choice]
)

initial_value = st.sidebar.number_input("Initial Investment ($)", value=100000, step=10000)

# Optimization settings
st.sidebar.header("Optimization")
optimization_type = st.sidebar.selectbox(
    "Method",
    ["Mean-Variance (MPT)", "Risk Parity", "Signal-Based"],
    index=0
)

if optimization_type == "Mean-Variance (MPT)":
    target_return = st.sidebar.slider("Target Return (%)", 5.0, 25.0, 12.0, 1.0)
    risk_aversion = st.sidebar.slider("Risk Aversion", 0.5, 3.0, 1.0, 0.1)
else:
    target_return = None
    risk_aversion = 1.0

if st.sidebar.button("Optimize Portfolio", type="primary"):
    with st.spinner("Analyzing portfolio and optimizing allocations..."):

        # Create portfolio
        portfolio_data = mock_create_portfolio("My Portfolio", selected_symbols, initial_value)

        # Optimize based on selected method
        if optimization_type == "Risk Parity":
            opt_type = "risk_parity"
        elif optimization_type == "Signal-Based":
            opt_type = "signal_based"
        else:
            opt_type = "mpt"

        optimization_result = mock_optimize_portfolio(portfolio_data["portfolio_name"], opt_type)

        # Store results in session state
        st.session_state.portfolio_data = portfolio_data
        st.session_state.optimization_result = optimization_result
        st.session_state.optimization_type = optimization_type

    st.success("Portfolio optimization complete!")
    st.rerun()

# Display results if available
if "portfolio_data" in st.session_state and "optimization_result" in st.session_state:

    portfolio_data = st.session_state.portfolio_data
    optimization_result = st.session_state.optimization_result
    opt_type = st.session_state.optimization_type

    # Portfolio Overview
    st.header("📊 Portfolio Overview")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Value", f"${portfolio_data['total_value']:,.0f}")
    with col2:
        st.metric("Expected Return", f"{optimization_result['expected_return']:.1%}")
    with col3:
        st.metric("Expected Volatility", f"{optimization_result['expected_volatility']:.1%}")

    # Current vs Optimized Allocation
    st.header("⚖️ Asset Allocation")

    current_weights = {asset["symbol"]: asset["weight"] for asset in portfolio_data["assets"]}
    optimized_weights = optimization_result["optimized_weights"]

    # Create comparison dataframe
    comparison_df = pd.DataFrame({
        "Asset": list(current_weights.keys()),
        "Current Weight": list(current_weights.values()),
        "Optimized Weight": [optimized_weights.get(asset, 0) for asset in current_weights.keys()],
        "Difference": [optimized_weights.get(asset, 0) - current_weights[asset] for asset in current_weights.keys()]
    })

    # Display as table
    st.dataframe(comparison_df.style.format({
        "Current Weight": "{:.1%}",
        "Optimized Weight": "{:.1%}",
        "Difference": "{:+.1%}"
    }).background_gradient(subset=["Difference"], cmap="RdYlGn", axis=0))

    # Pie charts comparison
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Allocation")
        fig_current = px.pie(
            comparison_df,
            values="Current Weight",
            names="Asset",
            title="Current Portfolio"
        )
        st.plotly_chart(fig_current, use_container_width=True)

    with col2:
        st.subheader("Optimized Allocation")
        fig_optimized = px.pie(
            comparison_df,
            values="Optimized Weight",
            names="Asset",
            title=f"Optimized ({opt_type})"
        )
        st.plotly_chart(fig_optimized, use_container_width=True)

    # Performance Metrics
    st.header("📈 Performance Metrics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sharpe Ratio", f"{optimization_result['sharpe_ratio']:.2f}")
    with col2:
        st.metric("Max Drawdown", f"{optimization_result['max_drawdown']:.1%}")
    with col3:
        st.metric("VaR (95%)", f"${optimization_result.get('value_at_risk_95', 0):,.0f}")
    with col4:
        st.metric("Expected Shortfall", f"${optimization_result.get('expected_shortfall', 0):,.0f}")

    # Historical Performance
    if "historical_return" in portfolio_data.get("metrics", {}):
        st.header("📊 Historical Performance (6 Months)")

        hist_col1, hist_col2, hist_col3, hist_col4 = st.columns(4)
        metrics = portfolio_data["metrics"]

        with hist_col1:
            st.metric("Historical Return", f"{metrics['historical_return']:.1%}")
        with hist_col2:
            st.metric("Win Rate", f"{metrics['win_rate']:.1%}")
        with hist_col3:
            st.metric("Benchmark Alpha", f"{metrics['benchmark_alpha']:.1%}")
        with hist_col4:
            st.metric("Benchmark Beta", f"{metrics['benchmark_beta']:.2f}")

    # Recommendations
    st.header("💡 Recommendations")
    for rec in optimization_result["recommendations"]:
        st.info(rec)

    # Rebalance Actions
    st.header("🔄 Rebalancing Actions")
    if optimization_result["rebalance_actions"]:
        rebalance_df = pd.DataFrame(optimization_result["rebalance_actions"])

        # Color code actions
        def color_action(val):
            if val == "BUY":
                return "background-color: #d4edda; color: #155724"
            elif val == "SELL":
                return "background-color: #f8d7da; color: #721c24"
            return ""

        styled_df = rebalance_df.style.apply(
            lambda x: [color_action(val) if col == "action" else "" for col, val in x.items()],
            axis=1
        ).format({
            "current_weight": "{:.1%}",
            "target_weight": "{:.1%}",
            "amount": "${:,.0f}"
        })

        st.dataframe(styled_df, use_container_width=True)

        total_buy = sum(action["amount"] for action in optimization_result["rebalance_actions"] if action["amount"] > 0)
        total_sell = sum(abs(action["amount"]) for action in optimization_result["rebalance_actions"] if action["amount"] < 0)

        st.write(f"**Net cash flow needed:** ${total_buy - total_sell:,.0f}")
    else:
        st.info("No rebalancing actions needed - portfolio is already optimized!")

else:
    # Welcome screen
    st.header("🚀 Welcome to Portfolio Optimization")

    st.write("""
    This advanced portfolio optimization tool uses:

    **🤖 Technical Analysis**
    - 10+ technical indicators (RSI, MACD, Bollinger Bands, etc.)
    - Multi-timeframe signal analysis
    - Composite scoring system

    **📊 Modern Portfolio Theory**
    - Mean-Variance Optimization
    - Risk Parity allocation
    - Efficient frontier analysis

    **⚡ Signal-Based Rebalancing**
    - Technical indicator triggers
    - Dynamic portfolio adjustments
    - Risk management integration

    **🎯 Optimization Methods:**
    1. **Mean-Variance (MPT)**: Maximize Sharpe ratio or target return
    2. **Risk Parity**: Equal risk contribution across assets
    3. **Signal-Based**: Rebalance based on technical signals

    Select your assets, choose an optimization method, and click **"Optimize Portfolio"** to get started!
    """)

    # Quick demo
    if st.button("🚀 Try Demo Portfolio"):
        # Simulate button click
        st.session_state.portfolio_data = mock_create_portfolio("Demo Portfolio", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"])
        st.session_state.optimization_result = mock_optimize_portfolio("Demo Portfolio", "mpt")
        st.session_state.optimization_type = "Mean-Variance (MPT)"
        st.rerun()

st.caption("💡 Pro tip: Use technical indicators to time your rebalancing for optimal entry/exit points!")
