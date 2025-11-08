import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import engine
from app.db.models import Base


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


