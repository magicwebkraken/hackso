"""
Web-based Scanner - Thread-safe scanner for web interface
"""
import os
import time
import threading
from typing import Optional
from key_generator import KeyGenerator
from sequential_generator import SequentialKeyGenerator
from database import WalletDatabase
from balance_checker import BalanceChecker

class WebScanner:
    def __init__(self, db_file: str = None):
        """Initialize web scanner with thread safety"""
        self.key_generator = KeyGenerator()
        self.sequential_generator = None
        # Use environment variable or default path
        if db_file is None:
            db_file = os.getenv('DATABASE_PATH')
        self.database = WalletDatabase(db_file)
        self.balance_checker = BalanceChecker()
        self.scanning = False
        self.scan_thread = None
        self.scan_config = {
            'max_keys': None,
            'delay': 0.1,
            'mode': 'random',  # 'random' or 'sequential'
            'start_key': None,
            'end_key': None,
            'skip_searched': False  # Set to False to check ALL keys, even if already searched
        }
        self.current_stats = {
            'checked': 0,
            'with_balance': 0,
            'skipped': 0,
            'errors': 0,
            'keys_scanned': 0
        }
        self.lock = threading.Lock()
        self.last_found_wallet = None
        self.current_address = None
        self.current_private_key = None
        self.recent_searches = []  # Store recent searches in memory
    
    def scan_single_key(self, private_key: str, address: str) -> bool:
        """Scan a single private key"""
        # Update current key and address being checked
        with self.lock:
            self.current_address = address
            self.current_private_key = private_key
        
        # Check if we should skip already-searched keys
        if self.scan_config.get('skip_searched', False):
            if self.database.is_key_searched(private_key):
                with self.lock:
                    self.current_stats['skipped'] += 1
                return False
        
        # Add wallet to database (or get existing ID if already exists)
        wallet_id = self.database.add_wallet(private_key, address)
        
        # Check balances across all chains
        balances = self.balance_checker.check_all_chains(address)
        
        total_balance = 0
        has_balance = False
        
        for balance_info in balances:
            chain = balance_info['chain']
            balance_eth = balance_info.get('balance_eth', 0)
            symbol = balance_info.get('symbol', 'ETH')
            balance_wei = str(balance_info.get('balance', 0))
            
            if not balance_info.get('error'):
                # Update balance (will update if already exists)
                self.database.add_balance(
                    wallet_id, chain, balance_wei, balance_eth, symbol
                )
                
                if balance_eth > 0:
                    has_balance = True
                    total_balance += balance_eth
        
        # Update wallet balance (always update, even if re-checking)
        self.database.update_wallet_balance(wallet_id, has_balance, total_balance)
        
        # Add to recent searches
        with self.lock:
            self.current_stats['checked'] += 1
            self.current_stats['keys_scanned'] += 1
            if has_balance:
                self.current_stats['with_balance'] += 1
                self.last_found_wallet = {
                    'address': address,
                    'private_key': private_key,
                    'total_balance': total_balance,
                    'timestamp': time.time()
                }
            
            # Add to recent searches list (keep last 50)
            self.recent_searches.insert(0, {
                'private_key': private_key,
                'address': address,
                'has_balance': has_balance,
                'total_balance': total_balance,
                'timestamp': time.time()
            })
            if len(self.recent_searches) > 50:
                self.recent_searches.pop()
        
        return has_balance
    
    def _scan_loop(self):
        """Main scanning loop (runs in thread)"""
        keys_scanned = 0
        
        while self.scanning:
            try:
                # Get key based on mode
                if self.scan_config['mode'] == 'sequential' and self.sequential_generator:
                    result = self.sequential_generator.next_key()
                    if result is None:
                        # Range exhausted
                        self.stop_scanning()
                        break
                    private_key, address = result
                else:
                    # Random mode
                    private_key, address = self.key_generator.generate_random_key()
                
                self.scan_single_key(private_key, address)
                
                keys_scanned += 1
                
                # Check if we've reached max keys
                if self.scan_config['max_keys'] and keys_scanned >= self.scan_config['max_keys']:
                    self.stop_scanning()
                    break
                
                # Delay (minimal for speed - can be set to 0 for maximum speed)
                if self.scan_config['delay'] > 0:
                    time.sleep(self.scan_config['delay'])
            
            except Exception as e:
                with self.lock:
                    self.current_stats['errors'] += 1
                print(f"Error in scan loop: {e}")
    
    def start_scanning(self, max_keys: Optional[int] = None, delay: float = 0.1, 
                      mode: str = 'random', start_key: Optional[str] = None, 
                      end_key: Optional[str] = None, skip_searched: bool = True):
        """Start scanning in background thread"""
        if self.scanning:
            return False
        
        self.scanning = True
        self.scan_config['max_keys'] = max_keys
        self.scan_config['delay'] = delay
        self.scan_config['mode'] = mode
        self.scan_config['start_key'] = start_key
        self.scan_config['end_key'] = end_key
        self.scan_config['skip_searched'] = skip_searched
        
        # Initialize sequential generator if needed
        if mode == 'sequential':
            try:
                self.sequential_generator = SequentialKeyGenerator(
                    start_key=start_key or '0' * 64,
                    end_key=end_key or '9' * 64
                )
            except Exception as e:
                print(f"Error initializing sequential generator: {e}")
                self.scanning = False
                return False
        else:
            self.sequential_generator = None
        
        # Reset stats
        with self.lock:
            self.current_stats = {
                'checked': 0,
                'with_balance': 0,
                'skipped': 0,
                'errors': 0,
                'keys_scanned': 0
            }
        
        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()
        return True
    
    def stop_scanning(self):
        """Stop scanning"""
        self.scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=2)
    
    def get_status(self):
        """Get current scanning status"""
        db_stats = self.database.get_statistics()
        
        # Get sequential progress if in sequential mode
        sequential_progress = None
        if self.scan_config.get('mode') == 'sequential' and self.sequential_generator:
            sequential_progress = self.sequential_generator.get_progress()
        
        with self.lock:
            return {
                'scanning': self.scanning,
                'stats': {
                    **self.current_stats,
                    'total_searched': db_stats['total_searched'],
                    'total_with_balance': db_stats['with_balance'],
                    'total_balance_found': db_stats['total_balance']
                },
                'last_found': self.last_found_wallet,
                'current_address': self.current_address,
                'current_private_key': self.current_private_key,
                'config': self.scan_config,
                'sequential_progress': sequential_progress
            }
    
    def get_recent_searches(self, limit: int = 100):
        """Get recently searched wallets"""
        with self.lock:
            # Return in-memory recent searches first, then from database
            return self.recent_searches[:limit]
    
    def get_wallets_with_balance(self):
        """Get all wallets with balance"""
        wallets = self.database.get_wallets_with_balance()
        result = []
        
        for wallet in wallets:
            balances = self.database.get_wallet_balances(wallet['id'])
            result.append({
                **wallet,
                'balances': balances
            })
        
        return result
    
    def close(self):
        """Close scanner"""
        self.stop_scanning()
        self.database.close()

