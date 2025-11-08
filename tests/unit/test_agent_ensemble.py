from app.agents.ensemble import combine
from app.schemas.agent import AgentSignal


class Dummy:
    pass


def test_combine_weights():
    s1 = AgentSignal(score=1.0, confidence=1.0, reason="a", features={})
    s2 = AgentSignal(score=0.0, confidence=0.0, reason="b", features={})
    result = combine([(Dummy(), s1, 0.75), (Dummy(), s2, 0.25)])
    assert 0.7 < result.score <= 1.0

