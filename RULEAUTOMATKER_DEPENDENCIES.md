# ruleautomatker 의존 파일 사용 현황

> insurance-web은 ruleautomatker 파일을 **수정 없이** 그대로 사용합니다.
> 참조 방식: `sys.path` 직접 추가(import) 또는 `sync_rules.py`로 복사.
>
> 기반 프로젝트 경로: `d:/code/claudecsw/ruleautomatker`

---

## 핵심 원칙

- ruleautomatker 파일은 **절대 수정하지 않는다**
- 룰 파일 변경은 ruleautomatker에서만 하고 `sync_rules.py`로 반영
- 상수·매핑은 import만 하고 insurance-web에서 오버라이드 금지 (예외: S00022 COLUMN_MAPPINGS — 기반 프로젝트 버그로 reporter.py에서만 오버라이드)

---

## 파일별 사용 현황

### 1. `rules/extraction_rules.py` — 핵심 추출 룰

| 항목 | 내용 |
|---|---|
| **원본 경로** | `ruleautomatker/rules/extraction_rules.py` |
| **참조 방식** | `sync_rules.py`로 `app/rules/`에 복사 (유일하게 복사 방식) |
| **사용 위치** | `app/core/pipeline.py` |
| **관련 파일** | `app/rules/product_exceptions.json`, `app/rules/rule_history.json` |

**사용 함수:**
```python
rules = ExtractionRules()
raw["S00026"] = rules.extract_age_table(text, product_code)        # 가입가능나이
raw["S00027"] = rules.extract_period_table(text, product_code)     # 가입가능보기납기
raw["S00028"] = rules.extract_payment_cycle(text, product_code)    # 가입가능납입주기
raw["S00022"] = rules.extract_benefit_start_age(text, product_code) # 보기개시나이
```

**동기화 방법:**
```bash
python sync_rules.py   # ruleautomatker/rules/ → app/rules/ 복사
```
앱 실행 중 룰 파일 mtime 변경 감지 → 자동 리로드

---

### 2. `generate_upload.py` — xlsx 생성 상수/컬럼 매핑

| 항목 | 내용 |
|---|---|
| **원본 경로** | `ruleautomatker/.claude/skills/xlsx-generator/scripts/generate_upload.py` |
| **참조 방식** | `sys.path` 직접 추가 후 import |
| **사용 위치** | `app/core/reporter.py` |

**사용 상수:**
```python
from generate_upload import DEFAULT_SALE_CHNL_CODE        # "1,2,3,4,7"
from generate_upload import COLUMN_MAPPINGS as _BASE_COLUMN_MAPPINGS
# COLUMN_MAPPINGS = {
#   "S00026": {"MIN_ISRN_TERM": "MIN_ISRN_TERM", "MAX_ISRN_TERM": "MAX_ISRN_TERM", ...},
#   "S00027": {...},
#   "S00028": {...},
#   "S00022": {...},  ← 버그 있음 (MIN_AG/MAX_AG → reporter.py에서 오버라이드)
# }
```

**주의:** S00022 COLUMN_MAPPINGS는 기반 프로젝트 버그(MIN_AG/MAX_AG 오매핑)로
reporter.py에서만 `FPIN/SPIN_STRT_*` 필드로 오버라이드합니다.

---

### 3. `model_key_loader.py` — 비교 키 동적 로드

| 항목 | 내용 |
|---|---|
| **원본 경로** | `ruleautomatker/.claude/skills/validator/scripts/model_key_loader.py` |
| **참조 방식** | `sys.path` 직접 추가 후 import |
| **사용 위치** | `app/core/comparator.py` |
| **데이터 파일** | `ruleautomatker/data/models/[S000XX]*_모델상세.xlsx` |

**사용 함수:**
```python
from model_key_loader import (
    load_model_key_cols,   # data/models/*.xlsx 에서 테이블별 비교 키 컬럼 추출
    make_row_key,          # 행 dict → 비교용 tuple 키 생성
    get_active_key_cols,   # GT·추출 행에 실제 존재하는 활성 키만 선별
    normalize_val,         # 65.0→"65", None→"" 정규화
)
```

**fallback:** 모델상세 파일 없거나 import 실패 시 하드코딩 `COMPARE_FIELDS` 사용:
```python
COMPARE_FIELDS = {
    "S00026": ["ISRN_TERM_INQY_CODE", "PAYM_TERM_INQY_CODE", "MINU_GNDR_CODE", "MIN_AG", "MAX_AG"],
    "S00027": ["ISRN_TERM_INQY_CODE", "PAYM_TERM_INQY_CODE"],
    "S00028": ["PAYM_CYCL_INQY_CODE"],
    "S00022": ["MIN_AG", "MAX_AG"],
}
```

---

### 4. `convert_codes.py` — 자연어 → 시스템 코드 변환

| 항목 | 내용 |
|---|---|
| **원본 경로** | `ruleautomatker/.claude/skills/code-converter/scripts/convert_codes.py` |
| **참조 방식** | `sys.path` 직접 추가 후 import |
| **사용 위치** | `app/core/converter.py` |

**사용 상수:**
```python
from convert_codes import TABLE_CONVERTERS
# TABLE_CONVERTERS = {
#   "S00026": <function>,   # 가입나이 raw_rows → coded_rows
#   "S00027": <function>,   # 보기납기 raw_rows → coded_rows
#   "S00028": <function>,   # 납입주기 raw_rows → coded_rows
#   "S00022": <function>,   # 보기개시나이 raw_rows → coded_rows
# }
```

---

## 데이터 파일 사용 현황

### 기본값으로 번들링된 파일 (`app/data/defaults/`)

복사 원본 위치: `ruleautomatker/data/existing/`, `ruleautomatker/data/templates/`

| 파일 | 원본 경로 | 용도 |
|---|---|---|
| `mapping.xlsx` | `existing/판매중_상품구성_사업방법서_매핑.xlsx` | 사업방법서 PDF명 → 상품코드(dtcd/itcd) 매핑 DB |
| `gt/판매중_가입나이정보_0312.xlsx` | `existing/판매중_가입나이정보_0312.xlsx` | S00026 비교검증 Ground Truth |
| `gt/판매중_보기납기정보_0312.xlsx` | `existing/판매중_보기납기정보_0312.xlsx` | S00027 비교검증 Ground Truth |
| `gt/판매중_납입주기정보_0312.xlsx` | `existing/판매중_납입주기정보_0312.xlsx` | S00028 비교검증 Ground Truth |
| `gt/판매중_보기개시나이정보_0312.xlsx` | `existing/판매중_보기개시나이정보_0312.xlsx` | S00022 비교검증 Ground Truth |
| `templates/template_S00026.xlsx` | `templates/[S00026]가입가능나이_단일속성_업로드양식.xlsx` | S00026 xlsx 생성 템플릿 |
| `templates/template_S00027.xlsx` | `templates/[S00027] 가입가능보기납기_업로드양식.xlsx` | S00027 xlsx 생성 템플릿 |
| `templates/template_S00028.xlsx` | `templates/[S00028] 가입가능납입주기_업로드양식.xlsx` | S00028 xlsx 생성 템플릿 |
| `templates/template_S00022.xlsx` | `templates/[S00022] 보기개시나이_업로드양식.xlsx` | S00022 xlsx 생성 템플릿 |

### 런타임에만 읽는 파일 (복사 없이 직접 경로 참조)

| 파일 | 경로 | 용도 |
|---|---|---|
| `[S00026]*_모델상세.xlsx` | `ruleautomatker/data/models/` | S00026 비교 키 컬럼 동적 로드 |
| `[S00027]*_모델상세.xlsx` | `ruleautomatker/data/models/` | S00027 비교 키 컬럼 동적 로드 |
| `[S00028]*_모델상세.xlsx` | `ruleautomatker/data/models/` | S00028 비교 키 컬럼 동적 로드 |
| `[S00022]*_모델상세.xlsx` | `ruleautomatker/data/models/` | S00022 비교 키 컬럼 동적 로드 |

---

## 전체 의존 구조

```
insurance-web/app/
│
├── core/pipeline.py ──────────────────────────────────────────────────────────┐
│     uses: ExtractionRules (4개 메서드)                                        │
│     file: app/rules/extraction_rules.py  ←──── sync_rules.py ←── ruleautomatker/rules/
│                                                                               │
├── core/converter.py ──────────────────────────────────────────────────────────┤
│     uses: TABLE_CONVERTERS                                                    │
│     file: ruleautomatker/.claude/skills/code-converter/scripts/convert_codes.py
│                                                                               │
├── core/comparator.py ─────────────────────────────────────────────────────────┤
│     uses: load_model_key_cols, make_row_key, get_active_key_cols, normalize_val
│     file: ruleautomatker/.claude/skills/validator/scripts/model_key_loader.py │
│     data: ruleautomatker/data/models/*.xlsx                                   │
│                                                                               │
└── core/reporter.py ───────────────────────────────────────────────────────────┘
      uses: DEFAULT_SALE_CHNL_CODE, COLUMN_MAPPINGS (base)
      file: ruleautomatker/.claude/skills/xlsx-generator/scripts/generate_upload.py
```

---

## 수정 금지 파일 및 이유

| 파일 | 수정 금지 이유 |
|---|---|
| `extraction_rules.py` | 룰 변경은 ruleautomatker에서만 관리. 수정 시 sync_rules.py로 반영. |
| `convert_codes.py` | TABLE_CONVERTERS 시그니처 변경 시 converter.py 전체 영향 |
| `model_key_loader.py` | normalize_val 로직 변경 시 모든 비교 결과 달라짐 |
| `generate_upload.py` | DEFAULT_SALE_CHNL_CODE, COLUMN_MAPPINGS 변경 시 reporter.py 영향 |

---

## 기반 프로젝트 업데이트 시 대응 방법

```
ruleautomatker 파일 변경
        ↓
1. extraction_rules.py 변경 → python sync_rules.py 실행
2. convert_codes.py 변경 → converter.py에서 import 재확인 (자동 반영)
3. model_key_loader.py 변경 → comparator.py 동작 확인
4. generate_upload.py 변경 → reporter.py COLUMN_MAPPINGS 오버라이드 재확인
5. data/existing/*.xlsx 변경 → app/data/defaults/ 에 재복사
6. data/templates/*.xlsx 변경 → app/data/defaults/templates/ 에 재복사
        ↓
python tests/run_tests.py   # 129개 테스트로 회귀 확인
```
