import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
import pandas as pd
import pytz
import config

class MarketHours:
    def __init__(self):
        self.gmt = pytz.timezone('GMT')
    
    def get_current_hour_gmt(self):
        """Get current hour in GMT"""
        now = datetime.now(self.gmt)
        return now.hour
    
    def is_london_session(self):
        """Check if it's London trading session (08:00-16:00 GMT)"""
        hour = self.get_current_hour_gmt()
        return config.LONDON_OPEN <= hour < config.LONDON_CLOSE
    
    def is_ny_session(self):
        """Check if it's New York trading session (13:00-21:00 GMT)"""
        hour = self.get_current_hour_gmt()
        return config.NY_OPEN <= hour < config.NY_CLOSE
    
    def is_optimal_session(self):
        """
        Check if current time is optimal for trading
        Optimal: London or NY session
        """
        return self.is_london_session() or self.is_ny_session()
    
    def get_session_overlap(self):
        """Check if both London and NY sessions overlap"""
        return self.is_london_session() and self.is_ny_session()
    
    def get_current_session(self):
        """Get name of current trading session"""
        hour = self.get_current_hour_gmt()
        
        sessions = []
        if self.is_london_session():
            sessions.append("London")
        if self.is_ny_session():
            sessions.append("New York")
        
        if sessions:
            return " + ".join(sessions)
        
        # Determine which session we're closest to
        if hour < config.LONDON_OPEN:
            return "Asian (Pre-London)"
        elif hour >= config.NY_CLOSE:
            return "After Hours"
        else:
            return "Between Sessions"
    
    def get_asian_range(self, df):
        """
        Get Asian session range (00:00-08:00 GMT)
        Returns (high, low) of Asian session
        """
        try:
            # Filter data for Asian hours
            asian_data = df.between_time('00:00', '08:00')
            
            if len(asian_data) == 0:
                return None, None
            
            asian_high = asian_data['High'].max()
            asian_low = asian_data['Low'].min()
            
            return asian_high, asian_low
            
        except Exception as e:
            print(f" Error calculating Asian range: {e}")
            return None, None
    
    def get_previous_day_levels(self, df):
        """Get previous day's high and low"""
        try:
            # Get yesterday's data
            yesterday = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
            
            return {
                'pdh': yesterday['High'],  # Previous Day High
                'pdl': yesterday['Low'],   # Previous Day Low
                'pdc': yesterday['Close']  # Previous Day Close
            }
        except Exception as e:
            print(f" Error getting previous day levels: {e}")
            return None
    
    def should_trade_now(self, timestamp=None):
        """
        Determine if we should scan for trades now
        
        Args:
            timestamp: Optional datetime to check (for backtesting)
        
        Returns: (bool, reason)
        """
        # Use provided timestamp or current time
        if timestamp is None:
            now = datetime.now(self.gmt)
        else:
            # Convert timestamp to GMT if it's not already
            if hasattr(timestamp, 'tz_localize'):
                now = timestamp.tz_localize('UTC').tz_convert(self.gmt)
            elif hasattr(timestamp, 'tz_convert'):
                now = timestamp.tz_convert(self.gmt)
            else:
                # Assume it's a pandas timestamp or datetime
                try:
                    now = pd.Timestamp(timestamp).tz_localize(None).tz_localize('UTC').tz_convert(self.gmt)
                except:
                    now = timestamp.replace(tzinfo=self.gmt)
        
        hour = now.hour
        
        # Check optimal session
        in_session = (config.LONDON_OPEN <= hour < config.LONDON_CLOSE) or \
                    (config.NY_OPEN <= hour < config.NY_CLOSE)
        
        if not in_session:
            return False, f"Outside trading hours (current hour: {hour} GMT)"
        
        # Check for weekend
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False, "Weekend - Market closed"
        
        # Determine session name
        sessions = []
        if config.LONDON_OPEN <= hour < config.LONDON_CLOSE:
            sessions.append("London")
        if config.NY_OPEN <= hour < config.NY_CLOSE:
            sessions.append("New York")
        
        session_name = " + ".join(sessions) if sessions else "Unknown"
        
        return True, f"Active trading session: {session_name}"


# Test the module
if __name__ == "__main__":
    market = MarketHours()
    
    print(" Current Time Analysis:")
    print(f"GMT Hour: {market.get_current_hour_gmt()}:00")
    print(f"Current Session: {market.get_current_session()}")
    print(f"London Session: {' Yes' if market.is_london_session() else '[ERROR] No'}")
    print(f"NY Session: {' Yes' if market.is_ny_session() else '[ERROR] No'}")
    print(f"Session Overlap: {' Yes' if market.get_session_overlap() else '[ERROR] No'}")
    
    should_trade, reason = market.should_trade_now()
    print(f"\n Should Trade Now: {' Yes' if should_trade else '[ERROR] No'}")
    print(f"Reason: {reason}")