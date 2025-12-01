"""Signal domain model."""

from dataclasses import dataclass
from typing import Literal

SignalType = Literal['BREAKOUT', 'BREAKDOWN']


@dataclass
class Signal:
    """Represents a trading signal (breakout/breakdown)."""
    
    symbol: str
    signal_type: SignalType
    price: float
    swing_level: float
    vol_ratio: float
    timestamp: datetime
    
    def is_breakout(self) -> bool:
        """Check if signal is a breakout."""
        return self.signal_type == 'BREAKOUT'
    
    def is_breakdown(self) -> bool:
        """Check if signal is a breakdown."""
        return self.signal_type == 'BREAKDOWN'

