# oracle_analysis/market/models.py
from dataclasses import dataclass
from typing import Optional
from web3.types import BlockIdentifier

@dataclass
class MarketParams:
    """Represents the parameters of a market."""
    loan_token: str
    collateral_token: str
    oracle: str
    irm: str
    lltv: int

    @classmethod
    def from_tuple(cls, data: tuple) -> 'MarketParams':
        """Create MarketParams from contract event tuple."""
        return cls(
            loan_token=data[0],
            collateral_token=data[1],
            oracle=data[2],
            irm=data[3],
            lltv=data[4]
        )

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'loan_token': self.loan_token,
            'collateral_token': self.collateral_token,
            'oracle': self.oracle,
            'irm': self.irm,
            'lltv': self.lltv
        }

@dataclass
class MarketEvent:
    """Represents a market creation event."""
    id: str
    params: MarketParams
    block_number: int
    transaction_hash: str
    timestamp: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'id': self.id,
            'block_number': self.block_number,
            'transaction_hash': self.transaction_hash,
            'timestamp': self.timestamp,
            **self.params.to_dict()
        }

