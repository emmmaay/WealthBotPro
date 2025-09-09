#!/usr/bin/env python3
"""
Private Key Validation Script
Run this to check if your private key is properly formatted
"""

import os
from dotenv import load_dotenv

def validate_private_key(private_key: str):
    """Enhanced private key validation with detailed error reporting"""
    try:
        if not private_key:
            return False, "Private key is empty or None"

        # Clean the private key - remove all possible formatting
        original = private_key
        clean_key = str(private_key).strip().strip('"').strip("'").replace(' ', '').replace('\n', '').replace('\r', '')
        
        # Handle both 0x and non-0x prefixed keys
        if clean_key.startswith('0x') or clean_key.startswith('0X'):
            clean_key = clean_key[2:]

        # Check length
        if len(clean_key) != 64:
            return False, f"Must be 64 hex characters, got {len(clean_key)} (original: {len(original)})"

        # Triple validation for hexadecimal format
        try:
            # Method 1: Convert to int
            int(clean_key, 16)
            
            # Method 2: Check character validity
            valid_hex_chars = set('0123456789abcdefABCDEF')
            invalid_chars = [c for c in clean_key if c not in valid_hex_chars]
            if invalid_chars:
                return False, f"Invalid hex characters found: {invalid_chars}"
            
            # Method 3: Bytes conversion test
            bytes.fromhex(clean_key)
            
            return True, "Valid private key format"
            
        except ValueError as e:
            return False, f"Hexadecimal validation failed: {e}"

    except Exception as e:
        return False, f"Unexpected validation error: {e}"

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
        is_valid, message = validate_private_key(private_key)
        if is_valid:
            print("✅ Private key format is valid!")
            print(f"Key length: {len(private_key)} characters")
            print(f"Preview: {private_key[:8]}...{private_key[-8:]}")
            print(f"Status: {message}")
        else:
            print("❌ Private key format is invalid.")
            print(f"Error: {message}")
            print("Expected: 64 hexadecimal characters (0-9, a-f, A-F) with optional 0x prefix")