# Financial Visual Inspector Pack v0.1

Fecha: 2026-06-20
Estado: `visual_complete_v0_1`

## 1. Verdict

This pack closes the missing visual evidence layer for:

```text
financial_v0_1
```

The correct institutional state is:

```text
data_quality_verdict = blocked_by_data_defect
foundations_completion_status = human_inspector_ready
visual_inspection_status = visual_complete
```

The family is now inspectable by a human at the same structural level required
for blocked or review families. It is still not approved for master tables,
backtesting, ML, RL, execution or live consumption.

## 2. Visual Asset Index

| Visual | State | Main question |
| --- | --- | --- |
| [Endpoint coverage heatmap](images/financial_endpoint_coverage_heatmap_v0_1.png) | `blocking_context` | Is complete endpoint coverage the same as usable quality? |
| [Severe issue distribution](images/financial_severe_issue_distribution_v0_1.png) | `blocking` | Where is the severe blocker concentrated? |
| [Temporal issue timeline](images/financial_temporal_issue_timeline_v0_1.png) | `review_blocking` | Do financial observations align with lifecycle windows? |
| [Empty sentinel case panel](images/financial_empty_sentinel_case_panel_v0_1.png) | `blocking` | Are empty files unreadable, or readable sentinels with an audit/schema mismatch? |
| [Multi-CIK identity panel](images/financial_multi_cik_identity_panel_v0_1.png) | `review` | Where can one ticker map to multiple CIK/entity histories? |
| [Payload schema drift panel](images/financial_payload_schema_drift_panel_v0_1.png) | `blocking_context` | Are all files expected to have the same business columns? |

Machine-readable manifests:

- `financial_visual_case_manifest_v0_1.csv`
- `financial_visual_asset_audit_v0_1.csv`

Builder:

- `build_financial_visual_inspector_pack.py`

## 3. Population And Coverage Visual

Image:

```text
images/financial_endpoint_coverage_heatmap_v0_1.png
```

What it shows:

- all four endpoint families have 100% downloaded files;
- statement endpoints have only about 64% business files;
- statement endpoints have about 35-36% zero-business and missing-required files;
- ratios have large zero-business mass but no missing-required severe count in the current audit.

Responds:

```text
Does 100% endpoint coverage mean this family is quality-approved?
```

Answer:

```text
No.
```

Consequence:

Endpoint coverage is a physical completeness fact, not a consumption pass. The
family remains blocked until severe and temporal issues are resolved, waived or
carried through an explicit filtered promotion contract.

## 4. Severe Issue Distribution

Image:

```text
images/financial_severe_issue_distribution_v0_1.png
```

What it shows:

- severe issues are concentrated in `balance_sheets`,
  `cash_flow_statements` and `income_statements`;
- all severe issues are `missing_required_cols`;
- ratios are not the severe-issue driver in this audit.

Responds:

```text
Where is the blocker concentrated?
```

Answer:

```text
In statement endpoint sentinel/schema-audit mismatch.
```

Consequence:

The repair path should not start with market data, price semantics or ratios.
It should first reconcile statement sentinel validity versus
`missing_required_cols` severity.

## 5. Temporal Issue Timeline

Image:

```text
images/financial_temporal_issue_timeline_v0_1.png
```

What it shows:

- temporal status distribution:
  - `OK`: 4,859 tickers;
  - `NO_DATA`: 4,438 tickers;
  - `ANOMALY_PRE_START`: 2,244 tickers;
  - `ANOMALY_POST_END`: 927 tickers;
- sample lifecycle/reference windows versus observed financial windows.

Responds:

```text
Are financial observations aligned to reference lifecycle windows?
```

Answer:

```text
Not reliably enough for consumption.
```

Consequence:

`filing_date` and lifecycle alignment must govern availability. `period_end`
cannot be treated as decision-time availability. This is a PIT and identity
review blocker.

## 6. Empty Sentinel Case Panel

Image:

```text
images/financial_empty_sentinel_case_panel_v0_1.png
```

What it shows:

- statement zero-business files are readable;
- representative sentinel rows contain compact fields such as `ticker`,
  `_empty`, `_dataset` and `_ingested_utc`;
- current audit marks statement sentinel rows as `missing_required_cols`.

Responds:

```text
Are empty files unreadable, or readable sentinel forms with an audit/schema mismatch?
```

Answer:

```text
They are readable sentinel forms, but the current audit treats them as severe.
```

Consequence:

This is the central blocking ambiguity: either the validator is too strict for
valid sentinel files, or the schema needs a stricter promotion rule. Until that
is resolved, the family cannot be consumed.

## 7. Multi-CIK Identity Panel

Image:

```text
images/financial_multi_cik_identity_panel_v0_1.png
```

What it shows:

- multi-CIK examples exist across statement endpoints;
- sample rows show tickers with multiple CIK histories and long observation
  windows;
- this is an identity/lifecycle problem, not a file-read problem.

Responds:

```text
Where can one ticker map to multiple entities or CIK histories?
```

Answer:

```text
In statement endpoints with business rows, especially where lifecycle history is complex.
```

Consequence:

`symbol_master`, PIT features, event discovery and downstream joins must not
consume this family until CIK/ticker identity policy is explicit.

## 8. Payload Schema/Form Panel

Image:

```text
images/financial_payload_schema_drift_panel_v0_1.png
```

What it shows:

- statement payloads include business columns, period fields and filing fields;
- ratio payloads use `ticker + date` style fields;
- sentinel files are intentionally compact and do not carry business columns;
- payload and sentinel forms should not be validated as if they were identical.

Responds:

```text
Are all files expected to have the same business columns?
```

Answer:

```text
No.
```

Consequence:

The audit must distinguish payload rows from sentinel rows. Promotion requires
a validator rule that can separate valid empty sentinel form from true missing
business payload.

## 9. What This Pack Does Not Prove

This visual pack does not prove:

- that the data is clean;
- that `financial_v0_1` is point-in-time safe;
- that ratios are a production feature layer;
- that multi-CIK tickers are resolved;
- that sentinel handling is repaired;
- that downstream consumers may use the family.

It proves only:

```text
the blocked verdict is now visually inspectable and reproducible.
```

## 10. Closure

The financial family now has the required visual inspection layer:

```text
population map: yes
coverage map: yes
quality-state distribution: yes
good/pass visual cases: yes, through payload/schema form panel
flagged/review visual cases: yes, through temporal and multi-CIK panels
bad/blocking visual cases: yes, through severe issue and empty sentinel panels
manifest: yes
asset audit: yes
builder: yes
```

Final operational reading:

```text
human_inspector_ready, but blocked_by_data_defect
```
