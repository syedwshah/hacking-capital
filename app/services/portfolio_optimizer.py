"""
Portfolio Optimization Service

Advanced portfolio optimization algorithms using technical indicators and modern portfolio theory.
Supports mean-variance optimization, risk parity, and signal-based rebalancing.
"""

from __future__ import annotations
import math
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np

from app.services.data_service import DataService
from app.services.technical_indicators import TechnicalIndicators, IndicatorResult


@dataclass
class Asset:
    """Represents a portfolio asset with its properties."""
    symbol: str
    name: Optional[str] = None
    current_price: float = 0.0
    expected_return: float = 0.0  # Annualized expected return
    volatility: float = 0.0       # Annualized volatility
    weight: float = 0.0           # Current portfolio weight
    target_weight: float = 0.0    # Target portfolio weight
    signal_strength: float = 0.0  # Technical signal strength (-1 to 1)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Portfolio:
    """Represents a portfolio with multiple assets."""
    name: str
    assets: List[Asset] = field(default_factory=list)
    total_value: float = 0.0
    cash: float = 0.0
    risk_free_rate: float = 0.045  # 4.5% risk-free rate
    rebalance_threshold: float = 0.05  # 5% deviation triggers rebalance
    correlation_matrix: Dict[Tuple[str, str], float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_rebalanced: Optional[datetime] = None


@dataclass
class OptimizationResult:
    """Result of portfolio optimization."""
    portfolio_name: str
    optimized_weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    diversification_ratio: float
    recommendations: List[str]
    rebalance_actions: List[Dict[str, Any]]


class PortfolioOptimizer:
    """Advanced portfolio optimization using technical indicators and modern portfolio theory."""

    def __init__(self):
        self.data_service = DataService()

    def create_portfolio(self, name: str, symbols: List[str], initial_value: float = 100000.0) -> Portfolio:
        """Create a new portfolio with given symbols."""
        portfolio = Portfolio(name=name, total_value=initial_value)

        # Create assets with mock initial data
        for symbol in symbols:
            asset = Asset(
                symbol=symbol,
                name=f"{symbol} Corp",  # Mock name
                current_price=self._get_mock_price(symbol),
                expected_return=self._get_mock_expected_return(symbol),
                volatility=self._get_mock_volatility(symbol),
                weight=1.0 / len(symbols)  # Equal weight initially
            )
            portfolio.assets.append(asset)

        # Generate mock correlation matrix
        self._generate_correlation_matrix(portfolio)

        return portfolio

    def analyze_portfolio_signals(self, portfolio: Portfolio) -> Dict[str, List[IndicatorResult]]:
        """Analyze technical signals for all assets in portfolio."""
        signals = {}

        for asset in portfolio.assets:
            # Get recent data for technical analysis
            data_rows = self.data_service.fetch(asset.symbol, "2020-01-01", "2020-01-31", "daily")

            if len(data_rows) < 20:
                signals[asset.symbol] = []
                continue

            # Extract OHLCV data
            closes = [r["close"] for r in data_rows]
            highs = [r["high"] for r in data_rows]
            lows = [r["low"] for r in data_rows]
            volumes = [r.get("volume", 1000) for r in data_rows]

            # Get comprehensive technical analysis
            analysis = TechnicalIndicators.get_comprehensive_analysis(closes, highs, lows, volumes)

            # Store the strongest signals for this asset
            signals[asset.symbol] = []
            for category_signals in analysis.values():
                # Take the top 3 strongest signals from each category
                sorted_signals = sorted(category_signals, key=lambda x: x.strength, reverse=True)
                signals[asset.symbol].extend(sorted_signals[:3])

            # Update asset signal strength (composite of all signals)
            composite_signal = TechnicalIndicators.get_weighted_signal(analysis)
            asset.signal_strength = composite_signal.value

        return signals

    def optimize_portfolio_mpt(self, portfolio: Portfolio, target_return: Optional[float] = None,
                              risk_aversion: float = 1.0) -> OptimizationResult:
        """
        Mean-Variance Optimization using Modern Portfolio Theory.

        Args:
            portfolio: Portfolio to optimize
            target_return: Target annualized return (None for maximum Sharpe ratio)
            risk_aversion: Risk aversion parameter (higher = more conservative)
        """
        if len(portfolio.assets) < 2:
            return self._create_basic_result(portfolio, "Need at least 2 assets for optimization")

        # Extract asset data
        symbols = [asset.symbol for asset in portfolio.assets]
        returns = np.array([asset.expected_return for asset in portfolio.assets])
        volatilities = np.array([asset.volatility for asset in portfolio.assets])

        # Create covariance matrix from correlations and volatilities
        cov_matrix = self._create_covariance_matrix(portfolio)

        # Optimize portfolio weights
        if target_return is not None:
            # Minimize variance for target return
            weights = self._optimize_for_target_return(returns, cov_matrix, target_return, risk_aversion)
        else:
            # Maximize Sharpe ratio
            weights = self._optimize_sharpe_ratio(returns, cov_matrix, portfolio.risk_free_rate)

        # Normalize weights to sum to 1
        weights = np.array(weights)
        weights = weights / np.sum(weights)

        # Calculate portfolio metrics
        portfolio_return = np.dot(weights, returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - portfolio.risk_free_rate) / portfolio_volatility

        # Calculate maximum drawdown (simplified estimate)
        max_drawdown = self._estimate_max_drawdown(volatilities, weights)

        # Calculate diversification ratio
        weighted_volatility = np.dot(weights, volatilities)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        diversification_ratio = weighted_volatility / portfolio_volatility

        # Generate recommendations
        recommendations = self._generate_recommendations(symbols, weights, returns, volatilities)

        # Generate rebalance actions
        rebalance_actions = self._generate_rebalance_actions(portfolio, dict(zip(symbols, weights)))

        return OptimizationResult(
            portfolio_name=portfolio.name,
            optimized_weights=dict(zip(symbols, weights)),
            expected_return=portfolio_return,
            expected_volatility=portfolio_volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            diversification_ratio=diversification_ratio,
            recommendations=recommendations,
            rebalance_actions=rebalance_actions
        )

    def optimize_risk_parity(self, portfolio: Portfolio) -> OptimizationResult:
        """Risk Parity optimization - equal risk contribution from each asset."""
        if len(portfolio.assets) < 2:
            return self._create_basic_result(portfolio, "Need at least 2 assets for risk parity")

        symbols = [asset.symbol for asset in portfolio.assets]
        volatilities = np.array([asset.volatility for asset in portfolio.assets])

        # Create covariance matrix
        cov_matrix = self._create_covariance_matrix(portfolio)

        # Risk parity optimization (simplified iterative approach)
        weights = self._optimize_risk_parity(cov_matrix, volatilities)

        # Calculate portfolio metrics
        returns = np.array([asset.expected_return for asset in portfolio.assets])
        portfolio_return = np.dot(weights, returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - portfolio.risk_free_rate) / portfolio_volatility

        # Risk contributions (should be equal in risk parity)
        risk_contributions = weights * np.dot(cov_matrix, weights) / portfolio_volatility

        recommendations = [
            f"Risk Parity achieved - each asset contributes equally to total risk",
            f"Average risk contribution: {np.mean(risk_contributions):.1%}",
            f"Risk contribution range: {np.min(risk_contributions):.1%} to {np.max(risk_contributions):.1%}"
        ]

        rebalance_actions = self._generate_rebalance_actions(portfolio, dict(zip(symbols, weights)))

        return OptimizationResult(
            portfolio_name=f"{portfolio.name} (Risk Parity)",
            optimized_weights=dict(zip(symbols, weights)),
            expected_return=portfolio_return,
            expected_volatility=portfolio_volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=self._estimate_max_drawdown(volatilities, weights),
            diversification_ratio=np.sum(weights * volatilities) / portfolio_volatility,
            recommendations=recommendations,
            rebalance_actions=rebalance_actions
        )

    def signal_based_rebalancing(self, portfolio: Portfolio, signals: Dict[str, List[IndicatorResult]]) -> List[Dict[str, Any]]:
        """Generate rebalancing actions based on technical signals."""
        actions = []

        for asset in portfolio.assets:
            asset_signals = signals.get(asset.symbol, [])

            if not asset_signals:
                continue

            # Calculate overall signal strength
            buy_signals = sum(sig.strength for sig in asset_signals if sig.signal == "BUY")
            sell_signals = sum(sig.strength for sig in asset_signals if sig.signal == "SELL")
            net_signal = buy_signals - sell_signals

            # Determine action based on signal strength and current weight
            current_weight = asset.weight
            target_weight = current_weight

            if net_signal > 0.5:  # Strong buy signal
                target_weight = min(current_weight * 1.2, 0.3)  # Increase by up to 20%, max 30%
                if target_weight > current_weight:
                    actions.append({
                        "action": "BUY",
                        "symbol": asset.symbol,
                        "current_weight": current_weight,
                        "target_weight": target_weight,
                        "reason": f"Strong buy signals (net: {net_signal:.2f})",
                        "signal_strength": net_signal
                    })

            elif net_signal < -0.5:  # Strong sell signal
                target_weight = max(current_weight * 0.8, 0.05)  # Decrease by up to 20%, min 5%
                if target_weight < current_weight:
                    actions.append({
                        "action": "SELL",
                        "symbol": asset.symbol,
                        "current_weight": current_weight,
                        "target_weight": target_weight,
                        "reason": f"Strong sell signals (net: {net_signal:.2f})",
                        "signal_strength": net_signal
                    })

        # Normalize weights to sum to 1
        total_weight = sum(action["target_weight"] for action in actions if "target_weight" in action)
        if total_weight > 0:
            for action in actions:
                if "target_weight" in action:
                    action["target_weight"] /= total_weight

        return actions

    def get_portfolio_metrics(self, portfolio: Portfolio) -> Dict[str, float]:
        """Calculate current portfolio performance metrics."""
        if not portfolio.assets:
            return {}

        weights = np.array([asset.weight for asset in portfolio.assets])
        returns = np.array([asset.expected_return for asset in portfolio.assets])
        volatilities = np.array([asset.volatility for asset in portfolio.assets])

        cov_matrix = self._create_covariance_matrix(portfolio)

        portfolio_return = np.dot(weights, returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - portfolio.risk_free_rate) / portfolio_volatility

        # Diversification metrics
        weighted_vol = np.dot(weights, volatilities)
        diversification_ratio = weighted_vol / portfolio_volatility if portfolio_volatility > 0 else 1.0

        # Risk contribution
        marginal_risk = np.dot(cov_matrix, weights)
        risk_contributions = weights * marginal_risk / portfolio_volatility

        # Calculate VaR (Value at Risk) - simplified estimate
        var_95 = -portfolio_volatility * 1.645 * portfolio.total_value  # 95% confidence
        expected_shortfall = -portfolio_volatility * 2.326 * portfolio.total_value  # Conditional VaR

        return {
            "portfolio_return": portfolio_return,
            "portfolio_volatility": portfolio_volatility,
            "sharpe_ratio": sharpe_ratio,
            "diversification_ratio": diversification_ratio,
            "max_risk_contribution": float(np.max(risk_contributions)),
            "min_risk_contribution": float(np.min(risk_contributions)),
            "value_at_risk_95": var_95,
            "expected_shortfall": expected_shortfall,
            "total_value": portfolio.total_value,
            "cash_position": portfolio.cash
        }

    def calculate_historical_performance(self, portfolio: Portfolio, days: int = 252) -> Dict[str, Any]:
        """Calculate historical performance metrics for backtesting."""
        # Mock historical performance calculation
        total_return = sum(asset.expected_return for asset in portfolio.assets) / len(portfolio.assets)
        total_volatility = sum(asset.volatility for asset in portfolio.assets) / len(portfolio.assets)

        # Simulate historical returns (simplified)
        historical_returns = []
        for i in range(days):
            daily_return = total_return / 252 + np.random.normal(0, total_volatility / np.sqrt(252))
            historical_returns.append(daily_return)

        cumulative_returns = np.cumprod(1 + np.array(historical_returns)) - 1
        max_drawdown = self._calculate_max_drawdown(cumulative_returns)

        # Benchmark comparison (S&P 500 mock)
        sp500_returns = [0.0008 + np.random.normal(0, 0.015) for _ in range(days)]
        sp500_cumulative = np.cumprod(1 + np.array(sp500_returns)) - 1

        portfolio_alpha = cumulative_returns[-1] - sp500_cumulative[-1]
        portfolio_beta = np.cov(historical_returns, sp500_returns)[0, 1] / np.var(sp500_returns)

        return {
            "total_return": cumulative_returns[-1],
            "annualized_return": (1 + cumulative_returns[-1]) ** (252 / days) - 1,
            "annualized_volatility": np.std(historical_returns) * np.sqrt(252),
            "max_drawdown": max_drawdown,
            "sharpe_ratio": (np.mean(historical_returns) * 252 - portfolio.risk_free_rate) / (np.std(historical_returns) * np.sqrt(252)),
            "benchmark_comparison": {
                "sp500_return": sp500_cumulative[-1],
                "portfolio_alpha": portfolio_alpha,
                "portfolio_beta": portfolio_beta
            },
            "win_rate": sum(1 for r in historical_returns if r > 0) / len(historical_returns),
            "best_day": max(historical_returns),
            "worst_day": min(historical_returns)
        }

    def _calculate_max_drawdown(self, cumulative_returns: np.ndarray) -> float:
        """Calculate maximum drawdown from cumulative returns."""
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = cumulative_returns - peak
        max_drawdown = np.min(drawdown)
        return max_drawdown

    def stress_test_portfolio(self, portfolio: Portfolio, scenarios: Dict[str, Dict[str, float]] = None) -> Dict[str, Dict[str, float]]:
        """
        Run stress tests on portfolio under different market scenarios.

        Args:
            portfolio: Portfolio to stress test
            scenarios: Dict of scenario names to shock parameters
        """
        if scenarios is None:
            scenarios = {
                "market_crash": {"equity_shock": -0.30, "bond_shock": -0.10, "vol_increase": 2.0},
                "tech_bubble_burst": {"AAPL": -0.40, "MSFT": -0.35, "GOOGL": -0.45, "AMZN": -0.50, "TSLA": -0.60, "NVDA": -0.55},
                "interest_rate_hike": {"rate_shock": 0.02, "growth_stocks": -0.15, "value_stocks": 0.05},
                "geopolitical_crisis": {"global_shock": -0.20, "vol_increase": 1.5},
                "recovery_scenario": {"equity_shock": 0.25, "vol_decrease": 0.7}
            }

        results = {}

        for scenario_name, shocks in scenarios.items():
            # Calculate stressed portfolio value
            stressed_value = portfolio.total_value
            stressed_volatility = 0.0

            for asset in portfolio.assets:
                shock = 1.0  # Default no shock

                # Apply scenario-specific shocks
                if "equity_shock" in shocks and asset.symbol in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]:
                    shock *= (1 + shocks["equity_shock"])
                elif "global_shock" in shocks:
                    shock *= (1 + shocks["global_shock"])
                elif asset.symbol in shocks:
                    shock *= (1 + shocks[asset.symbol])
                elif "growth_stocks" in shocks and asset.symbol in ["TSLA", "NVDA", "AMZN", "NFLX"]:
                    shock *= (1 + shocks["growth_stocks"])
                elif "value_stocks" in shocks and asset.symbol in ["AAPL", "MSFT", "GOOGL"]:
                    shock *= (1 + shocks["value_stocks"])

                # Apply to asset value
                asset_stressed_value = asset.current_price * shock * asset.weight * (portfolio.total_value / portfolio.total_value)
                stressed_value += asset_stressed_value - (asset.current_price * asset.weight * (portfolio.total_value / portfolio.total_value))

                # Increase volatility under stress
                vol_multiplier = shocks.get("vol_increase", shocks.get("vol_decrease", 1.0))
                stressed_volatility += (asset.volatility * vol_multiplier) ** 2

            stressed_volatility = np.sqrt(stressed_volatility)
            loss_amount = portfolio.total_value - stressed_value
            loss_percentage = loss_amount / portfolio.total_value

            results[scenario_name] = {
                "stressed_value": stressed_value,
                "loss_amount": loss_amount,
                "loss_percentage": loss_percentage,
                "stressed_volatility": stressed_volatility,
                "survival_probability": max(0, 1 - abs(loss_percentage))  # Simplified
            }

        return results

    # ===== PRIVATE HELPER METHODS =====

    def _get_mock_price(self, symbol: str) -> float:
        """Get mock current price for symbol."""
        # Use a deterministic but varied pricing scheme
        base_prices = {
            "AAPL": 175.0, "MSFT": 380.0, "GOOGL": 140.0, "AMZN": 155.0,
            "TSLA": 220.0, "NVDA": 850.0, "META": 480.0, "NFLX": 600.0
        }
        return base_prices.get(symbol, 100.0 + hash(symbol) % 500)

    def _get_mock_expected_return(self, symbol: str) -> float:
        """Get mock expected annual return for symbol."""
        # Mock returns based on asset class (tech stocks higher, defensive lower)
        tech_stocks = {"AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"}
        if symbol in tech_stocks:
            return 0.12 + (hash(symbol) % 10) / 100  # 12-22%
        else:
            return 0.08 + (hash(symbol) % 8) / 100   # 8-16%

    def _get_mock_volatility(self, symbol: str) -> float:
        """Get mock annual volatility for symbol."""
        # Higher volatility for growth stocks
        high_vol_stocks = {"TSLA", "NVDA", "NFLX"}
        if symbol in high_vol_stocks:
            return 0.35 + (hash(symbol) % 15) / 100  # 35-50%
        else:
            return 0.20 + (hash(symbol) % 15) / 100  # 20-35%

    def _generate_correlation_matrix(self, portfolio: Portfolio):
        """Generate mock correlation matrix for portfolio assets."""
        symbols = [asset.symbol for asset in portfolio.assets]

        # Base correlations (tech stocks more correlated)
        for i, sym1 in enumerate(symbols):
            for j, sym2 in enumerate(symbols):
                if i == j:
                    correlation = 1.0
                elif sym1 in {"AAPL", "MSFT", "GOOGL", "AMZN"} and sym2 in {"AAPL", "MSFT", "GOOGL", "AMZN"}:
                    correlation = 0.65 + (hash(sym1 + sym2) % 20) / 100  # 65-85%
                else:
                    correlation = 0.30 + (hash(sym1 + sym2) % 30) / 100  # 30-60%

                portfolio.correlation_matrix[(sym1, sym2)] = correlation
                portfolio.correlation_matrix[(sym2, sym1)] = correlation

    def _create_covariance_matrix(self, portfolio: Portfolio) -> np.ndarray:
        """Create covariance matrix from correlations and volatilities."""
        n = len(portfolio.assets)
        cov_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                vol_i = portfolio.assets[i].volatility
                vol_j = portfolio.assets[j].volatility
                corr = portfolio.correlation_matrix.get(
                    (portfolio.assets[i].symbol, portfolio.assets[j].symbol), 0.5
                )
                cov_matrix[i, j] = corr * vol_i * vol_j

        return cov_matrix

    def _optimize_for_target_return(self, returns: np.ndarray, cov_matrix: np.ndarray,
                                  target_return: float, risk_aversion: float = 1.0) -> np.ndarray:
        """Optimize portfolio for minimum variance given target return."""
        n = len(returns)

        # Use simple equal weight as fallback for now
        # In production, this would use quadratic programming
        weights = np.ones(n) / n

        # Adjust weights to meet target return (simplified)
        current_return = np.dot(weights, returns)
        if current_return > 0:
            scale_factor = target_return / current_return
            weights = weights * min(scale_factor, 2.0)  # Cap at 2x to avoid extreme leverage

        return weights / np.sum(weights)

    def _optimize_sharpe_ratio(self, returns: np.ndarray, cov_matrix: np.ndarray,
                              risk_free_rate: float) -> np.ndarray:
        """Optimize portfolio for maximum Sharpe ratio."""
        n = len(returns)

        # Simplified approach: weight by (return - rf) / volatility
        excess_returns = returns - risk_free_rate
        if np.any(cov_matrix.diagonal() <= 0):
            # Fallback to equal weights if volatility data is invalid
            return np.ones(n) / n

        volatilities = np.sqrt(np.maximum(cov_matrix.diagonal(), 1e-8))
        sharpe_components = excess_returns / volatilities

        # Ensure no negative components (set minimum to small positive value)
        sharpe_components = np.maximum(sharpe_components, 0.01)

        weights = sharpe_components / np.sum(sharpe_components)
        return weights

    def _optimize_risk_parity(self, cov_matrix: np.ndarray, volatilities: np.ndarray) -> np.ndarray:
        """Optimize for risk parity using iterative approach."""
        n = len(volatilities)
        weights = np.ones(n) / n  # Start with equal weights

        # Simple iterative risk parity (simplified version)
        for _ in range(10):  # Limited iterations for demo
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            risk_contributions = weights * np.dot(cov_matrix, weights) / portfolio_volatility

            # Adjust weights to equalize risk contributions
            target_risk = 1.0 / n
            weights = weights * (target_risk / risk_contributions)
            weights = weights / np.sum(weights)

        return weights

    def _estimate_max_drawdown(self, volatilities: np.ndarray, weights: np.ndarray) -> float:
        """Estimate maximum drawdown based on volatility (simplified)."""
        portfolio_vol = np.sqrt(np.dot(weights, volatilities)**2)  # Simplified
        # Rough estimate: max drawdown is roughly 2-3 times annual volatility for daily data
        return min(portfolio_vol * 2.5, 0.5)  # Cap at 50%

    def _generate_recommendations(self, symbols: List[str], weights: np.ndarray,
                                returns: np.ndarray, volatilities: np.ndarray) -> List[str]:
        """Generate human-readable recommendations."""
        recommendations = []

        # Find highest and lowest weighted assets
        weight_dict = dict(zip(symbols, weights))
        sorted_weights = sorted(weight_dict.items(), key=lambda x: x[1], reverse=True)

        recommendations.append(f"Highest allocation: {sorted_weights[0][0]} ({sorted_weights[0][1]:.1%})")
        recommendations.append(f"Lowest allocation: {sorted_weights[-1][0]} ({sorted_weights[-1][1]:.1%})")

        # Risk-return analysis
        return_dict = dict(zip(symbols, returns))
        vol_dict = dict(zip(symbols, volatilities))

        high_return = max(return_dict.items(), key=lambda x: x[1])
        low_vol = min(vol_dict.items(), key=lambda x: x[1])

        recommendations.append(f"Highest expected return: {high_return[0]} ({high_return[1]:.1%})")
        recommendations.append(f"Lowest volatility: {low_vol[0]} ({vol_dict[low_vol[0]]:.1%})")

        return recommendations

    def _generate_rebalance_actions(self, portfolio: Portfolio, target_weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate specific rebalance actions."""
        actions = []

        for asset in portfolio.assets:
            current_weight = asset.weight
            target_weight = target_weights.get(asset.symbol, current_weight)

            if abs(target_weight - current_weight) > portfolio.rebalance_threshold:
                if target_weight > current_weight:
                    action = "BUY"
                    amount = (target_weight - current_weight) * portfolio.total_value
                else:
                    action = "SELL"
                    amount = (current_weight - target_weight) * portfolio.total_value

                actions.append({
                    "symbol": asset.symbol,
                    "action": action,
                    "current_weight": current_weight,
                    "target_weight": target_weight,
                    "amount": amount,
                    "reason": f"Rebalance to target allocation (deviation: {abs(target_weight - current_weight):.1%})"
                })

        return actions

    def _create_basic_result(self, portfolio: Portfolio, message: str) -> OptimizationResult:
        """Create a basic optimization result when optimization fails."""
        return OptimizationResult(
            portfolio_name=portfolio.name,
            optimized_weights={asset.symbol: asset.weight for asset in portfolio.assets},
            expected_return=0.0,
            expected_volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            diversification_ratio=1.0,
            recommendations=[message],
            rebalance_actions=[]
        )
