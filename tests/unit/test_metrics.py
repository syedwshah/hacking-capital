from app.services.metrics import simple_moving_average, rsi, macd


def test_sma_basic():
    xs = [1, 2, 3, 4]
    sma = simple_moving_average(xs, 2)
    assert sma[-1] == 3.5


def test_rsi_macd_shapes():
    xs = list(range(1, 100))
    r = rsi(xs, 14)
    m_line, sig, hist = macd(xs)
    assert len(r) == len(xs)
    assert len(m_line) == len(xs)


