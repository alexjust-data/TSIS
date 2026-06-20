# Financial Inspection Readout v0.1

## 1. Verdict

`financial_v0_1` is now documented as a governed but blocked standalone fundamentals/context family.

Final state:

```text
audited_blocked_v0_1
```

Foundations completion status:

```text
human_inspector_ready
```

Visual inspection status:

```text
visual_complete
```

The family has complete endpoint file coverage and readable files, but the operational audit reports:

```text
status = FAIL
```

This blocks master-table, backtest, ML, RL, execution and live consumption.

## 2. Scope

Physical root:

```text
E:/TSIS/data/financial
```

Subfamilies:

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`
- `ratios`
- `_audit`
- `_run`

This readout does not audit or replace `E:/TSIS/data/additional/financials`.

## 3. Authorities

Contracts and registry:

- `../../contract_registry/dataset_contracts/financial_dataset_contract_v0_1.md`
- `../../dataset_registry/financial/financial_registry_entry.yaml`
- `../../data_consumption_policies/financial_consumption_policy.md`
- `../../validators/financial/financial_validators.md`

Schemas:

- `../../canonical_schemas/financial/balance_sheets_schema_contract.md`
- `../../canonical_schemas/financial/cash_flow_statements_schema_contract.md`
- `../../canonical_schemas/financial/income_statements_schema_contract.md`
- `../../canonical_schemas/financial/ratios_schema_contract.md`
- `../../canonical_schemas/financial/operational_audit_schema_contract.md`
- `../../canonical_schemas/financial/operational_run_schema_contract.md`

Data-quality report:

- `../../data_quality_report/families/financial_quality_report_v0_1.md`

Dossier-local evidence:

- `evidence_assets/README.md`
- `evidence_assets/financial_evidence_assets_manifest_v0_1.csv`
- `visual_inspector_pack/README.md`
- `visual_inspector_pack/financial_visual_inspector_pack_v0_1.md`
- `visual_inspector_pack/financial_visual_case_manifest_v0_1.csv`
- `visual_inspector_pack/financial_visual_asset_audit_v0_1.csv`
- `good_justification/financial_payload_examples_v0_1.md`
- `bad_case_evidence_packs/financial_blocking_schema_cases_v0_1.md`
- `flagged_case_evidence_packs/financial_temporal_cases_v0_1.md`
- `coverage_case_evidence_packs/financial_coverage_cases_v0_1.md`
- `build_financial_inspection_pack.md`

## 4. Physical Root Profile

Observed structure:

| Subroot | Dirs | Files | File type |
| --- | ---: | ---: | --- |
| `income_statements` | 12,468 | 12,468 | parquet |
| `balance_sheets` | 12,468 | 12,468 | parquet |
| `cash_flow_statements` | 12,468 | 12,468 | parquet |
| `ratios` | 12,468 | 12,468 | parquet |
| `_audit` | 0 | 8 | csv/json |
| `_run` | 0 | 2 | csv/json |

There are 49,872 endpoint parquet files under the four business subfamilies.

Dossier-local evidence assets summarize:

- audit summary and coverage;
- file-level quality by endpoint;
- severe issue counts and samples;
- temporal status counts and samples;
- payload and empty-sentinel examples;
- run progress and error samples.

## 5. File Structure And Technical Profile

### Statement payload form

Representative payload:

```text
E:/TSIS/data/financial/income_statements/ticker=A/income_statements_A.parquet
```

Observed:

- rows: 143;
- includes `ticker`, `tickers`, `cik`, `period_end`, `filing_date`, `fiscal_quarter`, `fiscal_year`, `timeframe`, `_dataset`, `_ingested_utc`;
- accounting fields are nullable numeric fields.

### Empty sentinel form

Representative sentinel:

```text
E:/TSIS/data/financial/income_statements/ticker=AABA/income_statements_AABA.parquet
```

Observed:

- rows: 1;
- columns: `ticker`, `_empty`, `_dataset`, `_ingested_utc`;
- no business rows.

This sentinel form is described as valid by the schema contracts, but current audit output flags many zero-business statement files as `missing_required_cols`. That mismatch is a blocker until resolved.

### Ratios

Representative payload:

```text
E:/TSIS/data/financial/ratios/ticker=A/ratios_A.parquet
```

Observed:

- rows: 1;
- includes `ticker`, `cik`, `date`, `price`, `average_volume`, `market_cap`, ratio fields, `_dataset`, `_ingested_utc`.

Ratios are vendor-derived snapshots, not audited accounting statements and not OHLCV authority.

## 6. Coverage

Endpoint coverage from `_audit/coverage_by_endpoint.csv`:

| Dataset | Expected tickers | Downloaded tickers | Missing | Extra | Multi-file tickers | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `income_statements` | 12,468 | 12,468 | 0 | 0 | 0 | 100.0% |
| `balance_sheets` | 12,468 | 12,468 | 0 | 0 | 0 | 100.0% |
| `cash_flow_statements` | 12,468 | 12,468 | 0 | 0 | 0 | 100.0% |
| `ratios` | 12,468 | 12,468 | 0 | 0 | 0 | 100.0% |

Interpretation:

- physical endpoint coverage is complete;
- coverage does not imply quality approval.

## 7. File-Level Quality

From `_audit/file_level_audit.csv`:

| Dataset | Files | Read errors | Rows total | Business rows | Zero-business files | Missing-required files |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `balance_sheets` | 12,468 | 0 | 280,285 | 275,836 | 4,449 | 4,449 |
| `cash_flow_statements` | 12,468 | 0 | 495,784 | 491,339 | 4,445 | 4,445 |
| `income_statements` | 12,468 | 0 | 496,350 | 491,907 | 4,443 | 4,443 |
| `ratios` | 12,468 | 0 | 12,470 | 4,311 | 8,159 | 0 |

Other file-level findings:

- `ticker_col_bad = 0`;
- `dataset_col_bad = 0`;
- `ingested_utc_parseable_bad = 0`;
- `suspicious_page_cap = 0`;
- `read_errors = 0`.

## 8. Severe Issues

From `_audit/severe_issues.csv`:

| Dataset | Severe issues |
| --- | ---: |
| `balance_sheets` | 4,449 |
| `cash_flow_statements` | 4,445 |
| `income_statements` | 4,443 |
| `ratios` | 0 |

All observed severe issues are:

```text
missing_required_cols
```

Technical reading:

- the issue appears concentrated in zero-business statement files;
- schema contracts say empty sentinel files are a valid physical form;
- the audit still treats the statement sentinel missing `cik` as severe;
- this is either a real validator defect, a schema/audit mismatch, or a promotion blocker requiring explicit waiver.

Consequence:

- the family cannot be considered clean while this remains unresolved.

## 9. Temporal And Lifecycle Findings

From `_audit/temporal_validation_by_ticker.csv`:

| Temporal status | Tickers |
| --- | ---: |
| `OK` | 4,859 |
| `NO_DATA` | 4,438 |
| `ANOMALY_PRE_START` | 2,244 |
| `ANOMALY_POST_END` | 927 |

From `_audit/temporal_issues.csv`:

| Temporal issue | Tickers |
| --- | ---: |
| `ANOMALY_PRE_START` | 2,244 |
| `ANOMALY_POST_END` | 927 |

Technical reading:

- large mass of financial observations does not align cleanly with lifecycle/reference windows;
- this is expected to involve listing dates, delisting dates, ticker reuse, CIK identity and reference incompleteness;
- it must not be hidden by file coverage.

## 10. Schema Expected Vs Observed

Expected:

- payload statements include identity, period and filing fields;
- payload ratios include ticker/date and ratio fields;
- empty sentinels contain `ticker`, `_empty`, `_dataset`, `_ingested_utc`.

Observed:

- representative payload and sentinel files match those forms;
- file-level audit is parseable and complete;
- operational audit marks statement zero-business files as severe missing-required cases.

Open mismatch:

```text
empty sentinel accepted by schema vs severe missing_required_cols in operational audit
```

This must be reconciled before promotion.

## 11. Consumer Matrix

| Consumer | Status | Reason |
| --- | --- | --- |
| `data_quality_report` | allowed | Audit/reporting use only. |
| `source_validation` | allowed | Needed to resolve failure. |
| `forensic_review` | allowed | Useful for diagnosis. |
| `repair_planning` | allowed | Primary next use. |
| `master_daily_table` | blocked | PIT and audit failures unresolved. |
| `symbol_master` | blocked | CIK/lifecycle conflicts unresolved. |
| `backtest_core` | blocked | Not clean, not PIT-promoted. |
| `backtest_extended` | blocked | Requires filtered promotion contract. |
| `ML/RL/live` | blocked | Audit FAIL and leakage/PIT unresolved. |

## 12. Case Evidence

The dossier now contains concrete human-inspection evidence for all required
financial states:

| Evidence group | Path | Reading |
| --- | --- | --- |
| Good payload examples | `good_justification/financial_payload_examples_v0_1.md` | Shows valid statement, ratio and empty-sentinel physical forms. |
| Blocking schema cases | `bad_case_evidence_packs/financial_blocking_schema_cases_v0_1.md` | Shows the `missing_required_cols` severe mass and the schema/audit sentinel mismatch. |
| Temporal cases | `flagged_case_evidence_packs/financial_temporal_cases_v0_1.md` | Shows `OK`, `NO_DATA`, `ANOMALY_PRE_START` and `ANOMALY_POST_END` populations and examples. |
| Coverage cases | `coverage_case_evidence_packs/financial_coverage_cases_v0_1.md` | Shows 100% endpoint file coverage and why coverage is not a quality pass. |
| Visual inspector pack | `visual_inspector_pack/financial_visual_inspector_pack_v0_1.md` | Shows coverage heatmap, severe issue distribution, temporal timeline, empty sentinel cases, multi-CIK identity review and schema/form matrix. |
| Stable evidence assets | `evidence_assets/` | Contains CSV/JSON summaries and sampled payloads used by this readout. |

This satisfies the human-inspector package requirement because the visual
inspection layer is now present. It does not clear the data-quality blockers.

## 13. Open Debt

Blocking:

- resolve `audit_summary.status = FAIL`;
- reconcile empty sentinel schema with `missing_required_cols` severe issues;
- classify whether the 13,337 severe issues are true data defects or validator/schema mismatch;
- resolve or flag 3,171 temporal/lifecycle issues;
- update or migrate schema paths from `D:/financial` to the current `E:/TSIS/data/financial` root;
- define per-subfamily promotion states.

Non-blocking but required before promotion:

- create executable validator or documented build command;
- regenerate dossier evidence assets after repair or re-audit;
- update changelog when promotion state changes.

## 14. Final Verdict

`financial_v0_1` is not clean and not production-ready.

It is now visible, governed and auditable at the human-inspector level. The
correct data-quality verdict remains:

```text
blocked_for_consumption_until_financial_audit_fail_is_resolved
```
