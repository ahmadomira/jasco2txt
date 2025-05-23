# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Get the current directory (where the spec file is located)
spec_root = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['jasco2txt_gui.py'],
    pathex=[spec_root],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'numpy',
        'struct',
        'threading',
        'pathlib',
        'json'
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
    name='Jasco2TXT-Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app, True for console app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here: icon='icon.ico'
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Jasco2TXT-Converter.app',
        icon=None,  # You can add an icon file here: icon='icon.icns'
        bundle_identifier='com.jasco2txt.converter',
        info_plist={
            'CFBundleName': 'Jasco2TXT Converter',
            'CFBundleDisplayName': 'Jasco2TXT Converter',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        }
    )
