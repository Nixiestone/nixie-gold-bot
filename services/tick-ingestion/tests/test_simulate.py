import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import main  # noqa: E402


def _bar():
    return {'ts': 1_700_000_000.0, 'open': 2000.0, 'high': 2005.0,
            'low': 1995.0, 'close': 2002.0, 'volume': 120.0}


def test_simulate_ticks_count_and_bounds():
    ticks = main.simulate_ticks(_bar(), n=12)
    assert len(ticks) == 12
    for t in ticks:
        assert 1995.0 <= t['bid'] <= 2005.0          # bid clipped to bar range
        assert t['ask'] == round(t['bid'] + main.SPREAD, 2)
        assert set(t) == {'ts', 'bid', 'ask', 'volume', 'source'}


def test_simulate_ticks_timestamps_monotonic():
    ts = [t['ts'] for t in main.simulate_ticks(_bar(), n=8)]
    assert ts == sorted(ts)


def test_random_walk_updates_last_price():
    bar = main.simulate_random_walk_bar()
    assert bar['high'] >= bar['low']
    assert main._last_price == bar['close']
