from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./hacking_capital.db"
    redis_url: str = "redis://localhost:6379/0"
    alphavantage_api_key: str | None = None
    openai_api_key: str | None = None  # optional dev tooling
    openal_api_key: str | None = None  # compatibility alias

    class Config:
        env_file = ".env"


settings = Settings()


