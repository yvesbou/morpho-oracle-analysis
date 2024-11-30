# oracle_analysis/oracle/__init__.py
"""Oracle identification and analysis module."""
from .models import OracleType, OraclePattern, OracleIdentificationResult
from .identifier import OracleIdentifier
from .patterns import (
    CHAINLINK_PATTERNS,
    TELLOR_PATTERNS,
    UNISWAP_PATTERNS,
    PYTH_PATTERNS,
    REDSTONE_PATTERNS
)

__all__ = [
    'OracleType',
    'OraclePattern',
    'OracleIdentificationResult',
    'OracleIdentifier',
    'CHAINLINK_PATTERNS',
    'TELLOR_PATTERNS',
    'UNISWAP_PATTERNS',
    'PYTH_PATTERNS',
    'REDSTONE_PATTERNS'
]

