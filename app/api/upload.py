"""
upload.py — 파일 업로드 API
POST /api/upload  : job 생성 + 파일 저장
POST /api/upload/{job_id} : 기존 job에 파일 추가
GET  /api/job/{job_id}   : job 상태 조회
"""

import os
import shutil
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.core import store as job_store

router = APIRouter()

TEMP_BASE = os.path.join(os.path.dirname(__file__), "../../temp")

# 템플릿 파일명 → 테이블 타입 매핑
TEMPLATE_TABLE_MAP = {
    "S00026": "S00026",
    "S00027": "S00027",
    "S00028": "S00028",
    "S00022": "S00022",
}


def _detect_table_type(filename: str) -> str:
    """파일명에서 테이블 타입 감지"""
    for key in TEMPLATE_TABLE_MAP:
        if key in filename:
            return TEMPLATE_TABLE_MAP[key]
    return ""


def _save_upload(upload_file: UploadFile, dest_path: str) -> None:
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)


@router.post("/upload")
async def create_upload():
    """새 job 생성 (job_id 반환)"""
    job_id = job_store.create_job()
    job_dir = os.path.join(TEMP_BASE, job_id)
    os.makedirs(job_dir, exist_ok=True)
    # SSE 큐 미리 생성
    job_store.get_or_create_queue(job_id)
    return {"job_id": job_id, "status": "created"}


@router.post("/upload/{job_id}/mapping")
async def upload_mapping(job_id: str, file: UploadFile = File(...)):
    """매핑 xlsx 업로드"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")

    job_dir = os.path.join(TEMP_BASE, job_id)
    dest = os.path.join(job_dir, "mapping.xlsx")
    _save_upload(file, dest)
    job["files"]["mapping"] = dest

    return {"status": "ok", "file": "mapping.xlsx"}


@router.post("/upload/{job_id}/template")
async def upload_template(job_id: str, file: UploadFile = File(...)):
    """템플릿 xlsx 업로드 (파일명으로 테이블 타입 자동 감지)"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")

    table_type = _detect_table_type(file.filename)
    if not table_type:
        raise HTTPException(400, f"테이블 타입을 파일명에서 감지할 수 없습니다: {file.filename}")

    job_dir = os.path.join(TEMP_BASE, job_id, "templates")
    dest = os.path.join(job_dir, file.filename)
    _save_upload(file, dest)
    job["files"]["templates"][table_type] = dest

    return {"status": "ok", "table_type": table_type, "file": file.filename}


@router.post("/upload/{job_id}/pdf")
async def upload_pdfs(job_id: str, files: List[UploadFile] = File(...)):
    """PDF 파일 업로드 (복수)"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")

    job_dir = os.path.join(TEMP_BASE, job_id, "pdfs")
    uploaded = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
        dest = os.path.join(job_dir, file.filename)
        _save_upload(file, dest)
        # 중복 방지
        existing = [p["name"] for p in job["files"]["pdfs"]]
        if file.filename not in existing:
            job["files"]["pdfs"].append({"name": file.filename, "path": dest})
        uploaded.append(file.filename)

    return {"status": "ok", "uploaded": uploaded, "total_pdfs": len(job["files"]["pdfs"])}


@router.get("/job/{job_id}")
async def get_job(job_id: str):
    """job 상태 조회"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "mapping_loaded": job["files"]["mapping"] is not None,
        "templates_loaded": list(job["files"]["templates"].keys()),
        "pdf_count": len(job["files"]["pdfs"]),
        "pdf_names": [p["name"] for p in job["files"]["pdfs"]],
        "selected_tables": job["selected_tables"],
        "pdf_results": {
            name: {
                "status": r["status"],
                "table_counts": {t: r["tables"].get(t, {}).get("count", 0) for t in r["tables"]},
                "xlsx_files": list(r.get("xlsx_files", {}).values()),
                "error": r.get("error"),
                "mapping_found": len(r.get("mapping_entries", [])) > 0,
            }
            for name, r in job.get("pdf_results", {}).items()
        },
    }


@router.delete("/upload/{job_id}/pdf/{filename}")
async def remove_pdf(job_id: str, filename: str):
    """PDF 파일 제거"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    before = len(job["files"]["pdfs"])
    job["files"]["pdfs"] = [p for p in job["files"]["pdfs"] if p["name"] != filename]
    if len(job["files"]["pdfs"]) == before:
        raise HTTPException(404, f"pdf not found: {filename}")
    return {"status": "ok"}


@router.put("/upload/{job_id}/tables")
async def set_selected_tables(job_id: str, tables: List[str]):
    """선택 테이블 업데이트"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    valid = {"S00022", "S00026", "S00027", "S00028"}
    job["selected_tables"] = [t for t in tables if t in valid]
    return {"status": "ok", "selected_tables": job["selected_tables"]}

# GT 파일명 → 테이블 타입 매핑
GT_TABLE_MAP = {
    '가입나이': 'S00026',
    '보기납기': 'S00027',
    '납입주기': 'S00028',
    '보기개시나이': 'S00022',
    'S00026': 'S00026',
    'S00027': 'S00027',
    'S00028': 'S00028',
    'S00022': 'S00022',
}


def _detect_gt_table_type(filename: str) -> str:
    for kw, table_type in GT_TABLE_MAP.items():
        if kw in filename:
            return table_type
    return ''


@router.post('/upload/{job_id}/gt')
async def upload_gt(job_id: str, files: List[UploadFile] = File(...)):
    """GT(판매중_*.xlsx) 파일 업로드 — 파일명으로 테이블 타입 자동 감지"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, 'job not found')

    job_dir = os.path.join(TEMP_BASE, job_id, 'gt')
    uploaded = []
    for file in files:
        table_type = _detect_gt_table_type(file.filename)
        if not table_type:
            continue
        dest = os.path.join(job_dir, file.filename)
        _save_upload(file, dest)
        job['files']['gt'][table_type] = dest
        uploaded.append({'table_type': table_type, 'file': file.filename})

    return {'status': 'ok', 'uploaded': uploaded, 'gt_loaded': list(job['files']['gt'].keys())}

