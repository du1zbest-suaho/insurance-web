"""
converter.py — 자연어 → 시스템코드 변환 래퍼
ruleautomatker/.claude/skills/code-converter/scripts/convert_codes.py 재사용
"""

import os
import sys

# ruleautomatker의 convert_codes.py import
_RULE_BASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../ruleautomatker")
)
_CONVERTER_DIR = os.path.join(_RULE_BASE, ".claude/skills/code-converter/scripts")

if _CONVERTER_DIR not in sys.path:
    sys.path.insert(0, _CONVERTER_DIR)

try:
    from convert_codes import TABLE_CONVERTERS  # noqa: F401
except ImportError:
    # fallback: 인라인 최소 구현
    TABLE_CONVERTERS = {}


def convert_table(table_type: str, raw_rows: list) -> list:
    """테이블 타입별 코드 변환"""
    converter = TABLE_CONVERTERS.get(table_type)
    if not converter:
        return raw_rows
    return converter(raw_rows)


def convert_all(raw_tables: dict) -> dict:
    """
    {table_type: raw_rows} → {table_type: coded_rows}
    """
    coded = {}
    for table_type, raw_rows in raw_tables.items():
        coded[table_type] = convert_table(table_type, raw_rows)
    return coded
