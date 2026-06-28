import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import main  # noqa: E402


def _signal():
    return {
        'signal': 'LONG', 'entry_price': 2000.0, 'stop_loss': 1998.0,
        'take_profit_1': 2003.0, 'take_profit_2': 2005.0, 'take_profit_3': 2008.0,
        'pips_risk': 20.0, 'confidence': 75, 'regime': 'Range-bound',
        'session': 'London', 'level_name': 'PDH', 'rr_ratio': 1.5,
        'risk_dollars': 150.0, 'latency_ms': 12.0,
    }


def test_format_contains_key_fields():
    msg = main.format_telegram_message(_signal())
    assert 'LONG' in msg
    assert '2000.00' in msg     # entry
    assert '1998.00' in msg     # stop loss
    assert '75%' in msg         # confidence


def test_format_handles_missing_fields():
    # Should not raise on a sparse signal dict
    msg = main.format_telegram_message({'signal': 'SHORT'})
    assert 'SHORT' in msg


def test_success_rate_tracking():
    main._sent_count = 0
    main._total_count = 0
    main._update_success_rate(True)
    main._update_success_rate(False)
    assert main._total_count == 2
    assert main._sent_count == 1
