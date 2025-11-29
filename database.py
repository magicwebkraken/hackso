"""
Database module to track searched private keys and their balances
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
import os
import threading

class WalletDatabase:
    def __init__(self, db_file: str = None):
        """
        Initialize the wallet database
        
        Args:
            db_file: Path to SQLite database file (defaults to wallet_scanner.db or /tmp/wallet_scanner.db for serverless)
        """
        if db_file is None:
            # For Vercel/serverless, use /tmp directory (writable)
            # For regular deployment, use current directory
            if os.getenv('VERCEL') or os.path.exists('/tmp'):
                db_file = '/tmp/wallet_scanner.db'
            else:
                db_file = 'wallet_scanner.db'
        self.db_file = db_file
        self._local = threading.local()
        self._init_database()
    
    def _get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_file,
                check_same_thread=False,
                timeout=10.0
            )
            # Enable WAL mode for better concurrency and thread safety
            self._local.conn.execute('PRAGMA journal_mode=WAL')
            self._local.conn.execute('PRAGMA synchronous=NORMAL')
            self._local.conn.execute('PRAGMA foreign_keys=ON')
        return self._local.conn
    
    @property
    def conn(self):
        """Thread-safe connection property"""
        return self._get_connection()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                private_key TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                has_balance BOOLEAN DEFAULT 0,
                total_balance REAL DEFAULT 0,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_id INTEGER NOT NULL,
                chain TEXT NOT NULL,
                balance_wei TEXT NOT NULL,
                balance_eth REAL NOT NULL,
                symbol TEXT NOT NULL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (wallet_id) REFERENCES wallets(id),
                UNIQUE(wallet_id, chain)
            )
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_address ON wallets(address)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_private_key ON wallets(private_key)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_searched_at ON wallets(searched_at)
        ''')
        
        conn.commit()
    
    def is_key_searched(self, private_key: str) -> bool:
        """Check if a private key has already been searched"""
        cursor = self.conn.execute(
            'SELECT id FROM wallets WHERE private_key = ?',
            (private_key,)
        )
        return cursor.fetchone() is not None
    
    def add_wallet(self, private_key: str, address: str) -> int:
        """
        Add a wallet to the database
        
        Returns:
            Wallet ID
        """
        try:
            cursor = self.conn.execute(
                'INSERT INTO wallets (private_key, address) VALUES (?, ?)',
                (private_key, address)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Key already exists, return existing ID
            cursor = self.conn.execute(
                'SELECT id FROM wallets WHERE private_key = ?',
                (private_key,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    def update_wallet_balance(self, wallet_id: int, has_balance: bool, total_balance: float):
        """Update wallet balance information"""
        self.conn.execute(
            '''UPDATE wallets 
               SET has_balance = ?, total_balance = ?, last_checked = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (has_balance, total_balance, wallet_id)
        )
        self.conn.commit()
    
    def add_balance(self, wallet_id: int, chain: str, balance_wei: str, 
                   balance_eth: float, symbol: str):
        """Add or update balance for a specific chain"""
        self.conn.execute(
            '''INSERT OR REPLACE INTO balances 
               (wallet_id, chain, balance_wei, balance_eth, symbol, checked_at)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
            (wallet_id, chain, balance_wei, balance_eth, symbol)
        )
        self.conn.commit()
    
    def get_wallet_balances(self, wallet_id: int) -> List[Dict]:
        """Get all balances for a wallet"""
        cursor = self.conn.execute(
            'SELECT chain, balance_wei, balance_eth, symbol FROM balances WHERE wallet_id = ?',
            (wallet_id,)
        )
        return [
            {
                'chain': row[0],
                'balance_wei': row[1],
                'balance_eth': row[2],
                'symbol': row[3]
            }
            for row in cursor.fetchall()
        ]
    
    def get_wallets_with_balance(self) -> List[Dict]:
        """Get all wallets that have balance"""
        cursor = self.conn.execute(
            '''SELECT id, private_key, address, total_balance, last_checked 
               FROM wallets WHERE has_balance = 1 
               ORDER BY total_balance DESC'''
        )
        return [
            {
                'id': row[0],
                'private_key': row[1],
                'address': row[2],
                'total_balance': row[3],
                'last_checked': row[4]
            }
            for row in cursor.fetchall()
        ]
    
    def get_statistics(self) -> Dict:
        """Get scanning statistics"""
        cursor = self.conn.execute('SELECT COUNT(*) FROM wallets')
        total_searched = cursor.fetchone()[0]
        
        cursor = self.conn.execute('SELECT COUNT(*) FROM wallets WHERE has_balance = 1')
        with_balance = cursor.fetchone()[0]
        
        cursor = self.conn.execute('SELECT SUM(total_balance) FROM wallets WHERE has_balance = 1')
        total_balance = cursor.fetchone()[0] or 0
        
        cursor = self.conn.execute(
            'SELECT MAX(searched_at) FROM wallets'
        )
        last_searched = cursor.fetchone()[0]
        
        return {
            'total_searched': total_searched,
            'with_balance': with_balance,
            'total_balance': total_balance,
            'last_searched': last_searched
        }
    
    def get_recent_searches(self, limit: int = 100) -> List[Dict]:
        """Get recently searched wallets"""
        cursor = self.conn.execute(
            '''SELECT id, private_key, address, has_balance, total_balance, searched_at, last_checked
               FROM wallets 
               ORDER BY searched_at DESC 
               LIMIT ?''',
            (limit,)
        )
        return [
            {
                'id': row[0],
                'private_key': row[1],
                'address': row[2],
                'has_balance': bool(row[3]),
                'total_balance': row[4],
                'searched_at': row[5],
                'last_checked': row[6]
            }
            for row in cursor.fetchall()
        ]
    
    def get_all_wallets(self) -> List[Dict]:
        """Get all wallets from database (for export)"""
        cursor = self.conn.execute(
            '''SELECT id, private_key, address, has_balance, total_balance, searched_at, last_checked
               FROM wallets 
               ORDER BY searched_at DESC'''
        )
        return [
            {
                'id': row[0],
                'private_key': row[1],
                'address': row[2],
                'has_balance': bool(row[3]),
                'total_balance': row[4],
                'searched_at': row[5],
                'last_checked': row[6]
            }
            for row in cursor.fetchall()
        ]
    
    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'conn') and self._local.conn:
            try:
                self._local.conn.close()
            except:
                pass
            self._local.conn = None

