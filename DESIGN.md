# 보험 사업방법서 추출 웹 애플리케이션 설계 문서

> 작성일: 2026-03-11
> 기반 프로젝트: `d:/code/claudecsw/ruleautomatker`

---

## 1. 요구사항 종합

| 항목 | 결정 |
|------|------|
| 배포 형태 | PyInstaller `.exe` (Python 불필요) |
| 실행 방식 | onedir 폴더 형태 배포 (시작 속도 + AV 차단 최소화) |
| 브라우저 | Edge (Chromium) — Windows 11 기본 |
| 인터넷 여부 | 차단 가능 → 모든 에셋 인라인 번들 (외부 CDN 없음) |
| PDF 원문 확인 | 추출 근거 텍스트 스팬 표시 (이미지 없음) |
| 미리보기 수준 | 추출된 테이블 그리드 + 근거 텍스트 나란히 |
| 배치 결과 | 전체 요약 카드 + 파일별 드릴다운 |
| 테이블 선택 | 4종 모두 포함, UI에서 개별 체크 선택 |
| 데이터 파일 | 매핑 xlsx + 템플릿 xlsx + PDF → 모두 UI 업로드 |
| 상품매핑 | 매핑 파일 먼저 로드 필수, 미로드 시 경고 표시 |
| UI 스타일 | 대시보드형 (요약 카드 + 상세 테이블) |
| GT 비교 | 기존 상품: 일치/불일치 셀 색상. 신규 상품: 추출값만 표시 |
| 다수 파일 처리 | 전체 요약표 + 파일별 드릴다운 |
| 회사 PC 제약 | Python 없음, 인터넷 차단 가능, 관리자 권한 없을 수 있음 |

---

## 2. 기술 스택

```
Backend  : FastAPI + Uvicorn  (exe 내부 내장 서버, localhost:랜덤포트)
Frontend : 단일 index.html   (Bootstrap 5 인라인, vanilla JS)
실시간   : Server-Sent Events (SSE) — 진행상태 스트리밍
Packaging: PyInstaller onedir (~80-120MB 예상)
자동실행  : 서버 기동 후 Edge 자동 오픈 (webbrowser.open)
```

**외부 CDN 없음** — Bootstrap CSS/JS, 아이콘 모두 HTML에 인라인 번들

---

## 3. 폴더 구조

```
d:/code/claudecsw/insurance-web/          ← 별도 프로젝트 폴더
├── app/
│   ├── main.py              # FastAPI 진입점 + 브라우저 자동오픈
│   ├── api/
│   │   ├── upload.py        # POST /api/upload (PDF, 매핑, 템플릿)
│   │   ├── process.py       # POST /api/process + GET /api/progress/{job_id} (SSE)
│   │   └── download.py      # GET /api/download/{job_id}/{filename}
│   ├── core/
│   │   ├── pipeline.py      # STEP 1→3→4→7 오케스트레이션
│   │   ├── extractor.py     # extraction_rules.py 래퍼
│   │   ├── converter.py     # convert_codes.py 래퍼
│   │   └── reporter.py      # 미리보기 데이터 빌더 + xlsx 생성
│   ├── static/
│   │   └── index.html       # SPA (모든 JS/CSS 인라인)
│   └── rules/               # ruleautomatker/rules/ 에서 복사
│       └── extraction_rules.py
├── temp/                    # 처리 임시 디렉토리 (job_id별 하위폴더)
├── requirements.txt
├── build.spec               # PyInstaller 스펙
├── run.py                   # 개발용 실행 진입점
└── sync_rules.py            # rules/ 동기화 스크립트 (룰 업데이트 시 실행)
```

---

## 4. 화면 구성 (대시보드형)

```
┌─────────────────────────────────────────────────────────┐
│  📋 보험 사업방법서 추출기          [매핑파일 로드]  ⚠   │
├──────────────────┬──────────────────────────────────────┤
│  📁 파일 업로드  │  🗂 테이블 선택                       │
│  ┌────────────┐  │  ☑ S00026 가입가능나이                │
│  │ PDF 드롭   │  │  ☑ S00027 보기납기                    │
│  │ 또는 선택  │  │  ☑ S00028 납입주기                    │
│  └────────────┘  │  ☑ S00022 보기개시나이                │
│  [파일 선택]     │                                       │
│  [폴더 선택]     │  [▶ 추출 시작]                        │
├──────────────────┴──────────────────────────────────────┤
│  처리현황    📄 3건  ✅ 2건 완료  ❌ 1건 실패  ⏱ 00:12  │
├─────────────────────────────────────────────────────────┤
│  파일명              S26    S27    S28    S22   상태     │
│  ──────────────────────────────────────────────────────  │
│  상생친구보장보험.pdf  73건   15건   8건    5건  ✅PASS  │
│  e암보험비갱신형.pdf   45건   12건   6건    3건  ✅PASS  │
│  신규상품2026.pdf      28건   10건   5건    -     신규   │
│                                              [전체다운]  │
├─────────────────────────────────────────────────────────┤
│  [선택 파일 미리보기 패널]                               │
│  ┌─────────────────────┐  ┌─────────────────────────┐   │
│  │ 추출 근거 텍스트     │  │ 추출 결과 테이블        │   │
│  │ (근거 구간 하이라이트)│  │ ip  | pp  | g | min|max│   │
│  │                     │  │ X90  N20   남  0   65 ✅ │   │
│  │                     │  │ X90  N20   여  0   60 ✅ │   │
│  └─────────────────────┘  └─────────────────────────┘   │
│                                       [xlsx 다운로드]    │
└─────────────────────────────────────────────────────────┘
```

### 4.1 주요 화면 상태

| 상태 | 표시 |
|------|------|
| 매핑 파일 미로드 | 상단 경고 배너 + 추출 시작 버튼 비활성화 |
| 처리 중 | 파일별 진행 단계 (STEP 1→2→3→4→7) + 스피너 |
| GT 있음 | 일치 행 초록, 불일치 행 빨강, miss 행 노랑 |
| GT 없음 (신규) | "신규" 배지, 색상 구분 없이 추출값만 표시 |
| 처리 실패 | 빨강 ❌ + 에러 메시지 툴팁 |

---

## 5. 처리 파이프라인 설계

```python
# pipeline.py — 각 PDF 처리 흐름 (비동기 + SSE 진행상태)
async def process_pdf(job_id, pdf_path, mapping_db, templates, tables):

    yield progress(job_id, "STEP1", "PDF 텍스트 추출 중...")
    text = extract_pdf_text(pdf_path)          # extract_pdf.py 로직 재사용

    yield progress(job_id, "STEP2", "상품 매핑 조회...")
    entries = lookup_mapping(pdf_path, mapping_db)   # 파일명 기준 직접 조회
    if not entries:
        yield progress(job_id, "WARN", "매핑 없음 — 건너뜀")
        return

    yield progress(job_id, "STEP3", "테이블 추출 중...")
    raw = {}
    for table in tables:
        raw[table] = run_extraction_rules(text, table)   # extraction_rules.py

    yield progress(job_id, "STEP4", "코드 변환 중...")
    coded = {}
    for table, data in raw.items():
        coded[table] = convert_codes(data)               # convert_codes.py

    yield progress(job_id, "STEP7", "xlsx 생성 중...")
    xlsx_path = generate_upload_xlsx(coded, templates, entries)

    yield progress(job_id, "DONE", xlsx_path)
```

### 5.1 API 엔드포인트

| Method | URL | 설명 |
|--------|-----|------|
| POST | `/api/upload` | PDF, 매핑xlsx, 템플릿xlsx 업로드 → `job_id` 반환 |
| POST | `/api/process` | 처리 시작 (테이블 선택, job_id) |
| GET  | `/api/progress/{job_id}` | SSE 스트리밍 진행상태 |
| GET  | `/api/result/{job_id}` | 처리 결과 JSON (미리보기 데이터) |
| GET  | `/api/download/{job_id}/{filename}` | xlsx 파일 다운로드 |
| GET  | `/api/download/{job_id}/all.zip` | 전체 결과 ZIP 다운로드 |

### 5.2 진행 상태 이벤트 (SSE)

```json
{ "file": "상생친구.pdf", "step": "STEP3", "msg": "S00026 추출 중...", "pct": 60 }
{ "file": "상생친구.pdf", "step": "DONE",  "msg": "완료", "pct": 100, "result_url": "/api/result/..." }
```

---

## 6. 재사용 모듈 연결 전략

| 원본 위치 (ruleautomatker) | 웹앱 내 처리 방식 |
|---------------------------|-----------------|
| `rules/extraction_rules.py` | `app/rules/`에 복사 (sync_rules.py로 동기화) |
| `skills/code-converter/scripts/convert_codes.py` | `app/core/converter.py`에서 직접 import |
| `skills/pdf-preprocessor/scripts/extract_pdf.py` | `app/core/extractor.py`에서 핵심 로직만 추출 |
| `skills/xlsx-generator/scripts/generate_upload.py` | `app/core/reporter.py`에서 직접 import |

### sync_rules.py (룰 업데이트 시 실행)

```bash
# ruleautomatker에서 룰 고도화 후 실행
python sync_rules.py
# → ruleautomatker/rules/extraction_rules.py → insurance-web/app/rules/ 복사
```

---

## 7. exe 빌드 계획

```python
# build.spec
a = Analysis(
    ['run.py'],
    datas=[
        ('app/static', 'static'),
        ('app/rules',  'rules'),
    ],
    hiddenimports=[
        'uvicorn.logging', 'uvicorn.loops', 'uvicorn.protocols',
        'uvicorn.lifespan.off', 'uvicorn.protocols.http.auto',
        'pdfplumber', 'openpyxl', 'fastapi',
    ],
)
```

```bash
# 빌드 명령
pyinstaller build.spec --onedir --name insurance-extractor
# 결과: dist/insurance-extractor/ 폴더 → zip으로 배포
```

**onefile 대신 onedir 선택 이유**:
- 실행 시 압축 해제 없어 시작 3-5배 빠름
- 바이러스 백신 차단 가능성 낮음
- 파일 교체(rules 업데이트)가 쉬움

### 실행 흐름

```
insurance-extractor.exe 더블클릭
  → 랜덤 포트 탐색 (8765 → 8766 → ...)
  → Uvicorn 서버 스레드 시작
  → Edge 자동오픈 (localhost:{port})
  → 사용자 인터랙션
  → 창 닫으면 서버 종료
```

---

## 8. requirements.txt

```
fastapi>=0.111
uvicorn>=0.29
python-multipart>=0.0.9   # 파일 업로드
pdfplumber>=0.11
openpyxl>=3.1
pandas>=2.2
```

---

## 9. 구현 단계 (Phase)

| Phase | 내용 | 완료 기준 |
|-------|------|----------|
| 1 | FastAPI 뼈대 + 파일 업로드 + 기본 UI (`index.html`) | 파일 업로드 후 job_id 반환 |
| 2 | 파이프라인 연결 (extraction_rules → convert_codes → xlsx) | 단일 PDF → xlsx 다운로드 |
| 3 | SSE 실시간 진행 + 미리보기 패널 (근거텍스트+추출그리드) | 진행바 + 결과 미리보기 |
| 4 | 다수 파일/폴더 처리 + 전체 ZIP 다운로드 | 폴더 선택 → 전체 다운로드 |
| 5 | PyInstaller 빌드 + Edge 자동오픈 테스트 | exe 더블클릭으로 실행 |
| 6 | 데모 시나리오 최적화 (GT 비교, 신규상품, UI polish) | 데모 시연 가능 수준 |

---

## 10. 데모 시나리오

1. **기존 상품**: `상생친구보장보험.pdf` 업로드 → 추출 → GT 대비 70/73 일치 표시
2. **신규 상품**: 새 PDF 업로드 → 매핑 없음 경고 → DTCD 입력 → 추출 → 결과만 표시
3. **배치**: 폴더 선택 → 3개 PDF 동시 처리 → 요약 카드 → 전체 ZIP 다운로드

---

*설계 문서 v1.0 — 인터뷰 기반 작성*
