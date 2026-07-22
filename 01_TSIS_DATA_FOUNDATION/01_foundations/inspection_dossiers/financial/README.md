# Financial Inspection Dossier

## Role

This dossier records the human-inspection package for:

```text
financial_v0_1
```

Physical root:

```text
E:/TSIS/data/financial
```

Current data-quality verdict:

```text
blocked_by_data_defect
```

Current foundations completion status:

```text
human_inspector_ready
```

Current visual inspection status:

```text
visual_complete
```

The family is blocked for consumption, but the reason is now inspectable from `01_foundations`.

## Scope

Covered subfamilies:

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`
- `ratios`
- `_audit`
- `_run`

This dossier does not replace:

- `E:/TSIS/data/additional/financials`;
- `reference`;
- market data roots;
- point-in-time feature engineering contracts.

## Structure

```text
inspection_dossiers/financial/
  README.md
  build_financial_inspection_pack.md
  financial_inspection_readout_v0_1.md
  evidence_assets/
    README.md
    financial_*_v0_1.csv/json
    sample_payloads/
  visual_inspector_pack/
    README.md
    financial_visual_inspector_pack_v0_1.md
    financial_visual_case_manifest_v0_1.csv
    financial_visual_asset_audit_v0_1.csv
    build_financial_visual_inspector_pack.py
    images/*.png
  good_justification/
    financial_payload_examples_v0_1.md
  bad_case_evidence_packs/
    financial_blocking_schema_cases_v0_1.md
  flagged_case_evidence_packs/
    financial_temporal_cases_v0_1.md
  coverage_case_evidence_packs/
    financial_coverage_cases_v0_1.md
```

## Reading Order

1. `financial_inspection_readout_v0_1.md`
2. `visual_inspector_pack/financial_visual_inspector_pack_v0_1.md`
3. `visual_inspector_pack/financial_visual_case_manifest_v0_1.csv`
4. `evidence_assets/README.md`
5. `coverage_case_evidence_packs/financial_coverage_cases_v0_1.md`
6. `good_justification/financial_payload_examples_v0_1.md`
7. `bad_case_evidence_packs/financial_blocking_schema_cases_v0_1.md`
8. `flagged_case_evidence_packs/financial_temporal_cases_v0_1.md`
9. `build_financial_inspection_pack.md`

## Key Finding

The downloader achieved complete endpoint file coverage:

```text
4 endpoints x 12,468 tickers = 49,872 endpoint parquet files
```

But the operational audit reports:

```text
status = FAIL
severe_issues = 13,337
temporal_issues = 3,171
```

Therefore the family is inspectable and governed, but not approved for consumption.

## Evidence Rule

Primary physical audit evidence remains in:

```text
E:/TSIS/data/financial/_audit
E:/TSIS/data/financial/_run
```

Compact, dossier-local evidence lives in:

```text
inspection_dossiers/financial/evidence_assets/
```

Visual inspector evidence lives in:

```text
inspection_dossiers/financial/visual_inspector_pack/
```

The dossier-local evidence exists so an inspector can understand the blocked verdict without first opening multi-million-row audit files.

## Final Rule

Do not describe `financial_v0_1` as complete for production.

Describe it as:

```text
human_inspector_ready, but blocked_by_data_defect
```

The reason this is allowed is:

```text
visual_inspection_status = visual_complete
```
