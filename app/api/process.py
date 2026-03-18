"""
process.py — 처리 시작 + SSE 진행상태 스트리밍
POST /api/process       : 처리 시작
GET  /api/progress/{job_id} : SSE 스트리밍
GET  /api/result/{job_id}   : 처리 결과 JSON
GET  /api/result/{job_id}/{pdf_name}/{table_type} : 특정 테이블 미리보기
"""

import asyncio
import json
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core import store as job_store
from app.core.pipeline import run_pipeline

router = APIRouter()


class ProcessRequest(BaseModel):
    job_id: str
    selected_tables: Optional[List[str]] = None


@router.post("/process")
async def start_process(req: ProcessRequest, background_tasks: BackgroundTasks):
    """처리 시작"""
    job = job_store.get_job(req.job_id)
    if not job:
        raise HTTPException(404, "job not found")

    if job["status"] == "processing":
        raise HTTPException(409, "이미 처리 중입니다.")

    if not job["files"].get("mapping"):
        raise HTTPException(400, "매핑 파일을 먼저 업로드하세요.")

    if not job["files"].get("pdfs"):
        raise HTTPException(400, "PDF 파일을 먼저 업로드하세요.")

    # 선택 테이블 업데이트
    if req.selected_tables:
        valid = {"S00022", "S00026", "S00027", "S00028"}
        job["selected_tables"] = [t for t in req.selected_tables if t in valid]

    # SSE 큐 초기화
    job_store.get_or_create_queue(req.job_id)

    # 백그라운드에서 파이프라인 실행
    background_tasks.add_task(run_pipeline, req.job_id)

    return {"status": "started", "job_id": req.job_id}


@router.get("/progress/{job_id}")
async def stream_progress(job_id: str):
    """SSE 진행상태 스트리밍"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")

    queue = job_store.get_or_create_queue(job_id)

    async def event_generator():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                except asyncio.TimeoutError:
                    # keep-alive
                    yield ": keep-alive\n\n"
                    continue

                if event is None:
                    # 종료 신호
                    yield f"data: {json.dumps({'type': 'END'})}\n\n"
                    break

                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    """전체 처리 결과 JSON"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")

    pdf_results = {}
    for pdf_name, r in job.get("pdf_results", {}).items():
        pdf_results[pdf_name] = {
            "status": r["status"],
            "mapping_entries": r.get("mapping_entries", []),
            "table_counts": {
                t: r["tables"].get(t, {}).get("count", 0)
                for t in r.get("tables", {})
            },
            "xlsx_files": r.get("xlsx_files", {}),
            "gt_summaries": r.get("gt_summaries", {}),
            "error": r.get("error"),
            "preview": {
                t: {
                    "headers": p.get("headers", []),
                    "count": p.get("count", 0),
                }
                for t, p in r.get("preview", {}).items()
            },
        }

    return {
        "job_id": job_id,
        "status": job["status"],
        "pdf_count": len(job["files"]["pdfs"]),
        "done_count": sum(1 for r in pdf_results.values() if r["status"] in ("done", "new")),
        "error_count": sum(1 for r in pdf_results.values() if r["status"] == "error"),
        "pdf_results": pdf_results,
    }


@router.get("/result/{job_id}/{pdf_name}/{table_type}")
async def get_table_preview(job_id: str, pdf_name: str, table_type: str):
    """특정 PDF × 테이블 미리보기 상세"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")

    pdf_result = job.get("pdf_results", {}).get(pdf_name)
    if not pdf_result:
        raise HTTPException(404, f"PDF 결과 없음: {pdf_name}")

    preview = pdf_result.get("preview", {}).get(table_type)
    if not preview:
        raise HTTPException(404, f"테이블 결과 없음: {table_type}")

    return preview
