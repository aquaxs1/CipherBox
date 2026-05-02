# CipherBox - Secure File Encryption Application

## Overview

**CipherBox** is a modern, secure desktop application for encrypting and decrypting local files. Built with a sleek GUI and enterprise-grade cryptography, it ensures your sensitive files remain protected.

### Key Security Features

- **PBKDF2-HMAC-SHA256 Key Derivation**: 480,000 iterations (OWASP 2024 recommendation)
- **Fernet Encryption**: Symmetric AES encryption with authentication
- **Master Password Protection**: One secure password to encrypt/decrypt all files
- **Secure File Deletion**: Multi-pass overwriting before file removal
- **Optional Filename Encryption**: Hide original filenames using random UUIDs
- **No Plain Text Storage**: Password is never stored; only cryptographically-derived keys

---

## Installation

### Requirements

- **Python 3.10 or higher**
- **Windows, macOS, or Linux**

### Step 1: Install Python

Download Python from [python.org](https://www.python.org/downloads/) (3.10+)

Verify installation:
```bash
python --version
```

### Step 2: Install Dependencies

Navigate to the CipherBox directory and install required packages:

```bash
pip install -r requirements.txt
```

This installs:
- **customtkinter** (v5.2.0): Modern GUI framework
- **cryptography** (v41.0.7): Strong cryptographic primitives

---

## First-Time Setup

When you launch CipherBox for the first time:

1. **Master Password Generation**: A 32-character cryptographically-random password is auto-generated
2. **Critical Warning Screen**: Read the warning carefully—this is your ONLY password
3. **Copy & Confirm**: Copy the password to clipboard and confirm you've saved it
4. **Setup Complete**: Your encryption key is derived and secured

### ⚠️ IMPORTANT SECURITY NOTES

- **Save your Master Password securely**:
  - Write it down on paper and store in a safe
  - Use a password manager (Bitwarden, 1Password, KeePass)
  - **NEVER** store it in plain text files on your computer
  - **NEVER** share it with anyone
  
- **If you lose your Master Password**:
  - All encrypted files are **permanently inaccessible**
  - There is NO recovery method
  - This is by design for maximum security

---

## Usage

### Launching the Application

```bash
python main.py
```

### Encrypting Files

1. Open the **"📝 Encrypt Files"** tab
2. Click **"➕ Add Files"** and select one or more files
3. (Optional) Check **"🔒 Encrypt filenames"** to hide original filenames
4. Click **"🔐 Encrypt Files"**
5. Wait for completion message
6. Original files are securely deleted; encrypted `.cipherbox` files remain

**What happens:**
- Files are encrypted with your Master Password
- If filenames are encrypted, original names are stored securely inside
- Original files are overwritten 3 times before deletion for security
- Encrypted files can be moved/copied safely

### Decrypting Files

1. Open the **"🔓 Decrypt Files"** tab
2. Click **"➕ Add Files"** and select `.cipherbox` files to decrypt
3. Click **"🔓 Decrypt Files"**
4. Enter your Master Password when prompted
5. Wait for completion message
6. Original files are restored with original names and extensions

**What happens:**
- Encrypted `.cipherbox` files are decrypted
- Original filenames are restored (if they were encrypted)
- Original files are reconstructed
- Encrypted `.cipherbox` files are securely deleted
- If a file with the same name exists, a number is appended (e.g., `document_1.pdf`)

---

## File Format & Structure

### Encrypted File Format

Each `.cipherbox` file contains:

```
┌─ Fernet Encryption ─────────────────────────────────┐
│ ┌─ Plaintext Payload (before encryption) ─────────┐ │
│ │ [Metadata Length: 4 bytes]                       │ │
│ │ [JSON Metadata (variable length)]                │ │
│ │ │ • version: 1                                  │ │
│ │ │ • original_filename: "document.pdf"           │ │
│ │ │ • encrypted_filename: true/false              │ │
│ │ [Original File Content (binary)]                 │ │
│ └─────────────────────────────────────────────────┘ │
│ ← Fernet-encrypted (includes authentication tag)    │
└─────────────────────────────────────────────────────┘
```

### Configuration Storage

- **Location**: `~/.cipherbox/config.json` (user's home directory)
- **Contents**: Salt for key derivation (never the password)
- **Permissions**: `0o600` (read/write by owner only)

---

## Technical Specifications

### Cryptography Details

| Component | Specification |
|-----------|---|
| **Key Derivation** | PBKDF2-HMAC-SHA256 |
| **Iterations** | 480,000 (OWASP 2024) |
| **Salt Length** | 32 bytes (256 bits) |
| **Encryption Cipher** | Fernet (AES-128-CBC + HMAC-SHA256) |
| **Key Size** | 32 bytes (256 bits) |
| **Secure Deletion** | 3-pass overwrite + final zero fill |

### Code Architecture

```
CipherBox/
├── main.py              # GUI application & orchestration
├── crypto_utils.py      # Encryption/decryption logic
├── config_manager.py    # Configuration & salt management
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

**Separation of Concerns:**
- **main.py**: User interface (customtkinter)
- **crypto_utils.py**: All cryptographic operations
- **config_manager.py**: Configuration file management

---

## Troubleshooting

### "Permission denied" Error

**Problem**: File is in use by another application (e.g., open in editor)

**Solution**: Close the file in all applications and try again

### "Wrong password or corrupted file"

**Problem**: Master Password is incorrect or file is damaged

**Solution**: 
- Verify you've entered the correct Master Password
- Check that the `.cipherbox` file hasn't been corrupted or modified

### Application won't start

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install --upgrade -r requirements.txt
```

### Forgot Master Password

**Problem**: Cannot decrypt files

**Solution**: There is no recovery. Your encrypted files are permanently inaccessible. This is intentional for security.

---

## Security Considerations

### ✓ What CipherBox Does Well

- Uses industry-standard, audited cryptographic libraries
- Implements proper key derivation with high iteration count
- Securely deletes original files
- Never stores passwords in any form
- Uses Fernet for authenticated encryption (prevents tampering)

### ⚠️ What CipherBox Cannot Protect Against

- **Malware**: If your computer is compromised, malware could intercept your password
- **Physical Access**: Someone with physical access and admin privileges could potentially intercept memory
- **Weak Master Passwords**: CipherBox auto-generates strong passwords, so this is not a concern

### Best Practices

1. **Use on a clean system**: Run on a trusted computer without malware
2. **Keep backups**: Maintain backups of encrypted files in multiple locations
3. **Test recovery**: Regularly test decryption to ensure files aren't corrupted
4. **Update Python**: Keep Python and libraries updated for security patches

---

## Advanced Usage

### Command-Line Usage (For Scripting)

You can import CipherBox modules for programmatic use:

```python
from crypto_utils import CryptoManager
from config_manager import ConfigManager

crypto = CryptoManager()
config = ConfigManager()

# Generate password
master_pwd = crypto.generate_master_password(32)

# Load salt and derive key
salt = config.load_salt()
key = crypto.derive_key(master_pwd, salt)

# Encrypt file
success, msg = crypto.encrypt_file("document.pdf", key, encrypt_filename=True)

# Decrypt file
success, msg, output_path = crypto.decrypt_file("randomuuid.cipherbox", key)
```

---

## Performance

- **Encryption/Decryption Speed**: Depends on file size and system
  - Key derivation: ~1-2 seconds (PBKDF2 with 480,000 iterations)
  - Typical file (1-100 MB): < 1 second
  - Large files (> 1 GB): Proportional to size
  
- **Memory Usage**: Minimal; files are read/written in chunks

---

## License & Support

This application is provided as-is for personal use.

For security issues, please do NOT publicly disclose vulnerabilities. Instead, review the code and make improvements locally.

---

## FAQ

**Q: Can I change my Master Password?**
A: Not in the current version. If needed, you would need to decrypt all files with the old password and re-encrypt with a new one.

**Q: Can I use this on external drives?**
A: Yes, but keep the `.cipherbox` config directory on your main system for easy access.

**Q: How large can encrypted files be?**
A: CipherBox can handle multi-GB files, limited only by available disk space and memory.

**Q: Is CipherBox open-source?**
A: The code is provided in a straightforward format. Feel free to review, modify, and improve it.

**Q: Can I use CipherBox on multiple devices?**
A: Yes, but you need to manually copy the `~/.cipherbox/config.json` salt file to other devices to decrypt files. Keep it in a safe location.

---

## Version History

- **v1.0** (2026-05-02): Initial release
  - Master password auto-generation
  - File encryption/decryption with Fernet
  - Optional filename encryption
  - Modern customtkinter GUI

---

Enjoy secure file encryption with **CipherBox**! 🔐
