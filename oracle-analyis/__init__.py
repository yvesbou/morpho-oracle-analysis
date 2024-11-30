# oracle_analysis/__init__.py
"""
Oracle Analysis Package
A tool for analyzing Ethereum oracle usage in DeFi protocols.
"""
from .config import Config
from .market.events import MarketEventFetcher
from .oracle.identifier import OracleIdentifier

__version__ = "0.1.0"

