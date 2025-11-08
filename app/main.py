from fastapi import FastAPI
from app.api.v1.health import router as health_router
from app.api.v1.data import router as data_router
from app.api.v1.summaries import router as summaries_router
from app.api.v1.trade import router as trade_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.simulate import router as simulate_router
from app.api.v1.agents import router as agents_router

app = FastAPI(title="Hacking Capital API", version="0.1.0")

app.include_router(health_router, prefix="/api/v1")
app.include_router(data_router, prefix="/api/v1")
app.include_router(summaries_router, prefix="/api/v1")
app.include_router(trade_router, prefix="/api/v1")
app.include_router(backtest_router, prefix="/api/v1")
app.include_router(simulate_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")


