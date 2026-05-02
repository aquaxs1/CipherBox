"""
CipherBox - A secure desktop application for encrypting and decrypting local files.
Modern GUI built with customtkinter.
"""

import customtkinter as ctk
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from crypto_utils import CryptoManager
from config_manager import ConfigManager


class CipherBoxApp(ctk.CTk):
    """Main application window for CipherBox."""
    
    def __init__(self):
        """Initialize the CipherBox application."""
        super().__init__()
        
        # Configure window
        self.title("CipherBox - Secure File Encryption")
        self.geometry("900x700")
        self.resizable(True, True)
        
        # Initialize managers
        self.crypto = CryptoManager()
        self.config = ConfigManager()
        self.encryption_key = None
        self.master_password = None
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # First launch check
        if self.config.is_first_launch():
            self.show_first_launch_wizard()
        else:
            self.show_password_prompt()
    
    def show_first_launch_wizard(self) -> None:
        """Display the first-time setup wizard with master password generation."""
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔐 CipherBox Setup Wizard",
            font=("Helvetica", 28, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Warning frame (styled prominently)
        warning_frame = ctk.CTkFrame(main_frame, fg_color="#8B0000", corner_radius=10)
        warning_frame.pack(fill="x", pady=20)
        
        warning_title = ctk.CTkLabel(
            warning_frame,
            text="⚠️ CRITICAL WARNING ⚠️",
            font=("Helvetica", 18, "bold"),
            text_color="white"
        )
        warning_title.pack(pady=(15, 10))
        
        warning_text = ctk.CTkLabel(
            warning_frame,
            text="This is your ONLY Master Password.\n"
                 "If you lose it, your encrypted files are GONE FOREVER.\n"
                 "No recovery is possible. Save it immediately!",
            font=("Helvetica", 14),
            text_color="white",
            justify="center"
        )
        warning_text.pack(pady=(0, 15), padx=15)
        
        # Password display frame
        password_frame = ctk.CTkFrame(main_frame, fg_color="#2a2a2a", corner_radius=5)
        password_frame.pack(fill="x", pady=20)
        
        password_label = ctk.CTkLabel(
            password_frame,
            text="Your Master Password:",
            font=("Helvetica", 12, "bold")
        )
        password_label.pack(pady=(10, 5), anchor="w", padx=15)
        
        # Generate password
        self.master_password = self.crypto.generate_master_password(32)
        
        password_display = ctk.CTkLabel(
            password_frame,
            text=self.master_password,
            font=("Courier", 14, "bold"),
            text_color="#00FF00",
            wraplength=750
        )
        password_display.pack(pady=10, padx=15)
        
        # Copy button
        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(self.master_password)
            self.update()
            copy_btn.configure(text="✓ Copied to Clipboard!", state="disabled")
            self.after(2000, lambda: copy_btn.configure(
                text="📋 Copy to Clipboard",
                state="normal"
            ))
        
        copy_btn = ctk.CTkButton(
            password_frame,
            text="📋 Copy to Clipboard",
            command=copy_to_clipboard,
            fg_color="#0066cc",
            hover_color="#0052a3"
        )
        copy_btn.pack(pady=(0, 10))
        
        # Confirmation checkbox
        self.saved_password_var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(
            main_frame,
            text="✓ I have saved this password in a safe location",
            variable=self.saved_password_var,
            font=("Helvetica", 12),
            text_color="white"
        )
        checkbox.pack(pady=20, anchor="w")
        
        # Proceed button (initially disabled)
        def enable_proceed_button(*args):
            proceed_btn.configure(
                state="normal" if self.saved_password_var.get() else "disabled",
                fg_color="#00cc00" if self.saved_password_var.get() else "#444444"
            )
        
        self.saved_password_var.trace("w", enable_proceed_button)
        
        proceed_btn = ctk.CTkButton(
            main_frame,
            text="Proceed to Main Application",
            command=self.complete_first_launch,
            state="disabled",
            fg_color="#444444",
            font=("Helvetica", 14, "bold")
        )
        proceed_btn.pack(pady=20, fill="x")
        
        # Info text
        info_text = ctk.CTkLabel(
            main_frame,
            text="Recommendations:\n"
                 "• Write it down on paper and store in a safe\n"
                 "• Use a password manager to store it\n"
                 "• Never share it with anyone\n"
                 "• Do NOT store it in unencrypted files on this computer",
            font=("Helvetica", 10),
            text_color="#999999",
            justify="left"
        )
        info_text.pack(pady=20, anchor="w")
    
    def complete_first_launch(self) -> None:
        """Complete the first launch setup and generate encryption key."""
        if not self.saved_password_var.get():
            messagebox.showwarning("Warning", "Please confirm that you've saved your password.")
            return
        
        # Generate and save salt
        salt = self.crypto.generate_salt()
        if not self.config.save_salt(salt):
            messagebox.showerror("Error", "Failed to save configuration. Check file permissions.")
            return
        
        # Derive encryption key
        self.encryption_key = self.crypto.derive_key(self.master_password, salt)
        
        # Show main interface
        self.show_main_interface()
        messagebox.showinfo(
            "Success",
            "Setup complete! Your master password has been secured.\n\n"
            "You can now start encrypting and decrypting files."
        )
    
    def show_password_prompt(self) -> None:
        """Show password prompt on subsequent launches."""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔐 CipherBox",
            font=("Helvetica", 32, "bold")
        )
        title_label.pack(pady=(0, 30))
        
        # Prompt
        prompt_label = ctk.CTkLabel(
            main_frame,
            text="Enter your Master Password to continue:",
            font=("Helvetica", 14)
        )
        prompt_label.pack(pady=(0, 15))
        
        # Password entry
        password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Master Password",
            show="•",
            font=("Helvetica", 12),
            height=40
        )
        password_entry.pack(fill="x", pady=10)
        password_entry.focus()
        
        # Status label
        status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=("Helvetica", 12),
            text_color="#FF6B6B"
        )
        status_label.pack(pady=10)
        
        def verify_password():
            password = password_entry.get()
            if not password:
                status_label.configure(text="Please enter your password.", text_color="#FF6B6B")
                return
            
            # Load salt and derive key
            salt = self.config.load_salt()
            if salt is None:
                status_label.configure(text="Configuration error. Please reinstall.", text_color="#FF6B6B")
                return
            
            self.master_password = password
            self.encryption_key = self.crypto.derive_key(password, salt)
            
            # Show main interface
            self.show_main_interface()
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)
        
        unlock_btn = ctk.CTkButton(
            buttons_frame,
            text="🔓 Unlock",
            command=verify_password,
            font=("Helvetica", 14, "bold"),
            height=40
        )
        unlock_btn.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        exit_btn = ctk.CTkButton(
            buttons_frame,
            text="Exit",
            command=self.quit,
            fg_color="#555555",
            hover_color="#444444",
            font=("Helvetica", 14, "bold"),
            height=40
        )
        exit_btn.pack(side="left", fill="both", expand=True)
        
        # Allow pressing Enter to unlock
        password_entry.bind("<Return>", lambda e: verify_password())
    
    def show_main_interface(self) -> None:
        """Display the main application interface with Encrypt/Decrypt tabs."""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Top bar
        top_bar = ctk.CTkFrame(self, fg_color="#1a1a1a")
        top_bar.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            top_bar,
            text="🔐 CipherBox - Secure File Encryption",
            font=("Helvetica", 16, "bold")
        )
        title.pack(side="left", padx=10)
        
        # Lock button
        def lock_application():
            if messagebox.askyesno("Lock", "Lock the application and return to password prompt?"):
                self.master_password = None
                self.encryption_key = None
                self.show_password_prompt()
        
        lock_btn = ctk.CTkButton(
            top_bar,
            text="🔒 Lock",
            command=lock_application,
            fg_color="#555555",
            hover_color="#444444",
            width=100
        )
        lock_btn.pack(side="right", padx=10)
        
        # Tab view
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        encrypt_tab = self.tabview.add("📝 Encrypt Files")
        decrypt_tab = self.tabview.add("🔓 Decrypt Files")
        
        self.setup_encrypt_tab(encrypt_tab)
        self.setup_decrypt_tab(decrypt_tab)
    
    def setup_encrypt_tab(self, parent):
        """Set up the encryption tab UI."""
        # File selection frame
        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(fill="x", padx=15, pady=15)
        
        file_label = ctk.CTkLabel(
            file_frame,
            text="Select Files to Encrypt:",
            font=("Helvetica", 14, "bold")
        )
        file_label.pack(anchor="w", pady=(0, 10))
        
        # File list display
        self.encrypt_file_list = ctk.CTkTextbox(
            file_frame,
            height=150,
            width=600,
            state="disabled"
        )
        self.encrypt_file_list.pack(fill="both", expand=True, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)
        
        def add_files():
            files = filedialog.askopenfilenames(
                title="Select Files to Encrypt",
                parent=self
            )
            if files:
                self.encrypt_files.extend(files)
                self.update_encrypt_file_list()
        
        def clear_files():
            self.encrypt_files.clear()
            self.update_encrypt_file_list()
        
        add_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Add Files",
            command=add_files,
            width=150
        )
        add_btn.pack(side="left", padx=(0, 5))
        
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Clear",
            command=clear_files,
            fg_color="#555555",
            hover_color="#444444",
            width=150
        )
        clear_btn.pack(side="left")
        
        # Encryption options
        options_frame = ctk.CTkFrame(parent)
        options_frame.pack(fill="x", padx=15, pady=15)
        
        self.encrypt_filename_var = ctk.BooleanVar(value=False)
        filename_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="🔒 Encrypt filenames (filenames become random UUIDs)",
            variable=self.encrypt_filename_var,
            font=("Helvetica", 11)
        )
        filename_checkbox.pack(anchor="w")
        
        # Encrypt button
        encrypt_btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        encrypt_btn_frame.pack(fill="x", padx=15, pady=20)
        
        def start_encryption():
            if not self.encrypt_files:
                messagebox.showwarning("No Files", "Please select files to encrypt.")
                return
            
            encrypt_btn.configure(state="disabled", text="Encrypting...")
            threading.Thread(
                target=self.perform_encryption,
                daemon=True
            ).start()
        
        encrypt_btn = ctk.CTkButton(
            encrypt_btn_frame,
            text="🔐 Encrypt Files",
            command=start_encryption,
            font=("Helvetica", 14, "bold"),
            height=45,
            fg_color="#00cc00",
            hover_color="#009900"
        )
        encrypt_btn.pack(fill="x")
        
        self.encrypt_button_ref = encrypt_btn
        self.encrypt_files = []
    
    def update_encrypt_file_list(self):
        """Update the file list display in the encrypt tab."""
        self.encrypt_file_list.configure(state="normal")
        self.encrypt_file_list.delete("1.0", "end")
        
        for i, file_path in enumerate(self.encrypt_files, 1):
            path_obj = Path(file_path)
            size_mb = path_obj.stat().st_size / (1024 * 1024)
            self.encrypt_file_list.insert("end", f"{i}. {path_obj.name} ({size_mb:.2f} MB)\n")
        
        self.encrypt_file_list.configure(state="disabled")
    
    def perform_encryption(self):
        """Perform file encryption in a separate thread."""
        try:
            success_count = 0
            error_count = 0
            errors = []
            
            for file_path in self.encrypt_files:
                encrypt_filename = self.encrypt_filename_var.get()
                success, message = self.crypto.encrypt_file(
                    file_path,
                    self.encryption_key,
                    encrypt_filename
                )
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"{Path(file_path).name}: {message}")
            
            # Update UI on main thread
            self.after(0, lambda: self.encryption_complete(success_count, error_count, errors))
        
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Encryption failed: {str(e)}"))
            self.after(0, lambda: self.encrypt_button_ref.configure(
                state="normal",
                text="🔐 Encrypt Files"
            ))
    
    def encryption_complete(self, success_count, error_count, errors):
        """Handle encryption completion."""
        self.encrypt_button_ref.configure(
            state="normal",
            text="🔐 Encrypt Files"
        )
        
        message = f"✓ Encrypted: {success_count} file(s)"
        if error_count > 0:
            message += f"\n✗ Failed: {error_count} file(s)"
            for error in errors:
                message += f"\n  • {error}"
            messagebox.showwarning("Encryption Complete", message)
        else:
            messagebox.showinfo("Encryption Complete", message)
        
        # Clear file list
        self.encrypt_files.clear()
        self.update_encrypt_file_list()
    
    def setup_decrypt_tab(self, parent):
        """Set up the decryption tab UI."""
        # File selection frame
        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(fill="x", padx=15, pady=15)
        
        file_label = ctk.CTkLabel(
            file_frame,
            text="Select Files to Decrypt:",
            font=("Helvetica", 14, "bold")
        )
        file_label.pack(anchor="w", pady=(0, 10))
        
        # File list display
        self.decrypt_file_list = ctk.CTkTextbox(
            file_frame,
            height=150,
            width=600,
            state="disabled"
        )
        self.decrypt_file_list.pack(fill="both", expand=True, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)
        
        def add_files():
            files = filedialog.askopenfilenames(
                title="Select .cipherbox Files to Decrypt",
                filetypes=[("CipherBox Files", "*.cipherbox"), ("All Files", "*.*")],
                parent=self
            )
            if files:
                self.decrypt_files.extend(files)
                self.update_decrypt_file_list()
        
        def clear_files():
            self.decrypt_files.clear()
            self.update_decrypt_file_list()
        
        add_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Add Files",
            command=add_files,
            width=150
        )
        add_btn.pack(side="left", padx=(0, 5))
        
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Clear",
            command=clear_files,
            fg_color="#555555",
            hover_color="#444444",
            width=150
        )
        clear_btn.pack(side="left")
        
        # Decrypt button
        decrypt_btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        decrypt_btn_frame.pack(fill="x", padx=15, pady=20)
        
        def start_decryption():
            if not self.decrypt_files:
                messagebox.showwarning("No Files", "Please select files to decrypt.")
                return
            
            decrypt_btn.configure(state="disabled", text="Decrypting...")
            threading.Thread(
                target=self.perform_decryption,
                daemon=True
            ).start()
        
        decrypt_btn = ctk.CTkButton(
            decrypt_btn_frame,
            text="🔓 Decrypt Files",
            command=start_decryption,
            font=("Helvetica", 14, "bold"),
            height=45,
            fg_color="#0066cc",
            hover_color="#0052a3"
        )
        decrypt_btn.pack(fill="x")
        
        self.decrypt_button_ref = decrypt_btn
        self.decrypt_files = []
    
    def update_decrypt_file_list(self):
        """Update the file list display in the decrypt tab."""
        self.decrypt_file_list.configure(state="normal")
        self.decrypt_file_list.delete("1.0", "end")
        
        for i, file_path in enumerate(self.decrypt_files, 1):
            path_obj = Path(file_path)
            size_mb = path_obj.stat().st_size / (1024 * 1024)
            self.decrypt_file_list.insert("end", f"{i}. {path_obj.name} ({size_mb:.2f} MB)\n")
        
        self.decrypt_file_list.configure(state="disabled")
    
    def perform_decryption(self):
        """Perform file decryption in a separate thread."""
        try:
            success_count = 0
            error_count = 0
            errors = []
            
            for file_path in self.decrypt_files:
                success, message, _ = self.crypto.decrypt_file(
                    file_path,
                    self.encryption_key
                )
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"{Path(file_path).name}: {message}")
            
            # Update UI on main thread
            self.after(0, lambda: self.decryption_complete(success_count, error_count, errors))
        
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Decryption failed: {str(e)}"))
            self.after(0, lambda: self.decrypt_button_ref.configure(
                state="normal",
                text="🔓 Decrypt Files"
            ))
    
    def decryption_complete(self, success_count, error_count, errors):
        """Handle decryption completion."""
        self.decrypt_button_ref.configure(
            state="normal",
            text="🔓 Decrypt Files"
        )
        
        message = f"✓ Decrypted: {success_count} file(s)"
        if error_count > 0:
            message += f"\n✗ Failed: {error_count} file(s)"
            for error in errors:
                message += f"\n  • {error}"
            messagebox.showwarning("Decryption Complete", message)
        else:
            messagebox.showinfo("Decryption Complete", message)
        
        # Clear file list
        self.decrypt_files.clear()
        self.update_decrypt_file_list()


def main():
    """Main entry point."""
    app = CipherBoxApp()
    app.mainloop()


if __name__ == "__main__":
    main()
