# CipherBox Quick Start Guide

> **For users.** Get running and encrypt your first file, step by step.
> Reference documentation lives in [README.md](README.md); architecture and
> development notes in [GUIDE.md](GUIDE.md).

## 🚀 Installation (2 minutes)

### Option 1: Windows — download the app (Recommended)

1. Download **[CipherBox.exe](https://github.com/aquaxs1/CipherBox/releases/latest/download/CipherBox.exe)**
2. Double-click it

That is the whole installation. No Python, no dependencies, no unpacking.

On first launch Windows SmartScreen shows a blue warning, because the build is
not code-signed. Choose **More info → Run anyway**.

To check the download against the published hash first:
```powershell
certutil -hashfile CipherBox.exe SHA256
```
Compare the result with `SHA256SUMS.txt` on the
[releases page](https://github.com/aquaxs1/CipherBox/releases/latest).

### Option 2: Run from source (any platform)

Needs **Python 3.10+**. On macOS/Linux this is currently the way to run
CipherBox unless a release ships a binary for your platform.

```bash
git clone https://github.com/aquaxs1/CipherBox.git
cd CipherBox
pip install -r requirements.txt
python main.py
```

To confirm everything works before you trust it with real files:
```bash
python test_cipherbox.py
```

---

## 📝 First Launch Walkthrough

### Step 1: Security Warning
When you launch CipherBox for the first time, you'll see a bright red warning screen.

**Why?** Your Master Password is being generated. This is your ONLY password.

### Step 2: Master Password Display
A 32-character cryptographically-random password appears:
- **Example**: `aBc123XyZ9kL7mN0pQrS4tUvW5xYz8aB`

### Step 3: Save Your Password
1. Click **"📋 Copy to Clipboard"**
2. Paste it in a SECURE location:
   - Password manager (Bitwarden, 1Password, KeePass)
   - Paper stored in a safe
   - Encrypted note on an external drive
   - **NOT** in a plain text file on your computer

### Step 4: Confirmation
Check the box: "✓ I have saved this password in a safe location"

### Step 5: Proceed
Click **"Proceed to Main Application"**

You're now ready to encrypt/decrypt files!

---

## 🔐 How to Encrypt Files

### Basic Encryption (Keep filename)

1. Open the **"📝 Encrypt Files"** tab
2. Click **"➕ Add Files"**
3. Select one or more files to encrypt
4. Click **"🔐 Encrypt Files"**
5. Wait for completion
6. Original files are securely deleted
7. `.cipherbox` encrypted files remain

**Example:**
```
Before: document.pdf (1.5 MB)
After:  document.pdf.cipherbox (1.5 MB)
```

### Advanced: Hide Filenames

1. Open the **"📝 Encrypt Files"** tab
2. Click **"➕ Add Files"**
3. Select files
4. ✓ Check **"🔒 Encrypt filenames"**
5. Click **"🔐 Encrypt Files"**

**What happens:**
- Filename becomes a random UUID
- Original filename stored securely inside the encrypted file
- Restoring filename during decryption is automatic

**Example:**
```
Before: confidential_report.xlsx (2.1 MB)
After:  a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6.cipherbox (2.1 MB)
```

**Benefits:**
- Files can't be identified by name
- Plausible deniability (could be any file type)
- Extra privacy layer

---

## 🔓 How to Decrypt Files

1. Open the **"🔓 Decrypt Files"** tab
2. Click **"➕ Add Files"**
3. Select `.cipherbox` files to decrypt
4. Click **"🔓 Decrypt Files"**
5. Original files are restored with original names and extensions
6. `.cipherbox` files are securely deleted

**Example:**
```
Before: a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6.cipherbox
After:  confidential_report.xlsx
```

**File Naming:**
- If a file with the same name already exists, a number is appended
- Example: `document_1.pdf`, `document_2.pdf`

---

## 🔒 Master Password Management

### What You Need to Know

- ✓ Your Master Password is **YOUR ONLY PASSWORD**
- ✓ It CANNOT be recovered if lost
- ✓ It is NEVER stored anywhere
- ✗ No recovery options exist
- ✗ No "forgot password" reset
- ✗ Losing it means losing ALL encrypted files forever

### Where to Store Your Master Password

**SECURE Locations:**
1. **Password Manager** (Recommended)
   - Bitwarden (open-source, free)
   - 1Password (commercial)
   - KeePass (open-source)
   - LastPass

2. **Physical Backup** (Recommended)
   - Written on paper in a safe
   - Safety deposit box
   - Home safe

3. **Redundancy** (Best Practice)
   - Store in password manager + write down
   - Store in multiple physical locations
   - Share with trusted family member (in case of emergency)

**INSECURE Locations:**
- ✗ Plain text files on your computer
- ✗ Sticky notes on your monitor
- ✗ Email drafts
- ✗ Cloud storage (unless encrypted)
- ✗ Text messages
- ✗ Slack/Teams messages

---

## 💡 Common Scenarios

### Scenario 1: Backup Important Files

**Goal**: Encrypt files for secure backup

```
1. Select important files (documents, photos, etc.)
2. Encrypt with filename encryption enabled
3. Copy encrypted .cipherbox files to external drive
4. Store in multiple locations
5. Original files are securely deleted from computer
6. Decrypt on external drive when needed
```

### Scenario 2: Protect Sensitive Documents

**Goal**: Protect documents from prying eyes

```
1. Select sensitive PDFs/spreadsheets
2. Encrypt with standard filename (keeps .pdf/.xlsx visible)
3. Move encrypted files to protected folder
4. Delete original files permanently
5. Only you can decrypt them
```

### Scenario 3: Secure File Transfer

**Goal**: Send encrypted files to someone else

```
1. Encrypt files with filename encryption
2. Share encrypted .cipherbox files via any channel (email, cloud, USB)
3. Share Master Password separately (NOT via same channel)
4. Recipient installs CipherBox
5. Recipient decrypts files with your password
```

---

## ⚠️ Important Reminders

### Before You Start

- [ ] I have saved my Master Password in a secure location
- [ ] I understand that losing my password means losing all files
- [ ] I understand that there is NO recovery mechanism
- [ ] I have read and understand the security warnings

### During Use

- [ ] Close files before encrypting (don't encrypt open files)
- [ ] Keep backups of important encrypted files
- [ ] Test decryption periodically to ensure files aren't corrupted
- [ ] Keep Python and libraries updated

### Best Practices

- [ ] Use a password manager to store your Master Password
- [ ] Write your Master Password on paper in a secure location
- [ ] Never share your Master Password with anyone
- [ ] Test decryption on a small file before encrypting large files
- [ ] Keep the `~/.cipherbox/config.json` file safe (contains the salt)

---

## 🐛 Troubleshooting

### CipherBox won't start

**Problem**: "ModuleNotFoundError: No module named 'customtkinter'"

**Solution**:
```bash
pip install -r requirements.txt
```

### "Permission denied" error

**Problem**: Can't encrypt/decrypt file

**Solution**: 
- Close the file in all applications
- Close any file explorer/finder windows showing the file
- Try again

### "Wrong password or corrupted file" error

**Problem**: Can't decrypt even with correct password

**Solutions**:
- Double-check that you've entered the correct Master Password exactly
- Verify the `.cipherbox` file hasn't been corrupted or modified
- Try decrypting a different file to confirm password is correct
- If multiple files fail, your password may be wrong

### Lost Master Password

**Problem**: Can't decrypt files

**Solution**: 
- If you saved it in a password manager, retrieve it there
- If you wrote it down, look for it in your safe
- If you truly lost it: YOUR FILES ARE PERMANENTLY INACCESSIBLE
  - There is no recovery
  - This is by design for maximum security

---

## 🔧 Advanced Tips

### Batch Encryption

You can select multiple files at once:
1. Click "➕ Add Files"
2. Hold **Ctrl** (Windows/Linux) or **Cmd** (macOS)
3. Click each file you want to encrypt
4. Click "Open"
5. All files will be encrypted together

### Folder Encryption Workaround

CipherBox encrypts individual files. To encrypt a folder:
1. Compress folder to ZIP file
2. Encrypt the ZIP file
3. To recover: Decrypt ZIP file, then extract

### Multiple Encryption

You can encrypt an encrypted file again:
1. Encrypt `document.pdf` → creates `document.pdf.cipherbox`
2. Encrypt `document.pdf.cipherbox` again (yes, it works!)
3. Result: `document.pdf.cipherbox.cipherbox`
4. To decrypt: decrypt once, then decrypt again

---

## 📊 Performance Expectations

### Key Derivation
- **Time**: roughly 0.1–0.5 seconds on a modern CPU, once per unlock
- **Why**: PBKDF2 with 480,000 iterations (deliberately slow, to make guessing
  your master password expensive)

### Encryption
- **1 MB**: well under a second
- **10 MB**: under half a second
- **50 MB**: a few seconds
- **Above 256 MB**: CipherBox warns first — see the memory note below
- **Factors**: file size, CPU speed, disk I/O

### Memory use — the real limit
Files are loaded into memory whole rather than streamed, so encrypting or
decrypting needs roughly **9x the file size** in free RAM. A 100 MB file wants
about 900 MB free; a 1 GB file needs several GB and will fail on most machines.
Split very large archives before encrypting them.

### Decryption
- Similar speed to encryption
- Key derivation (1-2 seconds) + decryption time

---

## 🎓 Security Concepts Explained

### Why PBKDF2?
- **PBKDF2** (Password-Based Key Derivation Function 2) is a standard way to convert passwords into encryption keys
- **480,000 iterations** means it takes time to derive the key, making brute-force attacks infeasible
- **HMAC-SHA256** uses a cryptographically secure hash function

### Why Fernet?
- **Fernet** combines AES (Advanced Encryption Standard) with authentication
- **Authentication** ensures encrypted files haven't been tampered with
- If someone modifies the encrypted file, decryption will fail safely

### Why Secure Deletion?
- Simply deleting a file only removes the directory entry
- The actual data remains on disk
- **3-pass overwriting** + **zero fill**, each pass flushed to the device, makes
  recovery very difficult on a magnetic disk. On an SSD, USB stick or SD card, wear
  levelling writes each pass to a fresh block and the original data survives out of
  reach — full-disk encryption is the dependable answer there.

---

## 📞 Support & Contact

### Having Issues?

1. **Check README.md** for detailed troubleshooting
2. **Review test results** from `test_cipherbox.py`
3. **Check Python version**: `python --version` (must be 3.10+)
4. **Check dependencies**: `pip list | grep customtkinter`

### Reporting Issues

When reporting issues, include:
- Your operating system (Windows 10/11, macOS version, Linux distro)
- Python version (`python --version`)
- Error message (exact text)
- Steps to reproduce the issue

---

## 📚 Further Learning

### Cryptography Concepts
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Fernet (cryptography.io)](https://cryptography.io/en/latest/fernet/)
- [PBKDF2 RFC 8018](https://tools.ietf.org/html/rfc8018)

### Python Security
- [Official cryptography Library Docs](https://cryptography.io/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---

**Last Updated**: May 2, 2026  
**Version**: 1.0  
**Status**: Production Ready ✓

Enjoy secure file encryption with CipherBox! 🔐
