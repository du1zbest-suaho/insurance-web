"""
store.py — 인메모리 Job 상태 저장소 + SSE 이벤트 큐
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

# {job_id: job_state}
jobs: Dict[str, Dict[str, Any]] = {}

# {job_id: asyncio.Queue} — SSE 스트리밍용
event_queues: Dict[str, asyncio.Queue] = {}

# ─── 기본값 파일 경로 ─────────────────────────────────────────────────────────
# PyInstaller onedir 실행 시: sys._MEIPASS/_internal 기준
# 개발 실행 시: 프로젝트 루트 app/data/defaults 기준
def _default_data_dir() -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    return os.path.join(base, "app", "data", "defaults")


def _build_default_files() -> Dict[str, Any]:
    d = _default_data_dir()
    mapping = os.path.join(d, "mapping.xlsx")
    gt_dir = os.path.join(d, "gt")
    tmpl_dir = os.path.join(d, "templates")

    gt_map = {
        "S00026": os.path.join(gt_dir, "판매중_가입나이정보_0312.xlsx"),
        "S00027": os.path.join(gt_dir, "판매중_보기납기정보_0312.xlsx"),
        "S00028": os.path.join(gt_dir, "판매중_납입주기정보_0312.xlsx"),
        "S00022": os.path.join(gt_dir, "판매중_보기개시나이정보_0312.xlsx"),
    }
    tmpl_map = {
        "S00026": os.path.join(tmpl_dir, "template_S00026.xlsx"),
        "S00027": os.path.join(tmpl_dir, "template_S00027.xlsx"),
        "S00028": os.path.join(tmpl_dir, "template_S00028.xlsx"),
        "S00022": os.path.join(tmpl_dir, "template_S00022.xlsx"),
    }

    return {
        "mapping": mapping if os.path.exists(mapping) else None,
        "gt": {k: v for k, v in gt_map.items() if os.path.exists(v)},
        "templates": {k: v for k, v in tmpl_map.items() if os.path.exists(v)},
    }


def create_job() -> str:
    job_id = str(uuid.uuid4())
    defaults = _build_default_files()
    jobs[job_id] = {
        "job_id": job_id,
        "created_at": datetime.now().isoformat(),
        "files": {
            "mapping": defaults["mapping"],    # 기본값: app/data/defaults/mapping.xlsx
            "templates": defaults["templates"],# 기본값: app/data/defaults/templates/
            "pdfs": [],                        # [{name, path}, ...]
            "gt": defaults["gt"],              # 기본값: app/data/defaults/gt/
        },
        "selected_tables": ["S00026", "S00027", "S00028", "S00022"],
        "status": "idle",          # idle | processing | done | error
        "pdf_results": {},         # {pdf_name: PdfResult}
        "error": None,
    }
    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    return jobs.get(job_id)


def get_or_create_queue(job_id: str) -> asyncio.Queue:
    if job_id not in event_queues:
        event_queues[job_id] = asyncio.Queue()
    return event_queues[job_id]


async def emit(job_id: str, event: Dict[str, Any]) -> None:
    """SSE 이벤트 발행"""
    q = event_queues.get(job_id)
    if q:
        await q.put(event)


def emit_sync(job_id: str, event: Dict[str, Any]) -> None:
    """동기 컨텍스트에서 SSE 이벤트 발행 (별도 스레드에서 호출)"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(emit(job_id, event), loop)
    except RuntimeError:
        pass
