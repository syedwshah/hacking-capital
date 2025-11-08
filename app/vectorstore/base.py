from typing import Any


class VectorStoreProtocol:
    def upsert(self, key: str, vector: list[float], metadata: dict) -> None:  # pragma: no cover
        raise NotImplementedError

    def query(self, vector: list[float], top_k: int = 10, where: dict | None = None) -> list[dict]:  # pragma: no cover
        raise NotImplementedError


