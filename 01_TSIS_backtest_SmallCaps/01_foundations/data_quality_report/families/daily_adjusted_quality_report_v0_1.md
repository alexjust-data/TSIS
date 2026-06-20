# Daily Adjusted Quality Report v0.1

## 1. Scope And Role

Family:

```text
daily_adjusted_v0_1
```

Physical root:

```text
E:/TSIS/data/ohlcv_daily_adjusted
```

Role:

- derived ETL adjusted daily price view;
- split/dividend-aware daily layer;
- not raw daily, quotes, trades, tape or execution authority.

## 2. Final Status

```text
complete_import_ready
```

The full-universe audit supports institutional use as a derived adjusted daily view.

Foundations completion status:

```text
human_inspector_ready
```

Visual inspection status:

```text
visual_complete
```

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/daily_adjusted_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/daily_adjusted_consumption_policy.md` |
| Schema contract | present | `01_foundations/canonical_schemas/daily/daily_adjusted_schema_contract.md` |
| Full-universe audit | present | `01_foundations/inspection_dossiers/daily/daily_adjusted_full_universe_audit_v0_1.md` |
| Complex corporate-actions tail audit | present | `01_foundations/inspection_dossiers/daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md` |
| Evidence assets | present | `01_foundations/inspection_dossiers/daily/evidence_assets/daily_adjusted_full_universe_audit/` |
| Daily adjusted wrapper dossier | present | `01_foundations/inspection_dossiers/daily_adjusted/README.md` |
| Visual inspector pack | present | `01_foundations/inspection_dossiers/daily_adjusted/visual_inspector_pack/` |

## 4. Coverage And Technical Profile

Full-universe audit:

| Metric | Value |
| --- | ---: |
| raw tickers | 12,494 |
| adjusted tickers | 12,230 |
| raw tickers with files | 12,230 |
| adjusted tickers with files | 12,230 |
| raw year files | 125,438 |
| adjusted year files | 125,438 |
| ticker-with-files coverage | 100.0000% |
| year-file coverage | 100.0000% |
| adjusted rows total | 27,418,158 |

Validation:

| Check | Count |
| --- | ---: |
| missing outputs | 0 |
| extra adjusted outputs | 0 |
| read error files | 0 |
| files missing required columns | 0 |
| nonpositive factor rows | 0 |
| null factor rows | 0 |
| bad price-view rows | 0 |

## 5. Semantic Quality

Activation profile:

| Profile | Tickers |
| --- | ---: |
| neutral control | 9,816 |
| split only | 1,210 |
| dividend only | 861 |
| split and dividend | 343 |

Interpretation:

- physical materialization debt is closed;
- adjusted daily is defended as a derived daily view;
- raw daily remains raw price authority;
- complex corporate-action tails remain governed by separate audit restrictions.

## 6. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| `daily_return_labels` | allowed under label contract |
| `daily adjusted research` | allowed |
| `master_daily_table adjusted view` | allowed if declared |
| `raw daily replacement` | prohibited |
| `execution_simulator` | prohibited |
| `quotes/trades validation` | prohibited |
| `RL/live` | not enabled by this report |

## 7. Verdict

`daily_adjusted_v0_1` meets the data-quality standard as a full-universe derived adjusted daily price view.

It also meets the human-inspector package standard through a formal visual
inspector pack with coverage, validation, factor-integrity, corporate-action
tail and consumer-boundary panels.

Final verdict:

```text
complete_full_universe_derived_daily_adjusted_view
```
