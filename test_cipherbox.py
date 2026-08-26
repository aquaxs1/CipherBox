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


_test_counter = 0


def print_section(title):
    """Print a formatted section header, numbering tests in the order they run."""
    global _test_counter
    _test_counter += 1
    print_banner(f"TEST {_test_counter}: {title}")


def print_banner(title):
    """Print a formatted header that is not a numbered test."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_master_password_generation():
    """Test master password generation."""
    print_section("Master Password Generation")
    
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
    print_section("Salt Generation & Storage")
    
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
    print_section("Key Derivation (PBKDF2-HMAC-SHA256)")
    
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
    print_section("Configuration Manager")
    
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


def test_stale_config_cleanup():
    """Test that residue from old tests or builds does not break a fresh install."""
    print_section("Stale Config Cleanup")
    
    # A config file left behind by an interrupted setup, an old test run or a
    # previous build holds no usable salt. It must not masquerade as an
    # existing install -- that is the dead end where no password works.
    residue_cases = {
        "empty file": "",
        "truncated JSON": '{"version": 1, "sal',
        "no salt key": '{"version": 1}',
        "null salt": '{"version": 1, "salt": null}',
        "malformed base64": '{"version": 1, "salt": "not!valid!base64!"}',
        "salt too short": '{"version": 1, "salt": "YWJj"}',
        "JSON but not an object": '["old", "test", "fixture"]',
    }
    
    for label, contents in residue_cases.items():
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            config.config_file.write_text(contents)
            
            assert config.load_salt() is None, f"{label}: should yield no salt"
            assert not config.has_valid_config(), f"{label}: should not count as valid"
            assert config.is_first_launch(), f"{label}: should be treated as first launch"
            
            assert config.clear_stale_config(), f"{label}: should be cleared"
            assert not config.config_file.exists(), f"{label}: file should be gone"
            print(f"✓ Residue cleared: {label}")
    
    # A config holding a real salt is never removed -- deleting it would make
    # already encrypted files permanently unreadable.
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager(tmpdir)
        salt = CryptoManager.generate_salt()
        config.save_salt(salt)
        
        assert not config.clear_stale_config(), "Valid config must not be cleared"
        assert config.config_file.exists(), "Valid config file must survive"
        assert config.load_salt() == salt, "Valid salt must be untouched"
        print("✓ Valid config is preserved")
    
    # Setup over residue produces a working install.
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager(tmpdir)
        config.config_file.write_text('{"version": 1, "salt": "junk"}')
        config.clear_stale_config()
        
        salt = CryptoManager.generate_salt()
        assert config.save_salt(salt), "Should save after clearing residue"
        assert config.load_salt() == salt, "Fresh salt should load back"
        assert not config.is_first_launch(), "Should be set up now"
        print("✓ Fresh setup works after residue cleanup")
    
    # An invalid salt is rejected rather than written out as new residue.
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager(tmpdir)
        assert not config.save_salt(b"short"), "Should refuse a too-short salt"
        assert config.is_first_launch(), "Refused save must not create an install"
        print("✓ Invalid salt is refused")
    
    # No temp files are left behind by config writes.
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager(tmpdir)
        config.save_salt(CryptoManager.generate_salt())
        config.save_salt(CryptoManager.generate_salt())
        
        leftovers = [p.name for p in Path(tmpdir).iterdir() if p.name != "config.json"]
        assert not leftovers, f"Config writes left residue behind: {leftovers}"
        print("✓ Config writes leave no temp files behind")
    
    print("✓ PASSED")

def test_password_verification():
    """Test that a wrong master password is rejected at login."""
    print_section("Master Password Verification")
    
    salt = CryptoManager.generate_salt()
    right_key = CryptoManager.derive_key("CorrectHorseBattery", salt, iterations=1000)
    wrong_key = CryptoManager.derive_key("NotThePassword", salt, iterations=1000)
    
    verifier = CryptoManager.make_verifier(right_key)
    print("✓ Verifier created")
    
    assert CryptoManager.check_verifier(right_key, verifier), "Correct key must pass"
    print("✓ Correct password accepted")
    
    assert not CryptoManager.check_verifier(wrong_key, verifier), "Wrong key must fail"
    print("✓ Wrong password rejected")
    
    # The token must not leak the key, and must not be accepted when tampered with.
    assert not CryptoManager.check_verifier(right_key, verifier[:-4] + "AAAA"), \
        "Tampered verifier must fail"
    print("✓ Tampered verifier rejected")
    
    for junk in ["", "not-a-token", "!!!"]:
        assert not CryptoManager.check_verifier(right_key, junk), \
            f"Junk verifier {junk!r} must fail"
    print("✓ Malformed verifiers rejected")
    
    # Two setups with the same password must still produce different tokens,
    # since the salt differs -- a token must never identify a password.
    other_salt = CryptoManager.generate_salt()
    other_key = CryptoManager.derive_key("CorrectHorseBattery", other_salt, iterations=1000)
    assert not CryptoManager.check_verifier(other_key, verifier), \
        "Same password under a different salt must not verify"
    print("✓ Verifier is salt-bound")
    
    # Round-trip through the config.
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager(tmpdir)
        config.save_salt(salt)
        
        assert config.load_verifier() is None, "No verifier before one is saved"
        assert config.save_verifier(verifier), "Verifier should save"
        assert config.load_verifier() == verifier, "Verifier should round-trip"
        assert config.load_salt() == salt, "Saving a verifier must not disturb the salt"
        print("✓ Verifier round-trips through the config")
        
        assert not config.save_verifier(""), "Empty verifier must be refused"
        assert config.load_verifier() == verifier, "Refused save must not overwrite"
        print("✓ Empty verifier refused")
    
    # A config carrying only a salt (written before verification existed) stays
    # valid -- older installs must keep working.
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigManager(tmpdir)
        config.save_salt(salt)
        assert config.has_valid_config(), "Legacy config must stay valid"
        assert not config.clear_stale_config(), "Legacy config must not be cleared"
        assert config.load_verifier() is None, "Legacy config has no verifier"
        print("✓ Configs without a verifier still work")
    
    print("✓ PASSED")

def test_file_encryption_decryption():
    """Test file encryption and decryption."""
    print_section("File Encryption & Decryption")
    
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


def test_secure_deletion():
    """Test that secure deletion overwrites and removes the file."""
    print_section("Secure Deletion")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        secret = b"TOP SECRET PAYLOAD " * 1000
        target = tmpdir / "secret.bin"
        target.write_bytes(secret)
        
        CryptoManager._secure_delete(target)
        assert not target.exists(), "File should be gone"
        print("✓ File removed")
        
        # Nothing left in the directory either.
        assert not list(tmpdir.iterdir()), "Directory should be empty"
        print("✓ No residue left behind")
    
    # A file larger than one overwrite chunk must be wiped in chunks rather
    # than by allocating a buffer its own size.
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        big = tmpdir / "big.bin"
        size = CryptoManager.SECURE_DELETE_CHUNK_SIZE * 2 + 12345
        big.write_bytes(b"A" * size)
        
        CryptoManager._secure_delete(big, passes=1)
        assert not big.exists(), "Large file should be gone"
        print(f"✓ Multi-chunk file wiped ({size / 1024 / 1024:.1f} MB)")
    
    # An empty file is a valid input and must not raise.
    with tempfile.TemporaryDirectory() as tmpdir:
        empty = Path(tmpdir) / "empty.bin"
        empty.touch()
        CryptoManager._secure_delete(empty)
        assert not empty.exists(), "Empty file should be gone"
        print("✓ Empty file handled")
    
    print("✓ PASSED")

def test_filename_encryption():
    """Test filename encryption feature."""
    print_section("Filename Encryption")
    
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
    print_section("Wrong Password Handling")
    
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


def test_large_file_detection():
    """Test that oversized files are flagged before they exhaust memory."""
    print_section("Large File Detection")
    
    threshold = CryptoManager.LARGE_FILE_THRESHOLD
    
    estimate = CryptoManager.estimate_memory_required(100 * 1024 * 1024)
    assert estimate > 100 * 1024 * 1024, "Estimate must exceed the file size"
    print(f"✓ 100 MB file estimated at {estimate / 1024 / 1024:,.0f} MB of RAM")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Sparse files: the size is what matters, not the bytes on disk.
        small = tmpdir / "small.bin"
        with open(small, "wb") as f:
            f.truncate(threshold // 2)
        
        big = tmpdir / "big.bin"
        with open(big, "wb") as f:
            f.truncate(threshold * 3)
        
        bigger = tmpdir / "bigger.bin"
        with open(bigger, "wb") as f:
            f.truncate(threshold * 5)
        
        assert CryptoManager.find_large_files([small]) == [], \
            "A file under the threshold must not be flagged"
        print("✓ Small file not flagged")
        
        flagged = CryptoManager.find_large_files([small, big, bigger])
        assert len(flagged) == 2, f"Expected 2 flagged files, got {len(flagged)}"
        print("✓ Oversized files flagged")
        
        assert flagged[0][0] == bigger, "Largest file must come first"
        print("✓ Sorted largest first")
        
        _, size, needed = flagged[0]
        assert needed == CryptoManager.estimate_memory_required(size), \
            "Flagged entry must carry the memory estimate"
        print("✓ Memory estimate reported per file")
        
        # A path that cannot be stat'd is skipped, not fatal.
        flagged = CryptoManager.find_large_files([big, tmpdir / "gone.bin"])
        assert len(flagged) == 1, "Missing files should be skipped silently"
        print("✓ Missing paths skipped")
    
    print("✓ PASSED")

def test_large_file():
    """Test encryption/decryption of a larger file."""
    print_section("Large File Handling (10 MB)")
    
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
        test_stale_config_cleanup()
        test_password_verification()
        test_file_encryption_decryption()
        test_secure_deletion()
        test_filename_encryption()
        test_wrong_password()
        test_large_file_detection()
        test_large_file()
        
        print_banner("ALL TESTS PASSED ✓")
        print("\n✓ CipherBox is functioning correctly!")
        print("✓ Cryptographic operations are secure")
        print("✓ File handling is robust")
        print("✓ Error handling works as expected\n")
        
        return 0
    
    except AssertionError as e:
        print_banner("TEST FAILED ✗")
        print(f"\n✗ Assertion failed: {str(e)}\n")
        return 1
    
    except Exception as e:
        print_banner("TEST ERROR ✗")
        print(f"\n✗ Unexpected error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
