"""
Portfolio Optimization API Endpoints

Provides REST endpoints for portfolio analysis, optimization, and management.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.services.portfolio_optimizer import PortfolioOptimizer, Portfolio, OptimizationResult

router = APIRouter(tags=["portfolio"])


class CreatePortfolioRequest(BaseModel):
    name: str
    symbols: List[str]
    initial_value: float = 100000.0


class OptimizePortfolioRequest(BaseModel):
    portfolio_name: str
    optimization_type: str = "mpt"  # "mpt", "risk_parity"
    target_return: Optional[float] = None
    risk_aversion: float = 1.0


class PortfolioAnalysisResponse(BaseModel):
    portfolio_name: str
    assets: List[Dict[str, Any]]
    total_value: float
    metrics: Dict[str, float]
    signals: Dict[str, List[Dict[str, Any]]]


@router.post("/portfolio/create", response_model=Dict[str, Any])
def create_portfolio(request: CreatePortfolioRequest) -> Dict[str, Any]:
    """Create a new portfolio with specified assets."""
    try:
        optimizer = PortfolioOptimizer()
        portfolio = optimizer.create_portfolio(
            name=request.name,
            symbols=request.symbols,
            initial_value=request.initial_value
        )

        return {
            "portfolio_name": portfolio.name,
            "assets": [
                {
                    "symbol": asset.symbol,
                    "current_price": asset.current_price,
                    "expected_return": asset.expected_return,
                    "volatility": asset.volatility,
                    "weight": asset.weight
                }
                for asset in portfolio.assets
            ],
            "total_value": portfolio.total_value,
            "risk_free_rate": portfolio.risk_free_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create portfolio: {str(e)}")


@router.post("/portfolio/analyze", response_model=PortfolioAnalysisResponse)
def analyze_portfolio(request: CreatePortfolioRequest) -> PortfolioAnalysisResponse:
    """Analyze portfolio with technical signals and current metrics."""
    try:
        optimizer = PortfolioOptimizer()
        portfolio = optimizer.create_portfolio(
            name=request.name,
            symbols=request.symbols,
            initial_value=request.initial_value
        )

        # Analyze technical signals
        signals = optimizer.analyze_portfolio_signals(portfolio)

        # Get portfolio metrics
        metrics = optimizer.get_portfolio_metrics(portfolio)

        # Get historical performance (simulated)
        historical_perf = optimizer.calculate_historical_performance(portfolio, days=126)  # 6 months

        # Add historical metrics to the response
        metrics.update({
            "historical_return": historical_perf["total_return"],
            "historical_volatility": historical_perf["annualized_volatility"],
            "historical_max_drawdown": historical_perf["max_drawdown"],
            "win_rate": historical_perf["win_rate"],
            "benchmark_alpha": historical_perf["benchmark_comparison"]["portfolio_alpha"],
            "benchmark_beta": historical_perf["benchmark_comparison"]["portfolio_beta"]
        })

        # Convert signals to serializable format
        serializable_signals = {}
        for symbol, indicator_results in signals.items():
            serializable_signals[symbol] = [
                {
                    "name": result.name,
                    "value": result.value,
                    "signal": result.signal,
                    "strength": result.strength,
                    "reason": result.reason
                }
                for result in indicator_results
            ]

        return PortfolioAnalysisResponse(
            portfolio_name=portfolio.name,
            assets=[
                {
                    "symbol": asset.symbol,
                    "current_price": asset.current_price,
                    "expected_return": asset.expected_return,
                    "volatility": asset.volatility,
                    "weight": asset.weight,
                    "signal_strength": asset.signal_strength
                }
                for asset in portfolio.assets
            ],
            total_value=portfolio.total_value,
            metrics=metrics,
            signals=serializable_signals
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze portfolio: {str(e)}")


@router.post("/portfolio/performance")
def get_portfolio_performance(request: CreatePortfolioRequest) -> Dict[str, Any]:
    """Get detailed historical performance analysis for portfolio."""
    try:
        optimizer = PortfolioOptimizer()
        portfolio = optimizer.create_portfolio(
            name=request.name,
            symbols=request.symbols,
            initial_value=request.initial_value
        )

        performance = optimizer.calculate_historical_performance(portfolio, days=252)  # 1 year
        stress_tests = optimizer.stress_test_portfolio(portfolio)

        return {
            "portfolio_name": portfolio.name,
            "performance": performance,
            "stress_tests": stress_tests,
            "risk_metrics": {
                "value_at_risk_95": optimizer.get_portfolio_metrics(portfolio).get("value_at_risk_95", 0),
                "expected_shortfall": optimizer.get_portfolio_metrics(portfolio).get("expected_shortfall", 0),
                "worst_case_loss": max(test["loss_amount"] for test in stress_tests.values())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate performance: {str(e)}")


@router.post("/portfolio/optimize", response_model=Dict[str, Any])
def optimize_portfolio(request: OptimizePortfolioRequest) -> Dict[str, Any]:
    """Optimize portfolio using specified optimization method."""
    try:
        optimizer = PortfolioOptimizer()
        portfolio = optimizer.create_portfolio(
            name=request.portfolio_name,
            symbols=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],  # Mock symbols for now
            initial_value=100000.0
        )

        if request.optimization_type == "risk_parity":
            result = optimizer.optimize_risk_parity(portfolio)
        else:  # Default to MPT
            result = optimizer.optimize_portfolio_mpt(
                portfolio=portfolio,
                target_return=request.target_return,
                risk_aversion=request.risk_aversion
            )

        return {
            "portfolio_name": result.portfolio_name,
            "optimized_weights": result.optimized_weights,
            "expected_return": result.expected_return,
            "expected_volatility": result.expected_volatility,
            "sharpe_ratio": result.sharpe_ratio,
            "max_drawdown": result.max_drawdown,
            "diversification_ratio": result.diversification_ratio,
            "recommendations": result.recommendations,
            "rebalance_actions": result.rebalance_actions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to optimize portfolio: {str(e)}")


@router.post("/portfolio/rebalance", response_model=Dict[str, Any])
def rebalance_portfolio(request: CreatePortfolioRequest) -> Dict[str, Any]:
    """Analyze portfolio and recommend rebalancing actions based on technical signals."""
    try:
        optimizer = PortfolioOptimizer()
        portfolio = optimizer.create_portfolio(
            name=request.name,
            symbols=request.symbols,
            initial_value=request.initial_value
        )

        # Analyze signals
        signals = optimizer.analyze_portfolio_signals(portfolio)

        # Generate rebalancing actions
        rebalance_actions = optimizer.signal_based_rebalancing(portfolio, signals)

        return {
            "portfolio_name": portfolio.name,
            "current_allocations": {
                asset.symbol: {
                    "weight": asset.weight,
                    "signal_strength": asset.signal_strength
                }
                for asset in portfolio.assets
            },
            "rebalance_actions": rebalance_actions,
            "total_actions": len(rebalance_actions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rebalance portfolio: {str(e)}")


@router.get("/portfolio/templates", response_model=Dict[str, List[Dict[str, Any]]])
def get_portfolio_templates() -> Dict[str, List[Dict[str, Any]]]:
    """Get predefined portfolio templates."""
    templates = {
        "conservative": [
            {"symbol": "AAPL", "weight": 0.3, "description": "Stable tech giant"},
            {"symbol": "MSFT", "weight": 0.3, "description": "Enterprise software leader"},
            {"symbol": "GOOGL", "weight": 0.2, "description": "Search and advertising"},
            {"symbol": "AMZN", "weight": 0.2, "description": "E-commerce and cloud"}
        ],
        "aggressive": [
            {"symbol": "TSLA", "weight": 0.25, "description": "Electric vehicle pioneer"},
            {"symbol": "NVDA", "weight": 0.25, "description": "AI chip leader"},
            {"symbol": "AAPL", "weight": 0.2, "description": "Consumer electronics"},
            {"symbol": "META", "weight": 0.15, "description": "Social media platform"},
            {"symbol": "NFLX", "weight": 0.15, "description": "Streaming entertainment"}
        ],
        "balanced": [
            {"symbol": "AAPL", "weight": 0.2, "description": "Large-cap tech"},
            {"symbol": "MSFT", "weight": 0.2, "description": "Software and cloud"},
            {"symbol": "GOOGL", "weight": 0.15, "description": "Internet services"},
            {"symbol": "AMZN", "weight": 0.15, "description": "E-commerce"},
            {"symbol": "TSLA", "weight": 0.15, "description": "Growth stock"},
            {"symbol": "NVDA", "weight": 0.15, "description": "Semiconductors"}
        ]
    }

    return {"templates": templates}
