# -*- mode: python ; coding: utf-8 -*-
"""
build.spec — PyInstaller onedir 빌드 설정

빌드 명령:
    pyinstaller build.spec

결과: dist/insurance-extractor/ 폴더 → zip으로 배포
더블클릭: insurance-extractor.exe
"""

import os

block_cipher = None

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("app/static",        "app/static"),
        ("app/rules",         "app/rules"),
        ("app/data/defaults", "app/data/defaults"),
    ],
    hiddenimports=[
        # uvicorn 내부 모듈
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        # fastapi / starlette
        "fastapi",
        "starlette",
        "starlette.routing",
        "starlette.middleware",
        # 데이터 처리
        "pdfplumber",
        "openpyxl",
        "pandas",
        "pandas.io.formats.style",
        # PyMuPDF
        "fitz",
        # 파일 업로드
        "multipart",
        "python_multipart",
        # 기타
        "email.mime.multipart",
        "anyio",
        "anyio._backends._asyncio",
        "h11",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "scipy",
        "IPython",
        "jupyter",
        "notebook",
        "pytest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="insurance-extractor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # 콘솔창 숨김
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # TODO: 아이콘 추가 시 "app/static/icon.ico"
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="insurance-extractor",
)
