"""
extractor.py — PDF 텍스트 추출 래퍼
ruleautomatker/.claude/skills/pdf-preprocessor/scripts/extract_pdf.py 핵심 로직 재사용
"""

import os
import re


def extract_pdf_text(pdf_path: str) -> str:
    """PDF에서 전체 텍스트 추출 (PyMuPDF)"""
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        pages.append(f"[PAGE {page_num + 1}]\n{text}")
    doc.close()
    full_text = "\n".join(pages)

    # PDF 줄바꿈 아티팩트 보정
    full_text = re.sub(r"(\d+)\n세", r"\1세", full_text)
    return full_text


def extract_pdf_pages(pdf_path: str, output_dir: str, run_id: str) -> dict:
    """PDF에서 페이지별 텍스트 파일 생성 (extraction_rules.py 호환)"""
    import fitz

    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    pages_info = {}

    for page_num in range(len(doc)):
        page_str = str(page_num + 1)
        page = doc[page_num]
        text = page.get_text("text")
        txt_path = os.path.join(output_dir, f"{run_id}_page_{page_str}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        pages_info[page_str] = {"text_path": txt_path, "image_path": None}

    doc.close()
    return pages_info
