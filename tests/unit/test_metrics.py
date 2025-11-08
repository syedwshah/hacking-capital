from app.services.metrics import simple_moving_average


def test_sma_basic():
    xs = [1, 2, 3, 4]
    sma = simple_moving_average(xs, 2)
    assert sma[-1] == 3.5


