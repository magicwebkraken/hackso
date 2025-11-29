"""
Multi-chain Balance Checker - Optimized for speed
"""
from web3 import Web3
from typing import Dict, List, Optional
import time
import concurrent.futures
from threading import Thread
from config import RPC_ENDPOINTS, NATIVE_TOKENS, MAX_RETRIES, REQUEST_TIMEOUT

class BalanceChecker:
    def __init__(self):
        """Initialize balance checker with connections to all chains"""
        self.connections: Dict[str, Web3] = {}
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup Web3 connections for all chains"""
        for chain_name, rpc_url in RPC_ENDPOINTS.items():
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': REQUEST_TIMEOUT}))
                if w3.is_connected():
                    self.connections[chain_name] = w3
                    print(f"[OK] Connected to {chain_name}")
                else:
                    print(f"[FAIL] Failed to connect to {chain_name}")
            except Exception as e:
                print(f"[ERROR] Error connecting to {chain_name}: {e}")
    
    def check_balance(self, address: str, chain: str) -> Dict:
        """
        Check balance for an address on a specific chain
        
        Args:
            address: Wallet address
            chain: Chain name (ethereum, bsc, polygon, etc.)
        
        Returns:
            Dictionary with balance information
        """
        if chain not in self.connections:
            return {
                'chain': chain,
                'balance': 0,
                'balance_eth': 0,
                'error': f'Chain {chain} not connected'
            }
        
        w3 = self.connections[chain]
        
        for attempt in range(MAX_RETRIES):
            try:
                # Get balance in Wei
                balance_wei = w3.eth.get_balance(address)
                # Convert to ETH (or native token)
                balance_eth = w3.from_wei(balance_wei, 'ether')
                
                return {
                    'chain': chain,
                    'balance': balance_wei,
                    'balance_eth': float(balance_eth),
                    'symbol': NATIVE_TOKENS.get(chain, 'ETH'),
                    'error': None
                }
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(0.5)  # Reduced wait time for faster retries
                    continue
                return {
                    'chain': chain,
                    'balance': 0,
                    'balance_eth': 0,
                    'error': str(e)
                }
    
    def check_all_chains(self, address: str) -> List[Dict]:
        """
        Check balance for an address across all supported chains (parallel execution)
        
        Args:
            address: Wallet address
        
        Returns:
            List of balance dictionaries for each chain
        """
        # Use ThreadPoolExecutor for parallel chain checks
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(RPC_ENDPOINTS)) as executor:
            # Submit all chain checks in parallel
            future_to_chain = {
                executor.submit(self.check_balance, address, chain): chain 
                for chain in RPC_ENDPOINTS.keys()
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_chain):
                chain = future_to_chain[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'chain': chain,
                        'balance': 0,
                        'balance_eth': 0,
                        'error': str(e)
                    })
        
        return results
    
    def get_chain_info(self, chain: str) -> Optional[Dict]:
        """Get chain information"""
        if chain not in self.connections:
            return None
        
        w3 = self.connections[chain]
        try:
            return {
                'chain_id': w3.eth.chain_id,
                'block_number': w3.eth.block_number,
                'is_connected': w3.is_connected()
            }
        except:
            return None

