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

excluded_prefixes = (
    "babel"
    "Cython",
    "matplotlib",
    "mkl_",
    "numpy",
    "pandas",
    "scipy",
    "sqlalchemy"
    "zmq",
)

a.binaries = [x for x in a.binaries if not any(
    [x[0].startswith(prefix) for prefix in excluded_prefixes])]

a.binaries = a.binaries - TOC([
 ('sqlite3.dll', None, None),
 ('tcl85.dll', None, None),
 ('tk85.dll', None, None),
 ('tcl86t.dll', None, None),
 ('tk86t.dll', None, None),
 ('_sqlite3', None, None),
 ('_ssl', None, None),
 ('_tkinter', None, None)])

 # icon
 a.datas += [('icon-32.png','resources\\icon-32.png','DATA')]

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
