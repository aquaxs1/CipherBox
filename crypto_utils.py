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
    
    # Metadata constants
    METADATA_VERSION = 1
    METADATA_ENCODING = 'utf-8'
    
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
        Securely delete a file by overwriting it multiple times before deletion.
        
        Args:
            file_path: Path to the file to delete
            passes: Number of overwrite passes (3 for reasonable security)
        """
        try:
            file_size = file_path.stat().st_size
            
            # Overwrite with random data multiple times
            for _ in range(passes):
                with open(file_path, 'wb') as f:
                    f.write(os.urandom(file_size))
            
            # Final overwrite with zeros
            with open(file_path, 'wb') as f:
                f.write(b'\x00' * file_size)
            
            # Delete the file
            file_path.unlink()
        except Exception as e:
            # If secure deletion fails, try regular deletion
            try:
                file_path.unlink()
            except Exception:
                # Silently fail - file will remain but encryption succeeded
                pass
