from collections import deque


def simple_moving_average(values: list[float], window: int) -> list[float]:
    if window <= 0:
        return []
    q: deque[float] = deque(maxlen=window)
    result: list[float] = []
    for v in values:
        q.append(v)
        result.append(sum(q) / len(q))
    return result


