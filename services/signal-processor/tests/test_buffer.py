import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import main  # noqa: E402


def test_to_ohlcv_resamples_and_is_ordered():
    buf = main.TickBuffer(maxlen=1000)
    base = 1_700_000_000
    for i in range(60):
        price = 2000 + i * 0.1
        buf.add({'ts': base + i * 60, 'bid': price, 'ask': price + 0.1, 'volume': 1.0})

    df = buf.to_ohlcv('15min')
    assert not df.empty
    assert list(df.columns) == ['Open', 'High', 'Low', 'Close', 'Volume']
    assert (df['High'] >= df['Low']).all()


def test_buffer_respects_maxlen():
    buf = main.TickBuffer(maxlen=10)
    for i in range(25):
        buf.add({'ts': i, 'bid': 1.0, 'ask': 1.1, 'volume': 1.0})
    assert len(buf) == 10


def test_empty_buffer_returns_empty_frame():
    assert main.TickBuffer().to_ohlcv('15min').empty
