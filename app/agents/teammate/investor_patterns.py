from app.agents.teammate.base import TeammateAgentProtocol
from app.schemas.agent import AgentSignal


class InvestorPatternsAgent(TeammateAgentProtocol):
    name = "investor_patterns"
    version = "v1"

    def signal(self, symbol: str, at_ts: str, context: dict) -> AgentSignal:
        return AgentSignal(score=0.0, confidence=0.0, reason="investor-patterns-stub", features={})


