# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from glob import glob
import os

block_cipher = None

cwd = os.getcwd()

a = Analysis(['src/main.py'],
             pathex=[cwd],
             binaries=[],
             datas=[(Path("img/lola_toolbox-icon_64px.png"), Path("img")),
                    ("src", ".")],
             hiddenimports=["cryptncompress", "requests"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
