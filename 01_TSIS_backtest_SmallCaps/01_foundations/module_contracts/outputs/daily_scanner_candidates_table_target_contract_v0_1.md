# Daily Scanner Candidates Table Target Contract v0.1

## Estado

Tipo: output table target contract.

Modulo: `01_TSIS_backtest_SmallCaps`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status:

```text
builder_implemented_controlled_replay_not_official
```

## Rol

`daily_scanner_candidates_table` es la capa gobernada para reconstruir
candidatos diarios/in-play.

Responde:

```text
que tickers estaban en play bajo este scanner, en esta fecha/as-of, y por que?
```

No responde:

```text
cual es el estado completo?
que estrategia operar?
que outcome ocurrio?
que reward asignar?
hubo fill?
```

## Relacion Con Market State

La relacion correcta es:

```text
daily_scanner_candidates_table
  -> candidate set / in-play discovery
  -> market_state_table builder
  -> event_state_table builder
  -> ML/RL/backtest/evaluator datasets
```

La tabla de scanner dice donde mirar.
El `market_state_table` dice que se sabia legalmente en ese instante.

Lectura obligatoria:

```text
01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
```

## Scanner Framework v0.1

`daily_scanner_candidates_table` no debe gobernarse por un unico scanner
general.

La decision v0.1 es un framework con definiciones separadas:

```text
trade_station_like_scanner_v0_1
broad_in_play_discovery_scanner_v0_1
```

`trade_station_like_scanner_v0_1` reproduce visibilidad operativa humana:

```text
market_cap_usd < 100000000
volume_today > 500000
0.5 < last_price <= 20
rank by pct_chg_1d desc
top_n = 25
```

`broad_in_play_discovery_scanner_v0_1` protege el research contra sesgo de
llegada tardia. No usa `volume_today > 500000` como hard filter universal y no
depende solo de `% change 1D`. Debe permitir entrada por razones como:

```text
volume_acceleration
rvol_to_time
afterhours_breakout
premarket_new_high
prior_day_high_reclaim
range_expansion
news_context
halt_or_reopen_context
```

Ambos son definiciones de scanner, no definiciones de universo completo ni
senales de estrategia.

Configs versionadas:

```text
configs/data_foundation_outputs/scanner_definitions/trade_station_like_scanner_v0_1.yaml
configs/data_foundation_outputs/scanner_definitions/broad_in_play_discovery_scanner_v0_1.yaml
```

## Builder And Controlled Replay v0.1

Builder:

```text
scripts/materialize_daily_scanner_candidates_table.py
```

Builder test:

```text
tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder.py
```

First controlled replay evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/
```

Replay scope:

```text
start_date: 2025-01-02
end_date: 2025-01-10
price_view: daily_raw
as_of_policy: session_close_utc_from_market_calendar
official_e_root_materialization: false
full_universe_claim: false
```

Replay validations:

```text
rows: 30646
sessions: 6
instruments: 2590
selected_trade_station_like_top25_rows: 150
selected_broad_discovery_rows: 3196
broad_selected_below_500k_volume_rows: 2383
duplicate_key_groups: 0
full_universe_claim_true_rows: 0
ml_feature_candidate_rows: 0
rl_state_candidate_rows: 0
live_downstream_candidate_rows: 0
```

Interpretation:

```text
This proves the builder/replay shape and the operational-vs-broad scanner
comparison. It does not promote an official E:/ output and does not make scanner
rows ML/RL states, labels, strategy signals, orders, fills or execution truth.
```

## Output Root Policy

Small controlled samples, smoke runs, notebook demos and test evidence must be
written under:

```text
C:/TSIS_Data/tests/test_runs/<run_date>/<run_id>/
```

Long-range candidate replays, including multi-year or 20-year scanner runs,
must be written under:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/candidate_replays/<run_id>/
```

The official promoted dataset root is reserved:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/daily_scanner_candidates_table_v0_1/
```

Rules:

- never write small notebook/test samples to the official E-root;
- never write long 20-year candidate runs under `C:/TSIS_Data/tests/test_runs/`;
- never reuse the same `output-root` for a different date range unless
  intentionally rebuilding that same `run_id`;
- `--overwrite` may only overwrite the exact declared `output-root`;
- candidate replays under `candidate_replays/` are not official materialized
  outputs and must keep `promotion_level = controlled_replay_candidate` or an
  equivalent non-promoted state;
- official promotion requires a separate promotion step, validator suite,
  manifest review and status update.

Deduplication policy:

```text
master_daily grain = instrument_id + session_date + price_view.
If source aliases create multiple ticker rows for the same instrument/session/
price_view, the builder keeps one deterministic row ordered by data_present,
backtest_core_row_candidate, dollar_volume desc and ticker asc. The run
manifest records source duplicate alias groups and excess rows.
```

## Fuentes Esperadas

Historical replay:

```text
instrument_master_v0_1
market_calendar_v0_1
master_daily_table_v0_1
master_intraday_bar_table_v0_1 where scoped/legal
fundamentals_asof_table_v0_1 for market-cap/float context when legal
short_context_table_v0_1 when source lag/as-of rules permit
regime_context_table_v0_1 when source lag/as-of rules permit
news_context_table_v0_1 for catalyst-aware variants
```

Live/vendor replay requires separate contracts:

```text
broker_live_scanner
vendor_market_snapshot
broker_api_snapshot
```

## Required Output Semantics

Every row must preserve:

- scanner definition and version;
- scanner run id;
- session/as-of timestamp;
- population denominator;
- evaluated count;
- selected count;
- rank and rank metric;
- filters passed/failed;
- candidate reasons;
- volume tier and volume-to-time features when available;
- independent ranks for `pct_chg_1d`, volume acceleration, dollar volume and
  composite in-play score when available;
- flags distinguishing `trade_station_like` visibility from broad discovery;
- source lineage;
- quality state;
- whether the row is selected or only evaluated;
- whether the row was manual research seed;
- downstream usage flags.

## Required Separation

The table must distinguish:

```text
candidate discovery
state construction
event definition
outcome/label construction
strategy decision
execution simulation
```

No builder may collapse these into one output.

## Mandatory Flags

Target default:

```text
valid_for_event_discovery_candidate = true after validators pass
valid_for_market_state_seed_candidate = true after validators pass
valid_for_sampling_lineage = true after validators pass
valid_for_ml_feature_candidate = false by default
valid_for_rl_state_candidate = false by default
valid_for_live_downstream_candidate = false by default
```

Scanner-derived features can become ML/RL features only after a later feature
contract declares legal namespaces and anti-leakage tests.

## Prohibited Uses

Queda prohibido:

- tratar `top_n` como universo completo;
- tratar scanner rows como `market_state_table`;
- entrenar ML/RL directamente con scanner rows como estado final;
- mezclar labels/outcomes/rewards/fills/PnL;
- usar full-session daily values para decisiones intradia sin cutoff policy;
- ocultar seleccion manual como si fuera scanner.

## Contract Stack

```text
schema: 01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
dataset_contract: 01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
consumption_policy: 01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md
registry: 01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
validators: 01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
coverage_policy: 01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
scanner_framework: 01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
scanner_definitions: configs/data_foundation_outputs/scanner_definitions/
```

## Next Required Work

Completed in controlled replay:

1. validate the versioned scanner-definition configs;
2. implement historical replay builder;
3. generate controlled sample only;
4. write manifest, summary and run evidence;
5. run isolated deterministic builder test.

Before official materialization or state-builder promotion:

1. implement full validator suite against the replay output;
2. add visual/forensic evidence if scanner output is used to seed state samples;
3. decide wider replay period and denominator policy;
4. preserve controlled replay as candidate evidence, not official output;
5. update status matrix, changelog and Graphify queue after each semantic
   change.
