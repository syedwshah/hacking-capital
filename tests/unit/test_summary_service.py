from app.services.summary_service import SummaryService


def test_generate_stub():
    svc = SummaryService()
    rows = svc.generate("AAPL", "daily")
    assert isinstance(rows, list)


