"""
comparator.py — 추출 결과 vs Ground Truth(판매중_*.xlsx) 행 단위 비교
ruleautomatker/.claude/skills/validator/scripts/compare_with_db.py 로직 재사용

핵심 변경:
- GT 필터링: ISRN_KIND_DTCD 컬럼 우선 사용 (UPPER_OBJECT_CODE fallback)
- S00026 MAX_AG=999 umbrella 행 제외
- model_key_loader 동적 로드 (모델상세 xlsx 기반 비교키), fallback COMPARE_FIELDS
- pandas 사용 (openpyxl → pandas로 교체)
"""

import os
import sys
import warnings
from typing import Any, Dict, List

import pandas as pd

# ruleautomatker validator 스크립트 경로 추가
_RULE_BASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../ruleautomatker")
)
_VALIDATOR_DIR = os.path.join(_RULE_BASE, ".claude/skills/validator/scripts")
_MODELS_DIR = os.path.join(_RULE_BASE, "data/models")

if _VALIDATOR_DIR not in sys.path:
    sys.path.insert(0, _VALIDATOR_DIR)

try:
    from model_key_loader import (  # noqa: F401
        load_model_key_cols, make_row_key, get_active_key_cols, normalize_val,
    )
    _MODEL_KEY_AVAILABLE = True
except ImportError:
    _MODEL_KEY_AVAILABLE = False


# ─── 하드코딩 fallback (모델상세 파일 없을 때) ─────────────────────────────

COMPARE_FIELDS: Dict[str, List[str]] = {
    "S00026": ["ISRN_TERM_INQY_CODE", "PAYM_TERM_INQY_CODE", "MINU_GNDR_CODE", "MIN_AG", "MAX_AG"],
    "S00027": ["ISRN_TERM_INQY_CODE", "PAYM_TERM_INQY_CODE"],
    "S00028": ["PAYM_CYCL_INQY_CODE"],
    "S00022": ["MIN_AG", "MAX_AG"],
}

# GT 파일명 → 테이블 타입 매핑
GT_FILENAME_MAP: Dict[str, str] = {
    "가입나이": "S00026",
    "보기납기": "S00027",
    "납입주기": "S00028",
    "보기개시나이": "S00022",
    "S00026": "S00026",
    "S00027": "S00027",
    "S00028": "S00028",
    "S00022": "S00022",
}


def detect_gt_table_type(filename: str) -> str:
    """GT 파일명에서 테이블 타입 감지"""
    for keyword, table_type in GT_FILENAME_MAP.items():
        if keyword in filename:
            return table_type
    return ""


def load_gt_rows(gt_path: str, dtcd_list: List[str]) -> List[Dict]:
    """
    GT xlsx에서 특정 상품코드의 행 로드.

    필터링 우선순위 (compare_with_db.py 동일 로직):
      1. UPPER_OBJECT_CODE 컬럼 → product_code(dtcd+itcd) startswith dtcd 매칭
      2. ISRN_KIND_DTCD 컬럼 → dtcd 정확 매칭 (판매중_*.xlsx 표준)

    S00026: MAX_AG=999 umbrella 행 제외 (GT 관례)
    """
    if not os.path.exists(gt_path):
        return []

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = pd.read_excel(gt_path)

    if df.empty:
        return []

    # 컬럼명 공백 제거
    df.columns = [str(c).strip() for c in df.columns]

    dtcd_set = {str(d).strip() for d in dtcd_list if d}

    if dtcd_set:
        if "UPPER_OBJECT_CODE" in df.columns:
            # UPPER_OBJECT_CODE = dtcd+itcd (예: "2061001")
            # dtcd가 앞 부분에 있으므로 startswith 매칭
            mask = df["UPPER_OBJECT_CODE"].astype(str).str.strip().apply(
                lambda v: any(v.startswith(dtcd) for dtcd in dtcd_set)
            )
            df = df[mask]
        elif "ISRN_KIND_DTCD" in df.columns:
            # 판매중_*.xlsx 표준: ISRN_KIND_DTCD = 정수 DTCD
            df = df[df["ISRN_KIND_DTCD"].astype(str).str.strip().isin(dtcd_set)]

    # S00026: MAX_AG=999 umbrella 행 제외
    fname = os.path.basename(gt_path)
    table_type = detect_gt_table_type(fname)
    if table_type == "S00026" and "MAX_AG" in df.columns:
        try:
            df = df[df["MAX_AG"].astype(float) != 999]
        except (ValueError, TypeError):
            df = df[df["MAX_AG"].astype(str).str.strip() != "999"]

    return df.to_dict("records")


# ─── 비교 키 결정 ──────────────────────────────────────────────────────────

def _get_compare_fields(
    table_type: str,
    gt_rows: List[Dict],
    coded_rows: List[Dict],
) -> List[str]:
    """비교 키 컬럼 결정: model_key_loader 우선, fallback COMPARE_FIELDS"""
    if _MODEL_KEY_AVAILABLE:
        all_key_cols = load_model_key_cols(table_type, _MODELS_DIR)
        if all_key_cols:
            active = get_active_key_cols(gt_rows, coded_rows, all_key_cols)
            if active:
                return active
    return COMPARE_FIELDS.get(table_type, [])


# ─── 값 정규화 ─────────────────────────────────────────────────────────────

def _normalize(val) -> str:
    """비교용 값 정규화: None→"", float 정수→"65", 공백 제거"""
    if _MODEL_KEY_AVAILABLE:
        v = normalize_val(val)
        return v if v is not None else ""
    if val is None:
        return ""
    s = str(val).strip()
    # 65.0 → "65"
    if s.endswith(".0") and s[:-2].lstrip("-").isdigit():
        s = s[:-2]
    return s


def _make_key(row: Dict, fields: List[str]) -> tuple:
    return tuple(_normalize(row.get(f)) for f in fields)


# ─── 비교 메인 ─────────────────────────────────────────────────────────────

def compare(
    table_type: str,
    coded_rows: List[Dict],
    gt_rows: List[Dict],
) -> Dict[str, Any]:
    """
    coded_rows vs gt_rows 행 단위 비교.
    반환:
    {
        "has_gt": bool,
        "compare_fields": [str, ...],
        "summary": {total_extracted, total_gt, match, new, missing, pass},
        "annotated_rows": coded_rows + _gt_status,
        "missing_rows": GT에만 있는 행 목록,
    }
    """
    fields = _get_compare_fields(table_type, gt_rows, coded_rows)

    if not gt_rows:
        return {
            "has_gt": False,
            "compare_fields": fields,
            "summary": {
                "total_extracted": len(coded_rows),
                "total_gt": 0,
                "match": 0, "new": 0, "missing": 0, "pass": None,
            },
            "annotated_rows": [dict(r) for r in coded_rows],
            "missing_rows": [],
        }

    gt_key_map = {_make_key(r, fields): r for r in gt_rows}
    ext_key_set = {_make_key(r, fields) for r in coded_rows}

    annotated: List[Dict] = []
    n_match = 0
    n_new = 0

    for row in coded_rows:
        key = _make_key(row, fields)
        if key in gt_key_map:
            annotated.append({**row, "_gt_status": "match"})
            n_match += 1
        else:
            annotated.append({**row, "_gt_status": "new"})
            n_new += 1

    # GT에는 있으나 추출 안 된 행
    missing_rows: List[Dict] = []
    for key, gt_row in gt_key_map.items():
        if key not in ext_key_set:
            missing_row: Dict[str, Any] = {f: gt_row.get(f) for f in fields}
            missing_row["sub_type"] = str(gt_row.get("LOWER_OBJECT_CODE", "") or "")
            missing_row["_gt_status"] = "missing"
            missing_rows.append(missing_row)

    n_missing = len(missing_rows)

    return {
        "has_gt": True,
        "compare_fields": fields,
        "summary": {
            "total_extracted": len(coded_rows),
            "total_gt": len(gt_rows),
            "match": n_match,
            "new": n_new,
            "missing": n_missing,
            "pass": n_missing == 0,
        },
        "annotated_rows": annotated,
        "missing_rows": missing_rows,
    }
