from app.services.data_service import DataService


def test_fetch_stub():
    svc = DataService()
    rows = svc.fetch("AAPL", "2020-01-01", "2020-01-31", "daily")
    assert isinstance(rows, list)

