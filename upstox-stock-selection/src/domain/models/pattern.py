"""Pattern domain model."""

from dataclasses import dataclass
from typing import Literal, Optional
from datetime import datetime

PatternType = Literal[
    'RSI_BULLISH_DIVERGENCE',
    'RSI_BEARISH_DIVERGENCE',
    'UPTREND_RETEST',
    'DOWNTREND_RETEST',
    'INVERSE_HEAD_SHOULDERS',
    'DOUBLE_BOTTOM',
    'DOUBLE_TOP',
    'TRIPLE_BOTTOM',
    'TRIPLE_TOP'
]


@dataclass
class Pattern:
    """Represents a detected trading pattern."""
    
    symbol: str
    pattern_type: PatternType
    price: float
    timestamp: datetime
    entry_price: float
    stop_loss: float
    target_price: float
    vol_ratio: Optional[float] = None
    
    def is_bullish(self) -> bool:
        """Check if pattern is bullish."""
        bullish_patterns = [
            'RSI_BULLISH_DIVERGENCE',
            'UPTREND_RETEST',
            'INVERSE_HEAD_SHOULDERS',
            'DOUBLE_BOTTOM',
            'TRIPLE_BOTTOM'
        ]
        return self.pattern_type in bullish_patterns
    
    def is_bearish(self) -> bool:
        """Check if pattern is bearish."""
        return not self.is_bullish()
