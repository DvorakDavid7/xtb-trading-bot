from datetime import datetime
import time

class TimeStamp:

    timestamp: float

    def __init__(self, input_time=None) -> None:
        """
        Initialize the timestamp. Accepts:
        - None: initializes with the current time
        - float (POSIX timestamp in seconds)
        - str (ISO 8601 date-time string)
        - datetime object
        """
        if input_time is None:
            self.timestamp = round(time.time() * 1000)
        elif isinstance(input_time, (int, float)):
            self.timestamp = round(input_time * 1000)
        elif isinstance(input_time, str):
            dt = datetime.fromisoformat(input_time)
            self.timestamp = round(dt.timestamp() * 1000)
        elif isinstance(input_time, datetime):
            self.timestamp = round(input_time.timestamp() * 1000)
        else:
            raise TypeError("Unsupported input type for TimeStamp")
    
    def now(self):
        self.timestamp = round(time.time() * 1000)
        return self

    def add_ms(self, ms: float) -> "TimeStamp":
        """Add milliseconds to the current timestamp."""
        self.timestamp += ms
        return self

    def sub_ms(self, ms: float) -> "TimeStamp":
        """Subtract milliseconds from the current timestamp."""
        self.timestamp -= ms
        return self

    def add_sec(self, sec: float) -> "TimeStamp":
        """Add seconds to the current timestamp."""
        ms = sec * 1000
        return self.add_ms(ms)

    def sub_sec(self, sec: float) -> "TimeStamp":
        """Subtract seconds from the current timestamp."""
        ms = sec * 1000
        return self.sub_ms(ms)

    def add_min(self, min: float) -> "TimeStamp":
        """Add minutes to the current timestamp."""
        ms = min * 60 * 1000
        return self.add_ms(ms)

    def sub_min(self, min: float) -> "TimeStamp":
        """Subtract minutes from the current timestamp."""
        ms = min * 60 * 1000
        return self.sub_ms(ms)

    def add_hr(self, hr: float) -> "TimeStamp":
        """Add hours to the current timestamp."""
        ms = hr * 60 * 60 * 1000
        return self.add_ms(ms)

    def sub_hr(self, hr: float) -> "TimeStamp":
        """Subtract hours from the current timestamp."""
        ms = hr * 60 * 60 * 1000
        return self.sub_ms(ms)

    def add_day(self, day: float) -> "TimeStamp":
        """Add days to the current timestamp."""
        ms = day * 24 * 60 * 60 * 1000
        return self.add_ms(ms)

    def sub_day(self, day: float) -> "TimeStamp":
        """Subtract days from the current timestamp."""
        ms = day * 24 * 60 * 60 * 1000
        return self.sub_ms(ms)

    def __repr__(self) -> str:
        """Return the string representation of the timestamp."""
        human_readable = datetime.fromtimestamp(self.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        return f"TimeStamp({self.timestamp} ms, {human_readable})"

    def value(self) -> float:
        """Return the raw timestamp value."""
        return self.timestamp
