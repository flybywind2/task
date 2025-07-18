# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 현재 디렉토리 경로
current_dir = Path(os.getcwd())

# 정적 파일 및 템플릿 경로 설정
datas = [
    (str(current_dir / 'static'), 'static'),
    (str(current_dir / 'templates'), 'templates'),
    (str(current_dir / 'app'), 'app'),
]

# 숨겨진 imports (PyInstaller가 자동으로 감지하지 못하는 모듈들)
hiddenimports = [
    'uvicorn',
    'uvicorn.workers',
    'uvicorn.workers.uvicorn_worker',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.websockets',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'fastapi.staticfiles',
    'fastapi.templating',
    'sqlalchemy',
    'sqlalchemy.dialects',
    'sqlalchemy.dialects.sqlite',
    'jinja2',
    'jinja2.ext',
    'aiofiles',
    'multipart',
    'multipart.multipart',
    'starlette',
    'starlette.applications',
    'starlette.middleware',
    'starlette.routing',
    'starlette.staticfiles',
    'starlette.templating',
    'starlette.responses',
    'pydantic',
    'pydantic.fields',
    'pydantic.validators',
    'alembic',
    'alembic.config',
    'email_validator',
    'pystray',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'win10toast',
    'win32gui',
    'win32con',
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='Todo2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # CMD 창 숨기기
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 파일이 있다면 여기에 경로 지정
)