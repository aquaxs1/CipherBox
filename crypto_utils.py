"""
Cryptographic utilities for CipherBox application.
Handles key derivation, encryption, and decryption operations.
"""

import os
import json
import secrets
import string
import hashlib
import binascii
from pathlib import Path
from cryptography.fernet import Fernet
import base64


class CryptoManager:
    """Manages all cryptographic operations for CipherBox."""
    
    # Encryption parameters
    PBKDF2_ITERATIONS = 480000  # OWASP recommendation (2024)
    PBKDF2_SALT_LENGTH = 32  # 32 bytes = 256 bits
    FERNET_KEY_LENGTH = 32  # Fernet requires 32-byte key
    
    # Overwrite buffer for secure deletion, so wiping a large file does not
    # allocate a buffer the size of the file.
    SECURE_DELETE_CHUNK_SIZE = 4 * 1024 * 1024
    
    # Encryption holds the whole file in memory: the original bytes, the
    # payload built around them, and Fernet's base64-encoded ciphertext, plus
    # the copies the cipher makes internally. Measured at roughly 9x the file
    # size across 8 MB to 96 MB inputs. A file is not streamed, so this scales
    # linearly -- a 1 GB file needs several GB of free RAM.
    MEMORY_OVERHEAD_FACTOR = 9
    
    # Above this, warn before starting rather than letting the process die with
    # a MemoryError halfway through.
    LARGE_FILE_THRESHOLD = 256 * 1024 * 1024
    
    # Metadata constants
    METADATA_VERSION = 1
    METADATA_ENCODING = 'utf-8'
    
    # Known plaintext encrypted with the derived key at setup and stored in the
    # config. Decrypting it proves the entered password produced the same key,
    # which is what lets us reject a wrong password at the login screen instead
    # of letting the user in and failing on their first real file.
    VERIFIER_PLAINTEXT = b'cipherbox-key-verification-v1'
    
    def __init__(self):
        """Initialize the CryptoManager."""
        pass  # No initialization needed
    
    @staticmethod
    def generate_master_password(length: int = 32) -> str:
        """
        Generate a cryptographically strong, random master password.
        
        Args:
            length: Desired password length (default 32 chars for extra security)
        
        Returns:
            A secure alphanumeric master password
        """
        # Use alphanumeric characters (no special chars for easier copying/storage)
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_salt(length: int = PBKDF2_SALT_LENGTH) -> bytes:
        """Generate a cryptographically random salt."""
        return os.urandom(length)
    
    @staticmethod
    def derive_key(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
        """
        Derive an encryption key from a master password using PBKDF2-HMAC-SHA256.
        Uses Python's built-in hashlib for maximum compatibility.
        
        Args:
            password: The master password
            salt: The salt (should be stored and reused)
            iterations: Number of iterations (higher = slower but more secure)
        
        Returns:
            A 32-byte key suitable for Fernet encryption
        """
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        # Use hashlib.pbkdf2_hmac - available in all Python versions
        # This is more compatible than cryptography.hazmat
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',           # Hash algorithm
            password,           # Password
            salt,              # Salt
            iterations,        # Iterations
            dklen=CryptoManager.FERNET_KEY_LENGTH  # Output length (32 bytes)
        )
        
        # Fernet requires base64-encoded key
        return base64.urlsafe_b64encode(derived_key)
    
    @staticmethod
    def estimate_memory_required(file_size: int) -> int:
        """
        Estimate the peak memory needed to encrypt or decrypt a file.
        
        Args:
            file_size: Size of the file in bytes
        
        Returns:
            Estimated peak memory use in bytes
        """
        return file_size * CryptoManager.MEMORY_OVERHEAD_FACTOR
    
    @staticmethod
    def find_large_files(file_paths, threshold: int = LARGE_FILE_THRESHOLD) -> list:
        """
        Find files big enough that processing them may exhaust memory.
        
        Args:
            file_paths: Paths to check
            threshold: Size in bytes above which a file counts as large
        
        Returns:
            List of (path, size, estimated_memory) tuples, largest first
        """
        large = []
        for file_path in file_paths:
            try:
                size = Path(file_path).stat().st_size
            except OSError:
                continue
            if size > threshold:
                large.append(
                    (file_path, size, CryptoManager.estimate_memory_required(size))
                )
        
        large.sort(key=lambda item: item[1], reverse=True)
        return large
    
    @staticmethod
    def make_verifier(key: bytes) -> str:
        """
        Build a verification token for a derived key.
        
        Args:
            key: The encryption key (from derive_key)
        
        Returns:
            The token as a string, ready to store in the config
        """
        token = Fernet(key).encrypt(CryptoManager.VERIFIER_PLAINTEXT)
        return token.decode('ascii')
    
    @staticmethod
    def check_verifier(key: bytes, verifier: str) -> bool:
        """
        Check a derived key against a stored verification token.
        
        Fernet authenticates with HMAC, so a key that did not create the token
        fails to decrypt it rather than returning wrong bytes.
        
        Args:
            key: The encryption key to test
            verifier: The stored token
        
        Returns:
            True if the key matches the token, False otherwise
        """
        try:
            plaintext = Fernet(key).decrypt(verifier.encode('ascii'))
        except Exception:
            return False
        return plaintext == CryptoManager.VERIFIER_PLAINTEXT
    
    @staticmethod
    def encrypt_file(file_path: str, key: bytes, encrypt_filename: bool = False) -> tuple[bool, str]:
        """
        Encrypt a file with optional filename encryption.
        
        Args:
            file_path: Path to the file to encrypt
            key: The encryption key (from derive_key)
            encrypt_filename: If True, encrypt the filename and use UUID + .cipherbox
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            
            if not file_path.is_file():
                return False, f"Path is not a file: {file_path}"
            
            # Read the original file
            with open(file_path, 'rb') as f:
                original_content = f.read()
            
            # Initialize Fernet cipher
            cipher = Fernet(key)
            
            # Build metadata (original filename)
            original_name = file_path.name
            metadata = {
                'version': CryptoManager.METADATA_VERSION,
                'original_filename': original_name,
                'encrypted_filename': encrypt_filename
            }
            metadata_json = json.dumps(metadata).encode(CryptoManager.METADATA_ENCODING)
            
            # Create header: metadata_length (4 bytes) + metadata + content
            metadata_length = len(metadata_json).to_bytes(4, byteorder='big')
            payload = metadata_length + metadata_json + original_content
            
            # Encrypt the entire payload
            encrypted_payload = cipher.encrypt(payload)
            
            # Determine output filename
            if encrypt_filename:
                # Generate UUID-based filename
                import uuid
                output_filename = f"{uuid.uuid4()}.cipherbox"
                output_path = file_path.parent / output_filename
            else:
                # Append .cipherbox extension
                output_path = file_path.with_suffix(file_path.suffix + '.cipherbox')
            
            # Write encrypted file
            with open(output_path, 'wb') as f:
                f.write(encrypted_payload)
            
            # Securely delete original file
            CryptoManager._secure_delete(file_path)
            
            return True, f"File encrypted successfully: {output_path.name}"
        
        except PermissionError:
            return False, "Permission denied. File may be in use or requires admin privileges."
        except Exception as e:
            return False, f"Encryption failed: {str(e)}"
    
    @staticmethod
    def decrypt_file(file_path: str, key: bytes) -> tuple[bool, str, str | None]:
        """
        Decrypt a file and restore original filename if it was encrypted.
        
        Args:
            file_path: Path to the .cipherbox file to decrypt
            key: The encryption key (must match the one used for encryption)
        
        Returns:
            Tuple of (success: bool, message: str, output_path: str | None)
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False, f"File not found: {file_path}", None
            
            if not file_path.is_file():
                return False, f"Path is not a file: {file_path}", None
            
            # Read encrypted file
            with open(file_path, 'rb') as f:
                encrypted_payload = f.read()
            
            # Initialize Fernet cipher
            cipher = Fernet(key)
            
            # Decrypt payload
            try:
                payload = cipher.decrypt(encrypted_payload)
            except Exception as e:
                return False, f"Decryption failed. Wrong password or corrupted file: {str(e)}", None
            
            # Extract metadata
            if len(payload) < 4:
                return False, "Invalid encrypted file format (corrupted).", None
            
            metadata_length = int.from_bytes(payload[:4], byteorder='big')
            
            if len(payload) < 4 + metadata_length:
                return False, "Invalid encrypted file format (metadata truncated).", None
            
            metadata_json = payload[4:4+metadata_length]
            original_content = payload[4+metadata_length:]
            
            # Parse metadata
            try:
                metadata = json.loads(metadata_json.decode(CryptoManager.METADATA_ENCODING))
                original_filename = metadata.get('original_filename', 'decrypted_file')
            except json.JSONDecodeError:
                return False, "Invalid encrypted file format (metadata corrupted).", None
            
            # Determine output filename
            output_path = file_path.parent / original_filename
            
            # Avoid overwriting existing files
            counter = 1
            base_name = Path(original_filename).stem
            extension = Path(original_filename).suffix
            while output_path.exists():
                output_path = file_path.parent / f"{base_name}_{counter}{extension}"
                counter += 1
            
            # Write decrypted content
            with open(output_path, 'wb') as f:
                f.write(original_content)
            
            # Delete encrypted file
            CryptoManager._secure_delete(file_path)
            
            return True, f"File decrypted successfully: {output_path.name}", str(output_path)
        
        except PermissionError:
            return False, "Permission denied. File may be in use or requires admin privileges.", None
        except Exception as e:
            return False, f"Decryption failed: {str(e)}", None
    
    @staticmethod
    def _secure_delete(file_path: Path, passes: int = 3) -> None:
        """
        Overwrite a file's contents before deleting it.
        
        Each pass is flushed and fsync'd. Without that the OS is free to cache
        the writes and collapse them, so the overwrites need never reach the
        device and the original bytes survive.
        
        This helps on a traditional spinning disk. It does NOT reliably destroy
        data on an SSD, a USB flash drive or an SD card: wear levelling writes
        each pass to a fresh physical block and leaves the old ones intact, out
        of reach of any file API. Copy-on-write and journalling filesystems
        (Btrfs, ZFS, APFS) and any snapshot or backup keep old copies too. Full
        disk encryption is the dependable answer there.
        
        Args:
            file_path: Path to the file to delete
            passes: Number of random overwrite passes before the zero pass
        """
        try:
            file_size = file_path.stat().st_size
            
            # Overwrite in chunks so a large file does not need a buffer of its
            # own size in memory.
            chunk_size = CryptoManager.SECURE_DELETE_CHUNK_SIZE
            
            def overwrite(fill):
                with open(file_path, 'r+b') as f:
                    remaining = file_size
                    while remaining > 0:
                        block = min(chunk_size, remaining)
                        f.write(fill(block))
                        remaining -= block
                    f.flush()
                    # Push the pass out of the OS cache to the device; without
                    # this the overwrite may never actually happen.
                    os.fsync(f.fileno())
            
            for _ in range(passes):
                overwrite(os.urandom)
            
            # Final overwrite with zeros
            overwrite(lambda n: b'\x00' * n)
            
            # Delete the file
            file_path.unlink()
        except Exception as e:
            # If secure deletion fails, try regular deletion
            try:
                file_path.unlink()
            except Exception:
                # Silently fail - file will remain but encryption succeeded
                pass
