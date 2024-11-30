# oracle_analysis/oracle/models.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict

class OracleType(Enum):
    """Supported oracle protocol types."""
    CHAINLINK = "chainlink"
    TELLOR = "tellor"
    REDSTONE = "redstone"
    UNISWAP = "uniswap"
    PYTH = "pyth"
    API3 = "api3"
    BAND = "band"
    DIA = "dia"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, value: str) -> 'OracleType':
        """Create OracleType from string value."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.UNKNOWN

@dataclass
class OraclePattern:
    """Pattern definitions for oracle identification."""
    # Function dispatcher patterns (PUSH4 + signature)
    function_patterns: List[str]
    
    # Storage layout patterns
    storage_patterns: List[str]
    
    # Minimum required function matches for positive identification
    required_function_matches: int
    
    # Contract creation patterns (optional)
    creation_patterns: Optional[List[str]] = None
    
    # Common function names (for documentation and verification)
    function_names: Optional[List[str]] = None
    
    # Known factory addresses for this oracle type
    factory_addresses: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        """Convert pattern to dictionary format."""
        return {
            'function_patterns': self.function_patterns,
            'storage_patterns': self.storage_patterns,
            'required_function_matches': self.required_function_matches,
            'creation_patterns': self.creation_patterns,
            'function_names': self.function_names,
            'factory_addresses': self.factory_addresses
        }

@dataclass
class OracleIdentificationResult:
    """Result of oracle identification process."""
    oracle_type: OracleType
    address: str
    confidence: float
    matched_functions: List[str]
    matched_storage: List[str]
    creation_match: Optional[bool] = None
    factory_match: Optional[bool] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary format."""
        return {
            'type': self.oracle_type.value,
            'address': self.address,
            'confidence': self.confidence,
            'matched_functions': self.matched_functions,
            'matched_storage': self.matched_storage,
            'creation_match': self.creation_match,
            'factory_match': self.factory_match,
            'error': self.error
        }

