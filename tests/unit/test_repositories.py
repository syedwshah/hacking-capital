from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.repositories.summary_repo import SummaryRepository
from app.repositories.decision_repo import DecisionRepository
from app.repositories.trade_repo import TradeRepository


def make_memory_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return Session()


def test_summary_repo_insert_and_get():
    session = make_memory_session()
    repo = SummaryRepository()
    rows = [
        {"symbol": "AAPL", "granularity": "daily", "period": "2020-01-01", "stats": {"close": 1.0}},
        {"symbol": "AAPL", "granularity": "daily", "period": "2020-01-02", "stats": {"close": 2.0}},
    ]
    repo.insert_many(session, rows)
    got = repo.get(session, "AAPL", "daily")
    assert len(got) == 2


def test_decision_and_trade_repos_insert_and_list():
    session = make_memory_session()
    d_repo = DecisionRepository()
    t_repo = TradeRepository()
    d_repo.insert(session, symbol="AAPL", action="BUY", quantity=1.0, confidence=0.9, reason="test")
    t_repo.insert(session, symbol="AAPL", action="BUY", price=100.0, quantity=1.0)
    decisions = d_repo.list_for_symbol(session, "AAPL")
    trades = t_repo.list_for_symbol(session, "AAPL")
    assert decisions and trades


