# -*- mode: python ; coding: utf-8 -*-

import sys

block_cipher = None

# Exclude platform-specific packages that don't apply to the build host
excludes = []
if sys.platform != 'win32':
    excludes.extend([
        'pywin32', 'pypiwin32', 'win32api', 'win32com',
        'windows_curses', 'pywintypes', 'win32security',
    ])

a = Analysis(['yojenkins/__main__.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[
                 'yaml',
                 'click',
                 'click_help_colors',
                 'coloredlogs',
                 'defusedxml',
                 'defusedxml.ElementTree',
                 'json2xml',
                 'json2xml.json2xml',
                 'jenkins',
                 'requests_futures',
                 'requests_futures.sessions',
                 'tomli',
                 'tomli_w',
                 'xmltodict',
                 'yaspin',
                 'yaspin.spinners',
                 'pkg_resources.py2_warn',
             ],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=excludes,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += Tree('./yojenkins/resources', prefix='resources/')
a.datas += Tree('./yojenkins/yo_jenkins/groovy_scripts', prefix='yo_jenkins/groovy_scripts/')

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='yojenkins',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='yojenkins')
