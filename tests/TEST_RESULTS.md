# 테스트 결과 기록

> `python tests/run_tests.py` 실행 시 자동 기록됩니다.
> 시나리오 명세: [TEST_SCENARIOS.md](TEST_SCENARIOS.md)

---
## ✅ 2026-03-18 19:07:41 — PASS (전체)

| 항목 | 결과 |
|---|---|
| 전체 | 121 |
| 통과 | 121 |
| 실패 | 0 |
| 오류 | 0 |
| 건너뜀 | 0 |
| 소요시간 | 20.50s |

### 통과한 테스트 (121개)

**test_api.py** (21개)
- ✅ `test_health_check`
- ✅ `test_index_html_served`
- ✅ `test_docs_available`
- ✅ `test_create_job`
- ✅ `test_get_job_status`
- ✅ `test_get_nonexistent_job_returns_404`
- ✅ `test_multiple_jobs_independent`
- ✅ `test_upload_mapping_xlsx`
- ✅ `test_upload_mapping_nonexistent_job_returns_404`
- ✅ `test_upload_invalid_file_returns_error`
- ✅ `test_upload_pdf`
- ✅ `test_upload_multiple_pdfs`
- ✅ `test_delete_pdf`
- ✅ `test_delete_nonexistent_pdf_returns_404`
- ✅ `test_upload_gt_s00026`
- ✅ `test_upload_gt_multiple_tables`
- ✅ `test_select_tables`
- ✅ `test_default_tables_all_four`
- ✅ `test_result_nonexistent_job_404`
- ✅ `test_result_idle_job`
- ✅ `test_progress_sse_nonexistent_404`

**test_comparator.py** (32개)
- ✅ `test_detect[\ud310\ub9e4\uc911_\uac00\uc785\ub098\uc774\uc815\ubcf4_0312.xlsx-S00026]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\ub0a9\uae30\uc815\ubcf4.xlsx-S00027]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ub0a9\uc785\uc8fc\uae30\uc815\ubcf4_20240101.xlsx-S00028]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\uac1c\uc2dc\ub098\uc774\uc815\ubcf4.xlsx-S00022]`
- ✅ `test_detect[S00026_template.xlsx-S00026]`
- ✅ `test_detect[S00027_\uc5c5\ub85c\ub4dc\uc591\uc2dd.xlsx-S00027]`
- ✅ `test_detect[unknown_file.xlsx-]`
- ✅ `test_filter_by_isrn_kind_dtcd`
- ✅ `test_umbrella_row_excluded_s00026`
- ✅ `test_no_dtcd_filter_loads_all`
- ✅ `test_nonexistent_file_returns_empty`
- ✅ `test_real_gt_s00026_loads_rows`
- ✅ `test_real_gt_s00026_no_umbrella`
- ✅ `test_real_gt_s00027_loads_rows`
- ✅ `test_real_gt_s00028_loads_rows`
- ✅ `test_returns_fields_for_each_table[S00026]`
- ✅ `test_returns_fields_for_each_table[S00027]`
- ✅ `test_returns_fields_for_each_table[S00028]`
- ✅ `test_returns_fields_for_each_table[S00022]`
- ✅ `test_fallback_to_compare_fields_when_empty_rows`
- ✅ `test_model_key_loader_active`
- ✅ `test_all_match`
- ✅ `test_missing_rows_detected`
- ✅ `test_new_rows_detected`
- ✅ `test_empty_gt_returns_has_gt_false`
- ✅ `test_empty_coded_rows`
- ✅ `test_annotated_rows_have_gt_status`
- ✅ `test_compare_fields_in_result`
- ✅ `test_s00028_comparison`
- ✅ `test_compare_s00026_real_gt`
- ✅ `test_compare_s00027_real_gt`
- ✅ `test_compare_s00028_real_gt`

**test_converter.py** (25개)
- ✅ `test_all_four_tables_loaded`
- ✅ `test_each_converter_is_callable`
- ✅ `test_basic_conversion`
- ✅ `test_insurance_period_code_generated`
- ✅ `test_payment_period_code_generated`
- ✅ `test_gender_code_male`
- ✅ `test_gender_code_female`
- ✅ `test_age_range_preserved`
- ✅ `test_gender_neutral_rows_generated`
- ✅ `test_sub_type_preserved`
- ✅ `test_convert_all_includes_s00026`
- ✅ `test_insurance_period_lifetime`
- ✅ `test_payment_period_5yr`
- ✅ `test_jeonginap_equals_insurance_period`
- ✅ `test_20yr_period_code`
- ✅ `test_monthly_cycle`
- ✅ `test_quarterly_cycle`
- ✅ `test_annual_cycle`
- ✅ `test_lump_sum_cycle`
- ✅ `test_all_four_cycles_present`
- ✅ `test_age_range_preserved`
- ✅ `test_all_rows_converted`
- ✅ `test_multi_table_conversion`
- ✅ `test_empty_table_returns_empty`
- ✅ `test_unknown_table_passthrough`

**test_pipeline.py** (16개)
- ✅ `test_loads_real_mapping_file`
- ✅ `test_key_is_pdf_filename`
- ✅ `test_entry_has_required_fields`
- ✅ `test_prod_sale_nm_in_entries`
- ✅ `test_dtcd_is_string_of_int`
- ✅ `test_multiple_entries_per_pdf`
- ✅ `test_exact_match`
- ✅ `test_stem_match_without_extension`
- ✅ `test_no_match_returns_empty`
- ✅ `test_rules_load_successfully`
- ✅ `test_required_methods_exist`
- ✅ `test_hot_reload_same_instance`
- ✅ `test_steps_list`
- ✅ `test_process_real_pdf`
- ✅ `test_process_pdf_with_mapping_entries`
- ✅ `test_process_pdf_xlsx_generated`

**test_reporter.py** (27개)
- ✅ `test_upper_is_dtcd_plus_itcd`
- ✅ `test_default_key_exists`
- ✅ `test_upper_name_from_sale_nm`
- ✅ `test_lower_name_from_prod_sale_nm`
- ✅ `test_empty_entries_returns_empty`
- ✅ `test_multiple_entries_first_is_default`
- ✅ `test_sub_type_fallback_uses_default`
- ✅ `test_creates_file`
- ✅ `test_header_row_4_has_columns`
- ✅ `test_set_code_written`
- ✅ `test_upper_object_code_written`
- ✅ `test_upper_object_name_written`
- ✅ `test_valid_start_date_written`
- ✅ `test_data_starts_at_row_7`
- ✅ `test_all_coded_rows_written`
- ✅ `test_creates_file_with_template`
- ✅ `test_template_set_code_written`
- ✅ `test_template_upper_object_code`
- ✅ `test_other_tables_with_template[S00027]`
- ✅ `test_other_tables_with_template[S00028]`
- ✅ `test_other_tables_with_template[S00022]`
- ✅ `test_basic_preview`
- ✅ `test_preview_with_gt_match`
- ✅ `test_preview_missing_rows_appended`
- ✅ `test_preview_no_gt`
- ✅ `test_preview_text_snippet_truncated`
- ✅ `test_preview_compare_fields_included`


---
## ✅ 2026-03-18 19:08:16 — PASS (전체)

| 항목 | 결과 |
|---|---|
| 전체 | 121 |
| 통과 | 121 |
| 실패 | 0 |
| 오류 | 0 |
| 건너뜀 | 0 |
| 소요시간 | 20.48s |

### 통과한 테스트 (121개)

**test_api.py** (21개)
- ✅ `test_health_check`
- ✅ `test_index_html_served`
- ✅ `test_docs_available`
- ✅ `test_create_job`
- ✅ `test_get_job_status`
- ✅ `test_get_nonexistent_job_returns_404`
- ✅ `test_multiple_jobs_independent`
- ✅ `test_upload_mapping_xlsx`
- ✅ `test_upload_mapping_nonexistent_job_returns_404`
- ✅ `test_upload_invalid_file_returns_error`
- ✅ `test_upload_pdf`
- ✅ `test_upload_multiple_pdfs`
- ✅ `test_delete_pdf`
- ✅ `test_delete_nonexistent_pdf_returns_404`
- ✅ `test_upload_gt_s00026`
- ✅ `test_upload_gt_multiple_tables`
- ✅ `test_select_tables`
- ✅ `test_default_tables_all_four`
- ✅ `test_result_nonexistent_job_404`
- ✅ `test_result_idle_job`
- ✅ `test_progress_sse_nonexistent_404`

**test_comparator.py** (32개)
- ✅ `test_detect[\ud310\ub9e4\uc911_\uac00\uc785\ub098\uc774\uc815\ubcf4_0312.xlsx-S00026]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\ub0a9\uae30\uc815\ubcf4.xlsx-S00027]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ub0a9\uc785\uc8fc\uae30\uc815\ubcf4_20240101.xlsx-S00028]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\uac1c\uc2dc\ub098\uc774\uc815\ubcf4.xlsx-S00022]`
- ✅ `test_detect[S00026_template.xlsx-S00026]`
- ✅ `test_detect[S00027_\uc5c5\ub85c\ub4dc\uc591\uc2dd.xlsx-S00027]`
- ✅ `test_detect[unknown_file.xlsx-]`
- ✅ `test_filter_by_isrn_kind_dtcd`
- ✅ `test_umbrella_row_excluded_s00026`
- ✅ `test_no_dtcd_filter_loads_all`
- ✅ `test_nonexistent_file_returns_empty`
- ✅ `test_real_gt_s00026_loads_rows`
- ✅ `test_real_gt_s00026_no_umbrella`
- ✅ `test_real_gt_s00027_loads_rows`
- ✅ `test_real_gt_s00028_loads_rows`
- ✅ `test_returns_fields_for_each_table[S00026]`
- ✅ `test_returns_fields_for_each_table[S00027]`
- ✅ `test_returns_fields_for_each_table[S00028]`
- ✅ `test_returns_fields_for_each_table[S00022]`
- ✅ `test_fallback_to_compare_fields_when_empty_rows`
- ✅ `test_model_key_loader_active`
- ✅ `test_all_match`
- ✅ `test_missing_rows_detected`
- ✅ `test_new_rows_detected`
- ✅ `test_empty_gt_returns_has_gt_false`
- ✅ `test_empty_coded_rows`
- ✅ `test_annotated_rows_have_gt_status`
- ✅ `test_compare_fields_in_result`
- ✅ `test_s00028_comparison`
- ✅ `test_compare_s00026_real_gt`
- ✅ `test_compare_s00027_real_gt`
- ✅ `test_compare_s00028_real_gt`

**test_converter.py** (25개)
- ✅ `test_all_four_tables_loaded`
- ✅ `test_each_converter_is_callable`
- ✅ `test_basic_conversion`
- ✅ `test_insurance_period_code_generated`
- ✅ `test_payment_period_code_generated`
- ✅ `test_gender_code_male`
- ✅ `test_gender_code_female`
- ✅ `test_age_range_preserved`
- ✅ `test_gender_neutral_rows_generated`
- ✅ `test_sub_type_preserved`
- ✅ `test_convert_all_includes_s00026`
- ✅ `test_insurance_period_lifetime`
- ✅ `test_payment_period_5yr`
- ✅ `test_jeonginap_equals_insurance_period`
- ✅ `test_20yr_period_code`
- ✅ `test_monthly_cycle`
- ✅ `test_quarterly_cycle`
- ✅ `test_annual_cycle`
- ✅ `test_lump_sum_cycle`
- ✅ `test_all_four_cycles_present`
- ✅ `test_age_range_preserved`
- ✅ `test_all_rows_converted`
- ✅ `test_multi_table_conversion`
- ✅ `test_empty_table_returns_empty`
- ✅ `test_unknown_table_passthrough`

**test_pipeline.py** (16개)
- ✅ `test_loads_real_mapping_file`
- ✅ `test_key_is_pdf_filename`
- ✅ `test_entry_has_required_fields`
- ✅ `test_prod_sale_nm_in_entries`
- ✅ `test_dtcd_is_string_of_int`
- ✅ `test_multiple_entries_per_pdf`
- ✅ `test_exact_match`
- ✅ `test_stem_match_without_extension`
- ✅ `test_no_match_returns_empty`
- ✅ `test_rules_load_successfully`
- ✅ `test_required_methods_exist`
- ✅ `test_hot_reload_same_instance`
- ✅ `test_steps_list`
- ✅ `test_process_real_pdf`
- ✅ `test_process_pdf_with_mapping_entries`
- ✅ `test_process_pdf_xlsx_generated`

**test_reporter.py** (27개)
- ✅ `test_upper_is_dtcd_plus_itcd`
- ✅ `test_default_key_exists`
- ✅ `test_upper_name_from_sale_nm`
- ✅ `test_lower_name_from_prod_sale_nm`
- ✅ `test_empty_entries_returns_empty`
- ✅ `test_multiple_entries_first_is_default`
- ✅ `test_sub_type_fallback_uses_default`
- ✅ `test_creates_file`
- ✅ `test_header_row_4_has_columns`
- ✅ `test_set_code_written`
- ✅ `test_upper_object_code_written`
- ✅ `test_upper_object_name_written`
- ✅ `test_valid_start_date_written`
- ✅ `test_data_starts_at_row_7`
- ✅ `test_all_coded_rows_written`
- ✅ `test_creates_file_with_template`
- ✅ `test_template_set_code_written`
- ✅ `test_template_upper_object_code`
- ✅ `test_other_tables_with_template[S00027]`
- ✅ `test_other_tables_with_template[S00028]`
- ✅ `test_other_tables_with_template[S00022]`
- ✅ `test_basic_preview`
- ✅ `test_preview_with_gt_match`
- ✅ `test_preview_missing_rows_appended`
- ✅ `test_preview_no_gt`
- ✅ `test_preview_text_snippet_truncated`
- ✅ `test_preview_compare_fields_included`


---
## ✅ 2026-03-18 19:09:00 — PASS (전체)

| 항목 | 결과 |
|---|---|
| 전체 | 121 |
| 통과 | 121 |
| 실패 | 0 |
| 오류 | 0 |
| 건너뜀 | 0 |
| 소요시간 | 20.44s |

### 통과한 테스트 (121개)

**test_api.py** (21개)
- ✅ `test_health_check`
- ✅ `test_index_html_served`
- ✅ `test_docs_available`
- ✅ `test_create_job`
- ✅ `test_get_job_status`
- ✅ `test_get_nonexistent_job_returns_404`
- ✅ `test_multiple_jobs_independent`
- ✅ `test_upload_mapping_xlsx`
- ✅ `test_upload_mapping_nonexistent_job_returns_404`
- ✅ `test_upload_invalid_file_returns_error`
- ✅ `test_upload_pdf`
- ✅ `test_upload_multiple_pdfs`
- ✅ `test_delete_pdf`
- ✅ `test_delete_nonexistent_pdf_returns_404`
- ✅ `test_upload_gt_s00026`
- ✅ `test_upload_gt_multiple_tables`
- ✅ `test_select_tables`
- ✅ `test_default_tables_all_four`
- ✅ `test_result_nonexistent_job_404`
- ✅ `test_result_idle_job`
- ✅ `test_progress_sse_nonexistent_404`

**test_comparator.py** (32개)
- ✅ `test_detect[\ud310\ub9e4\uc911_\uac00\uc785\ub098\uc774\uc815\ubcf4_0312.xlsx-S00026]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\ub0a9\uae30\uc815\ubcf4.xlsx-S00027]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ub0a9\uc785\uc8fc\uae30\uc815\ubcf4_20240101.xlsx-S00028]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\uac1c\uc2dc\ub098\uc774\uc815\ubcf4.xlsx-S00022]`
- ✅ `test_detect[S00026_template.xlsx-S00026]`
- ✅ `test_detect[S00027_\uc5c5\ub85c\ub4dc\uc591\uc2dd.xlsx-S00027]`
- ✅ `test_detect[unknown_file.xlsx-]`
- ✅ `test_filter_by_isrn_kind_dtcd`
- ✅ `test_umbrella_row_excluded_s00026`
- ✅ `test_no_dtcd_filter_loads_all`
- ✅ `test_nonexistent_file_returns_empty`
- ✅ `test_real_gt_s00026_loads_rows`
- ✅ `test_real_gt_s00026_no_umbrella`
- ✅ `test_real_gt_s00027_loads_rows`
- ✅ `test_real_gt_s00028_loads_rows`
- ✅ `test_returns_fields_for_each_table[S00026]`
- ✅ `test_returns_fields_for_each_table[S00027]`
- ✅ `test_returns_fields_for_each_table[S00028]`
- ✅ `test_returns_fields_for_each_table[S00022]`
- ✅ `test_fallback_to_compare_fields_when_empty_rows`
- ✅ `test_model_key_loader_active`
- ✅ `test_all_match`
- ✅ `test_missing_rows_detected`
- ✅ `test_new_rows_detected`
- ✅ `test_empty_gt_returns_has_gt_false`
- ✅ `test_empty_coded_rows`
- ✅ `test_annotated_rows_have_gt_status`
- ✅ `test_compare_fields_in_result`
- ✅ `test_s00028_comparison`
- ✅ `test_compare_s00026_real_gt`
- ✅ `test_compare_s00027_real_gt`
- ✅ `test_compare_s00028_real_gt`

**test_converter.py** (25개)
- ✅ `test_all_four_tables_loaded`
- ✅ `test_each_converter_is_callable`
- ✅ `test_basic_conversion`
- ✅ `test_insurance_period_code_generated`
- ✅ `test_payment_period_code_generated`
- ✅ `test_gender_code_male`
- ✅ `test_gender_code_female`
- ✅ `test_age_range_preserved`
- ✅ `test_gender_neutral_rows_generated`
- ✅ `test_sub_type_preserved`
- ✅ `test_convert_all_includes_s00026`
- ✅ `test_insurance_period_lifetime`
- ✅ `test_payment_period_5yr`
- ✅ `test_jeonginap_equals_insurance_period`
- ✅ `test_20yr_period_code`
- ✅ `test_monthly_cycle`
- ✅ `test_quarterly_cycle`
- ✅ `test_annual_cycle`
- ✅ `test_lump_sum_cycle`
- ✅ `test_all_four_cycles_present`
- ✅ `test_age_range_preserved`
- ✅ `test_all_rows_converted`
- ✅ `test_multi_table_conversion`
- ✅ `test_empty_table_returns_empty`
- ✅ `test_unknown_table_passthrough`

**test_pipeline.py** (16개)
- ✅ `test_loads_real_mapping_file`
- ✅ `test_key_is_pdf_filename`
- ✅ `test_entry_has_required_fields`
- ✅ `test_prod_sale_nm_in_entries`
- ✅ `test_dtcd_is_string_of_int`
- ✅ `test_multiple_entries_per_pdf`
- ✅ `test_exact_match`
- ✅ `test_stem_match_without_extension`
- ✅ `test_no_match_returns_empty`
- ✅ `test_rules_load_successfully`
- ✅ `test_required_methods_exist`
- ✅ `test_hot_reload_same_instance`
- ✅ `test_steps_list`
- ✅ `test_process_real_pdf`
- ✅ `test_process_pdf_with_mapping_entries`
- ✅ `test_process_pdf_xlsx_generated`

**test_reporter.py** (27개)
- ✅ `test_upper_is_dtcd_plus_itcd`
- ✅ `test_default_key_exists`
- ✅ `test_upper_name_from_sale_nm`
- ✅ `test_lower_name_from_prod_sale_nm`
- ✅ `test_empty_entries_returns_empty`
- ✅ `test_multiple_entries_first_is_default`
- ✅ `test_sub_type_fallback_uses_default`
- ✅ `test_creates_file`
- ✅ `test_header_row_4_has_columns`
- ✅ `test_set_code_written`
- ✅ `test_upper_object_code_written`
- ✅ `test_upper_object_name_written`
- ✅ `test_valid_start_date_written`
- ✅ `test_data_starts_at_row_7`
- ✅ `test_all_coded_rows_written`
- ✅ `test_creates_file_with_template`
- ✅ `test_template_set_code_written`
- ✅ `test_template_upper_object_code`
- ✅ `test_other_tables_with_template[S00027]`
- ✅ `test_other_tables_with_template[S00028]`
- ✅ `test_other_tables_with_template[S00022]`
- ✅ `test_basic_preview`
- ✅ `test_preview_with_gt_match`
- ✅ `test_preview_missing_rows_appended`
- ✅ `test_preview_no_gt`
- ✅ `test_preview_text_snippet_truncated`
- ✅ `test_preview_compare_fields_included`


---
## ✅ 2026-03-18 19:47:24 — PASS (전체)

| 항목 | 결과 |
|---|---|
| 전체 | 121 |
| 통과 | 121 |
| 실패 | 0 |
| 오류 | 0 |
| 건너뜀 | 0 |
| 소요시간 | 25.07s |

### 통과한 테스트 (121개)

**test_api.py** (21개)
- ✅ `test_health_check`
- ✅ `test_index_html_served`
- ✅ `test_docs_available`
- ✅ `test_create_job`
- ✅ `test_get_job_status`
- ✅ `test_get_nonexistent_job_returns_404`
- ✅ `test_multiple_jobs_independent`
- ✅ `test_upload_mapping_xlsx`
- ✅ `test_upload_mapping_nonexistent_job_returns_404`
- ✅ `test_upload_invalid_file_returns_error`
- ✅ `test_upload_pdf`
- ✅ `test_upload_multiple_pdfs`
- ✅ `test_delete_pdf`
- ✅ `test_delete_nonexistent_pdf_returns_404`
- ✅ `test_upload_gt_s00026`
- ✅ `test_upload_gt_multiple_tables`
- ✅ `test_select_tables`
- ✅ `test_default_tables_all_four`
- ✅ `test_result_nonexistent_job_404`
- ✅ `test_result_idle_job`
- ✅ `test_progress_sse_nonexistent_404`

**test_comparator.py** (32개)
- ✅ `test_detect[\ud310\ub9e4\uc911_\uac00\uc785\ub098\uc774\uc815\ubcf4_0312.xlsx-S00026]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\ub0a9\uae30\uc815\ubcf4.xlsx-S00027]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ub0a9\uc785\uc8fc\uae30\uc815\ubcf4_20240101.xlsx-S00028]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\uac1c\uc2dc\ub098\uc774\uc815\ubcf4.xlsx-S00022]`
- ✅ `test_detect[S00026_template.xlsx-S00026]`
- ✅ `test_detect[S00027_\uc5c5\ub85c\ub4dc\uc591\uc2dd.xlsx-S00027]`
- ✅ `test_detect[unknown_file.xlsx-]`
- ✅ `test_filter_by_isrn_kind_dtcd`
- ✅ `test_umbrella_row_excluded_s00026`
- ✅ `test_no_dtcd_filter_loads_all`
- ✅ `test_nonexistent_file_returns_empty`
- ✅ `test_real_gt_s00026_loads_rows`
- ✅ `test_real_gt_s00026_no_umbrella`
- ✅ `test_real_gt_s00027_loads_rows`
- ✅ `test_real_gt_s00028_loads_rows`
- ✅ `test_returns_fields_for_each_table[S00026]`
- ✅ `test_returns_fields_for_each_table[S00027]`
- ✅ `test_returns_fields_for_each_table[S00028]`
- ✅ `test_returns_fields_for_each_table[S00022]`
- ✅ `test_fallback_to_compare_fields_when_empty_rows`
- ✅ `test_model_key_loader_active`
- ✅ `test_all_match`
- ✅ `test_missing_rows_detected`
- ✅ `test_new_rows_detected`
- ✅ `test_empty_gt_returns_has_gt_false`
- ✅ `test_empty_coded_rows`
- ✅ `test_annotated_rows_have_gt_status`
- ✅ `test_compare_fields_in_result`
- ✅ `test_s00028_comparison`
- ✅ `test_compare_s00026_real_gt`
- ✅ `test_compare_s00027_real_gt`
- ✅ `test_compare_s00028_real_gt`

**test_converter.py** (25개)
- ✅ `test_all_four_tables_loaded`
- ✅ `test_each_converter_is_callable`
- ✅ `test_basic_conversion`
- ✅ `test_insurance_period_code_generated`
- ✅ `test_payment_period_code_generated`
- ✅ `test_gender_code_male`
- ✅ `test_gender_code_female`
- ✅ `test_age_range_preserved`
- ✅ `test_gender_neutral_rows_generated`
- ✅ `test_sub_type_preserved`
- ✅ `test_convert_all_includes_s00026`
- ✅ `test_insurance_period_lifetime`
- ✅ `test_payment_period_5yr`
- ✅ `test_jeonginap_equals_insurance_period`
- ✅ `test_20yr_period_code`
- ✅ `test_monthly_cycle`
- ✅ `test_quarterly_cycle`
- ✅ `test_annual_cycle`
- ✅ `test_lump_sum_cycle`
- ✅ `test_all_four_cycles_present`
- ✅ `test_age_range_preserved`
- ✅ `test_all_rows_converted`
- ✅ `test_multi_table_conversion`
- ✅ `test_empty_table_returns_empty`
- ✅ `test_unknown_table_passthrough`

**test_pipeline.py** (16개)
- ✅ `test_loads_real_mapping_file`
- ✅ `test_key_is_pdf_filename`
- ✅ `test_entry_has_required_fields`
- ✅ `test_prod_sale_nm_in_entries`
- ✅ `test_dtcd_is_string_of_int`
- ✅ `test_multiple_entries_per_pdf`
- ✅ `test_exact_match`
- ✅ `test_stem_match_without_extension`
- ✅ `test_no_match_returns_empty`
- ✅ `test_rules_load_successfully`
- ✅ `test_required_methods_exist`
- ✅ `test_hot_reload_same_instance`
- ✅ `test_steps_list`
- ✅ `test_process_real_pdf`
- ✅ `test_process_pdf_with_mapping_entries`
- ✅ `test_process_pdf_xlsx_generated`

**test_reporter.py** (27개)
- ✅ `test_upper_is_dtcd_plus_itcd`
- ✅ `test_default_key_exists`
- ✅ `test_upper_name_from_sale_nm`
- ✅ `test_lower_name_from_prod_sale_nm`
- ✅ `test_empty_entries_returns_empty`
- ✅ `test_multiple_entries_first_is_default`
- ✅ `test_sub_type_fallback_uses_default`
- ✅ `test_creates_file`
- ✅ `test_header_row_4_has_columns`
- ✅ `test_set_code_written`
- ✅ `test_upper_object_code_written`
- ✅ `test_upper_object_name_written`
- ✅ `test_valid_start_date_written`
- ✅ `test_data_starts_at_row_7`
- ✅ `test_all_coded_rows_written`
- ✅ `test_creates_file_with_template`
- ✅ `test_template_set_code_written`
- ✅ `test_template_upper_object_code`
- ✅ `test_other_tables_with_template[S00027]`
- ✅ `test_other_tables_with_template[S00028]`
- ✅ `test_other_tables_with_template[S00022]`
- ✅ `test_basic_preview`
- ✅ `test_preview_with_gt_match`
- ✅ `test_preview_missing_rows_appended`
- ✅ `test_preview_no_gt`
- ✅ `test_preview_text_snippet_truncated`
- ✅ `test_preview_compare_fields_included`


---
## ✅ 2026-03-18 19:50:33 — PASS (전체)

| 항목 | 결과 |
|---|---|
| 전체 | 129 |
| 통과 | 129 |
| 실패 | 0 |
| 오류 | 0 |
| 건너뜀 | 0 |
| 소요시간 | 24.81s |

### 통과한 테스트 (129개)

**test_api.py** (21개)
- ✅ `test_health_check`
- ✅ `test_index_html_served`
- ✅ `test_docs_available`
- ✅ `test_create_job`
- ✅ `test_get_job_status`
- ✅ `test_get_nonexistent_job_returns_404`
- ✅ `test_multiple_jobs_independent`
- ✅ `test_upload_mapping_xlsx`
- ✅ `test_upload_mapping_nonexistent_job_returns_404`
- ✅ `test_upload_invalid_file_returns_error`
- ✅ `test_upload_pdf`
- ✅ `test_upload_multiple_pdfs`
- ✅ `test_delete_pdf`
- ✅ `test_delete_nonexistent_pdf_returns_404`
- ✅ `test_upload_gt_s00026`
- ✅ `test_upload_gt_multiple_tables`
- ✅ `test_select_tables`
- ✅ `test_default_tables_all_four`
- ✅ `test_result_nonexistent_job_404`
- ✅ `test_result_idle_job`
- ✅ `test_progress_sse_nonexistent_404`

**test_comparator.py** (32개)
- ✅ `test_detect[\ud310\ub9e4\uc911_\uac00\uc785\ub098\uc774\uc815\ubcf4_0312.xlsx-S00026]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\ub0a9\uae30\uc815\ubcf4.xlsx-S00027]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ub0a9\uc785\uc8fc\uae30\uc815\ubcf4_20240101.xlsx-S00028]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\uac1c\uc2dc\ub098\uc774\uc815\ubcf4.xlsx-S00022]`
- ✅ `test_detect[S00026_template.xlsx-S00026]`
- ✅ `test_detect[S00027_\uc5c5\ub85c\ub4dc\uc591\uc2dd.xlsx-S00027]`
- ✅ `test_detect[unknown_file.xlsx-]`
- ✅ `test_filter_by_isrn_kind_dtcd`
- ✅ `test_umbrella_row_excluded_s00026`
- ✅ `test_no_dtcd_filter_loads_all`
- ✅ `test_nonexistent_file_returns_empty`
- ✅ `test_real_gt_s00026_loads_rows`
- ✅ `test_real_gt_s00026_no_umbrella`
- ✅ `test_real_gt_s00027_loads_rows`
- ✅ `test_real_gt_s00028_loads_rows`
- ✅ `test_returns_fields_for_each_table[S00026]`
- ✅ `test_returns_fields_for_each_table[S00027]`
- ✅ `test_returns_fields_for_each_table[S00028]`
- ✅ `test_returns_fields_for_each_table[S00022]`
- ✅ `test_fallback_to_compare_fields_when_empty_rows`
- ✅ `test_model_key_loader_active`
- ✅ `test_all_match`
- ✅ `test_missing_rows_detected`
- ✅ `test_new_rows_detected`
- ✅ `test_empty_gt_returns_has_gt_false`
- ✅ `test_empty_coded_rows`
- ✅ `test_annotated_rows_have_gt_status`
- ✅ `test_compare_fields_in_result`
- ✅ `test_s00028_comparison`
- ✅ `test_compare_s00026_real_gt`
- ✅ `test_compare_s00027_real_gt`
- ✅ `test_compare_s00028_real_gt`

**test_converter.py** (25개)
- ✅ `test_all_four_tables_loaded`
- ✅ `test_each_converter_is_callable`
- ✅ `test_basic_conversion`
- ✅ `test_insurance_period_code_generated`
- ✅ `test_payment_period_code_generated`
- ✅ `test_gender_code_male`
- ✅ `test_gender_code_female`
- ✅ `test_age_range_preserved`
- ✅ `test_gender_neutral_rows_generated`
- ✅ `test_sub_type_preserved`
- ✅ `test_convert_all_includes_s00026`
- ✅ `test_insurance_period_lifetime`
- ✅ `test_payment_period_5yr`
- ✅ `test_jeonginap_equals_insurance_period`
- ✅ `test_20yr_period_code`
- ✅ `test_monthly_cycle`
- ✅ `test_quarterly_cycle`
- ✅ `test_annual_cycle`
- ✅ `test_lump_sum_cycle`
- ✅ `test_all_four_cycles_present`
- ✅ `test_age_range_preserved`
- ✅ `test_all_rows_converted`
- ✅ `test_multi_table_conversion`
- ✅ `test_empty_table_returns_empty`
- ✅ `test_unknown_table_passthrough`

**test_pipeline.py** (16개)
- ✅ `test_loads_real_mapping_file`
- ✅ `test_key_is_pdf_filename`
- ✅ `test_entry_has_required_fields`
- ✅ `test_prod_sale_nm_in_entries`
- ✅ `test_dtcd_is_string_of_int`
- ✅ `test_multiple_entries_per_pdf`
- ✅ `test_exact_match`
- ✅ `test_stem_match_without_extension`
- ✅ `test_no_match_returns_empty`
- ✅ `test_rules_load_successfully`
- ✅ `test_required_methods_exist`
- ✅ `test_hot_reload_same_instance`
- ✅ `test_steps_list`
- ✅ `test_process_real_pdf`
- ✅ `test_process_pdf_with_mapping_entries`
- ✅ `test_process_pdf_xlsx_generated`

**test_reporter.py** (35개)
- ✅ `test_upper_is_dtcd_plus_itcd`
- ✅ `test_default_key_exists`
- ✅ `test_upper_name_from_sale_nm`
- ✅ `test_lower_name_from_prod_sale_nm`
- ✅ `test_empty_entries_returns_empty`
- ✅ `test_multiple_entries_first_is_default`
- ✅ `test_sub_type_fallback_uses_default`
- ✅ `test_lower_object_code_zero_padded`
- ✅ `test_lower_object_code_nondigit_prod_itcd_not_padded`
- ✅ `test_lower_equals_upper_when_no_prod_info`
- ✅ `test_creates_file`
- ✅ `test_header_row_4_has_columns`
- ✅ `test_set_code_written`
- ✅ `test_upper_object_code_written`
- ✅ `test_upper_object_name_written`
- ✅ `test_valid_start_date_written`
- ✅ `test_data_starts_at_row_7`
- ✅ `test_lower_object_code_written`
- ✅ `test_sale_chnl_code_written`
- ✅ `test_valid_end_date_written`
- ✅ `test_all_coded_rows_written`
- ✅ `test_creates_file_with_template`
- ✅ `test_template_set_code_written`
- ✅ `test_template_upper_object_code`
- ✅ `test_s00022_fpin_spin_fields_written`
- ✅ `test_s00022_no_template_has_correct_headers`
- ✅ `test_other_tables_with_template[S00027]`
- ✅ `test_other_tables_with_template[S00028]`
- ✅ `test_other_tables_with_template[S00022]`
- ✅ `test_basic_preview`
- ✅ `test_preview_with_gt_match`
- ✅ `test_preview_missing_rows_appended`
- ✅ `test_preview_no_gt`
- ✅ `test_preview_text_snippet_truncated`
- ✅ `test_preview_compare_fields_included`


---
## ❌ 2026-03-18 20:20:59 — FAIL (전체)

| 항목 | 결과 |
|---|---|
| 전체 | 129 |
| 통과 | 128 |
| 실패 | 1 |
| 오류 | 0 |
| 건너뜀 | 0 |
| 소요시간 | 23.50s |

### 실패한 테스트
- ❌ `tests/test_api.py::TestJobLifecycle::test_get_job_status           [  3%]`
- ❌ `tests/test_api.py::TestJobLifecycle::test_get_job_status - assert True...`

<details><summary>실패 상세 로그</summary>

```
FAILED tests/test_api.py::TestJobLifecycle::test_get_job_status - assert True...
======================= 1 failed, 128 passed in 23.50s ========================
```

</details>


---
## ✅ 2026-03-18 20:21:50 — PASS (전체)

| 항목 | 결과 |
|---|---|
| 전체 | 129 |
| 통과 | 129 |
| 실패 | 0 |
| 오류 | 0 |
| 건너뜀 | 0 |
| 소요시간 | 25.33s |

### 통과한 테스트 (129개)

**test_api.py** (21개)
- ✅ `test_health_check`
- ✅ `test_index_html_served`
- ✅ `test_docs_available`
- ✅ `test_create_job`
- ✅ `test_get_job_status`
- ✅ `test_get_nonexistent_job_returns_404`
- ✅ `test_multiple_jobs_independent`
- ✅ `test_upload_mapping_xlsx`
- ✅ `test_upload_mapping_nonexistent_job_returns_404`
- ✅ `test_upload_invalid_file_returns_error`
- ✅ `test_upload_pdf`
- ✅ `test_upload_multiple_pdfs`
- ✅ `test_delete_pdf`
- ✅ `test_delete_nonexistent_pdf_returns_404`
- ✅ `test_upload_gt_s00026`
- ✅ `test_upload_gt_multiple_tables`
- ✅ `test_select_tables`
- ✅ `test_default_tables_all_four`
- ✅ `test_result_nonexistent_job_404`
- ✅ `test_result_idle_job`
- ✅ `test_progress_sse_nonexistent_404`

**test_comparator.py** (32개)
- ✅ `test_detect[\ud310\ub9e4\uc911_\uac00\uc785\ub098\uc774\uc815\ubcf4_0312.xlsx-S00026]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\ub0a9\uae30\uc815\ubcf4.xlsx-S00027]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ub0a9\uc785\uc8fc\uae30\uc815\ubcf4_20240101.xlsx-S00028]`
- ✅ `test_detect[\ud310\ub9e4\uc911_\ubcf4\uae30\uac1c\uc2dc\ub098\uc774\uc815\ubcf4.xlsx-S00022]`
- ✅ `test_detect[S00026_template.xlsx-S00026]`
- ✅ `test_detect[S00027_\uc5c5\ub85c\ub4dc\uc591\uc2dd.xlsx-S00027]`
- ✅ `test_detect[unknown_file.xlsx-]`
- ✅ `test_filter_by_isrn_kind_dtcd`
- ✅ `test_umbrella_row_excluded_s00026`
- ✅ `test_no_dtcd_filter_loads_all`
- ✅ `test_nonexistent_file_returns_empty`
- ✅ `test_real_gt_s00026_loads_rows`
- ✅ `test_real_gt_s00026_no_umbrella`
- ✅ `test_real_gt_s00027_loads_rows`
- ✅ `test_real_gt_s00028_loads_rows`
- ✅ `test_returns_fields_for_each_table[S00026]`
- ✅ `test_returns_fields_for_each_table[S00027]`
- ✅ `test_returns_fields_for_each_table[S00028]`
- ✅ `test_returns_fields_for_each_table[S00022]`
- ✅ `test_fallback_to_compare_fields_when_empty_rows`
- ✅ `test_model_key_loader_active`
- ✅ `test_all_match`
- ✅ `test_missing_rows_detected`
- ✅ `test_new_rows_detected`
- ✅ `test_empty_gt_returns_has_gt_false`
- ✅ `test_empty_coded_rows`
- ✅ `test_annotated_rows_have_gt_status`
- ✅ `test_compare_fields_in_result`
- ✅ `test_s00028_comparison`
- ✅ `test_compare_s00026_real_gt`
- ✅ `test_compare_s00027_real_gt`
- ✅ `test_compare_s00028_real_gt`

**test_converter.py** (25개)
- ✅ `test_all_four_tables_loaded`
- ✅ `test_each_converter_is_callable`
- ✅ `test_basic_conversion`
- ✅ `test_insurance_period_code_generated`
- ✅ `test_payment_period_code_generated`
- ✅ `test_gender_code_male`
- ✅ `test_gender_code_female`
- ✅ `test_age_range_preserved`
- ✅ `test_gender_neutral_rows_generated`
- ✅ `test_sub_type_preserved`
- ✅ `test_convert_all_includes_s00026`
- ✅ `test_insurance_period_lifetime`
- ✅ `test_payment_period_5yr`
- ✅ `test_jeonginap_equals_insurance_period`
- ✅ `test_20yr_period_code`
- ✅ `test_monthly_cycle`
- ✅ `test_quarterly_cycle`
- ✅ `test_annual_cycle`
- ✅ `test_lump_sum_cycle`
- ✅ `test_all_four_cycles_present`
- ✅ `test_age_range_preserved`
- ✅ `test_all_rows_converted`
- ✅ `test_multi_table_conversion`
- ✅ `test_empty_table_returns_empty`
- ✅ `test_unknown_table_passthrough`

**test_pipeline.py** (16개)
- ✅ `test_loads_real_mapping_file`
- ✅ `test_key_is_pdf_filename`
- ✅ `test_entry_has_required_fields`
- ✅ `test_prod_sale_nm_in_entries`
- ✅ `test_dtcd_is_string_of_int`
- ✅ `test_multiple_entries_per_pdf`
- ✅ `test_exact_match`
- ✅ `test_stem_match_without_extension`
- ✅ `test_no_match_returns_empty`
- ✅ `test_rules_load_successfully`
- ✅ `test_required_methods_exist`
- ✅ `test_hot_reload_same_instance`
- ✅ `test_steps_list`
- ✅ `test_process_real_pdf`
- ✅ `test_process_pdf_with_mapping_entries`
- ✅ `test_process_pdf_xlsx_generated`

**test_reporter.py** (35개)
- ✅ `test_upper_is_dtcd_plus_itcd`
- ✅ `test_default_key_exists`
- ✅ `test_upper_name_from_sale_nm`
- ✅ `test_lower_name_from_prod_sale_nm`
- ✅ `test_empty_entries_returns_empty`
- ✅ `test_multiple_entries_first_is_default`
- ✅ `test_sub_type_fallback_uses_default`
- ✅ `test_lower_object_code_zero_padded`
- ✅ `test_lower_object_code_nondigit_prod_itcd_not_padded`
- ✅ `test_lower_equals_upper_when_no_prod_info`
- ✅ `test_creates_file`
- ✅ `test_header_row_4_has_columns`
- ✅ `test_set_code_written`
- ✅ `test_upper_object_code_written`
- ✅ `test_upper_object_name_written`
- ✅ `test_valid_start_date_written`
- ✅ `test_data_starts_at_row_7`
- ✅ `test_lower_object_code_written`
- ✅ `test_sale_chnl_code_written`
- ✅ `test_valid_end_date_written`
- ✅ `test_all_coded_rows_written`
- ✅ `test_creates_file_with_template`
- ✅ `test_template_set_code_written`
- ✅ `test_template_upper_object_code`
- ✅ `test_s00022_fpin_spin_fields_written`
- ✅ `test_s00022_no_template_has_correct_headers`
- ✅ `test_other_tables_with_template[S00027]`
- ✅ `test_other_tables_with_template[S00028]`
- ✅ `test_other_tables_with_template[S00022]`
- ✅ `test_basic_preview`
- ✅ `test_preview_with_gt_match`
- ✅ `test_preview_missing_rows_appended`
- ✅ `test_preview_no_gt`
- ✅ `test_preview_text_snippet_truncated`
- ✅ `test_preview_compare_fields_included`

