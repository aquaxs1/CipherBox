# START HERE - CipherBox Installation & First Steps

## ⚡ QUICK SETUP (5 minutes)

### For Windows Users

1. Download Python 3.10+ from https://www.python.org/downloads/
   - **IMPORTANT**: Check ☑️ "Add Python to PATH" during installation
   - Click "Install Now"

2. Open Command Prompt (Win+R → type `cmd` → Enter)

3. Navigate to CipherBox folder:
   ```
   cd C:\Verkrypter
   ```

4. Run the installer:
   ```
   install.bat
   ```

5. Wait for "Installation Complete! ✓"

6. Launch CipherBox:
   ```
   python main.py
   ```

### For macOS Users

1. Install Python 3.10+ (if not installed):
   ```bash
   brew install python3
   ```

2. Open Terminal and navigate to CipherBox folder:
   ```bash
   cd ~/CipherBox
   ```

3. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. Launch CipherBox:
   ```bash
   python3 main.py
   ```

### For Linux Users

1. Install Python 3.10+:
   ```bash
   sudo apt-get install python3 python3-pip
   ```

2. Navigate to CipherBox folder:
   ```bash
   cd ~/CipherBox
   ```

3. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. Launch CipherBox:
   ```bash
   python3 main.py
   ```

---

## 🔐 FIRST LAUNCH - WHAT TO EXPECT

### Screen 1: Big Red Warning

You'll see a HUGE red warning screen saying:
> "This is your ONLY Master Password.  
> If you lose it, your files are GONE FOREVER."

**This is intentional.** Your security depends on this password.

### Screen 2: Your Master Password

A 32-character random password appears (looks like): 
```
aBc123XyZ9kL7mN0pQrS4tUvW5xYz8aB
```

**SAVE THIS PASSWORD NOW:**

1. Click **"📋 Copy to Clipboard"**
2. Paste it into ONE of these:
   - Password manager (Bitwarden, 1Password, KeePass)
   - Paper in a safe
   - Encrypted note on external drive
   - **NOT** in a file on your computer

3. Check the box: "✓ I have saved this password in a safe location"

4. Click **"Proceed to Main Application"**

### Screen 3: Main Application

You're in! Now you can encrypt and decrypt files.

---

## 📝 HOW TO USE - THE BASICS

### Encrypt Files

**Goal**: Turn a regular file into a locked file

1. Click the **"📝 Encrypt Files"** tab
2. Click **"➕ Add Files"**
3. Select one or more files to encrypt
4. Click **"🔐 Encrypt Files"**
5. Wait for "Encryption Complete ✓"
6. Your files are now encrypted!

**What happened:**
- Original file is DELETED securely
- Encrypted `.cipherbox` file remains
- Only someone with your Master Password can open it

### Decrypt Files

**Goal**: Turn an encrypted `.cipherbox` file back into a regular file

1. Click the **"🔓 Decrypt Files"** tab
2. Click **"➕ Add Files"**
3. Select `.cipherbox` files
4. Click **"🔓 Decrypt Files"**
5. Wait for "Decryption Complete ✓"
6. Your files are restored!

**What happened:**
- Original filename is restored automatically
- `.cipherbox` file is DELETED securely
- Regular file is back and ready to use

---

## 🔒 YOUR MASTER PASSWORD - CRITICAL INFO

### Remember

✓ This is your ONLY password for ALL files  
✓ If you lose it, your files are GONE FOREVER  
✓ There is NO recovery or "forgot password" option  
✓ You must save it immediately  

### Save It In Multiple Places

**GOOD (DO THIS):**
- Password manager + write on paper
- Physical backup in a safe + digital backup
- Multiple secure locations

**BAD (DON'T DO THIS):**
- ✗ Sticky note on your monitor
- ✗ Plain text file on your computer
- ✗ Email draft
- ✗ Only one location

---

## ❓ COMMON QUESTIONS

### Q: Can I encrypt a folder?

**A**: CipherBox encrypts individual files. To encrypt a folder:
1. Compress folder to ZIP
2. Encrypt the ZIP
3. To recover: Decrypt ZIP, then extract

### Q: Can I use the same password for multiple computers?

**A**: Yes, but you need to copy the salt file `~/.cipherbox/config.json` to other computers.

### Q: How long does encryption take?

**A**: 
- Small file (1 MB): < 1 second
- Large file (1 GB): A few seconds
- Key derivation: 1-2 seconds (normal, for security)

### Q: What if I need to decrypt files on another computer?

**A**: 
1. Copy the `.cipherbox` files to the other computer
2. Install CipherBox there
3. Copy the salt file `~/.cipherbox/config.json` to the other computer
4. Launch CipherBox and enter your Master Password

### Q: Can I change my Master Password?

**A**: Not in this version. To change passwords:
1. Decrypt all files with old password
2. Encrypt all files with new password

### Q: Is my password stored anywhere?

**A**: No. Only the "salt" is stored. Your password is never stored.

### Q: What if someone hacks my computer?

**A**: Files are still encrypted. Your Master Password is the only way to decrypt them. If an attacker doesn't have your password, they can't access your files.

---

## ⚠️ IMPORTANT REMINDERS

### Before Using

- [ ] I have saved my Master Password securely
- [ ] I understand it can't be recovered if lost
- [ ] I have tested encryption on a sample file
- [ ] I have verified I can decrypt the test file

### During Use

- [ ] I close files before encrypting them
- [ ] I keep backups of important encrypted files
- [ ] I test decryption periodically
- [ ] I keep my Master Password safe

### Ongoing

- [ ] I verify my Master Password is still accessible
- [ ] I keep Python and dependencies updated
- [ ] I monitor disk space for large files

---

## 🚨 IF SOMETHING GOES WRONG

### Error: "Python not found"

**Solution**: 
1. Reinstall Python from https://www.python.org/downloads/
2. **IMPORTANT**: Check ☑️ "Add Python to PATH"
3. Restart your computer
4. Try again

### Error: "ModuleNotFoundError: No module named 'customtkinter'"

**Solution**:
```bash
pip install -r requirements.txt
```

### Error: "Permission denied"

**Solution**:
1. Close the file in all applications
2. Close any file explorer/finder windows
3. Try again

### Error: "Wrong password or corrupted file"

**Solution**:
- Verify your Master Password is exactly correct
- Try decrypting a different file
- If multiple files fail, your password may be wrong

### Lost Master Password

**Solution**:
- Check password manager (if you saved it there)
- Check your paper backup (if you wrote it down)
- If truly lost: Your files are permanently inaccessible
  - This is by design for maximum security
  - There is no recovery mechanism

---

## 📚 WHERE TO GET HELP

| Issue | Solution |
|-------|----------|
| Installation | See **README.md** |
| How to use | See **QUICKSTART.md** |
| Technical details | See **GUIDE.md** |
| First launch | See **PROJECT_COMPLETION.md** |
| Security questions | See **README.md** Security section |

---

## 🎯 NEXT STEPS

### Step 1: Verify Installation
```bash
python test_cipherbox.py
```

Expected: "All tests passed ✓"

### Step 2: Launch Application
```bash
python main.py
```

Expected: First-launch wizard appears

### Step 3: Complete Setup
1. Master password generated
2. Copy to clipboard
3. Save to password manager/paper
4. Confirm checkbox
5. Click "Proceed"

### Step 4: Test on Sample File
1. Create a test file
2. Encrypt it
3. Verify it's encrypted (`.cipherbox` file)
4. Decrypt it
5. Verify content matches

### Step 5: Start Using
Now you're ready to encrypt/decrypt your real files!

---

## 💡 PRO TIPS

### Batch Encryption

You can select multiple files at once:
1. Click "➕ Add Files"
2. Hold **Ctrl** (Windows/Linux) or **Cmd** (macOS)
3. Click each file you want
4. Click "Open"
5. All files will encrypt together

### Hide Filenames

For extra privacy:
1. Check **"🔒 Encrypt filenames"**
2. Filename becomes a random UUID
3. Original name stored inside the encrypted file
4. Automatically restored on decryption

### Encrypt Everything

You can encrypt:
- Documents (PDF, Word, Excel)
- Photos (JPG, PNG)
- Videos (MP4, AVI)
- Archives (ZIP, RAR)
- ANY file type

---

## 🔐 SECURITY IN PLAIN LANGUAGE

CipherBox uses two main security features:

### 1. Strong Password Derivation

Your Master Password is turned into an encryption key using PBKDF2-HMAC-SHA256:
- Takes 1-2 seconds to derive the key
- This delay makes it impossible to guess passwords
- 480,000 iterations = military-grade security

### 2. Authenticated Encryption (Fernet)

Your files are encrypted with AES encryption PLUS authentication:
- AES scrambles the data (unreadable without password)
- Authentication detects if someone modified the file
- Can't decrypt if file is corrupted or tampered with

---

## 📞 QUICK REFERENCE

| Task | Steps |
|------|-------|
| **Encrypt files** | Encrypt tab → Add Files → Encrypt |
| **Decrypt files** | Decrypt tab → Add Files → Decrypt |
| **Lock app** | Click "🔒 Lock" button |
| **Unlock app** | Enter Master Password → Click "Unlock" |
| **Change theme** | Edit main.py line: `ctk.set_appearance_mode()` |
| **Update dependencies** | Run: `pip install -r requirements.txt --upgrade` |

---

## ✅ QUICK CHECKLIST

- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests pass (`python test_cipherbox.py`)
- [ ] Application launches (`python main.py`)
- [ ] Master password saved securely
- [ ] Tested encryption on sample file
- [ ] Tested decryption on sample file
- [ ] Ready to use!

---

## 🎉 YOU'RE READY!

You now have a complete, production-ready file encryption application.

**Next**: Read the documentation for more detailed information:
- **README.md** - Full documentation
- **QUICKSTART.md** - Quick start guide
- **GUIDE.md** - Technical details

**Questions?** Check the FAQ or troubleshooting sections in the documentation.

**Ready to encrypt files?** Launch with `python main.py` and get started!

---

**CipherBox v1.0 - Secure File Encryption**  
**Status**: Production Ready ✓  
**Last Updated**: May 2, 2026

🔐 Secure your files. Control your data. 🔐
