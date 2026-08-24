# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build spec for the CipherBox desktop app.

Build with:

    pyinstaller packaging/cipherbox.spec --noconfirm --clean

Produces a single-file, double-click executable of the customtkinter GUI.
Run from the repo root (or pass --distpath/--workpath) so the relative paths
below resolve.

customtkinter ships its themes and assets as data files next to the package
rather than importing them, so PyInstaller cannot find them by following
imports -- they are collected explicitly below. Without them the app starts
and then dies on the first widget.
"""

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

REPO_ROOT = Path(SPECPATH).resolve().parent
ICONS = REPO_ROOT / "packaging" / "icons"

datas = collect_data_files("customtkinter")

icon = None
if sys.platform == "win32":
    candidate = ICONS / "cipherbox.ico"
    icon = str(candidate) if candidate.is_file() else None
elif sys.platform == "darwin":
    candidate = ICONS / "cipherbox.icns"
    icon = str(candidate) if candidate.is_file() else None

a = Analysis(
    [str(REPO_ROOT / "main.py")],
    pathex=[str(REPO_ROOT)],
    binaries=[],
    datas=datas,
    # crypto_utils and config_manager are top-level modules imported by name
    # from main.py; pathex covers them, but naming them here keeps the build
    # honest if the entry point is ever moved into a package.
    hiddenimports=[
        "crypto_utils",
        "config_manager",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # The test suite and its dependencies have no business in a shipped
        # binary.
        "pytest",
        "unittest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="cipherbox",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX-packed binaries trip antivirus heuristics.
    upx_exclude=[],
    runtime_tmpdir=None,
    # A GUI app: no console window behind it. Startup errors surface through
    # the tkinter message box, not a terminal that nobody sees.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)
