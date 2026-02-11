# -*- mode: python ; coding: utf-8 -*-
"""
🍭 Fillico - PyInstaller Spec File
"""

import sys
from pathlib import Path
import os

block_cipher = None

# Chemin absolu vers l'icône
ICON_PATH = os.path.join(os.getcwd(), 'fillico.ico')

a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('web', 'web'),
        ('assets', 'assets'),
        ('pyproject.toml', '.'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'webview',
        'PIL',
        'PIL.Image',
        'pymupdf',
        'fitz',
        'PyPDF2',
        'reportlab',
        'reportlab.lib.pagesizes',
        'reportlab.pdfgen.canvas',
        'ui',
        'ui.app',
        'ui.quick_mode',
        'core',
        'core.watermark_engine',
        'core.image_processor',
        'core.pdf_processor',
        'core.watermark_renderer',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Fillico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
)
