"""
main.py — FastAPI 진입점
Phase 5: 서버 기동 후 Edge 자동오픈 (webbrowser.open)
"""

import os
import sys
import threading
import time
import webbrowser

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api import upload, process, download

app = FastAPI(title="보험 사업방법서 추출기", version="1.0.0")

app.include_router(upload.router, prefix="/api")
app.include_router(process.router, prefix="/api")
app.include_router(download.router, prefix="/api")

# PyInstaller frozen 환경에서는 _MEIPASS/app 사용 (datas: app/static → _internal/app/static)
if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.join(sys._MEIPASS, "app")
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_STATIC_DIR = os.path.join(_BASE_DIR, "static")


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = os.path.join(_STATIC_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/health")
async def health():
    return {"status": "ok"}



# ─── 브라우저 자동오픈 ─────────────────────────────────────────────────────────

def _open_browser(url: str, delay: float = 1.5) -> None:
    """백그라운드 스레드에서 Edge 우선으로 브라우저 오픈"""
    time.sleep(delay)
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for edge in edge_paths:
        if os.path.exists(edge):
            webbrowser.register("edge", None, webbrowser.BackgroundBrowser(edge))
            webbrowser.get("edge").open(url)
            return
    webbrowser.open(url)


@app.on_event("startup")
async def startup_event():
    # INSURANCE_NO_BROWSER=1 로 자동오픈 비활성화 가능 (개발·테스트용)
    if os.environ.get("INSURANCE_NO_BROWSER") == "1":
        return
    port = int(os.environ.get("INSURANCE_PORT", "8765"))
    url = f"http://127.0.0.1:{port}"
    t = threading.Thread(target=_open_browser, args=(url,), daemon=True)
    t.start()
