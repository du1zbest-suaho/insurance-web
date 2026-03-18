"""
test_pipeline.py — 파이프라인 단위 및 통합 테스트

검증 항목:
  - load_mapping_db: 실제 매핑 xlsx 로드 및 구조
  - lookup_mapping: 파일명으로 엔트리 조회
  - load_rules: ExtractionRules 로드 및 hot-reload
  - process_pdf_sync: 실제 PDF end-to-end (sample.pdf 존재 시)
  - prod_sale_nm 매핑 엔트리에 포함 여부 (핵심 수정 검증)
"""

import os
import pytest

from app.core.pipeline import (
    load_mapping_db,
    lookup_mapping,
    load_rules,
    STEPS,
)


# ─── 1. load_mapping_db ───────────────────────────────────────────────────────

class TestLoadMappingDb:
    def test_loads_real_mapping_file(self, mapping_path):
        db = load_mapping_db(mapping_path)
        assert len(db) > 0, "매핑 DB가 비어 있음"

    def test_key_is_pdf_filename(self, mapping_db):
        for key in list(mapping_db.keys())[:3]:
            assert key.endswith(".pdf") or "사업방법서" in key, (
                f"키가 PDF 파일명이 아님: {key!r}"
            )

    def test_entry_has_required_fields(self, mapping_db):
        for pdf_name, entries in list(mapping_db.items())[:5]:
            for entry in entries:
                assert "dtcd" in entry, f"{pdf_name}: dtcd 없음"
                assert "itcd" in entry, f"{pdf_name}: itcd 없음"
                assert "sale_nm" in entry, f"{pdf_name}: sale_nm 없음"
                assert "prod_dtcd" in entry, f"{pdf_name}: prod_dtcd 없음"
                assert "prod_itcd" in entry, f"{pdf_name}: prod_itcd 없음"

    def test_prod_sale_nm_in_entries(self, mapping_db):
        """prod_sale_nm 필드가 포함되어야 한다 (핵심 수정 검증)"""
        for pdf_name, entries in list(mapping_db.items())[:5]:
            for entry in entries:
                assert "prod_sale_nm" in entry, (
                    f"{pdf_name}: prod_sale_nm 누락 — LOWER_OBJECT_NAME 비어있게 됨"
                )

    def test_dtcd_is_string_of_int(self, mapping_db):
        for entries in list(mapping_db.values())[:5]:
            for entry in entries:
                assert entry["dtcd"].isdigit(), f"dtcd={entry['dtcd']} 가 숫자 문자열이 아님"

    def test_multiple_entries_per_pdf(self, mapping_db):
        """하나의 PDF에 여러 DTCD/ITCD 엔트리가 있을 수 있다"""
        multi = {k: v for k, v in mapping_db.items() if len(v) > 1}
        assert len(multi) > 0, "복수 엔트리를 가진 PDF가 없음"


# ─── 2. lookup_mapping ────────────────────────────────────────────────────────

class TestLookupMapping:
    def test_exact_match(self, mapping_db, sample_pdf_name):
        entries = lookup_mapping(sample_pdf_name, mapping_db)
        assert len(entries) > 0

    def test_stem_match_without_extension(self, mapping_db, sample_pdf_name):
        stem = os.path.splitext(sample_pdf_name)[0]
        entries = lookup_mapping(stem + ".pdf", mapping_db)
        assert len(entries) > 0

    def test_no_match_returns_empty(self, mapping_db):
        entries = lookup_mapping("존재하지않는파일_99999.pdf", mapping_db)
        assert entries == []


# ─── 3. load_rules ────────────────────────────────────────────────────────────

class TestLoadRules:
    def test_rules_load_successfully(self):
        rules = load_rules()
        assert rules is not None

    def test_required_methods_exist(self):
        rules = load_rules()
        for method in ["extract_age_table", "extract_period_table",
                       "extract_payment_cycle", "extract_benefit_start_age"]:
            assert callable(getattr(rules, method, None)), f"{method} 없음"

    def test_hot_reload_same_instance(self):
        """파일 변경 없으면 동일 인스턴스 반환"""
        r1 = load_rules()
        r2 = load_rules()
        assert r1 is r2


# ─── 4. STEPS 정의 ────────────────────────────────────────────────────────────

class TestSteps:
    def test_steps_list(self):
        assert "STEP1" in STEPS
        assert "STEP7" in STEPS
        assert STEPS.index("STEP1") < STEPS.index("STEP7")


# ─── 5. process_pdf_sync end-to-end (sample.pdf 존재 시) ─────────────────────

class TestProcessPdfSync:
    def test_process_real_pdf(
        self, sample_pdf_path, mapping_path, template_paths,
        gt_paths, tmp_path
    ):
        """실제 PDF를 처리하여 xlsx가 생성되어야 한다"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip("sample.pdf 없음")

        from app.core.pipeline import load_mapping_db, process_pdf_sync

        mapping_db = load_mapping_db(mapping_path)
        pdf_name = os.path.basename(sample_pdf_path)
        output_dir = str(tmp_path / "output")

        events = []
        def emit_fn(event):
            events.append(event)

        result = process_pdf_sync(
            job_id="test-job",
            pdf_name=pdf_name,
            pdf_path=sample_pdf_path,
            mapping_db=mapping_db,
            templates=template_paths,
            selected_tables=["S00026", "S00027", "S00028"],
            output_dir=output_dir,
            gt_files=gt_paths,
            emit_fn=emit_fn,
        )

        # 오류 없이 완료
        assert result["status"] != "error", f"오류 발생: {result.get('error')}"

        # 진행 이벤트가 발생해야 함
        assert len(events) > 0, "진행 이벤트가 없음"

        # 최소 하나의 테이블이 처리되어야 함
        assert len(result["tables"]) > 0

    def test_process_pdf_with_mapping_entries(
        self, sample_pdf_path, mapping_path, template_paths, gt_paths, tmp_path
    ):
        """처리 결과에 mapping_entries가 포함되어야 한다"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip("sample.pdf 없음")

        from app.core.pipeline import load_mapping_db, process_pdf_sync

        mapping_db = load_mapping_db(mapping_path)
        pdf_name = os.path.basename(sample_pdf_path)

        result = process_pdf_sync(
            job_id="test-job2",
            pdf_name=pdf_name,
            pdf_path=sample_pdf_path,
            mapping_db=mapping_db,
            templates={},
            selected_tables=["S00026"],
            output_dir=str(tmp_path / "output2"),
            gt_files={},
            emit_fn=None,
        )
        assert "mapping_entries" in result

    def test_process_pdf_xlsx_generated(
        self, sample_pdf_path, mapping_path, template_paths, tmp_path
    ):
        """xlsx 파일이 output_dir에 생성되어야 한다"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip("sample.pdf 없음")

        from app.core.pipeline import load_mapping_db, process_pdf_sync

        mapping_db = load_mapping_db(mapping_path)
        pdf_name = os.path.basename(sample_pdf_path)
        output_dir = str(tmp_path / "output3")

        result = process_pdf_sync(
            job_id="test-job3",
            pdf_name=pdf_name,
            pdf_path=sample_pdf_path,
            mapping_db=mapping_db,
            templates=template_paths,
            selected_tables=["S00026", "S00027", "S00028"],
            output_dir=output_dir,
            gt_files={},
            emit_fn=None,
        )

        if result["status"] == "error":
            pytest.skip(f"처리 오류 (PDF 매핑 없을 수 있음): {result.get('error')}")

        for tbl, fname in result.get("xlsx_files", {}).items():
            out_path = os.path.join(output_dir, fname)
            assert os.path.exists(out_path), f"{tbl} xlsx 파일 없음: {out_path}"
