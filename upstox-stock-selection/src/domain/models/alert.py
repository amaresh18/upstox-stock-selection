"""Alert domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Alert:
    """Represents a trading alert."""
    
    symbol: str
    timestamp: datetime
    signal_type: str  # BREAKOUT, BREAKDOWN, or pattern type
    price: float
    vol_ratio: float
    
    # Optional fields
    swing_high: Optional[float] = None
    swing_low: Optional[float] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    pnl_pct: Optional[float] = None
    price_momentum: Optional[float] = None
    avg_momentum_7d: Optional[float] = None
    momentum_ratio: Optional[float] = None
    range: Optional[float] = None
    avg_range: Optional[float] = None
    bars_after: Optional[int] = None
    
    # Pattern-specific fields
    pattern_type: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        result = {
            'symbol': self.symbol,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.timestamp, datetime) else str(self.timestamp),
            'signal_type': self.signal_type,
            'price': self.price,
            'vol_ratio': self.vol_ratio,
        }
        
        if self.pattern_type:
            result['pattern_type'] = self.pattern_type
        
        optional_fields = [
            'swing_high', 'swing_low', 'entry_price', 'exit_price', 'pnl_pct',
            'price_momentum', 'avg_momentum_7d', 'momentum_ratio', 'range',
            'avg_range', 'bars_after'
        ]
        
        for field_name in optional_fields:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        
        result.update(self.additional_data)
        return result

