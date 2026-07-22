# Financial Quality Report v0.1

## 1. Scope And Role

Family:

```text
financial_v0_1
```

Physical root:

```text
E:/TSIS/data/financial
```

Role:

- standalone fundamentals/context data;
- statements, ratios, operational audit and run evidence;
- not market price authority;
- not a point-in-time feature layer by default.

## 2. Final Status

```text
blocked
```

Foundations completion status:

```text
human_inspector_ready
```

Visual inspection status:

```text
visual_complete
```

Reason:

```text
audit_summary.status = FAIL
```

The family has complete endpoint file coverage, but quality gates fail.

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/financial_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/financial/financial_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/financial_consumption_policy.md` |
| Validators | present as contract | `01_foundations/validators/financial/financial_validators.md` |
| Inspection readout | present | `01_foundations/inspection_dossiers/financial/financial_inspection_readout_v0_1.md` |
| Schemas | present | `01_foundations/canonical_schemas/financial/` |
| Operational audit evidence | present | `E:/TSIS/data/financial/_audit` |
| Operational run evidence | present | `E:/TSIS/data/financial/_run` |
| Dossier evidence assets | present | `01_foundations/inspection_dossiers/financial/evidence_assets/` |
| Visual inspector pack | present | `01_foundations/inspection_dossiers/financial/visual_inspector_pack/financial_visual_inspector_pack_v0_1.md` |
| Good payload examples | present | `01_foundations/inspection_dossiers/financial/good_justification/financial_payload_examples_v0_1.md` |
| Bad/blocking cases | present | `01_foundations/inspection_dossiers/financial/bad_case_evidence_packs/financial_blocking_schema_cases_v0_1.md` |
| Flagged temporal cases | present | `01_foundations/inspection_dossiers/financial/flagged_case_evidence_packs/financial_temporal_cases_v0_1.md` |
| Coverage case evidence | present | `01_foundations/inspection_dossiers/financial/coverage_case_evidence_packs/financial_coverage_cases_v0_1.md` |

## 4. File Structure And Technical Profile

Observed business endpoint files:

| Subfamily | Files | Primary unit |
| --- | ---: | --- |
| `income_statements` | 12,468 | `ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe` |
| `balance_sheets` | 12,468 | `ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe` |
| `cash_flow_statements` | 12,468 | `ticker + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe` |
| `ratios` | 12,468 | `ticker + date` |

Observed technical forms:

- payload files with business rows;
- empty sentinel files with `ticker`, `_empty`, `_dataset`, `_ingested_utc`;
- operational audit CSV/JSON files;
- operational run CSV/JSON files.

## 5. Coverage

Coverage by endpoint:

| Dataset | Expected tickers | Downloaded tickers | Missing | Extra | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| `income_statements` | 12,468 | 12,468 | 0 | 0 | 100.0% |
| `balance_sheets` | 12,468 | 12,468 | 0 | 0 | 100.0% |
| `cash_flow_statements` | 12,468 | 12,468 | 0 | 0 | 100.0% |
| `ratios` | 12,468 | 12,468 | 0 | 0 | 100.0% |

Interpretation:

```text
coverage is complete, quality is not approved
```

## 6. Cleanliness And Interpretability

File-level audit:

| Dataset | Files | Read errors | Rows total | Business rows | Zero-business files | Missing-required files |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `balance_sheets` | 12,468 | 0 | 280,285 | 275,836 | 4,449 | 4,449 |
| `cash_flow_statements` | 12,468 | 0 | 495,784 | 491,339 | 4,445 | 4,445 |
| `income_statements` | 12,468 | 0 | 496,350 | 491,907 | 4,443 | 4,443 |
| `ratios` | 12,468 | 0 | 12,470 | 4,311 | 8,159 | 0 |

Positive technical findings:

- no read errors;
- no missing outputs;
- no extra outputs;
- no multi-file ticker outputs;
- ticker column checks pass;
- `_dataset` checks pass;
- `_ingested_utc` is parseable;
- suspicious page cap count is zero.

Blocking technical findings:

- 13,337 severe issues;
- all severe issues are `missing_required_cols`;
- statement empty sentinel handling is unresolved;
- 3,171 temporal/lifecycle issues.

## 7. Semantic Quality

The main semantic issue is not price-scale or raw-vs-adjusted.

The main semantic issues are:

- point-in-time availability;
- lifecycle alignment;
- CIK/ticker identity;
- empty sentinel classification;
- vendor-derived ratios vs audited statement values.

Statements must use `filing_date` for availability. `period_end` is not decision-time availability.

## 8. Temporal Quality

Temporal status:

| Status | Tickers |
| --- | ---: |
| `OK` | 4,859 |
| `NO_DATA` | 4,438 |
| `ANOMALY_PRE_START` | 2,244 |
| `ANOMALY_POST_END` | 927 |

Blocking issue count:

| Issue | Tickers |
| --- | ---: |
| `ANOMALY_PRE_START` | 2,244 |
| `ANOMALY_POST_END` | 927 |

These must be resolved, filtered or carried as explicit flags before any downstream use.

## 9. Case Evidence

Representative payload:

```text
E:/TSIS/data/financial/income_statements/ticker=A/income_statements_A.parquet
```

Representative empty sentinel:

```text
E:/TSIS/data/financial/income_statements/ticker=AABA/income_statements_AABA.parquet
```

Representative ratio payload:

```text
E:/TSIS/data/financial/ratios/ticker=A/ratios_A.parquet
```

Representative temporal issue examples exist in:

```text
01_foundations/inspection_dossiers/financial/flagged_case_evidence_packs/financial_temporal_cases_v0_1.md
```

Stable evidence assets exist in:

```text
01_foundations/inspection_dossiers/financial/evidence_assets/
```

Visual inspector evidence exists in:

```text
01_foundations/inspection_dossiers/financial/visual_inspector_pack/
```

Casepack reading:

- `good_justification/financial_payload_examples_v0_1.md` documents valid payload and empty-sentinel forms;
- `bad_case_evidence_packs/financial_blocking_schema_cases_v0_1.md` documents the severe `missing_required_cols` blocker;
- `flagged_case_evidence_packs/financial_temporal_cases_v0_1.md` documents temporal/lifecycle populations and examples;
- `coverage_case_evidence_packs/financial_coverage_cases_v0_1.md` documents why 100% endpoint coverage is not a quality pass.
- `visual_inspector_pack/financial_visual_inspector_pack_v0_1.md` documents the same blocker visually with population, coverage, issue distribution, temporal, sentinel, identity and schema/form panels.

## 10. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| `source_validation` | allowed |
| `forensic_review` | allowed |
| `repair_planning` | allowed |
| `schema_review` | allowed |
| `master_daily_table` | blocked |
| `symbol_master` | blocked |
| `backtest_core` | blocked |
| `backtest_extended` | blocked |
| `ml_primary` | blocked |
| `ml_flagged` | blocked |
| `execution_simulator` | blocked |
| `rl_allowed` | blocked |
| `live_downstream_candidate` | blocked |

## 11. Open Debt

Blocking:

- resolve `audit_summary.status = FAIL`;
- classify 13,337 `missing_required_cols` severe issues;
- reconcile empty sentinel schema with audit severity;
- resolve or flag 3,171 temporal issues;
- update root references from `D:/financial` where needed;
- regenerate dossier evidence assets after repair or re-audit.

## 12. Verdict

`financial_v0_1` fails the current data-quality standard for consumption.

It now satisfies the documentation requirement for a blocked family:

- it is visible;
- it is registered;
- it has a contract;
- it has a policy;
- it has validator rules;
- it has a human readout;
- it has a quality report;
- it has a visual inspector pack;
- and its blockers are explicit.

Final verdict:

```text
blocked_for_consumption_until_reaudit_or_repair
```
