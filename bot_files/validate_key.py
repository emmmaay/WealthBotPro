#!/usr/bin/env python3
"""
Private Key Validation Script
Run this to check if your private key is properly formatted
"""

import os
from dotenv import load_dotenv

def validate_private_key(private_key: str) -> bool:
    """Validate private key format"""
    try:
        if not private_key:
            return False

        # Clean the private key - remove whitespace and quotes
        private_key = private_key.strip().strip('"').strip("'")

        # Remove 0x prefix if present
        if private_key.startswith('0x'):
            private_key = private_key[2:]

        # Check if it's 64 hexadecimal characters
        if len(private_key) != 64:
            return False

        # Validate hexadecimal format
        int(private_key, 16)
        return True

    except (ValueError, TypeError):
        return False

if __name__ == "__main__":
    print("🔑 Private Key Validation")
    print("=" * 30)
    load_dotenv()

    private_key = os.getenv('PRIVATE_KEY')

    if not private_key:
        print("❌ PRIVATE_KEY not found in environment variables")
        print("Please create a .env file with your private key:")
        print("PRIVATE_KEY=your_private_key_here")
    else:
        if validate_private_key(private_key):
            print("✅ Private key format is valid!")
            print(f"Key length: {len(private_key)} characters")
            print(f"First 8 chars: {private_key[:8]}...")
        else:
            print("❌ Private key format is invalid.")
            print("Please ensure your private key is 64 characters long and contains only valid hexadecimal characters (0-9, a-f, A-F).")