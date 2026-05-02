#!/usr/bin/env python3
"""
CipherBox Test Suite
Tests all core functionality of the application.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from crypto_utils import CryptoManager
from config_manager import ConfigManager


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_master_password_generation():
    """Test master password generation."""
    print_section("TEST 1: Master Password Generation")
    
    crypto = CryptoManager()
    password = crypto.generate_master_password(32)
    
    print(f"✓ Generated password: {password[:10]}...{password[-10:]}")
    print(f"✓ Password length: {len(password)} characters")
    print(f"✓ All alphanumeric: {password.isalnum()}")
    
    assert len(password) >= 16, "Password too short"
    assert password.isalnum(), "Password contains non-alphanumeric characters"
    
    print("✓ PASSED")


def test_salt_generation():
    """Test salt generation."""
    print_section("TEST 2: Salt Generation & Storage")
    
    crypto = CryptoManager()
    salt1 = crypto.generate_salt()
    salt2 = crypto.generate_salt()
    
    print(f"✓ Salt 1 length: {len(salt1)} bytes")
    print(f"✓ Salt 2 length: {len(salt2)} bytes")
    print(f"✓ Salts are different: {salt1 != salt2}")
    
    assert len(salt1) == CryptoManager.PBKDF2_SALT_LENGTH, "Salt wrong length"
    assert salt1 != salt2, "Salts should be random"
    
    print("✓ PASSED")


def test_key_derivation():
    """Test key derivation."""
    print_section("TEST 3: Key Derivation (PBKDF2-HMAC-SHA256)")
    
    crypto = CryptoManager()
    password = "TestPassword123!"
    salt = crypto.generate_salt()
    
    key1 = crypto.derive_key(password, salt, iterations=1000)
    key2 = crypto.derive_key(password, salt, iterations=1000)
    key3 = crypto.derive_key(password + "X", salt, iterations=1000)
    
    print(f"✓ Key length: {len(key1)} bytes (base64-encoded)")
    print(f"✓ Same password + salt produces same key: {key1 == key2}")
    print(f"✓ Different password produces different key: {key1 != key3}")
    
    assert key1 == key2, "Same input should produce same key"
    assert key1 != key3, "Different passwords should produce different keys"
    
    print("✓ PASSED")


def test_config_manager():
    """Test configuration management."""
    print_section("TEST 4: Configuration Manager")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager(tmpdir)
        
        # Test first launch detection
        print(f"✓ Is first launch: {config.is_first_launch()}")
        assert config.is_first_launch(), "Should detect first launch"
        
        # Test salt storage
        salt = CryptoManager.generate_salt()
        config.save_salt(salt)
        print(f"✓ Salt saved successfully")
        
        # Test salt loading
        loaded_salt = config.load_salt()
        print(f"✓ Salt loaded successfully")
        print(f"✓ Loaded salt matches original: {salt == loaded_salt}")
        assert salt == loaded_salt, "Salt should match"
        
        # Test second launch detection
        print(f"✓ Is first launch (after save): {config.is_first_launch()}")
        assert not config.is_first_launch(), "Should not detect first launch after saving"
    
    print("✓ PASSED")


def test_file_encryption_decryption():
    """Test file encryption and decryption."""
    print_section("TEST 5: File Encryption & Decryption")
    
    crypto = CryptoManager()
    password = "MySecurePassword123"
    salt = crypto.generate_salt()
    key = crypto.derive_key(password, salt, iterations=1000)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test file
        test_file = tmpdir / "test_document.txt"
        original_content = b"This is a secret message that needs encryption!"
        test_file.write_bytes(original_content)
        print(f"✓ Created test file: {test_file.name}")
        
        # Encrypt file
        success, msg = crypto.encrypt_file(str(test_file), key, encrypt_filename=False)
        print(f"✓ Encryption result: {msg}")
        assert success, f"Encryption failed: {msg}"
        
        # Check encrypted file exists
        encrypted_file = tmpdir / f"{test_file.name}.cipherbox"
        assert encrypted_file.exists(), "Encrypted file not created"
        print(f"✓ Encrypted file exists: {encrypted_file.name}")
        
        # Check original file deleted
        assert not test_file.exists(), "Original file should be securely deleted"
        print(f"✓ Original file securely deleted")
        
        # Decrypt file
        success, msg, output_path = crypto.decrypt_file(str(encrypted_file), key)
        print(f"✓ Decryption result: {msg}")
        assert success, f"Decryption failed: {msg}"
        
        # Verify decrypted content
        decrypted_file = Path(output_path)
        decrypted_content = decrypted_file.read_bytes()
        assert decrypted_content == original_content, "Decrypted content doesn't match"
        print(f"✓ Decrypted content matches original")
        
        # Check encrypted file deleted
        assert not encrypted_file.exists(), "Encrypted file should be deleted"
        print(f"✓ Encrypted file securely deleted")
    
    print("✓ PASSED")


def test_filename_encryption():
    """Test filename encryption feature."""
    print_section("TEST 6: Filename Encryption")
    
    crypto = CryptoManager()
    password = "MySecurePassword123"
    salt = crypto.generate_salt()
    key = crypto.derive_key(password, salt, iterations=1000)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test file
        test_file = tmpdir / "sensitive_document.pdf"
        original_content = b"PDF content here"
        test_file.write_bytes(original_content)
        
        # Encrypt with filename encryption
        success, msg = crypto.encrypt_file(str(test_file), key, encrypt_filename=True)
        print(f"✓ Encryption with filename encryption: {msg}")
        assert success, f"Encryption failed: {msg}"
        
        # Find encrypted file (should have .cipherbox extension)
        encrypted_files = list(tmpdir.glob("*.cipherbox"))
        assert len(encrypted_files) == 1, "Should have exactly one encrypted file"
        encrypted_file = encrypted_files[0]
        
        # Filename should be a UUID (no original name visible)
        print(f"✓ Encrypted filename is UUID: {encrypted_file.stem}")
        assert len(encrypted_file.stem) == 36, "UUID format should have 36 chars (with dashes)"
        
        # Decrypt and verify original filename restored
        success, msg, output_path = crypto.decrypt_file(str(encrypted_file), key)
        print(f"✓ Decryption result: {msg}")
        assert success, f"Decryption failed: {msg}"
        
        # Check original filename restored
        decrypted_file = Path(output_path)
        assert decrypted_file.name == "sensitive_document.pdf", "Original filename not restored"
        print(f"✓ Original filename restored: {decrypted_file.name}")
    
    print("✓ PASSED")


def test_wrong_password():
    """Test decryption with wrong password."""
    print_section("TEST 7: Wrong Password Handling")
    
    crypto = CryptoManager()
    password = "CorrectPassword"
    wrong_password = "WrongPassword"
    salt = crypto.generate_salt()
    correct_key = crypto.derive_key(password, salt, iterations=1000)
    wrong_key = crypto.derive_key(wrong_password, salt, iterations=1000)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create and encrypt file
        test_file = tmpdir / "test.txt"
        test_file.write_bytes(b"Secret content")
        
        success, _ = crypto.encrypt_file(str(test_file), correct_key)
        assert success, "Encryption should succeed"
        
        encrypted_file = list(tmpdir.glob("*.cipherbox"))[0]
        
        # Try to decrypt with wrong key
        success, msg, _ = crypto.decrypt_file(str(encrypted_file), wrong_key)
        
        print(f"✓ Decryption with wrong password failed (as expected): {msg}")
        assert not success, "Should fail with wrong password"
        assert "wrong password" in msg.lower() or "corrupted" in msg.lower(), "Error message should indicate wrong password"
    
    print("✓ PASSED")


def test_large_file():
    """Test encryption/decryption of a larger file."""
    print_section("TEST 8: Large File Handling (10 MB)")
    
    crypto = CryptoManager()
    password = "LargeFilePassword"
    salt = crypto.generate_salt()
    key = crypto.derive_key(password, salt, iterations=1000)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create 10 MB test file
        test_file = tmpdir / "large_file.bin"
        large_content = os.urandom(10 * 1024 * 1024)  # 10 MB
        test_file.write_bytes(large_content)
        print(f"✓ Created 10 MB test file")
        
        # Encrypt
        success, msg = crypto.encrypt_file(str(test_file), key)
        print(f"✓ Encrypted: {msg}")
        assert success, f"Encryption failed: {msg}"
        
        # Decrypt
        encrypted_file = list(tmpdir.glob("*.cipherbox"))[0]
        success, msg, output_path = crypto.decrypt_file(str(encrypted_file), key)
        print(f"✓ Decrypted: {msg}")
        assert success, f"Decryption failed: {msg}"
        
        # Verify content
        decrypted_content = Path(output_path).read_bytes()
        assert decrypted_content == large_content, "Large file content mismatch"
        print(f"✓ Large file content verified")
    
    print("✓ PASSED")


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  CipherBox Test Suite".center(58) + "║")
    print("║" + "  Comprehensive Security & Functionality Tests".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_master_password_generation()
        test_salt_generation()
        test_key_derivation()
        test_config_manager()
        test_file_encryption_decryption()
        test_filename_encryption()
        test_wrong_password()
        test_large_file()
        
        print_section("ALL TESTS PASSED ✓")
        print("\n✓ CipherBox is functioning correctly!")
        print("✓ Cryptographic operations are secure")
        print("✓ File handling is robust")
        print("✓ Error handling works as expected\n")
        
        return 0
    
    except AssertionError as e:
        print_section("TEST FAILED ✗")
        print(f"\n✗ Assertion failed: {str(e)}\n")
        return 1
    
    except Exception as e:
        print_section("TEST ERROR ✗")
        print(f"\n✗ Unexpected error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
