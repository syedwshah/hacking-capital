Hacking Capital — LLM‑free Trading Agent Scaffold

Overview
This repo scaffolds a deterministic, LLM‑free Python trading agent system with FastAPI (backend), Streamlit (UI), and Redis + SQLite for caching and storage. It is designed for a hackathon to test whether engineered Python summarizations and trend metrics can drive autonomous trading decisions, without LLM inference.

Key components
- FastAPI backend with modular services: data ingestion, summarization, trading, backtest/simulation, agent orchestration.
- Agents: a primary deterministic agent plus teammate stubs (investor patterns, sentiment/tailwinds) combined via weights.
- Redis knowledge cache for hot summaries and features, with deterministic fallback if cache misses.
- Streamlit UI for selecting tickers, adjusting agent weights, viewing summaries/reasons, and a paper-trade view.

Architecture (text)
Streamlit UI ⇄ FastAPI
→ DataService ⇄ SQLite (prices, summaries, decisions, trades, portfolio)
→ SummaryService → Redis cache (knowledge summaries)
→ Agents (primary + teammate stubs) → Ensemble (weights)
→ TradingService (deterministic metrics + agents)
→ Backtest/Simulation → SSE stream to UI

Prerequisites
- Python 3.11+
- Redis (local) optional for caching
- Homebrew (macOS) for optional Raindrop Code CLI

Optional dev tool: Raindrop Code CLI
brew install LiquidMetal-AI/tap/raindrop-code
export OPENAI_API_KEY="YOUR_KEY"
raindrop-code --help

Environment
Create a .env file or export environment variables:
- DATABASE_URL=sqlite:///./hacking_capital.db
- REDIS_URL=redis://localhost:6379/0
- ALPHAVANTAGE_API_KEY=your_key
- OPENAI_API_KEY=your_key  # Optional dev tooling
- OPENAL_API_KEY=your_key  # Compatibility alias for provided hackathon var

Quickstart
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
streamlit run ui/App.py

Makefile shortcuts
make run-api
make run-ui
make test

Sample API (stubs)
- GET /api/v1/health
- POST /api/v1/data/fetch
- POST /api/v1/summaries/generate
- GET  /api/v1/agents/weights
- POST /api/v1/agents/weights
- POST /api/v1/trade/decide
- POST /api/v1/backtest/run
- POST /api/v1/simulate/stream

Notes
- This scaffold intentionally avoids business logic; services and agents are stubs ready for implementation.
- The UI includes a paper-trade page with agent weight sliders and live stream placeholders.

# hacking-capital
MoA to create stock trading patterns for revenue generation
