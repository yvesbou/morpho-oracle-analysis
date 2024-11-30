# oracle_analysis/market/events.py
import logging
from typing import List, Optional
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import BlockNotFound, ContractLogicError
from web3.types import EventData
from tqdm import tqdm
import time

from ..config import Config
from .models import MarketEvent, MarketParams

logger = logging.getLogger(__name__)

class MarketEventFetcher:
    """Fetches and processes market creation events."""
    
    # ABI for the CreateMarket event
    EVENT_ABI = {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "id",
                "type": "bytes32"
            },
            {
                "indexed": False,
                "name": "marketParams",
                "type": "tuple",
                "components": [
                    {"name": "loanToken", "type": "address"},
                    {"name": "collateralToken", "type": "address"},
                    {"name": "oracle", "type": "address"},
                    {"name": "irm", "type": "address"},
                    {"name": "lltv", "type": "uint256"}
                ]
            }
        ],
        "name": "CreateMarket",
        "type": "event"
    }

    def __init__(self, web3_provider: str, contract_address: str):
        """Initialize the event fetcher."""
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=[self.EVENT_ABI]
        )
        self.retry_delay = Config.DELAY_BETWEEN_REQUESTS
        self.max_retries = Config.MAX_RETRIES

    def _process_event(self, event: EventData) -> MarketEvent:
        """Process a single event into a MarketEvent object."""
        try:
            # Get block timestamp
            block = self.w3.eth.get_block(event['blockNumber'])
            timestamp = block['timestamp'] if block else None

            return MarketEvent(
                id=event['args']['id'].hex(),
                params=MarketParams.from_tuple(event['args']['marketParams']),
                block_number=event['blockNumber'],
                transaction_hash=event['transactionHash'].hex(),
                timestamp=timestamp
            )
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            raise

    def fetch_events_batch(
        self,
        start_block: int,
        end_block: int,
        retry_count: int = 0
    ) -> List[MarketEvent]:
        """Fetch events for a specific block range."""
        try:
            event_filter = self.contract.events.CreateMarket.create_filter(
                fromBlock=start_block,
                toBlock=end_block
            )
            
            events = event_filter.get_all_entries()
            return [self._process_event(event) for event in events]
            
        except (BlockNotFound, ContractLogicError) as e:
            if retry_count >= self.max_retries:
                logger.error(f"Max retries reached for blocks {start_block}-{end_block}")
                raise
                
            logger.warning(f"Retrying blocks {start_block}-{end_block} after error: {e}")
            time.sleep(self.retry_delay * (retry_count + 1))
            return self.fetch_events_batch(start_block, end_block, retry_count + 1)

    def fetch_events(
        self,
        start_block: Optional[int] = None,
        end_block: Optional[int] = None,
        batch_size: Optional[int] = None
    ) -> List[MarketEvent]:
        """
        Fetch all CreateMarket events between specified blocks.
        
        Args:
            start_block: Starting block number (default: Config.START_BLOCK)
            end_block: Ending block number (default: latest block)
            batch_size: Number of blocks per batch (default: Config.BATCH_SIZE)
        
        Returns:
            List of MarketEvent objects
        """
        start_block = start_block if start_block is not None else Config.START_BLOCK
        end_block = end_block if end_block is not None else self.w3.eth.block_number
        batch_size = batch_size if batch_size is not None else Config.BATCH_SIZE

        if start_block > end_block:
            raise ValueError("Start block cannot be greater than end block")

        all_events = []
        total_batches = (end_block - start_block) // batch_size + 1

        logger.info(f"Fetching events from block {start_block} to {end_block}")
        
        with tqdm(total=total_batches, desc="Fetching events") as pbar:
            for batch_start in range(start_block, end_block + 1, batch_size):
                batch_end = min(batch_start + batch_size - 1, end_block)
                
                try:
                    batch_events = self.fetch_events_batch(batch_start, batch_end)
                    all_events.extend(batch_events)
                    
                    logger.debug(
                        f"Fetched {len(batch_events)} events for blocks "
                        f"{batch_start}-{batch_end}"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Failed to fetch events for blocks {batch_start}-{batch_end}: {e}"
                    )
                    continue
                
                finally:
                    pbar.update(1)
                    time.sleep(self.retry_delay)

        logger.info(f"Fetched total of {len(all_events)} events")
        return all_events

    def get_market_params(self, market_id: str) -> Optional[MarketParams]:
        """
        Get market parameters for a specific market ID.
        
        Args:
            market_id: The market ID to query
            
        Returns:
            MarketParams object if found, None otherwise
        """
        try:
            # Convert string ID to bytes if necessary
            if isinstance(market_id, str) and market_id.startswith('0x'):
                market_id = bytes.fromhex(market_id[2:])
                
            result = self.contract.functions.idToMarketParams(market_id).call()
            return MarketParams.from_tuple(result)
            
        except Exception as e:
            logger.error(f"Error fetching market params for ID {market_id}: {e}")
            return None