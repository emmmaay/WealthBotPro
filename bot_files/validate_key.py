
#!/usr/bin/env python3
"""
Private Key Validation Script
Run this to check if your private key is properly formatted
"""

import os
from dotenv import load_dotenv

def validate_private_key():
    """Validate private key format"""
    load_dotenv()
    
    private_key = os.getenv('PRIVATE_KEY')
    
    if not private_key:
        print("❌ PRIVATE_KEY not found in environment variables")
        print("Please create a .env file with your private key:")
        print("PRIVATE_KEY=your_private_key_here")
        return False
    
    private_key = private_key.strip()
    
    # Remove 0x prefix if present
    if private_key.startswith('0x'):
        private_key = private_key[2:]
    
    # Check length
    if len(private_key) != 64:
        print(f"❌ Private key must be 64 characters, got {len(private_key)}")
        print(f"Current key length: {len(private_key)}")
        return False
    
    # Check if valid hexadecimal
    try:
        int(private_key, 16)
        print("✅ Private key format is valid!")
        print(f"Key length: {len(private_key)} characters")
        print(f"First 8 chars: {private_key[:8]}...")
        return True
    except ValueError:
        print("❌ Private key contains invalid hexadecimal characters")
        print("Private key should only contain: 0-9, a-f, A-F")
        return False

if __name__ == "__main__":
    print("🔑 Private Key Validation")
    print("=" * 30)
    validate_private_key()
