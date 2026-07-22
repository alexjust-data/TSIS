# Halts Table Validators `v0_1`

## Scope

Validators for:

```text
halts_table_v0_1
```

Physical target:

```text
E:/TSIS/data/data_foundation_outputs/halts_table/
```

## 1. Manifest And Source Checks

Must verify:

- manifest exists;
- summary exists;
- output parquet exists;
- output sha256 matches manifest;
- source master exists;
- source master sha256 matches manifest;
- all contract paths in manifest exist.

Hard failure:

- missing output;
- missing source;
- hash drift;
- missing contract path.

## 2. Schema Checks

Must verify:

- required columns from schema contract exist;
- `halt_event_id` is unique and non-empty;
- `schema_version = halts_table_v0_1`;
- `source_dataset_id = halts_v0_1`;
- `source` values are only `nasdaq`, `nyse`, `sec`;
- `prohibited_as_alpha = true` for all rows.

## 3. Reconciliation Checks

Must verify:

- output row count equals source master row count;
- output source counts equal source master source counts;
- row-level source master hash is stable;
- known source anomalies are surfaced as flags.

Expected v0.1 source counts at materialization:

```text
nasdaq: 118592
nyse: 13178
sec: 1346
all: 133116
```

## 4. Quality-State Checks

Must verify:

- allowed `halt_event_state` vocabulary only;
- allowed `quality_state` vocabulary only;
- bad rows are not valid for event engine;
- review rows are not valid for intraday masks;
- `valid_for_backtest_event_mask_candidate` implies
  `valid_for_intraday_mask`;
- `regulatory_context_only` rows are not intraday masks.

## 5. Known Anomaly Checks

The validator must not hide source anomalies.

It must check that:

- missing halt-date rows are counted;
- future-date parse-suspect rows are counted;
- timestamp-order review rows are counted;
- duplicate source event keys are counted.

## 6. Non-Goals

These validators do not prove:

- live availability;
- execution feasibility;
- alpha;
- RL readiness;
- absence of unreported halts;
- quality of quotes/trades/minute data.

