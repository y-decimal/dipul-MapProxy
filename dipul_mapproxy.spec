# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for DiPul MapProxy GUI

import sys
import os
from pathlib import Path

# Get the project root - use the directory where this spec file is located
project_root = Path(os.getcwd())


a = Analysis(
    [str(project_root / "launch-gui.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / "gui"), "gui"),
        (str(project_root / "mapproxy_config"), "mapproxy_config"),
    ],
    hiddenimports=[
        "pystray",
        "pystray._win32" if sys.platform == "win32" else "",
        "pystray._xlib" if sys.platform == "linux" else "",
        "pystray._darwin" if sys.platform == "darwin" else "",
        "PIL",
        "mapproxy",
        "pyproj",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
    optimize=0,
)

# Filter out empty strings from hiddenimports
a.hiddenimports = [imp for imp in a.hiddenimports if imp]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="dipul-mapproxy",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
