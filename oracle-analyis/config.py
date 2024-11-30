import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class Config:
    """Configuration management for Oracle Analysis"""
    
    # Load environment variables
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)

    # Core settings
    RPC_URL: str = os.getenv('RPC_URL')
    CONTRACT_ADDRESS: str = os.getenv('CONTRACT_ADDRESS')
    ETHERSCAN_API_KEY: str = os.getenv('ETHERSCAN_API_KEY')
    START_BLOCK: int = int(os.getenv('START_BLOCK', '0'))
    
    # Analysis settings
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '2000'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    DELAY_BETWEEN_REQUESTS: float = float(os.getenv('DELAY_BETWEEN_REQUESTS', '0.1'))
    
    # Output settings
    OUTPUT_DIR: str = os.getenv('OUTPUT_DIR', 'results')
    
    @classmethod
    def validate(cls) -> Optional[str]:
        """
        Validate the configuration.
        Returns error message if invalid, None if valid.
        """
        if not cls.RPC_URL:
            return "RPC_URL is required"
        if not cls.CONTRACT_ADDRESS:
            return "CONTRACT_ADDRESS is required"
        if not cls.CONTRACT_ADDRESS.startswith('0x'):
            return "CONTRACT_ADDRESS must start with '0x'"
        if len(cls.CONTRACT_ADDRESS) != 42:
            return "CONTRACT_ADDRESS must be 42 characters long"
        return None
    
    @classmethod
    def create_output_dir(cls) -> None:
        """Create output directory if it doesn't exist"""
        Path(cls.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

