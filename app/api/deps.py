from typing import Generator

from app.db.base import get_session


def db_session() -> Generator:
    with get_session() as session:
        yield session


