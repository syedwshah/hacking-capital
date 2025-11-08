from app.agents.teammate.base import TeammateAgentProtocol
from app.schemas.agent import AgentSignal


class SentimentTailwindsAgent(TeammateAgentProtocol):
    name = "sentiment_tailwinds"
    version = "v1"

    def signal(self, symbol: str, at_ts: str, context: dict) -> AgentSignal:
        return AgentSignal(score=0.0, confidence=0.0, reason="sentiment-tailwinds-stub", features={})


