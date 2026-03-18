"""
훅 헬퍼: stdin JSON에서 file_path 읽어 app/ 경로인지 확인
exit(0) → app/ 경로 → 테스트 실행
exit(1) → 비대상 경로 → 건너뜀
"""
import json
import sys

try:
    d = json.load(sys.stdin)
    f = d.get("tool_input", {}).get("file_path", "")
    normalized = f.replace("\\", "/")
    if "/app/" in normalized:
        sys.exit(0)
    else:
        sys.exit(1)
except Exception:
    sys.exit(1)
