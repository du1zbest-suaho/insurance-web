"""
pipeline.py — 단일 PDF 처리 파이프라인 (STEP 1→2→3→4→5→7)
Phase 3: per-table 관련 텍스트 스니펫
Phase 4: asyncio.gather 동시 PDF 처리
Phase 6: STEP5 GT 비교 (판매중_*.xlsx 로드)
"""

import asyncio
import importlib.util
import os
import re
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from app.core import store as job_store
from app.core.extractor import extract_pdf_text
from app.core.converter import convert_all
from app.core.reporter import generate_xlsx, build_preview
from app.core.highlighter import extract_relevant_text
from app.core.comparator import compare, load_gt_rows

RULES_PATH = os.path.join(os.path.dirname(__file__), "../rules/extraction_rules.py")
EXCEPTIONS_PATH = os.path.join(os.path.dirname(__file__), "../rules/product_exceptions.json")

TABLE_METHOD_MAP = {
    "S00026": "extract_age_table",
    "S00027": "extract_period_table",
    "S00028": "extract_payment_cycle",
    "S00022": "extract_benefit_start_age",
}

STEPS = ["STEP1", "STEP2", "STEP3", "STEP4", "STEP5", "STEP7"]


# ─── 룰 로더 ─────────────────────────────────────────────────────────────────

_rules_instance = None
_rules_mtime = 0


def load_rules():
    global _rules_instance, _rules_mtime
    try:
        mtime = os.path.getmtime(RULES_PATH)
        if _rules_instance is None or mtime != _rules_mtime:
            spec = importlib.util.spec_from_file_location("extraction_rules", RULES_PATH)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            _rules_instance = module.ExtractionRules(exceptions_path=EXCEPTIONS_PATH)
            _rules_mtime = mtime
    except Exception as e:
        raise RuntimeError(f"룰 파일 로드 실패: {e}")
    return _rules_instance


# ─── 매핑 DB 로드 ─────────────────────────────────────────────────────────────

def load_mapping_db(mapping_path: str) -> Dict[str, List[Dict]]:
    def _is_na(val):
        if val is None:
            return True
        try:
            import math
            return math.isnan(float(val))
        except (TypeError, ValueError):
            return False

    df = pd.read_excel(mapping_path)
    result = {}
    for _, row in df.iterrows():
        pdf = str(row.get("사업방법서 파일명", "") or "").strip()
        if not pdf:
            continue
        entry = {
            "dtcd": str(int(row["ISRN_KIND_DTCD"])) if not _is_na(row.get("ISRN_KIND_DTCD")) else "",
            "itcd": str(row.get("ISRN_KIND_ITCD", "") or "").strip(),
            "sale_nm": str(row.get("ISRN_KIND_SALE_NM", "") or "").strip(),
            "prod_dtcd": str(int(row["PROD_DTCD"])) if not _is_na(row.get("PROD_DTCD")) else "",
            "prod_itcd": str(int(row["PROD_ITCD"])) if not _is_na(row.get("PROD_ITCD")) else "",
            "prod_sale_nm": str(row.get("PROD_SALE_NM", "") or "").strip(),
        }
        result.setdefault(pdf, []).append(entry)
    return result


def lookup_mapping(pdf_name: str, mapping_db: Dict) -> List[Dict]:
    if pdf_name in mapping_db:
        return mapping_db[pdf_name]
    stem = os.path.splitext(pdf_name)[0]
    for key, entries in mapping_db.items():
        if os.path.splitext(key)[0] == stem:
            return entries
    return []


# ─── 단일 PDF 처리 ────────────────────────────────────────────────────────────

def process_pdf_sync(
    job_id: str,
    pdf_name: str,
    pdf_path: str,
    mapping_db: Dict,
    templates: Dict[str, str],
    selected_tables: List[str],
    output_dir: str,
    gt_files: Dict[str, str],       # {table_type: gt_xlsx_path}
    emit_fn: Optional[Callable] = None,
) -> Dict[str, Any]:

    def emit(step, msg, pct):
        if emit_fn:
            emit_fn({
                "file": pdf_name,
                "step": step,
                "msg": msg,
                "pct": pct,
                "steps": STEPS,
                "current_step_idx": STEPS.index(step) if step in STEPS else -1,
            })

    result: Dict[str, Any] = {
        "status": "error",
        "tables": {},
        "xlsx_files": {},
        "mapping_entries": [],
        "error": None,
        "preview": {},
        "gt_summaries": {},         # {table_type: {match, new, missing, pass}}
    }

    try:
        # STEP 1: PDF 텍스트 추출
        emit("STEP1", "PDF 텍스트 추출 중...", 10)
        full_text = extract_pdf_text(pdf_path)

        # STEP 2: 상품 매핑 조회
        emit("STEP2", "상품 매핑 조회 중...", 22)
        entries = lookup_mapping(pdf_name, mapping_db)
        result["mapping_entries"] = entries
        is_new_product = len(entries) == 0

        if is_new_product:
            emit("WARN", "매핑 없음 → 신규 상품 (추출값만 표시)", 25)

        product_code = ""
        dtcd_list = []
        if entries:
            product_code = f"{entries[0]['dtcd']}{entries[0]['itcd']}"
            dtcd_list = list({e["dtcd"] for e in entries if e.get("dtcd")})

        # STEP 3: 테이블 추출
        emit("STEP3", "테이블 추출 중...", 38)
        rules = load_rules()
        raw_tables: Dict[str, List] = {}

        for i, table_type in enumerate(selected_tables):
            pct = 38 + int(18 * (i + 0.5) / max(len(selected_tables), 1))
            emit("STEP3", f"{table_type} 추출 중...", pct)
            method_name = TABLE_METHOD_MAP.get(table_type)
            if not method_name:
                continue
            method = getattr(rules, method_name, None)
            if not method:
                continue
            try:
                raw_rows = method(full_text, product_code)
                raw_tables[table_type] = raw_rows or []
            except Exception as ex:
                raw_tables[table_type] = []
                emit("WARN", f"{table_type} 추출 오류: {ex}", pct)

        result["tables"] = {k: {"raw": v, "count": len(v)} for k, v in raw_tables.items()}

        # STEP 4: 코드 변환
        emit("STEP4", "코드 변환 중...", 58)
        coded_tables = convert_all(raw_tables)

        # STEP 5: GT 비교 (GT 파일이 있는 테이블만)
        emit("STEP5", "GT 비교 중...", 72)
        gt_comparisons: Dict[str, Dict] = {}

        for table_type, coded_rows in coded_tables.items():
            gt_path = gt_files.get(table_type)
            if gt_path:
                gt_rows = load_gt_rows(gt_path, dtcd_list)
                gt_comp = compare(table_type, coded_rows, gt_rows)
            else:
                gt_comp = None
            gt_comparisons[table_type] = gt_comp

            if gt_comp and gt_comp.get("has_gt"):
                result["gt_summaries"][table_type] = gt_comp["summary"]

        # 미리보기 빌드 (GT 비교 결과 포함)
        for table_type, coded_rows in coded_tables.items():
            snippet = extract_relevant_text(full_text, table_type, max_chars=3000)
            result["preview"][table_type] = build_preview(
                table_type, coded_rows, snippet,
                gt_comparison=gt_comparisons.get(table_type),
            )

        # STEP 7: xlsx 생성
        emit("STEP7", "xlsx 생성 중...", 85)
        os.makedirs(output_dir, exist_ok=True)

        for table_type, coded_rows in coded_tables.items():
            if not coded_rows:
                continue
            template_path = templates.get(table_type)
            out_fname = f"{table_type}_{os.path.splitext(pdf_name)[0]}.xlsx"
            out_path = os.path.join(output_dir, out_fname)
            valid_start = _parse_valid_date(pdf_name)

            generate_xlsx(
                table_type=table_type,
                coded_rows=coded_rows,
                template_path=template_path,
                output_path=out_path,
                mapping_entries=entries,
                valid_start_date=valid_start,
            )
            result["xlsx_files"][table_type] = out_fname

        # 종합 상태 결정
        # GT가 있고 missing > 0이면 FAIL, GT 없으면 done/new
        has_any_gt = bool(result["gt_summaries"])
        if has_any_gt:
            all_pass = all(s.get("pass", True) for s in result["gt_summaries"].values())
            result["status"] = "done" if all_pass else "fail"
        else:
            result["status"] = "new" if is_new_product else "done"

        emit("DONE", "완료", 100)

    except Exception as e:
        result["error"] = str(e)
        result["status"] = "error"
        emit("ERROR", f"오류: {e}", 100)

    return result


def _parse_valid_date(pdf_name: str) -> str:
    m = re.search(r"(\d{8})", pdf_name)
    return m.group(1) if m else ""


# ─── 배치 파이프라인 ──────────────────────────────────────────────────────────

async def run_pipeline(job_id: str) -> None:
    job = job_store.get_job(job_id)
    if not job:
        return

    job["status"] = "processing"
    files = job["files"]
    selected_tables = job["selected_tables"]
    gt_files = files.get("gt", {})

    async def emit_async(event):
        await job_store.emit(job_id, event)

    try:
        if not files.get("mapping"):
            await emit_async({"type": "ERROR", "msg": "매핑 파일이 없습니다."})
            job["status"] = "error"
            return

        mapping_db = await asyncio.to_thread(load_mapping_db, files["mapping"])
        templates = files.get("templates", {})
        pdfs = files.get("pdfs", [])

        if not pdfs:
            await emit_async({"type": "ERROR", "msg": "처리할 PDF 파일이 없습니다."})
            job["status"] = "error"
            return

        await emit_async({
            "type": "START", "msg": f"{len(pdfs)}개 PDF 처리 시작", "total": len(pdfs)
        })

        loop = asyncio.get_event_loop()

        def make_emit_fn(loop_ref):
            def sync_emit(event):
                asyncio.run_coroutine_threadsafe(job_store.emit(job_id, event), loop_ref)
            return sync_emit

        emit_fn = make_emit_fn(loop)

        async def process_one(pdf_info):
            pdf_name = pdf_info["name"]
            pdf_path = pdf_info["path"]
            output_dir = os.path.join(os.path.dirname(pdf_path), "output")
            return pdf_name, await asyncio.to_thread(
                process_pdf_sync,
                job_id, pdf_name, pdf_path,
                mapping_db, templates, selected_tables,
                output_dir, gt_files, emit_fn,
            )

        results = await asyncio.gather(
            *[process_one(p) for p in pdfs],
            return_exceptions=True,
        )

        for item in results:
            if isinstance(item, Exception):
                continue
            pdf_name, pdf_result = item
            job["pdf_results"][pdf_name] = pdf_result

        job["status"] = "done"
        await emit_async({"type": "ALL_DONE", "msg": "모든 파일 처리 완료"})

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        await emit_async({"type": "ERROR", "msg": str(e)})
    finally:
        await job_store.emit(job_id, None)
