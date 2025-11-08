# Hacking Capital — LLM-free Trading Agent

A production-ready, deterministic trading agent experiment built with Python, FastAPI, and Streamlit. Features real-time streaming, vector-based historical similarity, and comprehensive backtesting with performance metrics.

## ✨ Features Implemented

### 🤖 **Advanced Trading Agents**
- **Primary Agent**: SMA crossover signals with configurable thresholds
- **Investor Patterns**: RSI-based momentum detection
- **Sentiment Tailwinds**: MACD histogram analysis
- **Vector Similarity**: Historical pattern matching using vector embeddings
- **Ensemble Weights**: Dynamic agent weighting with normalization

### 📊 **Real-time Capabilities**
- **Live Streaming**: Server-Sent Events for real-time trade simulation
- **Interactive UI**: Agent weight adjustment, live charts, and confidence tracking
- **Cache Monitoring**: Hit/miss badges for performance optimization

### 🔬 **Backtesting & Analytics**
- **Performance Metrics**: Max drawdown, Sharpe ratio, strategy vs buy-and-hold
- **Transaction Costs**: Realistic trading fees (0.1%)
- **Equity Curves**: Visual comparison with benchmarks
- **Comprehensive Reporting**: Detailed trade logs and summaries

### 🧠 **Vector Intelligence**
- **Semantic Search**: Vector embeddings of market summaries
- **Historical Similarity**: Nearest-period lookup for decision context
- **SQLite Vector Store**: Efficient L2 distance similarity search

### 🏗️ **Production Architecture**
- **Containerized**: Docker-first with multi-stage builds
- **Health Checks**: Automated service monitoring
- **Database Persistence**: SQLite with SQLAlchemy ORM
- **Redis Caching**: Knowledge cache with fallback

#### **System Architecture Flow**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │◄──►│    FastAPI      │◄──►│   Alpha Vantage │
│                 │    │   Backend API   │    │     Market Data │
│ • Real-time     │    │                 │    │                 │
│   Charts        │    │ • REST Endpoints│    │ • OHLCV Data    │
│ • Agent Weights │    │ • Health Checks │    │ • Real-time     │
│ • Live Trading  │    │ • SSE Streaming │    │   Updates       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │                         │
          ┌─────────▼─────────┐     ┌────────▼─────────┐
          │   DataService     │     │  SummaryService  │
          │                   │     │                  │
          │ • Market Data     │     │ • Knowledge      │
          │   Fetching        │     │   Summaries      │
          │ • Synthetic       │     │ • Vector Embed-  │
          │   Fallback        │     │   dings          │
          │ • Data Validation │     │ • Cache Layer    │
          └─────────┬─────────┘     └──────────┬───────┘
                    │                          │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │                         │
          ┌─────────▼─────────┐     ┌────────▼──────────┐
          │   TradingService  │     │  BacktestService  │
          │                   │     │                   │
          │ • Agent Ensemble  │     │ • Historical      │
          │ • Vector Similarity│     │   Simulation     │
          │ • Technical        │     │ • Performance     │
          │   Indicators       │     │   Metrics        │
          │ • Trade Execution  │     │ • Risk Analysis   │
          └─────────┬─────────┘     └─────────┬─────────┘
                    │                          │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │     Agent Ensemble      │
                    │                         │
          ┌─────────▼─────────┐     ┌────────▼──────────┐
          │   Trading Agents  │     │  Vector Store     │
          │                   │     │                   │
          │ • SMA Crossover   │     │ • SQLite Vector   │
          │ • RSI Momentum    │     │   Database        │
          │ • MACD Histogram  │     │ • L2 Similarity   │
          │ • Dynamic Weights │     │ • Pattern Matching│
          └───────────────────┘     └───────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Persistence Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   SQLite    │    │    Redis    │    │  File Sys  │      │
│  │             │    │             │    │            │      │
│  │ • Prices    │    │ • Summaries │    │ • Logs     │      │
│  │ • Trades    │    │ • Cache     │    │ • Config   │      │
│  │ • Decisions │    │ • Knowledge │    │ • Models   │      │
│  │ • Portfolio │    │             │    │            │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

#### **Data Flow & Processing Pipeline**

1. **Market Data Ingestion** → Alpha Vantage API → DataService → SQLite Storage
2. **Real-time Streaming** → FastAPI SSE → Streamlit UI → Live Charts
3. **Agent Decision Making** → Technical Indicators → Vector Similarity → Ensemble Weights → Trade Signals
4. **Backtesting Engine** → Historical Data → Performance Metrics → Risk Analysis
5. **Portfolio Management** → Trade Execution → Position Tracking → P&L Calculation
6. **Caching Strategy** → Redis (Summaries) → SQLite (Vector Store) → File System (Logs)

#### **Key Architectural Patterns**
- **Microservices**: Separated concerns with dedicated services for data, trading, and analysis
- **Event-Driven**: Server-Sent Events for real-time UI updates during trading
- **Repository Pattern**: Clean data access layer with SQLAlchemy ORM
- **Strategy Pattern**: Pluggable agent system with configurable weights
- **Cache-Aside**: Redis caching with database fallback for reliability
- **Vector Search**: Similarity-based pattern matching for historical context

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

Local Development
```bash
# Set up environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make env

# Run services
make run-api    # API on http://localhost:8000
make run-ui     # UI on http://localhost:8501
make test       # Run all tests
```

Docker / Compose
Build and run API + UI + Redis locally:

```bash
# Development stack
docker compose -f docker-compose.dev.yml up --build

# Production stack
docker compose up --build -d
```

API: http://localhost:8000/api/v1/health
UI:  http://localhost:8501

Deployment Options
Choose your preferred deployment platform:

## 🚀 Raindrop PaaS
```bash
# Using deployment script
./deploy.sh raindrop

# Or manually with raindrop CLI
raindrop deploy --config raindrop.yml
```

## 🐳 Docker (Self-hosted)
```bash
./deploy.sh docker
```

## 🎨 Other PaaS Platforms
```bash
# Render deployment instructions
./deploy.sh render

# Railway deployment instructions
./deploy.sh railway
```

## 📦 Container Registry
For manual container deployment:
```bash
# Build and push to registry
docker build -t your-registry/hacking-capital-api:latest -f Dockerfile.api .
docker build -t your-registry/hacking-capital-ui:latest -f Dockerfile.ui .
docker push your-registry/hacking-capital-api:latest
docker push your-registry/hacking-capital-ui:latest
```

Environment Variables Required:
- `ALPHAVANTAGE_API_KEY`
- `OPENAI_API_KEY`
- `DATABASE_URL=sqlite:///./data/hacking_capital.db`
- `REDIS_URL=redis://redis:6379/0`

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
