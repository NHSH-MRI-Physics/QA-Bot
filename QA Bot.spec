# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = []
datas += collect_data_files('randfacts')


a = Analysis(
    ['GUI.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=['scipy.signal', 'cv2', 'email.mime', 'email.mime.multipart', 'email.mime.text', 'skimage', 'skimage.feature', 'docopt', 'imutils', 'colorlog', 'skimage.segmentation'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='QA Bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='QA Bot',
)
