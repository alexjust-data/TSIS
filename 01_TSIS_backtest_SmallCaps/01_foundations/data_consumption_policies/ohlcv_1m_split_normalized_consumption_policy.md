# Ohlcv 1m Split-Normalized Consumption Policy v0.1

## 1. Scope

This policy governs:

```text
ohlcv_1m_split_normalized_v0_1
```

Physical root:

```text
E:/TSIS/data/ohlcv_1m_split_normalized
```

Candidate split-affected root:

```text
E:/TSIS/data/ohlcv_1m_split_normalized_full_universe_candidate
```

The candidate root is not the official production root until promotion gates are
closed.

## 2. Primary Rule

`ohlcv_1m_split_normalized_v0_1` is a derived ETL price view for split-sensitive intraday comparisons.

It is not raw 1m data.

It is not dividend-adjusted 1m data.

It is not a full replacement for raw intraday market data.

## 3. Allowed Uses

Allowed:

- split-sensitive cross-session intraday comparisons;
- validation of false split-driven gaps/shocks;
- scoped research consumers that declare the split-normalized view;
- `intraday_regime_features` pilot validation;
- CAPA 1 data-quality reporting.

## 4. Restricted Uses

Restricted:

- full-universe feature production;
- backtest consumers not specifically designed for split-normalized prices;
- any consumer that expects raw execution prices;
- joins against raw daily/quotes/trades without a price-view bridge.

## 5. Prohibited Uses

Prohibited by default:

- raw 1m replacement;
- execution simulation;
- live feed substitute;
- dividend-adjusted economic intraday truth;
- RL state source without dedicated downstream contract;
- certification of raw 1m quality.

## 6. Required Consumer Rules

Consumers must:

- declare `split_normalized` price view;
- preserve upstream raw 1m lineage;
- preserve `future_split_factor`;
- distinguish split-normalized corrections from raw price moves;
- not infer that non-materialized ticker-months are clean;
- not infer that all 1m data problems are solved by this view.

## 7. Current Evidence

Primary evidence:

- `inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_final_readout_v0_1.md`
- `inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md`
- `inspection_dossiers/1m_split_normalized/event_case_evidence_packs/ohlcv_1m_split_normalized_visual_inspector_pack_v0_1.md`
- `contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`
- `dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml`
- `canonical_schemas/ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md`
- `module_contracts/ohlcv_1m_split_normalized_split_affected_materialization_results_v0_1.md`

## 8. Current Status

Current status:

```text
complete_scoped_split_event_audit
```

Candidate materialization status:

```text
materialized_audited_candidate_pending_promotion_gate
```

The split-event audit reports:

- 3,335 event cases;
- 2,280 PASS;
- 0 FAIL;
- remaining non-PASS cases classified as coverage limits, not semantic failures.

The split-affected candidate materialization reports:

- 115,667 manifest rows;
- 115,667 output files present;
- 1,589 tickers in manifest;
- 24 chunks;
- 0 split-audit FAIL cases.

## 9. Final Rule

`ohlcv_1m_split_normalized_v0_1` is allowed for declared split-normalized intraday use.

It must not be used as raw intraday truth or as a universal 1m replacement.
