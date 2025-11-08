from app.agents.base import AgentProtocol
from app.agents.primary_agent import PrimaryAgent
from app.agents.teammate.investor_patterns import InvestorPatternsAgent
from app.agents.teammate.sentiment_tailwinds import SentimentTailwindsAgent


def available_agents() -> list[AgentProtocol]:
    return [PrimaryAgent(), InvestorPatternsAgent(), SentimentTailwindsAgent()]


