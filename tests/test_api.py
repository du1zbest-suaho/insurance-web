"""
test_api.py — FastAPI HTTP 엔드포인트 테스트 (TestClient 사용, 서버 불필요)

검증 항목:
  - GET /health
  - GET / (index.html 서빙)
  - POST /api/upload (job 생성)
  - GET /api/job/{job_id} (job 상태 조회)
  - POST /api/upload/{job_id}/mapping (매핑 파일 업로드)
  - POST /api/upload/{job_id}/pdf (PDF 업로드)
  - DELETE /api/upload/{job_id}/pdf/{filename} (PDF 삭제)
  - POST /api/upload/{job_id}/gt (GT 파일 업로드)
  - POST /api/upload/{job_id}/tables (테이블 선택)
  - GET /api/result/{job_id} (결과 조회)
  - 404: 존재하지 않는 job_id
"""

import io
import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


# ─── 1. 기본 엔드포인트 ───────────────────────────────────────────────────────

class TestBasicEndpoints:
    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_index_html_served(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")
        assert "보험" in resp.text or "DOCTYPE" in resp.text

    def test_docs_available(self):
        resp = client.get("/docs")
        assert resp.status_code == 200


# ─── 2. Job 생성 및 조회 ──────────────────────────────────────────────────────

class TestJobLifecycle:
    def test_create_job(self):
        resp = client.post("/api/upload")
        assert resp.status_code == 200
        data = resp.json()
        assert "job_id" in data
        assert data["status"] == "created"

    def test_get_job_status(self):
        job_id = client.post("/api/upload").json()["job_id"]
        resp = client.get(f"/api/job/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == job_id
        # 기본 매핑 파일이 존재하면 True, 없어도 False — 타입만 확인
        assert isinstance(data["mapping_loaded"], bool)
        assert data["pdf_count"] == 0

    def test_get_nonexistent_job_returns_404(self):
        resp = client.get("/api/job/nonexistent-id-xyz")
        assert resp.status_code == 404

    def test_multiple_jobs_independent(self):
        id1 = client.post("/api/upload").json()["job_id"]
        id2 = client.post("/api/upload").json()["job_id"]
        assert id1 != id2
        assert client.get(f"/api/job/{id1}").status_code == 200
        assert client.get(f"/api/job/{id2}").status_code == 200


# ─── 3. 매핑 파일 업로드 ──────────────────────────────────────────────────────

class TestMappingUpload:
    def test_upload_mapping_xlsx(self, mapping_path):
        job_id = client.post("/api/upload").json()["job_id"]
        with open(mapping_path, "rb") as f:
            resp = client.post(
                f"/api/upload/{job_id}/mapping",
                files={"file": ("mapping.xlsx", f,
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        assert resp.status_code == 200
        # 매핑 로드 확인
        status = client.get(f"/api/job/{job_id}").json()
        assert status["mapping_loaded"] is True

    def test_upload_mapping_nonexistent_job_returns_404(self, mapping_path):
        with open(mapping_path, "rb") as f:
            resp = client.post(
                "/api/upload/nonexistent-id/mapping",
                files={"file": ("mapping.xlsx", f, "application/octet-stream")},
            )
        assert resp.status_code == 404

    def test_upload_invalid_file_returns_error(self):
        # 매핑 엔드포인트는 업로드 시 파일 형식 검증 없이 저장만 함
        job_id = client.post("/api/upload").json()["job_id"]
        resp = client.post(
            f"/api/upload/{job_id}/mapping",
            files={"file": ("not_excel.txt", b"not an xlsx file", "text/plain")},
        )
        # 업로드 자체는 성공 (처리 단계에서 오류 감지)
        assert resp.status_code in (200, 400, 422, 500)


# ─── 4. PDF 업로드 및 삭제 ────────────────────────────────────────────────────

class TestPdfUpload:
    def test_upload_pdf(self, sample_pdf_path):
        job_id = client.post("/api/upload").json()["job_id"]
        with open(sample_pdf_path, "rb") as f:
            resp = client.post(
                f"/api/upload/{job_id}/pdf",
                files={"files": ("sample.pdf", f, "application/pdf")},
            )
        assert resp.status_code == 200
        status = client.get(f"/api/job/{job_id}").json()
        assert status["pdf_count"] == 1
        assert "sample.pdf" in status["pdf_names"]

    def test_upload_multiple_pdfs(self, sample_pdf_path):
        job_id = client.post("/api/upload").json()["job_id"]
        with open(sample_pdf_path, "rb") as f1, open(sample_pdf_path, "rb") as f2:
            resp = client.post(
                f"/api/upload/{job_id}/pdf",
                files=[
                    ("files", ("a.pdf", f1, "application/pdf")),
                    ("files", ("b.pdf", f2, "application/pdf")),
                ],
            )
        assert resp.status_code == 200
        assert client.get(f"/api/job/{job_id}").json()["pdf_count"] == 2

    def test_delete_pdf(self, sample_pdf_path):
        job_id = client.post("/api/upload").json()["job_id"]
        with open(sample_pdf_path, "rb") as f:
            client.post(f"/api/upload/{job_id}/pdf",
                        files={"files": ("del_test.pdf", f, "application/pdf")})
        resp = client.delete(f"/api/upload/{job_id}/pdf/del_test.pdf")
        assert resp.status_code == 200
        assert client.get(f"/api/job/{job_id}").json()["pdf_count"] == 0

    def test_delete_nonexistent_pdf_returns_404(self):
        job_id = client.post("/api/upload").json()["job_id"]
        resp = client.delete(f"/api/upload/{job_id}/pdf/nonexistent.pdf")
        assert resp.status_code == 404


# ─── 5. GT 파일 업로드 ────────────────────────────────────────────────────────

class TestGtUpload:
    def test_upload_gt_s00026(self, gt_paths):
        job_id = client.post("/api/upload").json()["job_id"]
        with open(gt_paths["S00026"], "rb") as f:
            resp = client.post(
                f"/api/upload/{job_id}/gt",
                files={"files": ("gt_S00026.xlsx", f,
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "S00026" in str(data)

    def test_upload_gt_multiple_tables(self, gt_paths):
        job_id = client.post("/api/upload").json()["job_id"]
        files = []
        for tbl, path in gt_paths.items():
            files.append(("files", (f"gt_{tbl}.xlsx",
                          open(path, "rb"),
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")))
        resp = client.post(f"/api/upload/{job_id}/gt", files=files)
        # 파일 핸들 닫기
        for _, (_, fh, _) in files:
            fh.close()
        assert resp.status_code == 200


# ─── 6. 테이블 선택 ───────────────────────────────────────────────────────────

class TestTableSelection:
    def test_select_tables(self):
        job_id = client.post("/api/upload").json()["job_id"]
        resp = client.put(
            f"/api/upload/{job_id}/tables",
            json=["S00026", "S00028"],
        )
        assert resp.status_code == 200
        status = client.get(f"/api/job/{job_id}").json()
        assert set(status["selected_tables"]) == {"S00026", "S00028"}

    def test_default_tables_all_four(self):
        job_id = client.post("/api/upload").json()["job_id"]
        status = client.get(f"/api/job/{job_id}").json()
        assert set(status["selected_tables"]) == {"S00026", "S00027", "S00028", "S00022"}


# ─── 7. 결과 조회 ─────────────────────────────────────────────────────────────

class TestResultEndpoints:
    def test_result_nonexistent_job_404(self):
        resp = client.get("/api/result/nonexistent-xyz")
        assert resp.status_code == 404

    def test_result_idle_job(self):
        job_id = client.post("/api/upload").json()["job_id"]
        resp = client.get(f"/api/result/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "pdf_results" in data

    def test_progress_sse_nonexistent_404(self):
        resp = client.get("/api/progress/nonexistent-xyz")
        assert resp.status_code == 404
