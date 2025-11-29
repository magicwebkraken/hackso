"""
Sequential Private Key Generator - Generates keys in a specific range
"""
from eth_account import Account
from typing import Optional, Tuple

class SequentialKeyGenerator:
    def __init__(self, start_key: str = None, end_key: str = None):
        """
        Initialize sequential key generator
        
        Args:
            start_key: Starting private key (hex string, with or without 0x)
            end_key: Ending private key (hex string, with or without 0x)
        """
        # Remove 0x prefix if present
        if start_key:
            self.start_key = start_key.replace('0x', '').lower()
        else:
            self.start_key = '0' * 64  # Start from all zeros
        
        if end_key:
            self.end_key = end_key.replace('0x', '').lower()
        else:
            self.end_key = 'f' * 64  # End at all F's (full range)
        
        # Convert to integers for comparison
        try:
            self.start_int = int(self.start_key, 16)
            self.end_int = int(self.end_key, 16)
        except ValueError:
            raise ValueError("Invalid hex key format")
        
        # Current position
        self.current_int = self.start_int
        
        # Validate range
        if self.start_int > self.end_int:
            raise ValueError("Start key must be less than or equal to end key")
        
        # Validate key length (should be 64 hex chars = 32 bytes)
        if len(self.start_key) != 64 or len(self.end_key) != 64:
            raise ValueError("Private keys must be 64 hex characters (32 bytes)")
    
    def get_current_key(self) -> Optional[Tuple[str, str]]:
        """
        Get current private key and address
        
        Returns:
            Tuple of (private_key, address) or None if range exhausted
        """
        if self.current_int > self.end_int:
            return None
        
        # Convert current integer to hex string (64 chars, no 0x)
        private_key_hex = format(self.current_int, '064x')
        
        # Validate key is within secp256k1 curve order (0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
        max_key = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16)
        if self.current_int > max_key:
            # Skip to end if we exceed max
            self.current_int = self.end_int + 1
            return None
        
        try:
            account = Account.from_key(private_key_hex)
            address = account.address
            return (private_key_hex, address)
        except Exception as e:
            # If key is invalid, skip to next
            self.current_int += 1
            return self.get_current_key()
    
    def next_key(self) -> Optional[Tuple[str, str]]:
        """
        Get next private key in sequence
        
        Returns:
            Tuple of (private_key, address) or None if range exhausted
        """
        result = self.get_current_key()
        if result:
            self.current_int += 1
        return result
    
    def get_progress(self) -> dict:
        """Get scanning progress"""
        total_range = self.end_int - self.start_int + 1
        scanned = self.current_int - self.start_int
        remaining = self.end_int - self.current_int + 1
        percent = (scanned / total_range * 100) if total_range > 0 else 0
        
        return {
            'start': f"0x{self.start_key}",
            'end': f"0x{self.end_key}",
            'current': f"0x{format(self.current_int, '064x')}",
            'scanned': scanned,
            'remaining': remaining,
            'total': total_range,
            'percent': percent
        }
    
    def set_position(self, position: int):
        """Set current position in range"""
        if self.start_int <= position <= self.end_int:
            self.current_int = position
        else:
            raise ValueError(f"Position must be between {self.start_int} and {self.end_int}")
    
    def reset(self):
        """Reset to start of range"""
        self.current_int = self.start_int

