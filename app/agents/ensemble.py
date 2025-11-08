from typing import Iterable
from app.schemas.agent import AgentSignal
from app.agents.base import AgentProtocol


def combine(signals: Iterable[tuple[AgentProtocol, AgentSignal, float]]) -> AgentSignal:
    # Weighted average of scores/confidences (placeholder)
    total_w = 0.0
    score_sum = 0.0
    conf_sum = 0.0
    reasons: list[str] = []
    for _, sig, w in signals:
        w = max(0.0, float(w))
        total_w += w
        score_sum += sig.score * w
        conf_sum += sig.confidence * w
        reasons.append(f"{sig.reason}")
    if total_w == 0:
        return AgentSignal(score=0.0, confidence=0.0, reason="no-weights", features={})
    return AgentSignal(
        score=score_sum / total_w, confidence=conf_sum / total_w, reason="; ".join(reasons), features={}
    )


