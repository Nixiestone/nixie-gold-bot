from datetime import datetime
import pandas as pd
import pytz
import config


class MarketHours:
    def __init__(self):
        self.gmt = pytz.timezone('GMT')

    def get_current_hour_gmt(self):
        return datetime.now(self.gmt).hour

    def is_london_session(self):
        return config.LONDON_OPEN <= self.get_current_hour_gmt() < config.LONDON_CLOSE

    def is_ny_session(self):
        return config.NY_OPEN <= self.get_current_hour_gmt() < config.NY_CLOSE

    def is_optimal_session(self):
        return self.is_london_session() or self.is_ny_session()

    def get_session_overlap(self):
        return self.is_london_session() and self.is_ny_session()

    def get_current_session(self):
        sessions = []
        if self.is_london_session():
            sessions.append('London')
        if self.is_ny_session():
            sessions.append('New York')
        if sessions:
            return ' + '.join(sessions)
        hour = self.get_current_hour_gmt()
        if hour < config.LONDON_OPEN:
            return 'Asian (Pre-London)'
        elif hour >= config.NY_CLOSE:
            return 'After Hours'
        return 'Between Sessions'

    def get_asian_range(self, df):
        try:
            asian_data = df.between_time('00:00', '08:00')
            if len(asian_data) == 0:
                return None, None
            return asian_data['High'].max(), asian_data['Low'].min()
        except Exception:
            return None, None

    def get_previous_day_levels(self, df):
        try:
            yesterday = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
            return {'pdh': yesterday['High'], 'pdl': yesterday['Low'], 'pdc': yesterday['Close']}
        except Exception:
            return None

    def should_trade_now(self, timestamp=None):
        if timestamp is None:
            now = datetime.now(self.gmt)
        else:
            if hasattr(timestamp, 'tz_localize'):
                now = timestamp.tz_localize('UTC').tz_convert(self.gmt)
            elif hasattr(timestamp, 'tz_convert'):
                now = timestamp.tz_convert(self.gmt)
            else:
                try:
                    now = pd.Timestamp(timestamp).tz_localize(None).tz_localize('UTC').tz_convert(self.gmt)
                except Exception:
                    now = timestamp.replace(tzinfo=self.gmt)

        hour = now.hour
        in_session = (config.LONDON_OPEN <= hour < config.LONDON_CLOSE) or \
                     (config.NY_OPEN <= hour < config.NY_CLOSE)

        if not in_session:
            return False, f'Outside trading hours (current hour: {hour} GMT)'
        if now.weekday() >= 5:
            return False, 'Weekend - Market closed'

        sessions = []
        if config.LONDON_OPEN <= hour < config.LONDON_CLOSE:
            sessions.append('London')
        if config.NY_OPEN <= hour < config.NY_CLOSE:
            sessions.append('New York')
        return True, f"Active trading session: {' + '.join(sessions)}"
