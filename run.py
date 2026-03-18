"""
run.py — 실행 진입점
- 개발: python run.py  (reload=True)
- exe : insurance-extractor.exe  (PyInstaller frozen, reload=False)
"""

import os
import socket
import sys


def find_free_port(start: int = 8765, max_tries: int = 100) -> int:
    """사용 가능한 포트 탐색 (8765 → 8766 → ...)"""
    for port in range(start, start + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start


def main():
    import uvicorn

    is_frozen = getattr(sys, "frozen", False)
    port = find_free_port()
    os.environ["INSURANCE_PORT"] = str(port)

    if is_frozen:
        # PyInstaller exe 환경: reload 불가, app 객체 직접 전달 (문자열 import 불가)
        sys.path.insert(0, sys._MEIPASS)
        # console=False → stdout/stderr == None → uvicorn logging 오류 방지
        import io
        if sys.stdout is None:
            sys.stdout = io.StringIO()
        if sys.stderr is None:
            sys.stderr = io.StringIO()
        from app.main import app as asgi_app
        uvicorn.run(
            asgi_app,
            host="127.0.0.1",
            port=port,
            reload=False,
            log_level="warning",
            log_config=None,   # console=False 시 formatter 오류 방지
            access_log=False,
        )
    else:
        # 개발 환경
        os.environ.setdefault("INSURANCE_NO_BROWSER", "1")  # 개발 중 자동오픈 OFF
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=port,
            reload=True,
            reload_dirs=["app"],
            log_level="info",
        )


if __name__ == "__main__":
    main()
