class SqliteJsonVectorStore:
    # Placeholder: stores vectors as JSON in SQLite via repository
    def upsert(self, key: str, vector: list[float], metadata: dict) -> None:
        return None

    def query(self, vector: list[float], top_k: int = 10, where: dict | None = None) -> list[dict]:
        return []


