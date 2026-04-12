# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


SAMPLE_ROSTER_CONTENT = """4-2-3-1
# starter,position,name,number
1,GK,Hugo Lloris,1
1,LB,Theo Hernandez,22
1,LCB,Raphael Varane,4
1,RCB,Benjamin Pavard,2
1,RB,Jules Kounde,5
1,RDM,Aurelien Tchouameni,8
1,LDM,Adrien Rabiot,14
1,LAM,Kylian Mbappe,10
1,AM,Antoine Griezmann,7
1,RAM,Ousmane Dembele,11
1,ST,Olivier Giroud,9
"""

project_dir = Path(globals().get("SPECPATH", ".")).resolve()
roster_dir = project_dir / "roster"
sample_roster_path = roster_dir / "sample_roster.txt"
assets_dir = project_dir / "assets"
preferred_icon = assets_dir / "thumbnail.ico"
icon_candidates = sorted(assets_dir.glob("*.ico"))
icon_path = str(preferred_icon if preferred_icon.exists() else icon_candidates[0]) if (preferred_icon.exists() or icon_candidates) else None

roster_dir.mkdir(parents=True, exist_ok=True)
if not sample_roster_path.exists():
    sample_roster_path.write_text(SAMPLE_ROSTER_CONTENT, encoding="utf-8")


a = Analysis(
    ['program.py'],
    pathex=[],
    binaries=[],
    datas=[('field.png', '.'), ('roster', 'roster'), ('assets', 'assets')],
    hiddenimports=['pygame'],
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
    name='TacticalPad',
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
    icon=icon_path,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TacticalPad',
)
