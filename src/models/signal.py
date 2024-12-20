from dataclasses import dataclass

@dataclass
class SignalConfig:
    symbol: str
    timeframe: str  # e.g., "7w" for 7 weeks
    
    @property
    def period(self) -> int:
        return int(self.timeframe[:-1])
        
    @property
    def unit(self) -> str:
        return self.timeframe[-1]