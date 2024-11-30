# oracle_analysis/utils/web3_utils.py
import logging
import time
from typing import Any, Optional, Tuple, Callable, Dict
from functools import wraps
import requests
from web3 import Web3
from web3.exceptions import ContractLogicError, BlockNotFound
from web3.types import BlockIdentifier

from ..config import Config

logger = logging.getLogger(__name__)

def setup_web3(provider_url: str) -> Web3:
    """
    Initialize and validate Web3 connection.
    
    Args:
        provider_url: Ethereum node RPC URL
        
    Returns:
        Configured Web3 instance
        
    Raises:
        ConnectionError: If unable to connect to the provider
    """
    w3 = Web3(Web3.HTTPProvider(provider_url))
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to Ethereum node at {provider_url}")
    return w3

def validate_address(address: str) -> bool:
    """
    Validate Ethereum address format.
    
    Args:
        address: Ethereum address to validate
        
    Returns:
        bool: True if address is valid
    """
    try:
        return Web3.is_address(address) and Web3.is_checksum_address(address)
    except ValueError:
        return False

def retry_web3_call(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (ContractLogicError, BlockNotFound, requests.exceptions.RequestException)
):
    """
    Decorator for retrying Web3 calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay between retries
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if retries == max_retries:
                        logger.error(f"Max retries ({max_retries}) reached for {func.__name__}")
                        raise
                        
                    retries += 1
                    logger.warning(
                        f"Retry {retries}/{max_retries} for {func.__name__} "
                        f"after error: {str(e)}"
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        return wrapper
    return decorator

@retry_web3_call()
def get_contract_creation(
    w3: Web3,
    contract_address: str
) -> Optional[Dict[str, Any]]:
    """
    Get contract creation transaction details.
    
    Args:
        w3: Web3 instance
        contract_address: Contract address to check
        
    Returns:
        Dict containing creation transaction details or None
    """
    # Convert to checksum address
    contract_address = Web3.to_checksum_address(contract_address)
    
    # Get the earliest transaction for this address
    block = w3.eth.get_block('latest')
    for tx_hash in block['transactions']:
        tx = w3.eth.get_transaction(tx_hash)
        if tx['to'] is None and tx['creates'] == contract_address:
            return {
                'creator': tx['from'],
                'creation_tx': tx_hash.hex(),
                'block_number': tx['blockNumber'],
                'creation_code': tx['input']
            }
    
    return None

@retry_web3_call()
def get_abi_for_address(
    contract_address: str,
    etherscan_api_key: Optional[str] = None
) -> Optional[list]:
    """
    Fetch contract ABI from Etherscan.
    
    Args:
        contract_address: Contract address
        etherscan_api_key: Etherscan API key (optional)
        
    Returns:
        Contract ABI as list or None if not found
    """
    if not etherscan_api_key:
        etherscan_api_key = Config.ETHERSCAN_API_KEY
        
    if not etherscan_api_key:
        logger.warning("No Etherscan API key provided")
        return None
        
    url = (
        f"https://api.etherscan.io/api"
        f"?module=contract"
        f"&action=getabi"
        f"&address={contract_address}"
        f"&apikey={etherscan_api_key}"
    )
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        
        if result['status'] == '1' and result['message'] == 'OK':
            return result['result']
        else:
            logger.warning(f"No verified contract found for {contract_address}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching ABI for {contract_address}: {e}")
        return None

@retry_web3_call()
def get_block_timestamp(w3: Web3, block_identifier: BlockIdentifier) -> int:
    """
    Get timestamp for a specific block.
    
    Args:
        w3: Web3 instance
        block_identifier: Block number or hash
        
    Returns:
        Block timestamp as Unix timestamp
    """
    block = w3.eth.get_block(block_identifier)
    return block['timestamp']

def estimate_blocks_per_day(w3: Web3, sample_size: int = 1000) -> float:
    """
    Estimate average blocks per day based on recent blocks.
    
    Args:
        w3: Web3 instance
        sample_size: Number of recent blocks to sample
        
    Returns:
        Estimated blocks per day
    """
    latest_block = w3.eth.block_number
    start_block = latest_block - sample_size
    
    start_time = get_block_timestamp(w3, start_block)
    end_time = get_block_timestamp(w3, latest_block)
    
    time_diff = end_time - start_time  # in seconds
    blocks_per_day = (sample_size / time_diff) * 86400  # 86400 seconds in a day
    
    return blocks_per_day

def calculate_block_range(
    w3: Web3,
    days_ago: float
) -> Tuple[int, int]:
    """
    Calculate block range for a given time period.
    
    Args:
        w3: Web3 instance
        days_ago: Number of days to look back
        
    Returns:
        Tuple of (start_block, end_block)
    """
    blocks_per_day = estimate_blocks_per_day(w3)
    blocks_to_search = int(blocks_per_day * days_ago)
    
    end_block = w3.eth.block_number
    start_block = max(0, end_block - blocks_to_search)
    
    return start_block, end_block