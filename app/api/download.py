"""
download.py — 결과 파일 다운로드
GET /api/download/{job_id}/{filename}   : 단일 xlsx
GET /api/download/{job_id}/all.zip      : 전체 ZIP
"""

import io
import os
import zipfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.core import store as job_store

router = APIRouter()

TEMP_BASE = os.path.join(os.path.dirname(__file__), "../../temp")


def _get_output_dir(job_id: str, pdf_name: str) -> str:
    job = job_store.get_job(job_id)
    if not job:
        return ""
    for pdf_info in job["files"]["pdfs"]:
        if pdf_info["name"] == pdf_name:
            return os.path.join(os.path.dirname(pdf_info["path"]), "output")
    return ""


@router.get("/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str):
    """단일 xlsx 다운로드"""
    if filename == "all.zip":
        return await download_all_zip(job_id)

    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")

    # 모든 output 디렉터리에서 파일 탐색
    for pdf_info in job["files"]["pdfs"]:
        output_dir = os.path.join(os.path.dirname(pdf_info["path"]), "output")
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            return FileResponse(
                file_path,
                filename=filename,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    raise HTTPException(404, f"파일 없음: {filename}")


async def download_all_zip(job_id: str):
    """전체 결과 ZIP 다운로드"""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for pdf_info in job["files"]["pdfs"]:
            output_dir = os.path.join(os.path.dirname(pdf_info["path"]), "output")
            if not os.path.isdir(output_dir):
                continue
            for fname in os.listdir(output_dir):
                if fname.endswith(".xlsx"):
                    fpath = os.path.join(output_dir, fname)
                    zf.write(fpath, fname)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=results.zip"},
    )
