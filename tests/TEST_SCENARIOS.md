# 테스트 시나리오 명세서

> 소스 수정 후 `python tests/run_tests.py` 실행 → 결과는 `tests/TEST_RESULTS.md` 에 자동 기록

---

## 파일 구성

| 파일 | 대상 모듈 | 시나리오 수 |
|---|---|---|
| `test_api.py` | `app/main.py`, `app/api/upload.py` | 21 |
| `test_comparator.py` | `app/core/comparator.py` | 26 |
| `test_converter.py` | `app/core/converter.py` | 25 |
| `test_pipeline.py` | `app/core/pipeline.py` | 15 |
| `test_reporter.py` | `app/core/reporter.py` | 35 |
| **합계** | | **122** |

---

## 1. test_api.py — HTTP API 엔드포인트

### TestBasicEndpoints (3)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 1 | `test_health_check` | GET /health 요청 | 200, `{"status": "ok"}` |
| 2 | `test_index_html_served` | GET / 요청 | 200, text/html, HTML 본문 |
| 3 | `test_docs_available` | GET /docs 요청 | 200 |

### TestJobLifecycle (4)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 4 | `test_create_job` | POST /api/upload | 200, job_id 포함, status="created" |
| 5 | `test_get_job_status` | job 생성 후 GET /api/job/{id} | 200, mapping_loaded=false, pdf_count=0 |
| 6 | `test_get_nonexistent_job_returns_404` | 없는 job_id 조회 | 404 |
| 7 | `test_multiple_jobs_independent` | job 2개 생성 | 각각 다른 id, 독립적으로 조회 가능 |

### TestMappingUpload (3)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 8 | `test_upload_mapping_xlsx` | 실제 mapping.xlsx 업로드 | 200, mapping_loaded=true |
| 9 | `test_upload_mapping_nonexistent_job_returns_404` | 없는 job에 업로드 | 404 |
| 10 | `test_upload_invalid_file_returns_error` | txt 파일 업로드 | 업로드 수락 (처리 시 오류 감지) |

### TestPdfUpload (4)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 11 | `test_upload_pdf` | PDF 1개 업로드 | 200, pdf_count=1 |
| 12 | `test_upload_multiple_pdfs` | PDF 2개 동시 업로드 | 200, pdf_count=2 |
| 13 | `test_delete_pdf` | 업로드 후 삭제 | 200, pdf_count=0 |
| 14 | `test_delete_nonexistent_pdf_returns_404` | 없는 PDF 삭제 | 404 |

### TestGtUpload (2)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 15 | `test_upload_gt_s00026` | GT 파일 1개 업로드 | 200, S00026 감지 |
| 16 | `test_upload_gt_multiple_tables` | GT 파일 4개 업로드 | 200 |

### TestTableSelection (2)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 17 | `test_select_tables` | PUT tables=["S00026","S00028"] | 200, selected_tables={S00026,S00028} |
| 18 | `test_default_tables_all_four` | job 생성 직후 | selected_tables={S00022,S00026,S00027,S00028} |

### TestResultEndpoints (3)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 19 | `test_result_nonexistent_job_404` | 없는 job 결과 조회 | 404 |
| 20 | `test_result_idle_job` | 미처리 job 결과 조회 | 200, status·pdf_results 필드 포함 |
| 21 | `test_progress_sse_nonexistent_404` | 없는 job SSE | 404 |

---

## 2. test_comparator.py — GT 비교 로직

### TestDetectGtTableType (7)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 22 | `test_detect[가입나이_0312.xlsx]` | 파일명에 "가입나이" 포함 | "S00026" |
| 23 | `test_detect[보기납기정보.xlsx]` | 파일명에 "보기납기" 포함 | "S00027" |
| 24 | `test_detect[납입주기정보.xlsx]` | 파일명에 "납입주기" 포함 | "S00028" |
| 25 | `test_detect[보기개시나이정보.xlsx]` | 파일명에 "보기개시나이" 포함 | "S00022" |
| 26 | `test_detect[S00026_template.xlsx]` | 파일명에 "S00026" 포함 | "S00026" |
| 27 | `test_detect[S00027_업로드양식.xlsx]` | 파일명에 "S00027" 포함 | "S00027" |
| 28 | `test_detect[unknown_file.xlsx]` | 알 수 없는 파일명 | "" |

### TestLoadGtRows (4)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 29 | `test_filter_by_isrn_kind_dtcd` | dtcd_list=["2061"], 타DTCD 9999 포함 | 9999 행 제외, 2061만 반환 |
| 30 | `test_umbrella_row_excluded_s00026` | S00026 GT에 MAX_AG=999 행 포함 | MAX_AG=999 행 제외 |
| 31 | `test_no_dtcd_filter_loads_all` | dtcd_list=[] | 전체 행 반환 |
| 32 | `test_nonexistent_file_returns_empty` | 없는 파일 경로 | 빈 리스트 반환 |

### TestLoadGtRowsRealFile (4)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 33 | `test_real_gt_s00026_loads_rows` | 실제 gt_S00026.xlsx + 샘플 DTCD | 1개 이상 행 반환 |
| 34 | `test_real_gt_s00026_no_umbrella` | 실제 gt_S00026.xlsx 로드 | MAX_AG=999 행 없음 |
| 35 | `test_real_gt_s00027_loads_rows` | 실제 gt_S00027.xlsx | 1개 이상 행 반환 |
| 36 | `test_real_gt_s00028_loads_rows` | 실제 gt_S00028.xlsx | 1개 이상 행 반환 |

### TestGetCompareFields (3)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 37~40 | `test_returns_fields_for_each_table[S00026/27/28/22]` | 각 테이블 비교 필드 조회 | 1개 이상 필드 반환 |
| 41 | `test_fallback_to_compare_fields_when_empty_rows` | GT/EX 행 없음 | COMPARE_FIELDS fallback 반환 |
| 42 | `test_model_key_loader_active` | model_key_loader 활성화 시 | 동적 비교키 반환 |

### TestCompare (8)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 43 | `test_all_match` | coded와 GT 완전 일치 | has_gt=true, missing=0, pass=true |
| 44 | `test_missing_rows_detected` | coded 일부만 추출 | missing>0, pass=false |
| 45 | `test_new_rows_detected` | GT에 없는 행 추가 | new 행 존재 |
| 46 | `test_empty_gt_returns_has_gt_false` | GT 빈 리스트 | has_gt=false, pass=None |
| 47 | `test_empty_coded_rows` | 추출 결과 없음 | missing=GT행수, match=0 |
| 48 | `test_annotated_rows_have_gt_status` | compare 실행 | 모든 행에 _gt_status 존재 |
| 49 | `test_compare_fields_in_result` | compare 결과 | compare_fields 키 포함 |
| 50 | `test_s00028_comparison` | S00028 납입주기 비교 | match=2 |

### TestCompareWithRealGT (3)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 51 | `test_compare_s00026_real_gt` | 실제 GT로 end-to-end | summary·annotated_rows 포함 |
| 52 | `test_compare_s00027_real_gt` | S00027 실제 GT | summary 포함 |
| 53 | `test_compare_s00028_real_gt` | S00028 실제 GT | summary 포함 |

---

## 3. test_converter.py — 코드 변환

### TestTableConvertersLoad (2)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 54 | `test_all_four_tables_loaded` | TABLE_CONVERTERS 키 확인 | {S00022,S00026,S00027,S00028} |
| 55 | `test_each_converter_is_callable` | 각 converter callable 확인 | 모두 callable |

### TestConvertS00026 — 가입가능나이 (9)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 56 | `test_basic_conversion` | 4개 raw 행 변환 | 4개 이상 coded 행 |
| 57 | `test_insurance_period_code_generated` | "60세만기" 변환 | ISRN_TERM_INQY_CODE="X60", ISRN_TERM=60 |
| 58 | `test_payment_period_code_generated` | "5년납" 변환 | PAYM_TERM_INQY_CODE="N5", PAYM_TERM=5 |
| 59 | `test_gender_code_male` | "남자" 변환 | MINU_GNDR_CODE="1" 행 존재 |
| 60 | `test_gender_code_female` | "여자" 변환 | MINU_GNDR_CODE="2" 행 존재 |
| 61 | `test_age_range_preserved` | min_age=19, max_age=65 | MIN_AG=19, MAX_AG=65 |
| 62 | `test_gender_neutral_rows_generated` | MIN_AG=0 남/여 쌍 | MINU_GNDR_CODE=None 행 자동 생성 |
| 63 | `test_sub_type_preserved` | sub_type="기본형" | 모든 행 sub_type="기본형" |
| 64 | `test_convert_all_includes_s00026` | convert_all 호출 | S00026 결과 포함 |

### TestConvertS00027 — 보기납기 (4)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 65 | `test_insurance_period_lifetime` | "종신" 변환 | ISRN_TERM_INQY_CODE="A999" 2개 이상 |
| 66 | `test_payment_period_5yr` | "5년납" 변환 | PAYM_TERM_INQY_CODE="N5" |
| 67 | `test_jeonginap_equals_insurance_period` | "전기납" 변환 | PAYM_TERM == ISRN_TERM |
| 68 | `test_20yr_period_code` | "20년만기" 변환 | ISRN_TERM_INQY_CODE="N20" |

### TestConvertS00028 — 납입주기 (5)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 69 | `test_monthly_cycle` | "월납" 변환 | PAYM_CYCL_INQY_CODE="M1" |
| 70 | `test_quarterly_cycle` | "3개월납" 변환 | PAYM_CYCL_INQY_CODE="M3" |
| 71 | `test_annual_cycle` | "연납" 변환 | PAYM_CYCL_INQY_CODE="M12" |
| 72 | `test_lump_sum_cycle` | "일시납" 변환 | PAYM_CYCL_INQY_CODE="M0" |
| 73 | `test_all_four_cycles_present` | 4개 주기 변환 | {M1,M3,M12,M0} 모두 포함 |

### TestConvertS00022 — 보기개시나이 (2)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 74 | `test_age_range_preserved` | min_age=45, max_age=80 | 36개 이상 행, SPIN_STRT_DVSN_VAL에 45·80 포함 |
| 75 | `test_all_rows_converted` | 2개 raw 행 | _convert_error 없음 |

### TestConvertAll (3)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 76 | `test_multi_table_conversion` | 4개 테이블 일괄 변환 | 모두 1개 이상 결과 |
| 77 | `test_empty_table_returns_empty` | 빈 리스트 입력 | 빈 리스트 반환 |
| 78 | `test_unknown_table_passthrough` | 미등록 테이블 | 원본 그대로 반환 |

---

## 4. test_pipeline.py — 파이프라인

### TestLoadMappingDb (6)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 79 | `test_loads_real_mapping_file` | 실제 mapping.xlsx 로드 | len > 0 |
| 80 | `test_key_is_pdf_filename` | DB 키 형식 확인 | .pdf 확장자 or "사업방법서" 포함 |
| 81 | `test_entry_has_required_fields` | 첫 5개 엔트리 필드 | dtcd·itcd·sale_nm·prod_dtcd·prod_itcd 모두 존재 |
| 82 | `test_prod_sale_nm_in_entries` | **핵심 수정 검증** | prod_sale_nm 필드 존재 (LOWER_OBJECT_NAME 기반) |
| 83 | `test_dtcd_is_string_of_int` | dtcd 타입 확인 | 숫자 문자열 |
| 84 | `test_multiple_entries_per_pdf` | 복수 엔트리 PDF | len(entries)>1인 PDF 존재 |

### TestLookupMapping (3)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 85 | `test_exact_match` | 파일명 정확 일치 | 1개 이상 엔트리 |
| 86 | `test_stem_match_without_extension` | 확장자 포함 재조회 | 1개 이상 엔트리 |
| 87 | `test_no_match_returns_empty` | 없는 파일명 | 빈 리스트 |

### TestLoadRules (3)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 88 | `test_rules_load_successfully` | load_rules() 호출 | not None |
| 89 | `test_required_methods_exist` | 4개 메서드 확인 | extract_age_table 등 모두 callable |
| 90 | `test_hot_reload_same_instance` | load_rules() 2회 호출 | 동일 인스턴스 (캐시) |

### TestSteps (1)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 91 | `test_steps_list` | STEPS 리스트 확인 | STEP1~STEP7 포함, 순서 보장 |

### TestProcessPdfSync (3)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 92 | `test_process_real_pdf` | 실제 PDF end-to-end | status≠"error", 이벤트 발생, 테이블 처리됨 |
| 93 | `test_process_pdf_with_mapping_entries` | 처리 결과 구조 | mapping_entries 키 포함 |
| 94 | `test_process_pdf_xlsx_generated` | xlsx 파일 생성 | output_dir에 xlsx 존재 |

---

## 5. test_reporter.py — xlsx 생성 및 미리보기

### TestBuildProductMapping (10)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 95 | `test_upper_is_dtcd_plus_itcd` | dtcd="206", itcd="1001" | upper="2061001" |
| 96 | `test_default_key_exists` | mapping_entries 1개 | \_\_default\_\_ 키 존재 |
| 97 | `test_upper_name_from_sale_nm` | sale_nm="테스트보험(표준체형)" | upper_name 동일 |
| 98 | `test_lower_name_from_prod_sale_nm` | prod_sale_nm="테스트보험" | lower_name 동일 |
| 99 | `test_empty_entries_returns_empty` | 빈 리스트 입력 | {} 반환 |
| 100 | `test_multiple_entries_first_is_default` | 2개 엔트리 | 첫 번째가 \_\_default\_\_ |
| 101 | `test_sub_type_fallback_uses_default` | 없는 sub_type 조회 | \_\_default\_\_ fallback |
| 102 | `test_lower_object_code_zero_padded` | **B7** prod_itcd="1", itcd="001" | lower="2061001" (20611 아님) |
| 103 | `test_lower_object_code_nondigit_prod_itcd_not_padded` | prod_itcd="A01" (문자 포함) | 그대로 사용 → lower="2257A01" |
| 104 | `test_lower_equals_upper_when_no_prod_info` | prod_dtcd/itcd 모두 빈값 | lower == upper |

### TestGenerateXlsxNoTemplate — 템플릿 없음 (11)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 105 | `test_creates_file` | xlsx 생성 | 파일 존재 |
| 106 | `test_header_row_4_has_columns` | 4행 헤더 | UPPER_OBJECT_CODE·SET_CODE 포함 |
| 107 | `test_set_code_written` | **핵심 수정** 7행 데이터 | SET_CODE="S00026" |
| 108 | `test_upper_object_code_written` | **핵심 수정** | UPPER_OBJECT_CODE="2061001" |
| 109 | `test_upper_object_name_written` | **핵심 수정** | UPPER_OBJECT_NAME="테스트보험(표준체형)" |
| 110 | `test_valid_start_date_written` | 유효시작일 기록 | VALID_START_DATE="20260101" |
| 111 | `test_data_starts_at_row_7` | 행 위치 확인 | 6행 비어있음, 7행 데이터 |
| 112 | `test_lower_object_code_written` | **B7** LOWER_OBJECT_CODE 기록 | "2061001" (zero-pad 검증) |
| 113 | `test_sale_chnl_code_written` | SALE_CHNL_CODE 고정값 | "1,2,3,4,7" |
| 114 | `test_valid_end_date_written` | VALID_END_DATE 고정값 | "99991231" |
| 115 | `test_all_coded_rows_written` | 전체 행 기록 | 기록 행수 == coded 행수 |

### TestGenerateXlsxWithTemplate — 실제 템플릿 (8)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 116 | `test_creates_file_with_template` | S00026 템플릿 사용 | 파일 생성 |
| 117 | `test_template_set_code_written` | 템플릿 + 데이터 | SET_CODE="S00026" |
| 118 | `test_template_upper_object_code` | 템플릿 + 데이터 | UPPER_OBJECT_CODE="2061001" |
| 119 | `test_s00022_fpin_spin_fields_written` | **B8** S00022 템플릿 + 데이터 | FPIN_STRT_DVSN_VAL 기록됨 |
| 120 | `test_s00022_no_template_has_correct_headers` | **B8** S00022 템플릿 없음 | 헤더에 FPIN_STRT_DVSN_VAL 포함, MIN_AG 없음 |
| 121~123 | `test_other_tables_with_template[S00027/28/22]` | 나머지 3개 테이블 | 파일 생성, SET_CODE 일치 |

### TestBuildPreview (6)
| # | 메서드 | 시나리오 | 기대 결과 |
|---|---|---|---|
| 124 | `test_basic_preview` | S00026 coded 행 | table_type·count·headers·rows 포함 |
| 125 | `test_preview_with_gt_match` | GT 비교 포함 | has_gt=true, _gt_status in {match,new,missing} |
| 126 | `test_preview_missing_rows_appended` | 일부만 추출 + GT | missing 행 preview에 추가됨 |
| 127 | `test_preview_no_gt` | GT 없음 | has_gt=false, _gt_status=None |
| 128 | `test_preview_text_snippet_truncated` | 5000자 텍스트 | text_snippet ≤ 3000자 |
| 129 | `test_preview_compare_fields_included` | GT 비교 결과 | compare_fields 키 포함 |

---

## 핵심 수정 검증 목록 (회귀 방지)

| # | 버그 | 검증 테스트 |
|---|---|---|
| B1 | GT 필터링 오류 — ISRN_KIND_DTCD 대신 UPPER_OBJECT_CODE로 필터 | `test_filter_by_isrn_kind_dtcd` |
| B2 | S00026 umbrella 행(MAX_AG=999) 미제외 | `test_umbrella_row_excluded_s00026`, `test_real_gt_s00026_no_umbrella` |
| B3 | build_product_mapping upper 오류 (dtcd만, itcd+dtcd 아님) | `test_upper_is_dtcd_plus_itcd` |
| B4 | SET_CODE xlsx 미기록 | `test_set_code_written`, `test_template_set_code_written` |
| B5 | UPPER_OBJECT_NAME xlsx 미기록 | `test_upper_object_name_written` |
| B6 | prod_sale_nm 매핑 미로드 → LOWER_OBJECT_NAME 공백 | `test_prod_sale_nm_in_entries`, `test_lower_name_from_prod_sale_nm` |
| B7 | prod_itcd 단일 숫자 → zero-pad 미적용 → LOWER_OBJECT_CODE 오계산 ("20611" → "2061001") | `test_lower_object_code_zero_padded`, `test_lower_object_code_written` |
| B8 | S00022 COLUMN_MAPPINGS 오류 (MIN_AG/MAX_AG) → FPIN/SPIN 컬럼 미기록 | `test_s00022_fpin_spin_fields_written`, `test_s00022_no_template_has_correct_headers` |
