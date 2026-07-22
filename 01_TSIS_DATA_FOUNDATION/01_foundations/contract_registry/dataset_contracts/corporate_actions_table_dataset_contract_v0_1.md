# Corporate Actions Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: corporate_actions_table_v0_1
family: data_foundation_outputs
class: reference/context table
grain: instrument_id + ticker + action_type + action_date + source_system
```

## 2. Purpose

`corporate_actions_table` gives TSIS one governed place to query corporate
actions relevant to CAPA 1:

- splits;
- dividends;
- ticker changes.

It exists to prevent price, event and label pipelines from guessing whether a
large move is market behavior or corporate-action mechanics.

## 3. Source Lineage

Primary source layer:

- `E:/TSIS/data/reference/splits`
- `E:/TSIS/data/reference/dividends`
- `E:/TSIS/data/reference/events`

Secondary/reconciliation source layer:

- `E:/TSIS/data/additional/corporate_actions/splits`
- `E:/TSIS/data/additional/corporate_actions/dividends`
- `E:/TSIS/data/additional/corporate_actions/ticker_events`

Identity source:

- `instrument_master_v0_1`

Rows are restricted to tickers present in `instrument_master_v0_1`.

## 4. Physical Layout

```text
E:/TSIS/data/data_foundation_outputs/corporate_actions_table/
  corporate_actions_table_v0_1.parquet
  _corporate_actions_table_summary_v0_1.csv
  _corporate_actions_table_manifest_v0_1.json
```

## 5. Materialized State

```text
rows: 104757
tickers: 3621
instrument_ids: 3497
split rows: 6630
dividend rows: 92033
ticker_change rows: 6094
reference rows: 52267
additional rows: 52490
build_run_id: corporate_actions_table_v0_1_20260622T144845Z
output_sha256: 01989eb301a2cdd83e297fbf6384e0bd4d5b4fb300bdccee6b1adbde87d5e4ce
hard_fail_count: 0
```

## 6. Allowed Consumers

Permitted:

- `master_daily_table`
- `master_intraday_bar_table`
- `data_quality_report`
- `dataset_certification_matrix`
- `event_engine`
- `research_only`
- `forensic_only`

Conditionally permitted:

- `backtest_core`, only as adjustment/event context after joining to an
  approved price view.
- `ml_flagged`, only when action flags are explicit and leakage-controlled.

Restricted:

- `execution_simulator`
- `rl_allowed`
- `live_downstream_candidate`

## 7. Quality Policy

Good:

- action date parseable;
- action type in vocabulary;
- instrument identity resolved;
- split ratios positive;
- dividend cash amounts non-negative;
- output manifest/hash reconciles.

Review:

- action outside current instrument valid window;
- source overlap between `reference` and `additional`;
- ticker changes before operational valid window;
- future-dated actions.

Bad:

- duplicate corporate_action_id;
- missing action date;
- missing instrument identity;
- invalid split ratio;
- negative dividend amount.

## 8. Known Limitations

- v0.1 does not solve full economic continuity across ticker changes.
- v0.1 keeps `reference` and `additional` observations separately rather than
  deduplicating them into a single canonical event.
- v0.1 does not compute final adjusted prices.
- Placeholder empty rows from source files are excluded from the table.

## 9. Change Policy

Version bump required when:

- action type vocabulary changes;
- source priority changes;
- deduplication policy changes;
- instrument identity semantics change;
- adjusted-price methodology is embedded into the table.

