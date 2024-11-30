# oracle_analysis/main.py
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from web3 import Web3
from web3.exceptions import Web3Exception

from .config import Config
from .market.events import MarketEventFetcher
from .market.models import MarketEvent
from .oracle.identifier import OracleIdentifier
from .oracle.models import OracleType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OracleAnalysis:
    def __init__(self):
        # Validate configuration
        if error := Config.validate():
            logger.error(f"Configuration error: {error}")
            sys.exit(1)
            
        # Create output directory
        Config.create_output_dir()
        
        # Initialize components
        self.w3 = Web3(Web3.HTTPProvider(Config.RPC_URL))
        if not self.w3.is_connected():
            logger.error("Failed to connect to Ethereum node")
            sys.exit(1)
            
        self.market_fetcher = MarketEventFetcher(Config.RPC_URL, Config.CONTRACT_ADDRESS)
        self.oracle_identifier = OracleIdentifier(Config.RPC_URL)
        
    def run_analysis(self) -> None:
        """Run the complete oracle analysis"""
        try:
            # Fetch market events
            logger.info("Fetching market events...")
            market_events = self.market_fetcher.fetch_events(
                start_block=Config.START_BLOCK,
                batch_size=Config.BATCH_SIZE
            )
            
            if not market_events:
                logger.warning("No market events found")
                return
                
            logger.info(f"Found {len(market_events)} market events")
            
            # Analyze oracle protocols
            logger.info("Analyzing oracle protocols...")
            oracle_analysis = self._analyze_oracles(market_events)
            
            # Generate reports
            logger.info("Generating reports...")
            self._generate_reports(market_events, oracle_analysis)
            
            logger.info("Analysis completed successfully")
            
        except Web3Exception as e:
            logger.error(f"Web3 error occurred: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            sys.exit(1)
    
    def _analyze_oracles(self, market_events: List[MarketEvent]) -> Dict[str, Dict]:
        """Analyze oracle protocols for all unique oracle addresses"""
        unique_oracles = {event.params.oracle for event in market_events}
        oracle_analysis = {}
        
        for oracle_address in unique_oracles:
            try:
                analysis = self.oracle_identifier.identify_oracle(oracle_address)
                oracle_analysis[oracle_address] = analysis
            except Exception as e:
                logger.warning(f"Failed to analyze oracle {oracle_address}: {e}")
                oracle_analysis[oracle_address] = {
                    'type': OracleType.UNKNOWN,
                    'confidence': 0,
                    'error': str(e)
                }
        
        return oracle_analysis
    
    def _generate_reports(
        self,
        market_events: List[MarketEvent],
        oracle_analysis: Dict[str, Dict]
    ) -> None:
        """Generate analysis reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create market events DataFrame
        market_data = [{
            'id': event.id,
            'oracle': event.params.oracle,
            'oracle_type': oracle_analysis[event.params.oracle]['type'].value,
            'confidence': oracle_analysis[event.params.oracle]['confidence'],
            'loan_token': event.params.loan_token,
            'collateral_token': event.params.collateral_token,
            'irm': event.params.irm,
            'lltv': event.params.lltv,
            'block_number': event.block_number,
            'tx_hash': event.transaction_hash
        } for event in market_events]
        
        df_markets = pd.DataFrame(market_data)
        
        # Create oracle analysis DataFrame
        oracle_data = [{
            'address': addr,
            'type': analysis['type'].value,
            'confidence': analysis['confidence'],
            'error': analysis.get('error', None)
        } for addr, analysis in oracle_analysis.items()]
        
        df_oracles = pd.DataFrame(oracle_data)
        
        # Save reports
        output_dir = Path(Config.OUTPUT_DIR)
        df_markets.to_csv(output_dir / f'market_analysis_{timestamp}.csv', index=False)
        df_oracles.to_csv(output_dir / f'oracle_analysis_{timestamp}.csv', index=False)
        
        # Generate statistics
        stats = {
            'total_markets': len(market_events),
            'unique_oracles': len(oracle_analysis),
            'oracle_types': df_markets['oracle_type'].value_counts().to_dict(),
            'avg_confidence': df_oracles['confidence'].mean(),
            'timestamp': timestamp
        }
        
        # Save statistics
        pd.Series(stats).to_json(output_dir / f'analysis_stats_{timestamp}.json')
        
        # Print summary
        logger.info("\nAnalysis Summary:")
        logger.info(f"Total markets analyzed: {stats['total_markets']}")
        logger.info(f"Unique oracles found: {stats['unique_oracles']}")
        logger.info("\nOracle Type Distribution:")
        for oracle_type, count in stats['oracle_types'].items():
            logger.info(f"{oracle_type}: {count}")
        logger.info(f"\nAverage confidence score: {stats['avg_confidence']:.2f}")

def main():
    """Main entry point for oracle analysis"""
    analysis = OracleAnalysis()
    analysis.run_analysis()

if __name__ == "__main__":
    main()