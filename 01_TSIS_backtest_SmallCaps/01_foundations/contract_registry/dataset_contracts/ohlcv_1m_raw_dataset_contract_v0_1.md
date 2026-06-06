# `ohlcv_1m_raw` Dataset Contract v0.1

## 1. Dataset Identity

- `dataset_id`: `ohlcv_1m_raw_v0_1`
- `dataset_family`: `ohlcv_1m`
- `dataset_layer`: `raw_market_bars`
- `status`: `institutional_raw_closeout_reconciled_lt1b`
- `canonical_schema`: `01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_schema_contract.md`
- `registry_entry`: `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_raw_registry_entry.yaml`
- `consumption_policy`: `01_foundations/data_consumption_policies/ohlcv_1m_raw_consumption_policy.md`
- `validators`: `01_foundations/validators/ohlcv_1m/ohlcv_1m_raw_validators.md`

## 2. Purpose

`ohlcv_1m_raw_v0_1` is the institutional raw minute-bar foundation for intraday OHLCV research.

It preserves the observed one-minute bar semantics before split normalization and before downstream feature materialization. Its role is to support:

- forensic inspection of intraday bars;
- reconciliation against `daily`, `trades`, and future quote/fill evidence;
- construction or validation of `ohlcv_1m_split_normalized` layers;
- explicitly flagged exploratory intraday research.

It is not the preferred layer for cross-session adjusted returns, split-safe ML features, or unflagged production backtests.

## 3. Semantic Scope

Each record represents one ticker-minute bar under the raw observed price scale available in the source file.

Expected semantics:

- `ticker`: security identifier represented by the file/partition.
- `timestamp`: minute timestamp for the bar.
- `open`, `high`, `low`, `close`: raw observed OHLC prices.
- `volume`: raw observed traded volume for the minute.
- `transactions`: transaction count where present.
- `vw`: source-provided volume-weighted price where present; this field has known quality debt and must be consumed under the validator policy.

The layer does not guarantee split-adjusted continuity across sessions. Consumers needing split-normalized continuity must use `ohlcv_1m_split_normalized_v0_1`.

## 4. Source Lineage

Primary raw inspection source:

- `D:\ohlcv_1m`

Institutional closeout evidence:

- `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
- `01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`

Related downstream normalized layer:

- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`

## 5. Coverage Snapshot

The `<1B>` institutional recalculation reports:

- `lt1b_tickers_reference`: `4,824`
- `lt1b_current_1m_unique_tickers`: `4,822`
- `lt1b_current_1m_unique_task_keys`: `334,660`
- `lt1b_current_1m_rows`: `334,660`

Operational inheritance buckets:

- `RESCUE_SCHEMA_ONLY`: `19,713` task keys, `5.890456%`
- `RESCUE_SCHEMA_PLUS_VW`: `314,947` task keys, `94.109544%`

Refined `<1B>` quality state:

- `good`: `46,652`, `13.940118%`
- `review`: `75,245`, `22.484014%`
- `bad`: `212,763`, `63.575868%`

The closeout demonstrates that `ohlcv_1m_raw` is institutionally understood, not globally clean.

## 6. Quality Policy

The refined state is authoritative for consumption:

- `good`: eligible for controlled intraday research and baseline raw-bar validation.
- `review`: eligible only for flagged, declared, non-core research or extended diagnostics.
- `bad`: forensic only; not eligible for production research, baseline backtests, or ML training.

The `vw` field is the dominant unresolved raw-layer debt. Consumers using `vw` must respect the severity taxonomy documented in the validators. Consumers not using `vw` still must preserve file-level quality flags and must not promote the raw layer as globally clean.

`RESCUE_SCHEMA_ONLY` is not equivalent to production-good. It is a narrower bucket whose main issue is structural read compatibility, especially ticker encoding/schema merge behavior, as documented in the schema-only readout.

## 7. Allowed Consumers

Allowed with `good` state:

- raw intraday diagnostics;
- minute-bar schema validation;
- split-normalized layer construction checks;
- controlled intraday research where raw scale is explicitly declared.

Allowed with `review` state:

- forensic comparison;
- flagged exploratory notebooks;
- sensitivity analysis that reports inclusion/exclusion policy.

Disallowed unless a later contract supersedes this one:

- unflagged production backtesting;
- unflagged ML training;
- cross-session return engineering;
- split-sensitive regime features;
- execution/fill simulation that assumes quote-level tradability.

## 8. Known Limitations

- The `<1B>` raw closeout remains dominated by `bad` rows after recalculation.
- `vw` quality families are materially present and cannot be ignored.
- The layer is raw observed price scale; it is not adjusted for split continuity.
- A near-complete ticker intersection does not imply full daily membership semantics. `<1B>` claims must still intersect with the universe PTI window.
- Source files may require schema-aware reading to avoid ticker encoding merge conflicts.

## 9. Change Policy

Any promotion of this layer beyond the current status requires:

- a new closeout or validator run with updated counts;
- explicit decision on `vw` consumption semantics;
- confirmation of `<1B>` membership and PTI filtering;
- update of this contract, registry entry, validators, and changelog in the same change.
