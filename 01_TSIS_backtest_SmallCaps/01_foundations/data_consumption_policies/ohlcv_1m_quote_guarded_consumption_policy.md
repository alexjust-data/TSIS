# ohlcv_1m_quote_guarded Consumption Policy

Status: `candidate_policy`

Date: 2026-07-16

## 1. Scope

This policy governs consumption of:

```text
dataset_id: ohlcv_1m_quote_guarded_v0_2_candidate
physical_root: C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

This dataset is a quote-guarded derived 1-minute OHLCV price view. It is not raw data and it is not an unrestricted institutional source of truth.

## 2. Primary Rule

Consumers must treat this dataset as:

```text
validated_candidate_for_controlled_downstream_consumption
```

It may be used to build downstream candidate tables, but only when the downstream artifact explicitly records:

- dataset id;
- physical root;
- validation manifest;
- consumption policy;
- run id.

## 3. Allowed Uses

Allowed controlled uses:

- candidate construction of `014 master_intraday_bar_table`;
- candidate construction of `018 intraday_scanner_candidates`;
- intraday price-quality diagnostics;
- raw-vs-quote-guarded forensic comparison;
- controlled research experiments that declare `quote_guarded_1m` as the price view.

## 4. Restricted Uses

The following require an additional downstream contract or promotion review before use:

- production backtests;
- model training datasets;
- offline RL state or reward construction;
- execution simulation;
- any process that treats this dataset as an institutional default.

## 5. Prohibited Uses

Consumers must not:

- overwrite raw 1m data with quote-guarded values;
- use the dataset as a replacement for raw quote or trade evidence;
- silently substitute it for `ohlcv_1m_raw`;
- remove repair provenance columns in institutional outputs;
- publish downstream tables without recording dataset lineage;
- call the dataset globally promoted or unrestricted.

## 6. Required Consumer Behavior

Every downstream consumer must:

1. Declare `price_view = quote_guarded_1m`.
2. Record `dataset_id = ohlcv_1m_quote_guarded_v0_2_candidate`.
3. Record the validation manifest path.
4. Preserve or propagate enough provenance to reconstruct whether a row came from original v0.1 output or from the repaired delta.
5. Fail closed if the validation manifest is missing or not `PASS`.

## 7. Evidence Required Before Consumption

Required validation manifest:

```text
C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate/_validation_runs/qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z/final_manifest_validation.json
```

Required validation values:

```text
status: PASS
errors: 0
warnings: 0
schema_mismatches: 0
candidate_files_seen: 1272004
expected_delta_pairs_observed: 3918
```

## 8. Promotion Boundary

This policy authorizes controlled downstream candidate consumption.

It does not authorize:

- unrestricted institutional promotion;
- raw dataset replacement;
- permanent defaulting of all intraday systems to quote-guarded bars;
- downstream promotion without downstream validation.

## 9. Final Rule

If a consumer cannot prove which price view it used, it must not consume this dataset.
