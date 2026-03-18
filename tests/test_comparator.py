"""
test_comparator.py — GT 비교 테스트

검증 항목:
  - GT 파일 로딩: ISRN_KIND_DTCD 컬럼으로 필터 (핵심 버그 수정 검증)
  - GT 로딩: MAX_AG=999 umbrella 행 자동 제외 (S00026)
  - GT 로딩: 타 DTCD 행 제외
  - model_key_loader 동적 비교키 로드
  - compare(): match / new / missing / pass 정확성
  - compare(): 빈 GT → has_gt=False
  - 실제 GT 파일(tests/fixtures/gt_S00026.xlsx)로 DTCD 필터 검증
  - 실제 GT 파일에서 umbrella 행이 제외되는지 검증
"""

import os
import tempfile

import openpyxl
import pytest

from app.core.comparator import (
    COMPARE_FIELDS,
    compare,
    detect_gt_table_type,
    load_gt_rows,
    _get_compare_fields,
    _MODEL_KEY_AVAILABLE,
)
from app.core.converter import TABLE_CONVERTERS


# ─── 1. detect_gt_table_type ─────────────────────────────────────────────────

class TestDetectGtTableType:
    @pytest.mark.parametrize("fname,expected", [
        ("판매중_가입나이정보_0312.xlsx",    "S00026"),
        ("판매중_보기납기정보.xlsx",          "S00027"),
        ("판매중_납입주기정보_20240101.xlsx", "S00028"),
        ("판매중_보기개시나이정보.xlsx",       "S00022"),
        ("S00026_template.xlsx",            "S00026"),
        ("S00027_업로드양식.xlsx",           "S00027"),
        ("unknown_file.xlsx",               ""),
    ])
    def test_detect(self, fname, expected):
        assert detect_gt_table_type(fname) == expected


# ─── 2. load_gt_rows — 인메모리 xlsx로 단위 테스트 ───────────────────────────

class TestLoadGtRows:
    def _make_gt_xlsx(self, rows, path):
        """테스트용 GT xlsx 생성 헬퍼"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["ISRN_KIND_DTCD", "ISRN_TERM_INQY_CODE",
                   "PAYM_TERM_INQY_CODE", "MINU_GNDR_CODE", "MIN_AG", "MAX_AG"])
        for r in rows:
            ws.append([r["ISRN_KIND_DTCD"], r.get("ISRN_TERM_INQY_CODE", ""),
                       r.get("PAYM_TERM_INQY_CODE", ""), r.get("MINU_GNDR_CODE", ""),
                       r.get("MIN_AG"), r.get("MAX_AG")])
        wb.save(path)

    def test_filter_by_isrn_kind_dtcd(self, tmp_path, synthetic_gt_rows_s00026):
        """ISRN_KIND_DTCD 컬럼으로 정확히 필터되어야 한다 (핵심 수정 검증)"""
        path = str(tmp_path / "gt_test.xlsx")
        # umbrella 제외한 5행, 타DTCD 1행 추가
        rows = [r for r in synthetic_gt_rows_s00026 if r["MAX_AG"] != 999]
        rows.append({"ISRN_KIND_DTCD": 9999, "ISRN_TERM_INQY_CODE": "X80",
                     "PAYM_TERM_INQY_CODE": "N5", "MINU_GNDR_CODE": "1",
                     "MIN_AG": 20, "MAX_AG": 70})
        self._make_gt_xlsx(rows, path)
        loaded = load_gt_rows(path, ["2061"])
        dtcds = {str(r.get("ISRN_KIND_DTCD", "")).strip().rstrip(".0") for r in loaded}
        assert "9999" not in dtcds, "타 DTCD(9999) 행이 제외되지 않음"
        assert all(d in {"2061", "2061.0"} or d.startswith("2061") for d in dtcds)

    def test_umbrella_row_excluded_s00026(self, tmp_path, synthetic_gt_rows_s00026):
        """S00026 GT에서 MAX_AG=999 umbrella 행이 제외되어야 한다"""
        path = str(tmp_path / "gt_s00026_umbrella.xlsx")
        # 파일명에 '가입나이' 포함해서 테이블 타입 감지
        path = str(tmp_path / "판매중_가입나이_test.xlsx")
        self._make_gt_xlsx(synthetic_gt_rows_s00026, path)
        loaded = load_gt_rows(path, ["2061"])
        max_ages = [r.get("MAX_AG") for r in loaded]
        assert 999 not in max_ages and "999" not in [str(a) for a in max_ages], (
            f"umbrella(MAX_AG=999) 행이 제외되지 않음: {max_ages}"
        )

    def test_no_dtcd_filter_loads_all(self, tmp_path, synthetic_gt_rows_s00026):
        """dtcd_list가 비어 있으면 전체 행을 반환한다"""
        rows_no_umbrella = [r for r in synthetic_gt_rows_s00026 if r["MAX_AG"] != 999]
        path = str(tmp_path / "판매중_가입나이_nofilter.xlsx")
        self._make_gt_xlsx(rows_no_umbrella, path)
        loaded = load_gt_rows(path, [])
        assert len(loaded) == len(rows_no_umbrella)

    def test_nonexistent_file_returns_empty(self):
        loaded = load_gt_rows("/nonexistent/path/gt.xlsx", ["2061"])
        assert loaded == []


# ─── 3. load_gt_rows — 실제 fixture 파일 ────────────────────────────────────

class TestLoadGtRowsRealFile:
    def test_real_gt_s00026_loads_rows(self, gt_paths, sample_dtcd_list):
        """실제 GT 파일에서 샘플 DTCD에 해당하는 행이 로드되어야 한다"""
        rows = load_gt_rows(gt_paths["S00026"], sample_dtcd_list)
        assert len(rows) > 0, (
            f"GT S00026에서 DTCD={sample_dtcd_list}에 해당하는 행 없음"
        )

    def test_real_gt_s00026_no_umbrella(self, gt_paths, sample_dtcd_list):
        """실제 GT 파일에서 umbrella(MAX_AG=999) 행이 제외되어야 한다"""
        rows = load_gt_rows(gt_paths["S00026"], sample_dtcd_list)
        max_ages = [r.get("MAX_AG") for r in rows]
        assert 999 not in max_ages and "999" not in [str(a) for a in max_ages], (
            "실제 GT에서 umbrella 행이 제외되지 않음"
        )

    def test_real_gt_s00027_loads_rows(self, gt_paths, sample_dtcd_list):
        rows = load_gt_rows(gt_paths["S00027"], sample_dtcd_list)
        assert len(rows) > 0, f"GT S00027에서 DTCD={sample_dtcd_list} 행 없음"

    def test_real_gt_s00028_loads_rows(self, gt_paths, sample_dtcd_list):
        rows = load_gt_rows(gt_paths["S00028"], sample_dtcd_list)
        assert len(rows) > 0, f"GT S00028에서 DTCD={sample_dtcd_list} 행 없음"


# ─── 4. _get_compare_fields — 비교키 동적 로드 ─────────────────────────────

class TestGetCompareFields:
    @pytest.mark.parametrize("tbl", ["S00026", "S00027", "S00028", "S00022"])
    def test_returns_fields_for_each_table(self, tbl):
        gt_sample = [{"ISRN_TERM_INQY_CODE": "X60", "PAYM_TERM_INQY_CODE": "N5",
                      "MINU_GNDR_CODE": "1", "MIN_AG": 19, "MAX_AG": 65,
                      "PAYM_CYCL_INQY_CODE": "M1"}]
        ex_sample = [{"ISRN_TERM_INQY_CODE": "X60", "PAYM_TERM_INQY_CODE": "N5",
                      "MINU_GNDR_CODE": "1", "MIN_AG": 19, "MAX_AG": 65,
                      "PAYM_CYCL_INQY_CODE": "M1"}]
        fields = _get_compare_fields(tbl, gt_sample, ex_sample)
        assert len(fields) > 0, f"{tbl} 비교키가 비어 있음"

    def test_fallback_to_compare_fields_when_empty_rows(self):
        """GT/EX 행이 없어도 COMPARE_FIELDS fallback으로 필드를 반환해야 한다"""
        fields = _get_compare_fields("S00026", [], [])
        assert len(fields) > 0
        assert fields == COMPARE_FIELDS["S00026"]

    @pytest.mark.skipif(not _MODEL_KEY_AVAILABLE, reason="model_key_loader 없음")
    def test_model_key_loader_active(self):
        """model_key_loader가 사용 가능하면 동적 키를 반환해야 한다"""
        gt = [{"MIN_AG": 19, "MAX_AG": 65, "MINU_GNDR_CODE": "1"}]
        ex = [{"MIN_AG": 19, "MAX_AG": 65, "MINU_GNDR_CODE": "1"}]
        fields = _get_compare_fields("S00026", gt, ex)
        assert len(fields) > 0


# ─── 5. compare() — 핵심 비교 로직 ─────────────────────────────────────────

class TestCompare:
    def _make_coded_s00026(self, raw_rows):
        return TABLE_CONVERTERS["S00026"](raw_rows)

    def test_all_match(self, raw_rows_s00026, synthetic_gt_rows_s00026):
        coded = self._make_coded_s00026(raw_rows_s00026)
        gt = [r for r in synthetic_gt_rows_s00026 if r["MAX_AG"] != 999]
        result = compare("S00026", coded, gt)
        assert result["has_gt"] is True
        assert result["summary"]["missing"] == 0
        assert result["summary"]["pass"] is True

    def test_missing_rows_detected(self, raw_rows_s00026, synthetic_gt_rows_s00026):
        """GT에는 있지만 추출 안 된 행 → missing으로 분류"""
        coded = self._make_coded_s00026(raw_rows_s00026[:2])  # 일부만 추출
        gt = [r for r in synthetic_gt_rows_s00026 if r["MAX_AG"] != 999]
        result = compare("S00026", coded, gt)
        assert result["summary"]["missing"] > 0
        assert result["summary"]["pass"] is False
        assert len(result["missing_rows"]) > 0

    def test_new_rows_detected(self, raw_rows_s00026, synthetic_gt_rows_s00026):
        """추출됐지만 GT에 없는 행 → new로 분류"""
        extra = [{"sub_type": "기본형", "insurance_period": "80세만기",
                  "payment_period": "20년납", "gender": "남자", "min_age": 19, "max_age": 79}]
        coded = self._make_coded_s00026(raw_rows_s00026 + extra)
        gt = [r for r in synthetic_gt_rows_s00026 if r["MAX_AG"] != 999]
        result = compare("S00026", coded, gt)
        new_rows = [r for r in result["annotated_rows"] if r.get("_gt_status") == "new"]
        assert len(new_rows) > 0

    def test_empty_gt_returns_has_gt_false(self, raw_rows_s00026):
        coded = self._make_coded_s00026(raw_rows_s00026)
        result = compare("S00026", coded, [])
        assert result["has_gt"] is False
        assert result["summary"]["pass"] is None

    def test_empty_coded_rows(self, synthetic_gt_rows_s00026):
        gt = [r for r in synthetic_gt_rows_s00026 if r["MAX_AG"] != 999]
        result = compare("S00026", [], gt)
        assert result["summary"]["missing"] == len(gt)
        assert result["summary"]["match"] == 0
        assert result["summary"]["pass"] is False

    def test_annotated_rows_have_gt_status(self, raw_rows_s00026, synthetic_gt_rows_s00026):
        coded = self._make_coded_s00026(raw_rows_s00026)
        gt = [r for r in synthetic_gt_rows_s00026 if r["MAX_AG"] != 999]
        result = compare("S00026", coded, gt)
        for row in result["annotated_rows"]:
            assert "_gt_status" in row
            assert row["_gt_status"] in ("match", "new")

    def test_compare_fields_in_result(self, raw_rows_s00026, synthetic_gt_rows_s00026):
        """compare() 결과에 사용된 비교 필드 목록이 포함되어야 한다"""
        coded = self._make_coded_s00026(raw_rows_s00026)
        gt = [r for r in synthetic_gt_rows_s00026 if r["MAX_AG"] != 999]
        result = compare("S00026", coded, gt)
        assert "compare_fields" in result
        assert len(result["compare_fields"]) > 0

    def test_s00028_comparison(self, raw_rows_s00028):
        coded = TABLE_CONVERTERS["S00028"](raw_rows_s00028)
        gt = [
            {"PAYM_CYCL_INQY_CODE": "M1"},
            {"PAYM_CYCL_INQY_CODE": "M12"},
        ]
        result = compare("S00028", coded, gt)
        assert result["has_gt"] is True
        assert result["summary"]["match"] == 2


# ─── 6. 실제 GT 파일로 end-to-end 비교 ──────────────────────────────────────

class TestCompareWithRealGT:
    def test_compare_s00026_real_gt(self, gt_rows_s00026, raw_rows_s00026):
        """실제 GT 데이터와 합성 coded_rows 비교 — 오류 없이 실행되어야 한다"""
        if not gt_rows_s00026:
            pytest.skip("샘플 DTCD에 해당하는 GT S00026 행 없음")
        coded = TABLE_CONVERTERS["S00026"](raw_rows_s00026)
        result = compare("S00026", coded, gt_rows_s00026)
        assert "summary" in result
        assert "annotated_rows" in result
        assert result["summary"]["total_extracted"] == len(coded)
        assert result["summary"]["total_gt"] == len(gt_rows_s00026)

    def test_compare_s00027_real_gt(self, gt_rows_s00027, raw_rows_s00027):
        if not gt_rows_s00027:
            pytest.skip("샘플 DTCD에 해당하는 GT S00027 행 없음")
        coded = TABLE_CONVERTERS["S00027"](raw_rows_s00027)
        result = compare("S00027", coded, gt_rows_s00027)
        assert "summary" in result

    def test_compare_s00028_real_gt(self, gt_rows_s00028, raw_rows_s00028):
        if not gt_rows_s00028:
            pytest.skip("샘플 DTCD에 해당하는 GT S00028 행 없음")
        coded = TABLE_CONVERTERS["S00028"](raw_rows_s00028)
        result = compare("S00028", coded, gt_rows_s00028)
        assert "summary" in result
