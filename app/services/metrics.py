from collections import deque
from typing import List


def simple_moving_average(values: list[float], window: int) -> list[float]:
    if window <= 0:
        return []
    q: deque[float] = deque(maxlen=window)
    result: list[float] = []
    for v in values:
        q.append(v)
        result.append(sum(q) / len(q))
    return result


def exponential_moving_average(values: List[float], window: int) -> List[float]:
    if window <= 0 or not values:
        return []
    k = 2 / (window + 1)
    ema: List[float] = []
    prev = values[0]
    for v in values:
        prev = v * k + prev * (1 - k)
        ema.append(prev)
    return ema


def rsi(values: List[float], period: int = 14) -> List[float]:
    if len(values) < period + 1:
        return [50.0] * len(values)
    gains = [0.0]
    losses = [0.0]
    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        gains.append(max(0.0, diff))
        losses.append(max(0.0, -diff))
    avg_gain = simple_moving_average(gains, period)
    avg_loss = simple_moving_average(losses, period)
    out: List[float] = []
    for g, l in zip(avg_gain, avg_loss):
        if l == 0:
            out.append(100.0)
        else:
            rs = g / l
            out.append(100 - (100 / (1 + rs)))
    # pad to length
    if len(out) < len(values):
        out = [50.0] * (len(values) - len(out)) + out
    return out


def macd(values: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[List[float], List[float], List[float]]:
    ema_fast = exponential_moving_average(values, fast)
    ema_slow = exponential_moving_average(values, slow)
    macd_line = [a - b for a, b in zip(ema_fast[-len(ema_slow):], ema_slow)]
    # Align lengths by trimming leading entries from ema_fast to length of ema_slow
    if len(macd_line) < len(values):
        macd_line = [0.0] * (len(values) - len(macd_line)) + macd_line
    signal_line = exponential_moving_average(macd_line, signal)
    hist = [m - s for m, s in zip(macd_line[-len(signal_line):], signal_line)]
    if len(hist) < len(values):
        hist = [0.0] * (len(values) - len(hist)) + hist
    return macd_line, signal_line, hist


