"""
Configuration manager for CipherBox application.
Handles salt storage and first-time setup detection.
"""

import base64
import json
import os
import tempfile
from pathlib import Path


class ConfigManager:
    """Manages application configuration and salt storage."""
    
    CONFIG_DIR_NAME = '.cipherbox'
    CONFIG_FILENAME = 'config.json'
    # A salt shorter than this cannot have come from CryptoManager.generate_salt()
    # (32 bytes), so it is leftover junk rather than a real install.
    MIN_SALT_LENGTH = 16
    
    def __init__(self, config_dir: str | None = None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_dir: Custom config directory. Defaults to ~/.cipherbox
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / self.CONFIG_DIR_NAME
        
        self.config_file = self.config_dir / self.CONFIG_FILENAME
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Ensure the config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def is_first_launch(self) -> bool:
        """
        Check if this is the first launch of the application.
        
        A config file that exists but holds no usable salt counts as a first
        launch: it is residue from an interrupted setup or an old test run, and
        there is nothing in it left to unlock.
        
        Returns:
            True if there is no usable configuration yet, False otherwise
        """
        return not self.has_valid_config()
    
    def has_valid_config(self) -> bool:
        """
        Check whether a usable configuration exists.
        
        Returns:
            True if the config file holds a salt we can actually derive keys from
        """
        return self.load_salt() is not None
    
    def save_salt(self, salt: bytes) -> bool:
        """
        Save the salt to the config file.
        
        The file is written atomically, so an interrupted write leaves the
        previous config intact instead of a half-written one.
        
        Args:
            salt: The salt bytes to save
        
        Returns:
            True if successful, False otherwise
        """
        if not isinstance(salt, (bytes, bytearray)) or len(salt) < self.MIN_SALT_LENGTH:
            print("Error saving salt: refusing to store an invalid salt")
            return False
        
        try:
            config = self._load_config()
            # Store salt as base64 for JSON compatibility
            config['salt'] = base64.b64encode(bytes(salt)).decode('utf-8')
            config['version'] = 1
            
            self._write_config(config)
            return True
        except Exception as e:
            print(f"Error saving salt: {e}")
            return False
    
    def _write_config(self, config: dict) -> None:
        """
        Write the config to disk atomically with owner-only permissions.
        
        Args:
            config: Configuration dictionary to persist
        """
        self._ensure_config_dir()
        
        # Create the temp file in the config dir so os.replace() stays on one
        # filesystem, and at 0600 from the start -- never world-readable, not
        # even for the moment between write and chmod.
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.config_dir), prefix='.config-', suffix='.tmp'
        )
        try:
            os.chmod(tmp_path, 0o600)
            with os.fdopen(fd, 'w') as f:
                json.dump(config, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.config_file)
        except Exception:
            # Do not leave the partial temp file behind.
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    
    def load_salt(self) -> bytes | None:
        """
        Load the salt from the config file.
        
        Returns:
            The salt bytes, or None if missing, malformed or too short
        """
        try:
            config = self._load_config()
            salt_b64 = config.get('salt')
            if not isinstance(salt_b64, str) or not salt_b64:
                return None
            
            # Decode base64 salt
            salt = base64.b64decode(salt_b64, validate=True)
            if len(salt) < self.MIN_SALT_LENGTH:
                return None
            return salt
        except Exception as e:
            # binascii.Error for malformed base64, anything else for a config
            # we simply cannot make sense of.
            print(f"Error loading salt: {e}")
            return None
    
    def save_verifier(self, verifier: str) -> bool:
        """
        Save the key verification token.
        
        Args:
            verifier: The token from CryptoManager.make_verifier()
        
        Returns:
            True if successful, False otherwise
        """
        if not isinstance(verifier, str) or not verifier:
            print("Error saving verifier: refusing to store an empty token")
            return False
        
        try:
            config = self._load_config()
            config['verifier'] = verifier
            self._write_config(config)
            return True
        except Exception as e:
            print(f"Error saving verifier: {e}")
            return False
    
    def load_verifier(self) -> str | None:
        """
        Load the key verification token.
        
        Returns:
            The token, or None if this config predates verification or has none
        """
        verifier = self._load_config().get('verifier')
        return verifier if isinstance(verifier, str) and verifier else None
    
    def clear_stale_config(self) -> bool:
        """
        Remove a config file that holds no usable salt.
        
        This clears residue from interrupted setups, old test runs and previous
        builds so a fresh install starts clean. A config with a usable salt is
        never touched -- deleting that would make already encrypted files
        permanently unreadable.
        
        Returns:
            True if a stale config file was removed, False otherwise
        """
        if not self.config_file.exists() or self.has_valid_config():
            return False
        
        try:
            self.config_file.unlink()
            return True
        except OSError as e:
            print(f"Error clearing stale config: {e}")
            return False
    
    def _load_config(self) -> dict:
        """
        Load the config file. Returns empty dict if file doesn't exist.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
        
        # A JSON file that is valid but not an object (an old test fixture, a
        # stray list) is not a config we can use.
        return config if isinstance(config, dict) else {}
    
    def get_config_dir(self) -> Path:
        """Get the config directory path."""
        return self.config_dir
