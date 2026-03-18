"""
highlighter.py — 테이블별 관련 텍스트 구간 추출
PDF 전체 텍스트에서 각 테이블 추출에 관련된 단락 식별
"""

import re
from typing import List

TABLE_KEYWORDS = {
    "S00026": [
        "가입나이", "가입가능나이", "피보험자", "최저나이", "최고나이",
        "만나이", "가입가능", "나이제한", "연령제한", "가입연령",
        "남자", "여자", "남녀", "성별",
    ],
    "S00027": [
        "보험기간", "납입기간", "보기납기", "보기", "납기",
        "만기", "종신", "년납", "년만기", "세만기",
        "전기납", "일시납", "납입방법",
    ],
    "S00028": [
        "납입주기", "납입방법", "월납", "분기납", "반기납",
        "연납", "일시납", "주기", "납입구분",
    ],
    "S00022": [
        "개시나이", "연금개시", "보험개시", "개시연령",
        "보기개시", "수익개시", "지급개시",
    ],
}


def extract_relevant_text(full_text: str, table_type: str, max_chars: int = 3000) -> str:
    """
    PDF 전체 텍스트에서 해당 테이블과 관련된 단락을 우선 추출.
    관련 단락이 없으면 앞부분 반환.
    """
    keywords = TABLE_KEYWORDS.get(table_type, [])
    if not keywords:
        return full_text[:max_chars]

    # 단락 분리 (빈 줄 기준, 또는 PAGE 구분자 기준)
    paragraphs = re.split(r"\n{2,}|\[PAGE \d+\]", full_text)

    scored: List[tuple] = []
    for para in paragraphs:
        para = para.strip()
        if len(para) < 10:
            continue
        score = sum(para.count(kw) for kw in keywords)
        if score > 0:
            scored.append((score, para))

    if not scored:
        return full_text[:max_chars]

    # 점수 내림차순 정렬, 상위 단락 결합
    scored.sort(key=lambda x: -x[0])
    selected = []
    total = 0
    for _, para in scored:
        if total + len(para) > max_chars:
            break
        selected.append(para)
        total += len(para)

    return "\n\n".join(selected)


def get_keyword_positions(text: str, table_type: str) -> List[dict]:
    """
    텍스트에서 키워드 위치 목록 반환 (프론트엔드 하이라이팅용).
    [{keyword, start, end}, ...]
    """
    keywords = TABLE_KEYWORDS.get(table_type, [])
    positions = []
    for kw in keywords:
        for m in re.finditer(re.escape(kw), text):
            positions.append({"keyword": kw, "start": m.start(), "end": m.end()})
    positions.sort(key=lambda x: x["start"])
    return positions
