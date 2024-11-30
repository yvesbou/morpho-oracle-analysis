# oracle_analysis/oracle/patterns.py
"""Oracle-specific pattern definitions."""
from .models import OraclePattern

CHAINLINK_PATTERNS = OraclePattern(
    function_patterns=[
        "63feaf968c",  # PUSH4 + latestRoundData()
        "6350d25bcd",  # PUSH4 + latestAnswer()
        "63668a0f02",  # PUSH4 + latestTimestamp()
        "639a6fc8f5",  # PUSH4 + getRoundData(uint80)
        "63313ce567",  # PUSH4 + decimals()
        "638ac28d",    # PUSH4 + description()
        "632fb5c8f",   # PUSH4 + version()
    ],
    storage_patterns=[
        "54roundId",   # Storage pattern for round ID
        "55answers",   # Storage pattern for answers
        "54timestamp"  # Storage pattern for timestamps
    ],
    required_function_matches=3,
    function_names=[
        "latestRoundData",
        "latestAnswer",
        "latestTimestamp",
        "getRoundData",
        "decimals",
        "description",
        "version"
    ],
    factory_addresses=[
        "0x47Fb2585D2C56Fe188D0E6ec628a38b74fCeeeDf",  # Chainlink price feeds deployer
        "0xf0c1f6c01dfaced1e9c6fcfbd1fd1f873bbf09ce"   # Another known deployer
    ]
)

TELLOR_PATTERNS = OraclePattern(
    function_patterns=[
        "63a22cb465",  # PUSH4 + getDataBefore()
        "637584a157",  # PUSH4 + depositStake()
        "632f1be0c",   # PUSH4 + retrieveData()
        "63842483d2",  # PUSH4 + getCurrentValue()
        "635c1f0a0",   # PUSH4 + getNewValueCountbyRequestId()
    ],
    storage_patterns=[
        "54disputeId",
        "55stakeAmount",
        "54reportedValue"
    ],
    required_function_matches=2,
    function_names=[
        "getDataBefore",
        "depositStake",
        "retrieveData",
        "getCurrentValue",
        "getNewValueCountbyRequestId"
    ]
)

UNISWAP_PATTERNS = OraclePattern(
    function_patterns=[
        "63b7be1850",  # PUSH4 + observe(uint32[])
        "636d154ea5",  # PUSH4 + consult()
        "63252c8c6c",  # PUSH4 + price{0,1}CumulativeLast()
        "639a19a593",  # PUSH4 + sync()
    ],
    storage_patterns=[
        "54price0",
        "54price1",
        "55cumulative"
    ],
    required_function_matches=2,
    function_names=[
        "observe",
        "consult",
        "price0CumulativeLast",
        "price1CumulativeLast",
        "sync"
    ]
)

PYTH_PATTERNS = OraclePattern(
    function_patterns=[
        "63d24ce607",  # PUSH4 + getPrice()
        "63fe834482",  # PUSH4 + queryPriceFeed()
        "63313ce567",  # PUSH4 + decimals()
        "63628f7074",  # PUSH4 + updatePrice()
    ],
    storage_patterns=[
        "54priceId",
        "55confidence",
        "54expo"
    ],
    required_function_matches=2,
    function_names=[
        "getPrice",
        "queryPriceFeed",
        "decimals",
        "updatePrice"
    ]
)

REDSTONE_PATTERNS = OraclePattern(
    function_patterns=[
        "63d0f2e915",  # PUSH4 + getValue()
        "63c8e4de0d",  # PUSH4 + getValueWithTimestamp()
        "634554ee00",  # PUSH4 + validateTimestamp()
    ],
    storage_patterns=[
        "54dataFeed",
        "55timestamp",
        "54signature"
    ],
    required_function_matches=2,
    function_names=[
        "getValue",
        "getValueWithTimestamp",
        "validateTimestamp"
    ]
)

