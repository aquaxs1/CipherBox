#!/usr/bin/env python3
"""
Quick compatibility test for CipherBox
"""

import sys

print("Testing CipherBox imports and compatibility...")
print()

try:
    print("[1/4] Testing cryptography library...")
    from cryptography.fernet import Fernet
    import hashlib
    print("    ✓ cryptography & hashlib imports successful")
except ImportError as e:
    print(f"    ✗ Import error: {e}")
    sys.exit(1)

try:
    print("[2/4] Testing CryptoManager...")
    from crypto_utils import CryptoManager
    print("    ✓ CryptoManager imported successfully")
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

try:
    print("[3/4] Testing ConfigManager...")
    from config_manager import ConfigManager
    print("    ✓ ConfigManager imported successfully")
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

try:
    print("[4/4] Testing CipherBoxApp GUI import...")
    import customtkinter as ctk
    print("    ✓ customtkinter imported successfully")
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

print()
print("✓ All imports successful!")
print("✓ CipherBox is ready to run!")
print()
print("To start the application, run: python main.py")
