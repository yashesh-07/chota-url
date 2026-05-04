import time
import threading
import os

class URLConverter:
    """Handles conversion between Snowflake IDs (Base10) and Short Codes (Base62)."""
    
    # 0-9, a-z, A-Z (Total 62 characters)
    CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @classmethod
    def encode(cls, num: int) -> str:
        """Converts a unique integer to a Base62 string."""
        if num == 0:
            return cls.CHARS[0]
        
        arr = []
        base = len(cls.CHARS)
        while num:
            num, rem = divmod(num, base)
            arr.append(cls.CHARS[rem])
        
        arr.reverse()
        return "".join(arr)

    @classmethod
    def decode(cls, string: str) -> int:
        """Converts a Base62 short code back to its original Snowflake ID."""
        base = len(cls.CHARS)
        num = 0
        for char in string:
            num = num * base + cls.CHARS.index(char)
        return num

class SnowflakeID:
    """Generates unique, time-sortable 64-bit IDs across multiple nodes."""
    
    def __init__(self):
        # Configuration from .env
        self.machine_id = int(os.getenv("MACHINE_ID", "1"))
        self.epoch = int(os.getenv("CUSTOM_EPOCH", "1714848000000"))
        
        # Internal state
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _timestamp(self):
        """Returns current time in milliseconds."""
        return int(time.time() * 1000)

    def generate(self):
        """Generates a new unique Snowflake ID."""
        with self.lock:
            timestamp = self._timestamp()
            
            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards! Cannot generate ID.")

            if timestamp == self.last_timestamp:
                # Same millisecond, increment sequence (0-7)
                self.sequence = (self.sequence + 1) & 7
                if self.sequence == 0:
                    # Sequence exhausted, wait for next millisecond
                    while timestamp <= self.last_timestamp:
                        timestamp = self._timestamp()
            else:
                # New millisecond, reset sequence
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            # ID structure: [41-bit Timestamp][2-bit Machine ID][3-bit Sequence]
            return ((timestamp - self.epoch) << 5) | (self.machine_id << 2) | self.sequence

# Single instance to be imported by the API routes
id_worker = SnowflakeID()