# Halts Table Dataset Contract `v0_1`

## 1. Dataset Identity

```yaml
dataset_id: halts_table_v0_1
source_dataset_id: halts_v0_1
logical_version: v0_1
domain: data_foundation_outputs
state_component_type: event_context_table
promotion_state: provisional_validated_for_declared_scope
```

Physical target:

```text
E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet
```

## 2. Purpose

`halts_table_v0_1` promotes the already-governed `halts_v0_1` family into a
CAPA 1 output table.

It exists so Event Engine, backtest research, data quality overlays and future
state builders can consume halts through a stable table with:

- stable event ids;
- source lineage;
- event taxonomy;
- quality flags;
- intraday/date-level/regulatory distinctions;
- explicit consumer gates.

It is not a strategy signal and it is not execution truth.

## 3. Source Lineage

Canonical source root:

```text
E:/TSIS/data/Halts/
```

Source file:

```text
E:/TSIS/data/Halts/processed/halts_master_multisource.parquet
```

Source contract:

```text
01_foundations/contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md
```

Source policy:

```text
01_foundations/data_consumption_policies/halts_consumption_policy.md
```

Historical compatibility root:

```text
D:/Halts/
```

`halts_table_v0_1` must derive from the E-root unless a future migration note
explicitly changes source authority.

## 4. Scientific And Institutional Justification

Decision TSIS:

```text
Treat halts as governed event-state context, not as alpha or price data.
```

Direct evidence:

- Nasdaq publishes official trade halt information as exchange/market
  structure event data:
  `https://www.nasdaqtrader.com/trader.aspx?id=TradeHalts`.
- The SEC publishes trading suspension records as regulatory intervention
  evidence:
  `https://www.sec.gov/enforcement-litigation/trading-suspensions`.
- The project-level `halts_v0_1` contract and visual dossier already establish
  that SEC context, date-level events, intraday halts and review overlays must
  not be collapsed into one undifferentiated feature.

Technical obligation:

```text
halts_table must preserve source, event granularity, quality state and consumer
gates so downstream systems cannot use review/context rows as precise intraday
truth.
```

Open limitation:

```text
v0.1 does not prove decision-time availability, live latency, execution
feasibility or ML/RL readiness.
```

## 5. Current Materialization

Expected output:

```text
E:/TSIS/data/data_foundation_outputs/halts_table/
  halts_table_v0_1.parquet
  _halts_table_summary_v0_1.csv
  _halts_table_manifest_v0_1.json
```

Expected source rows at creation:

```text
source rows: 133116
sources: nasdaq, nyse, sec
```

Known source issues preserved as flags:

- source master contains rows with null `halt_date`;
- source master contains rows with future-looking parsed `halt_date` values
  caused by source text parse ambiguity;
- duplicate source event keys exist and are preserved with a row-level
  `halt_event_id`.

These are not silently repaired in v0.1.

## 6. Allowed Consumers

Permitted:

- `event_engine`
- `data_quality_report`
- `data_audit_overlay`
- `forensic_review`
- `daily_event_context`
- `research_only`

Conditionally permitted:

- `backtest_event_mask_candidate`, only when
  `valid_for_backtest_event_mask_candidate = true` and decision-time
  availability is declared.
- `backtest_extended`, with all flags preserved.
- `ml_flagged`, only with leakage controls and lagged availability.
- `execution_simulator`, context only; never execution truth.

Prohibited:

- `strategy_alpha`
- `ml_primary`
- `rl_allowed`
- `live_downstream_candidate`
- treating absence of halt as proof that market data is clean.

## 7. Quality Policy

Good:

- `good_full_intraday_event`
- `good_date_level_event`
- `regulatory_context_only` for regulatory/date-level context only

Review:

- `review_partial_identity`
- `parse_suspect_flag = true`
- `timestamp_order_review_flag = true`
- `future_date_flag = true`

Bad:

- `bad_unusable_event`
- missing source/date required for the source family

## 8. Known Limitations

- v0.1 does not materialize UTC-normalized event timestamps.
- v0.1 does not repair source parse anomalies.
- v0.1 does not materialize visual overlay buckets from the inspection dossier.
- v0.1 does not establish decision-time availability.
- v0.1 does not authorize live, RL or alpha consumption.

## 9. Promotion Requirements

Before stronger downstream promotion:

- add executable availability/leakage tests;
- add UTC timestamp policy if consumers require UTC;
- connect visual overlay buckets if used by data quality reports;
- define event mask semantics for backtest;
- define live latency and source arrival semantics for live use.

## 10. Change Policy

Version bump required when:

- source root changes;
- event-state vocabulary changes;
- parse-suspect policy changes;
- timestamp normalization is added;
- visual overlay fields become materialized;
- consumers are expanded.

