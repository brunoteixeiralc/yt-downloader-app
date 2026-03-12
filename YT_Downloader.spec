# -*- mode: python ; coding: utf-8 -*-
import os

# Caminhos para os binários — sobrescritos por variáveis de ambiente no CI
YT_DLP_BIN = os.environ.get('YT_DLP_PATH', '/opt/homebrew/bin/yt-dlp')
FFMPEG_BIN  = os.environ.get('FFMPEG_PATH', '/opt/homebrew/bin/ffmpeg')

a = Analysis(
    ['yt_downloader_gui.py'],
    pathex=[],
    binaries=[
        (YT_DLP_BIN, '.'),
        (FFMPEG_BIN, '.'),
    ],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YT Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,      # Não comprime — evita problemas com Gatekeeper no macOS
    console=False,  # Sem janela de terminal
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
    upx=False,
    upx_exclude=[],
    name='YT Downloader',
)

app = BUNDLE(
    coll,
    name='YT Downloader.app',
    icon=None,
    bundle_identifier='com.ytdownloader.app',
    version='1.2.0',
    info_plist={
        'CFBundleName': 'YT Downloader',
        'CFBundleDisplayName': 'YT Downloader',
        'CFBundleGetInfoString': 'Baixador de vídeos do YouTube',
        'CFBundleShortVersionString': '1.2.0',
        'CFBundleVersion': '1.2.0',
        'NSHighResolutionCapable': True,
        'NSHumanReadableCopyright': 'Copyright © 2025',
    },
)
