"""
Configuration manager for CipherBox application.
Handles salt storage and first-time setup detection.
"""

import json
import os
from pathlib import Path
import base64


class ConfigManager:
    """Manages application configuration and salt storage."""
    
    CONFIG_DIR_NAME = '.cipherbox'
    CONFIG_FILENAME = 'config.json'
    
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
        
        Returns:
            True if config file doesn't exist (first launch), False otherwise
        """
        return not self.config_file.exists()
    
    def save_salt(self, salt: bytes) -> bool:
        """
        Save the salt to the config file.
        
        Args:
            salt: The salt bytes to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            config = self._load_config()
            # Store salt as base64 for JSON compatibility
            config['salt'] = base64.b64encode(salt).decode('utf-8')
            config['version'] = 1
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Secure file permissions (readable/writable by owner only)
            os.chmod(self.config_file, 0o600)
            return True
        except Exception as e:
            print(f"Error saving salt: {e}")
            return False
    
    def load_salt(self) -> bytes | None:
        """
        Load the salt from the config file.
        
        Returns:
            The salt bytes, or None if not found or error occurs
        """
        try:
            config = self._load_config()
            if 'salt' not in config:
                return None
            
            # Decode base64 salt
            salt_b64 = config['salt']
            return base64.b64decode(salt_b64)
        except Exception as e:
            print(f"Error loading salt: {e}")
            return None
    
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
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def get_config_dir(self) -> Path:
        """Get the config directory path."""
        return self.config_dir
