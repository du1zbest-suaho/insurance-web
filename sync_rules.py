"""
sync_rules.py — ruleautomatker/rules/ → app/rules/ 동기화
ruleautomatker에서 룰 고도화 후 실행: python sync_rules.py
"""

import os
import shutil

SRC_DIR = os.path.join(os.path.dirname(__file__), "../ruleautomatker/rules")
DST_DIR = os.path.join(os.path.dirname(__file__), "app/rules")
FILES = ["extraction_rules.py", "product_exceptions.json", "rule_history.json"]

os.makedirs(DST_DIR, exist_ok=True)

for fname in FILES:
    src = os.path.join(SRC_DIR, fname)
    dst = os.path.join(DST_DIR, fname)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"복사: {fname}")
    else:
        print(f"건너뜀 (없음): {fname}")

print("동기화 완료.")
