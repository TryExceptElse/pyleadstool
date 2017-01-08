# -*- mode: python -*-

block_cipher = None


a = Analysis(['leadmacro.py'],
             pathex=['C:\\Users\\user1\\PycharmProjects\\pyleadstool'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.binaries = [x for x in a.binaries if not x[0].startswith("scipy")]

a.binaries = [x for x in a.binaries if not x[0].startswith("zmq")]

a.binaries = [x for x in a.binaries if not x[0].startswith("matplotlib")]

a.binaries = [x for x in a.binaries if not x[0].startswith("numpy")]

a.binaries = [x for x in a.binaries if not x[0].startswith("pandas")]

a.binaries = a.binaries - TOC([
 ('sqlite3.dll', None, None),
 ('tcl85.dll', None, None),
 ('tk85.dll', None, None),
 ('_sqlite3', None, None),
 ('_ssl', None, None),
 ('_tkinter', None, None)])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='leadmacro',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='leadmacro')
