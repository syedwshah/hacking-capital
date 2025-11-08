from abc import ABC, abstractmethod
from app.schemas.agent import AgentSignal


class AgentProtocol(ABC):
    name: str = "base"
    version: str = "v1"

    @abstractmethod
    def prepare(self, symbol: str) -> None: ...

    @abstractmethod
    def signal(self, symbol: str, at_ts: str, context: dict) -> AgentSignal: ...


