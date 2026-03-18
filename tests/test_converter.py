"""
test_converter.py — 코드 변환 테스트 (convert_codes.py TABLE_CONVERTERS)

검증 항목:
  - TABLE_CONVERTERS 4개 테이블 로드 여부
  - S00026: 보험기간/납입기간/성별/나이 코드 변환
  - S00027: 보험기간/납입기간 조회코드 생성
  - S00028: 납입주기 코드 변환
  - S00022: 보기개시나이 범위 보존
  - 전기납 → 보험기간과 동일한 코드 생성
  - 성별 중립 행 자동 생성 (S00026)
  - 변환 오류 필드(_convert_error) 처리
"""

import pytest
from app.core.converter import TABLE_CONVERTERS, convert_all, convert_table


# ─── 1. 로드 검증 ─────────────────────────────────────────────────────────────

class TestTableConvertersLoad:
    def test_all_four_tables_loaded(self):
        """TABLE_CONVERTERS에 4개 테이블이 모두 로드되어야 한다"""
        assert set(TABLE_CONVERTERS.keys()) == {"S00026", "S00027", "S00028", "S00022"}

    def test_each_converter_is_callable(self):
        for tbl, fn in TABLE_CONVERTERS.items():
            assert callable(fn), f"{tbl} converter가 callable이 아님"


# ─── 2. S00026 가입가능나이 ────────────────────────────────────────────────────

class TestConvertS00026:
    def test_basic_conversion(self, raw_rows_s00026):
        coded = convert_table("S00026", raw_rows_s00026)
        assert len(coded) >= len(raw_rows_s00026)

    def test_insurance_period_code_generated(self, raw_rows_s00026):
        coded = convert_table("S00026", raw_rows_s00026)
        row = coded[0]
        assert row["ISRN_TERM_INQY_CODE"] == "X60", f"got {row['ISRN_TERM_INQY_CODE']}"
        assert row["ISRN_TERM_DVSN_CODE"] == "X"
        assert row["ISRN_TERM"] == 60

    def test_payment_period_code_generated(self, raw_rows_s00026):
        coded = convert_table("S00026", raw_rows_s00026)
        row = coded[0]
        assert row["PAYM_TERM_INQY_CODE"] == "N5"
        assert row["PAYM_TERM_DVSN_CODE"] == "N"
        assert row["PAYM_TERM"] == 5

    def test_gender_code_male(self, raw_rows_s00026):
        coded = convert_table("S00026", raw_rows_s00026)
        male_rows = [r for r in coded if r.get("MINU_GNDR_CODE") == "1"]
        assert len(male_rows) > 0, "남자 코드(1) 행이 없음"

    def test_gender_code_female(self, raw_rows_s00026):
        coded = convert_table("S00026", raw_rows_s00026)
        female_rows = [r for r in coded if r.get("MINU_GNDR_CODE") == "2"]
        assert len(female_rows) > 0, "여자 코드(2) 행이 없음"

    def test_age_range_preserved(self, raw_rows_s00026):
        coded = convert_table("S00026", raw_rows_s00026)
        row = coded[0]
        assert row["MIN_AG"] == 19
        assert row["MAX_AG"] == 65

    def test_gender_neutral_rows_generated(self):
        """MIN_AG=0인 남/여 쌍이 있으면 성별중립(None) 행이 자동 생성되어야 한다"""
        # gender-neutral 행 생성은 MIN_AG=0인 경우에만 적용됨
        raw = [
            {"sub_type": "기본형", "insurance_period": "60세만기",
             "payment_period": "5년납", "gender": "남자", "min_age": 0, "max_age": 65},
            {"sub_type": "기본형", "insurance_period": "60세만기",
             "payment_period": "5년납", "gender": "여자", "min_age": 0, "max_age": 65},
        ]
        coded = convert_table("S00026", raw)
        neutral_rows = [r for r in coded if r.get("MINU_GNDR_CODE") is None]
        assert len(neutral_rows) > 0, "성별 중립 행이 자동 생성되지 않음 (MIN_AG=0 조건)"

    def test_sub_type_preserved(self, raw_rows_s00026):
        coded = convert_table("S00026", raw_rows_s00026)
        assert all(r.get("sub_type") == "기본형" for r in coded)

    def test_convert_all_includes_s00026(self, raw_rows_s00026):
        result = convert_all({"S00026": raw_rows_s00026})
        assert "S00026" in result
        assert len(result["S00026"]) > 0


# ─── 3. S00027 보기납기 ───────────────────────────────────────────────────────

class TestConvertS00027:
    def test_insurance_period_lifetime(self, raw_rows_s00027):
        coded = convert_table("S00027", raw_rows_s00027)
        lifetime_rows = [r for r in coded if r.get("ISRN_TERM_INQY_CODE") == "A999"]
        assert len(lifetime_rows) >= 2, "종신 행이 없음"

    def test_payment_period_5yr(self, raw_rows_s00027):
        coded = convert_table("S00027", raw_rows_s00027)
        rows_5yr = [r for r in coded if r.get("PAYM_TERM_INQY_CODE") == "N5"]
        assert len(rows_5yr) > 0

    def test_jeonginap_equals_insurance_period(self, raw_rows_s00027):
        """전기납 → PAYM_TERM_INQY_CODE == ISRN_TERM_INQY_CODE"""
        coded = convert_table("S00027", raw_rows_s00027)
        for r in coded:
            if r.get("_raw", {}).get("payment_period") == "전기납":
                assert r["PAYM_TERM_INQY_CODE"] == r["ISRN_TERM_INQY_CODE"], (
                    f"전기납 코드 불일치: {r['PAYM_TERM_INQY_CODE']} != {r['ISRN_TERM_INQY_CODE']}"
                )

    def test_20yr_period_code(self, raw_rows_s00027):
        coded = convert_table("S00027", raw_rows_s00027)
        rows_20 = [r for r in coded if r.get("ISRN_TERM_INQY_CODE") == "N20"]
        assert len(rows_20) > 0, "20년만기(N20) 행이 없음"


# ─── 4. S00028 납입주기 ───────────────────────────────────────────────────────

class TestConvertS00028:
    def test_monthly_cycle(self, raw_rows_s00028):
        coded = convert_table("S00028", raw_rows_s00028)
        monthly = [r for r in coded if r.get("PAYM_CYCL_INQY_CODE") == "M1"]
        assert len(monthly) > 0, "월납(M1) 행 없음"

    def test_quarterly_cycle(self, raw_rows_s00028):
        coded = convert_table("S00028", raw_rows_s00028)
        quarterly = [r for r in coded if r.get("PAYM_CYCL_INQY_CODE") == "M3"]
        assert len(quarterly) > 0, "3개월납(M3) 행 없음"

    def test_annual_cycle(self, raw_rows_s00028):
        coded = convert_table("S00028", raw_rows_s00028)
        annual = [r for r in coded if r.get("PAYM_CYCL_INQY_CODE") == "M12"]
        assert len(annual) > 0, "연납(M12) 행 없음"

    def test_lump_sum_cycle(self, raw_rows_s00028):
        coded = convert_table("S00028", raw_rows_s00028)
        lump = [r for r in coded if r.get("PAYM_CYCL_INQY_CODE") == "M0"]
        assert len(lump) > 0, "일시납(M0) 행 없음"

    def test_all_four_cycles_present(self, raw_rows_s00028):
        coded = convert_table("S00028", raw_rows_s00028)
        codes = {r.get("PAYM_CYCL_INQY_CODE") for r in coded}
        assert {"M1", "M3", "M12", "M0"}.issubset(codes), f"누락 코드: {codes}"


# ─── 5. S00022 보기개시나이 ───────────────────────────────────────────────────

class TestConvertS00022:
    def test_age_range_preserved(self, raw_rows_s00022):
        # S00022은 나이 범위를 연도별 개별 행으로 확장 (X-type 전개)
        # min_age=45, max_age=80 → 36행 (45~80 각 1행), SPIN_STRT_DVSN_VAL 로 나이 저장
        coded = convert_table("S00022", raw_rows_s00022)
        # 두 raw 행 범위가 겹쳐 최소 36행 이상
        assert len(coded) >= 36
        spin_vals = {r.get("SPIN_STRT_DVSN_VAL") for r in coded}
        assert 45 in spin_vals, "min_age=45가 SPIN_STRT_DVSN_VAL에 없음"
        assert 80 in spin_vals, "max_age=80가 SPIN_STRT_DVSN_VAL에 없음"

    def test_all_rows_converted(self, raw_rows_s00022):
        coded = convert_table("S00022", raw_rows_s00022)
        for r in coded:
            assert "_convert_error" not in r or not r["_convert_error"]


# ─── 6. convert_all (일괄 변환) ──────────────────────────────────────────────

class TestConvertAll:
    def test_multi_table_conversion(
        self, raw_rows_s00026, raw_rows_s00027, raw_rows_s00028, raw_rows_s00022
    ):
        raw = {
            "S00026": raw_rows_s00026,
            "S00027": raw_rows_s00027,
            "S00028": raw_rows_s00028,
            "S00022": raw_rows_s00022,
        }
        result = convert_all(raw)
        assert set(result.keys()) == {"S00026", "S00027", "S00028", "S00022"}
        for tbl, rows in result.items():
            assert len(rows) > 0, f"{tbl} 변환 결과 행 없음"

    def test_empty_table_returns_empty(self):
        result = convert_all({"S00026": []})
        assert result["S00026"] == []

    def test_unknown_table_passthrough(self):
        raw = [{"dummy": 1}]
        result = convert_all({"S99999": raw})
        assert result["S99999"] == raw
