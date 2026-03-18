"""
conftest.py — pytest 공통 fixture

fixture 파일 위치: tests/fixtures/
  - mapping.xlsx        : 판매중_상품구성_사업방법서_매핑.xlsx (ruleautomatker 복사본)
  - gt_S00026.xlsx      : 판매중_가입나이정보_0312.xlsx
  - gt_S00027.xlsx      : 판매중_보기납기정보_0312.xlsx
  - gt_S00028.xlsx      : 판매중_납입주기정보_0312.xlsx
  - gt_S00022.xlsx      : 판매중_보기개시나이정보_0312.xlsx
  - template_S000XX.xlsx: 각 테이블 업로드양식 템플릿
  - sample.pdf          : 테스트용 사업방법서 PDF
"""

import os
import sys
import warnings

import openpyxl
import pandas as pd
import pytest

# 프로젝트 루트를 sys.path에 추가
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


# ─── 파일 경로 fixture ───────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def fixture_dir():
    return FIXTURES


@pytest.fixture(scope="session")
def mapping_path():
    return os.path.join(FIXTURES, "mapping.xlsx")


@pytest.fixture(scope="session")
def gt_paths():
    return {
        "S00026": os.path.join(FIXTURES, "gt_S00026.xlsx"),
        "S00027": os.path.join(FIXTURES, "gt_S00027.xlsx"),
        "S00028": os.path.join(FIXTURES, "gt_S00028.xlsx"),
        "S00022": os.path.join(FIXTURES, "gt_S00022.xlsx"),
    }


@pytest.fixture(scope="session")
def template_paths():
    return {
        "S00026": os.path.join(FIXTURES, "template_S00026.xlsx"),
        "S00027": os.path.join(FIXTURES, "template_S00027.xlsx"),
        "S00028": os.path.join(FIXTURES, "template_S00028.xlsx"),
        "S00022": os.path.join(FIXTURES, "template_S00022.xlsx"),
    }


@pytest.fixture(scope="session")
def sample_pdf_path():
    return os.path.join(FIXTURES, "sample.pdf")


# ─── 매핑 DB fixture ─────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def mapping_db(mapping_path):
    """실제 매핑 xlsx → pipeline.load_mapping_db() 결과"""
    from app.core.pipeline import load_mapping_db
    return load_mapping_db(mapping_path)


@pytest.fixture(scope="session")
def sample_pdf_name(mapping_db):
    """매핑 DB에서 첫 번째 PDF 파일명 반환"""
    return next(iter(mapping_db))


@pytest.fixture(scope="session")
def sample_mapping_entries(mapping_db, sample_pdf_name):
    """sample PDF 에 해당하는 매핑 엔트리 목록"""
    return mapping_db[sample_pdf_name]


@pytest.fixture(scope="session")
def sample_dtcd_list(sample_mapping_entries):
    """sample PDF 의 DTCD 목록"""
    return list({e["dtcd"] for e in sample_mapping_entries if e.get("dtcd")})


# ─── GT 행 fixture ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def gt_rows_s00026(gt_paths, sample_dtcd_list):
    """실제 GT 파일에서 sample DTCD 에 해당하는 S00026 행 로드"""
    from app.core.comparator import load_gt_rows
    return load_gt_rows(gt_paths["S00026"], sample_dtcd_list)


@pytest.fixture(scope="session")
def gt_rows_s00027(gt_paths, sample_dtcd_list):
    from app.core.comparator import load_gt_rows
    return load_gt_rows(gt_paths["S00027"], sample_dtcd_list)


@pytest.fixture(scope="session")
def gt_rows_s00028(gt_paths, sample_dtcd_list):
    from app.core.comparator import load_gt_rows
    return load_gt_rows(gt_paths["S00028"], sample_dtcd_list)


# ─── 인메모리 합성 데이터 (단위 테스트용) ────────────────────────────────────

@pytest.fixture
def synthetic_mapping_entries():
    return [
        {
            "dtcd": "2061",
            "itcd": "001",
            "sale_nm": "테스트보험(표준체형)",
            "prod_dtcd": "2061",
            "prod_itcd": "1",
            "prod_sale_nm": "테스트보험",
        }
    ]


@pytest.fixture
def raw_rows_s00026():
    """S00026 raw 추출 결과 (자연어)"""
    return [
        {"sub_type": "기본형", "insurance_period": "60세만기",
         "payment_period": "5년납",  "gender": "남자", "min_age": 19, "max_age": 65},
        {"sub_type": "기본형", "insurance_period": "60세만기",
         "payment_period": "5년납",  "gender": "여자", "min_age": 19, "max_age": 65},
        {"sub_type": "기본형", "insurance_period": "60세만기",
         "payment_period": "10년납", "gender": "남자", "min_age": 19, "max_age": 60},
        {"sub_type": "기본형", "insurance_period": "60세만기",
         "payment_period": "10년납", "gender": "여자", "min_age": 19, "max_age": 60},
    ]


@pytest.fixture
def raw_rows_s00027():
    return [
        {"sub_type": "기본형", "insurance_period": "종신",    "payment_period": "5년납"},
        {"sub_type": "기본형", "insurance_period": "종신",    "payment_period": "10년납"},
        {"sub_type": "기본형", "insurance_period": "20년만기","payment_period": "전기납"},
    ]


@pytest.fixture
def raw_rows_s00028():
    return [
        {"sub_type": "기본형", "payment_cycle": "월납"},
        {"sub_type": "기본형", "payment_cycle": "3개월납"},
        {"sub_type": "기본형", "payment_cycle": "연납"},
        {"sub_type": "기본형", "payment_cycle": "일시납"},
    ]


@pytest.fixture
def raw_rows_s00022():
    return [
        {"sub_type": "기본형", "min_age": 45, "max_age": 80},
        {"sub_type": "기본형", "min_age": 50, "max_age": 80},
    ]


@pytest.fixture
def synthetic_gt_rows_s00026():
    """비교용 합성 GT 행 (coded 형식)"""
    return [
        {"ISRN_KIND_DTCD": 2061, "ISRN_TERM_INQY_CODE": "X60",
         "PAYM_TERM_INQY_CODE": "N5",  "MINU_GNDR_CODE": "1", "MIN_AG": 19, "MAX_AG": 65},
        {"ISRN_KIND_DTCD": 2061, "ISRN_TERM_INQY_CODE": "X60",
         "PAYM_TERM_INQY_CODE": "N5",  "MINU_GNDR_CODE": "2", "MIN_AG": 19, "MAX_AG": 65},
        {"ISRN_KIND_DTCD": 2061, "ISRN_TERM_INQY_CODE": "X60",
         "PAYM_TERM_INQY_CODE": "N10", "MINU_GNDR_CODE": "1", "MIN_AG": 19, "MAX_AG": 60},
        {"ISRN_KIND_DTCD": 2061, "ISRN_TERM_INQY_CODE": "X60",
         "PAYM_TERM_INQY_CODE": "N10", "MINU_GNDR_CODE": "2", "MIN_AG": 19, "MAX_AG": 60},
        # umbrella (제외 대상)
        {"ISRN_KIND_DTCD": 2061, "ISRN_TERM_INQY_CODE": "X60",
         "PAYM_TERM_INQY_CODE": "N5",  "MINU_GNDR_CODE": "1", "MIN_AG": 0,  "MAX_AG": 999},
    ]
