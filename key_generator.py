"""
Private Key Generator - Generates random private keys for scanning
Equivalent to Node.js: crypto.randomBytes(32).toString('hex')
"""
import secrets
from eth_account import Account

class KeyGenerator:
    def __init__(self):
        """Initialize key generator"""
        pass
    
    def generate_random_key(self) -> tuple:
        """
        Generate a random private key
        Equivalent to Node.js: 
        const hex = crypto.randomBytes(32).toString('hex');
        return '0x' + hex;
        
        Returns:
            Tuple of (private_key, address)
            private_key: hex string without 0x prefix (64 chars)
            address: Ethereum address
        """
        # Generate 32 random bytes (256 bits) - equivalent to crypto.randomBytes(32)
        private_key_bytes = secrets.token_bytes(32)
        
        # Convert to hex string - equivalent to .toString('hex')
        # This gives us 64 hex characters (32 bytes * 2)
        private_key_hex = private_key_bytes.hex()
        
        # Note: We store without 0x prefix for consistency with eth_account
        # But the key is equivalent to '0x' + hex in Node.js
        private_key = private_key_hex  # 64 hex characters
        
        # Get address from private key
        account = Account.from_key(private_key)
        address = account.address
        
        return private_key, address

