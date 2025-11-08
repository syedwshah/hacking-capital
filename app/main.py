from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import time
import os

from app.api.v1.health import router as health_router
from app.api.v1.data import router as data_router
from app.api.v1.summaries import router as summaries_router
from app.api.v1.trade import router as trade_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.simulate import router as simulate_router
from app.api.v1.agents import router as agents_router
from app.api.v1.portfolio import router as portfolio_router
from app.db.base import engine
from app.db.models import Base
from app.services.summary_service import SummaryService
from app.core.cache import KnowledgeCache

# Global background task manager
background_tasks = {}

def background_summarization_worker():
    """Background worker for periodic AI summarization."""
    symbols_to_summarize = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
    granularities = ["daily", "weekly"]

    while True:
        try:
            print("🔄 Running background AI summarization...")

            # Only run if OpenAI is available
            if os.getenv("OPENAI_API_KEY"):
                svc = SummaryService()

                for symbol in symbols_to_summarize:
                    for granularity in granularities:
                        try:
                            print(f"📊 Generating AI summary for {symbol} ({granularity})")
                            summaries = svc.generate(symbol, granularity, period_days=30)

                            if summaries:
                                print(f"✅ Generated {len(summaries)} AI summaries for {symbol} ({granularity})")

                                # Cache the summaries
                                KnowledgeCache().set_summary(
                                    symbol,
                                    granularity,
                                    {"summaries": summaries, "ai_powered": True},
                                    ttl_s=86400
                                )

                        except Exception as e:
                            print(f"❌ Failed to summarize {symbol} ({granularity}): {e}")

            # Wait 10 minutes before next cycle (reduced for demo)
            time.sleep(600)  # 10 minutes

        except Exception as e:
            print(f"❌ Background summarization error: {e}")
            time.sleep(60)  # Wait 1 minute on error

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    KnowledgeCache()  # Initialize cache

    # Start background summarization if OpenAI is available
    if os.getenv("OPENAI_API_KEY"):
        print("🚀 Starting background AI summarization service...")
        summarization_thread = threading.Thread(
            target=background_summarization_worker,
            daemon=True,
            name="ai-summarization"
        )
        summarization_thread.start()
        background_tasks["summarization"] = summarization_thread
        print("✅ AI summarization service started - will run every 10 minutes")
    else:
        print("⚠️ OpenAI API key not found - summarization will use basic fallback")

    yield
    # Shutdown
    print("🛑 Shutting down background services...")

app = FastAPI(
    title="Hacking Capital API",
    description="AI-Powered Trading Agent API with Background Summarization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(data_router, prefix="/api/v1")
app.include_router(summaries_router, prefix="/api/v1")
app.include_router(trade_router, prefix="/api/v1")
app.include_router(backtest_router, prefix="/api/v1")
app.include_router(simulate_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")


