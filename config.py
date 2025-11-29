"""
Configuration file for multi-chain wallet balance checker
"""
import os
from dotenv import load_dotenv

load_dotenv()

# RPC Endpoints - Ethereum and BNB only
# Using paid Alchemy endpoints for maximum speed
RPC_ENDPOINTS = {
    'ethereum': os.getenv('ETHEREUM_RPC', 'https://eth-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC'),
    'bsc': os.getenv('BSC_RPC', 'https://bnb-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC'),
}

# Chain IDs
CHAIN_IDS = {
    'ethereum': 1,
    'bsc': 56,
}

# Native token symbols
NATIVE_TOKENS = {
    'ethereum': 'ETH',
    'bsc': 'BNB',
}

# Number of retries for failed requests
MAX_RETRIES = 2  # Reduced for speed

# Request timeout in seconds (reduced for faster scanning)
REQUEST_TIMEOUT = 10

