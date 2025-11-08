from pydantic import BaseModel


class AgentSignal(BaseModel):
    score: float        # -1..1
    confidence: float   # 0..1
    reason: str
    features: dict = {}


class AgentWeight(BaseModel):
    agent: str
    weight: float
    version: str = "v1"


