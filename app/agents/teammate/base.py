from abc import ABC, abstractmethod
from app.schemas.agent import AgentSignal


class TeammateAgentProtocol(ABC):
    name: str = "teammate"
    version: str = "v1"

    @abstractmethod
    def signal(self, symbol: str, at_ts: str, context: dict) -> AgentSignal: ...


