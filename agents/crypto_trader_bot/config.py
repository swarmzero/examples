import logging
from typing import Dict, NamedTuple

logger = logging.getLogger(__name__)


class ChainConfig(NamedTuple):
    name: str
    url_path: str
    native_token: str
    explorer: str


SUPPORTED_CHAINS: Dict[str, ChainConfig] = {
    "solana": ChainConfig("Solana", "solana", "SOL", "https://solscan.io"),
    "eth": ChainConfig("Ethereum", "eth", "ETH", "https://etherscan.io"),
    "tron": ChainConfig("Tron", "tron", "TRX", "https://tronscan.org"),
    "ton": ChainConfig("TON", "ton", "TON", "https://tonscan.org"),
    "base": ChainConfig("Base", "base", "ETH", "https://basescan.org"),
    "matic": ChainConfig("Polygon", "matic", "MATIC", "https://polygonscan.com"),
    "bsc": ChainConfig("BSC", "bsc", "BNB", "https://bscscan.com"),
    "opbnb": ChainConfig("opBNB", "opbnb", "BNB", "https://opbnbscan.com"),
    "optimism": ChainConfig("Optimism", "optimism", "ETH", "https://optimistic.etherscan.io"),
    "arbitrum": ChainConfig("Arbitrum", "arbitrum", "ETH", "https://arbiscan.io"),
}

# Chain name variations mapping
CHAIN_ALIASES = {
    # Ethereum variations
    "ethereum": "eth",
    "ether": "eth",
    # BSC variations
    "binance": "bsc",
    "binance smart chain": "bsc",
    # Polygon variations
    "polygon": "matic",
    # Common variations for other chains
    "sol": "solana",
    "opt": "optimism",
    "arb": "arbitrum",
}

# Log supported chains on module load
logger.info(f"Loaded {len(SUPPORTED_CHAINS)} supported chains:")
for chain_id, config in SUPPORTED_CHAINS.items():
    logger.debug(f"  {chain_id}: {config.name} ({config.native_token})")


def normalize_chain_name(chain: str) -> str:
    """Convert various chain name formats to our standard chain ID"""
    chain = chain.lower().strip()
    return CHAIN_ALIASES.get(chain, chain)


def validate_chain(chain: str) -> bool:
    """Validate if a chain is supported"""
    normalized_chain = normalize_chain_name(chain)
    is_valid = normalized_chain in SUPPORTED_CHAINS
    if not is_valid:
        logger.warning(f"Attempted to use unsupported chain: {chain} (normalized: {normalized_chain})")
    return is_valid


def get_chain_id(chain: str) -> str:
    """Get the standardized chain ID from any valid chain name variation"""
    normalized_chain = normalize_chain_name(chain)
    if normalized_chain in SUPPORTED_CHAINS:
        return normalized_chain
    raise ValueError(f"Unsupported chain: {chain}")
