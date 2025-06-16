# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/gui/main.py'],  
    pathex=['.', 'src'],  
    binaries=[],
    datas=[('src/gui/resources/*', 'gui/resources')],
    hiddenimports=[
    'utils.config_handler',
    'utils.xml_parser',
    'utils.xpath_builder',
    'utils.csv_export',
    'gui.controller',
    'gui.widgets.path_manager_window',
    'gui.resources.ui.XMLuvation_ui',
    'gui.resources.ui.CustomPathsManager_ui',
    'gui.resources.qrc.xmluvation_resources_rc'
    ],
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
    name='XMLuvation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='XMLuvation',
)
