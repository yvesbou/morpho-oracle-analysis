# oracle_analysis/oracle/identifier.py
import logging
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from web3.types import HexBytes

from .models import OracleType, OraclePattern, OracleIdentificationResult
from .patterns import (
    CHAINLINK_PATTERNS,
    TELLOR_PATTERNS,
    UNISWAP_PATTERNS,
    PYTH_PATTERNS,
    REDSTONE_PATTERNS
)

logger = logging.getLogger(__name__)

class OracleIdentifier:
    """Identifies oracle protocols based on contract analysis."""

    def __init__(self, web3_provider: str):
        """Initialize the oracle identifier."""
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.patterns = {
            OracleType.CHAINLINK: CHAINLINK_PATTERNS,
            OracleType.TELLOR: TELLOR_PATTERNS,
            OracleType.UNISWAP: UNISWAP_PATTERNS,
            OracleType.PYTH: PYTH_PATTERNS,
            OracleType.REDSTONE: REDSTONE_PATTERNS
        }

    def get_contract_code(self, address: str) -> Optional[HexBytes]:
        """Fetch contract bytecode from the blockchain."""
        try:
            code = self.w3.eth.get_code(Web3.to_checksum_address(address))
            return code if code and code != HexBytes('0x') else None
        except Exception as e:
            logger.error(f"Error fetching code for {address}: {e}")
            return None

    def analyze_code_patterns(
        self,
        bytecode: HexBytes,
        pattern: OraclePattern
    ) -> Tuple[List[str], List[str]]:
        """
        Analyze bytecode against oracle patterns.
        Returns tuple of (matched_functions, matched_storage).
        """
        bytecode_hex = bytecode.hex()
        
        matched_functions = [
            pattern for pattern in pattern.function_patterns
            if pattern in bytecode_hex
        ]
        
        matched_storage = [
            pattern for pattern in pattern.storage_patterns
            if pattern in bytecode_hex
        ]
        
        return matched_functions, matched_storage

    def check_factory_match(self, address: str, pattern: OraclePattern) -> bool:
        """Check if contract was deployed by a known factory."""
        if not pattern.factory_addresses:
            return False
            
        try:
            # Get contract creation transaction
            tx_hash = self.w3.eth.get_transaction_by_block(
                self.w3.eth.get_block_number(),
                0
            )
            if tx_hash and tx_hash['from'] in pattern.factory_addresses:
                return True
        except Exception as e:
            logger.debug(f"Error checking factory for {address}: {e}")
        
        return False

    def calculate_confidence(
        self,
        matched_functions: List[str],
        matched_storage: List[str],
        pattern: OraclePattern,
        factory_match: bool
    ) -> float:
        """Calculate confidence score for oracle identification."""
        # Base confidence from function matches
        func_ratio = len(matched_functions) / len(pattern.function_patterns)
        func_confidence = func_ratio * 0.6  # Functions are weighted at 60%
        
        # Storage pattern confidence
        storage_ratio = len(matched_storage) / len(pattern.storage_patterns)
        storage_confidence = storage_ratio * 0.3  # Storage is weighted at 30%
        
        # Factory match adds 10% confidence
        factory_confidence = 0.1 if factory_match else 0
        
        total_confidence = func_confidence + storage_confidence + factory_confidence
        
        # Require minimum function matches
        if len(matched_functions) < pattern.required_function_matches:
            total_confidence = 0
            
        return min(1.0, total_confidence)

    def identify_oracle(self, address: str) -> OracleIdentificationResult:
        """
        Identify oracle protocol for a given contract address.
        Returns detailed identification result.
        """
        try:
            # Get contract bytecode
            bytecode = self.get_contract_code(address)
            if not bytecode:
                return OracleIdentificationResult(
                    oracle_type=OracleType.UNKNOWN,
                    address=address,
                    confidence=0.0,
                    matched_functions=[],
                    matched_storage=[],
                    error="No contract code found"
                )

            best_match = None
            highest_confidence = 0.0

            # Test against each oracle pattern
            for oracle_type, pattern in self.patterns.items():
                # Analyze code patterns
                matched_functions, matched_storage = self.analyze_code_patterns(
                    bytecode, pattern
                )
                
                # Check factory match
                factory_match = self.check_factory_match(address, pattern)
                
                # Calculate confidence
                confidence = self.calculate_confidence(
                    matched_functions,
                    matched_storage,
                    pattern,
                    factory_match
                )
                
                if confidence > highest_confidence:
                    highest_confidence = confidence
                    best_match = OracleIdentificationResult(
                        oracle_type=oracle_type,
                        address=address,
                        confidence=confidence,
                        matched_functions=matched_functions,
                        matched_storage=matched_storage,
                        factory_match=factory_match
                    )

            return best_match or OracleIdentificationResult(
                oracle_type=OracleType.UNKNOWN,
                address=address,
                confidence=0.0,
                matched_functions=[],
                matched_storage=[]
            )

        except Exception as e:
            logger.error(f"Error identifying oracle {address}: {e}")
            return OracleIdentificationResult(
                oracle_type=OracleType.UNKNOWN,
                address=address,
                confidence=0.0,
                matched_functions=[],
                matched_storage=[],
                error=str(e)
            )