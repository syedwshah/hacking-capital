from app.agents.base import AgentProtocol
from app.schemas.agent import AgentSignal


class PrimaryAgent(AgentProtocol):
    name = "primary"
    version = "v1"

    def prepare(self, symbol: str) -> None:
        return None

    def signal(self, symbol: str, at_ts: str, context: dict) -> AgentSignal:
        return AgentSignal(score=0.0, confidence=0.5, reason="primary-stub", features={})


