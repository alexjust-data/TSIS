# Daily Scanner Candidates Table Target Contract v0.3

## Estado

Tipo: output table target contract.
Modulo: `01_TSIS_backtest_SmallCaps`.
Ambito: `CAPA 1 - DATA FOUNDATION`.
Status:

```text
builder_implemented_controlled_replay_not_official
```

## Rol

`daily_scanner_candidates_table_v0_3` separa:

```text
base_eligible_smallcap_denominator
in_play_momentum_candidate_denominator
strategy_overlay
```

Responde:

```text
que smallcaps fueron evaluadas, cuales pasaron la base elegible y cuales se
convirtieron en in-play momentum candidates bajo una policy declarada?
```

No responde:

```text
que estrategia operar?
que estado completo tenia el mercado?
que outcome/reward ocurrio?
hubo fill?
```

## Grain

```text
scanner_run_id + scanner_definition_id + session_date + as_of_utc + instrument_id
```

`scanner_definition_id`:

```text
base_eligible_smallcap_denominator_v0_3
```

## Required v0.3 Fields

Ademas de columnas heredadas compatibles, el output debe preservar:

```text
selected_in_play_momentum_candidate
daily_high_vs_prev_close_pct
daily_low_vs_prev_close_pct
in_play_motion_pct
in_play_motion_threshold_passed
in_play_volume_tradability_passed
in_play_momentum_min_push_pct
in_play_volume_min_shares
in_play_dollar_volume_min_usd
in_play_detection_scope
in_play_segment_detection_state
in_play_first_push_segment
in_play_first_cross_50_ts
in_play_max_move_segment
reason_daily_high_push_50
reason_premarket_push_50
reason_regular_push_50
reason_afterhours_push_50
reason_extended_session_push_50
```

## Pending Float Context Dependency

`daily_scanner_candidates_table_v0_3` reserva columnas de float, pero TSIS no
tiene todavia una fuente institucional point-in-time de float. Por tanto,
`float_shares`, `float_asof_date` y `float_source` no deben poblarse desde
`overview_weighted_shares_outstanding` ni desde cualquier campo de shares
outstanding.

Tabla pendiente para trabajo posterior:

```text
float_context_table
```

Campos minimos requeridos:

```text
ticker
instrument_id
as_of_date
float_shares
shares_outstanding
free_float_pct
source
source_document
source_field
point_in_time_valid
quality_state
is_estimated
```

Uso permitido futuro:

```text
daily_scanner_candidates_table_v0_3
  LEFT ASOF JOIN float_context_table
  ON instrument_id/ticker AND float_context_table.as_of_date <= scanner.as_of_utc
```

Uso prohibido hasta entonces:

```text
float as hard filter
float as strategy overlay filter
shares_outstanding as substitute for float
```

## Controlled Daily Replay Semantics

Para el replay diario/EOD:

```text
selected_in_play_momentum_candidate =
  all_filters_passed
  AND (
    daily_high_vs_prev_close_pct >= 50
    OR pct_chg_1d >= 50
    OR gap_pct >= 50
  )
  AND (
    volume_today >= 500000
    OR dollar_volume_today >= 250000
  )
```

Limitacion:

```text
daily_eod_proxy detecta que el ticker estuvo in-play durante la sesion, pero no
certifica el segmento exacto ni el primer timestamp del frontside.
```

## Output Root Policy

Small controlled samples, smoke runs, notebook demos and test evidence:

```text
C:/TSIS_Data/tests/test_runs/<run_date>/<run_id>/
```

Long-range candidate replays:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/candidate_replays/<run_id>/
```

Long-range/multi-year executions must use:

```text
scripts/run_daily_scanner_candidates_materialization_v0_3.ps1
```

The runner chunks by year and writes:

```text
pre_manifest
heartbeat
heartbeat.jsonl
pids
logs
_run_summary.json
```

Direct Python builder execution is allowed for small development samples only.

Official promoted root remains reserved:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/daily_scanner_candidates_table_v0_3/
```

## Current Controlled Evidence

```text
python -m pytest C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_3.py -q
```

Controlled replay:

```text
run_id: daily_scanner_candidates_replay_20250102_20250110_v0_3_0_in_play_momentum
root: C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_3_0_in_play_momentum/
rows: 15323
sessions: 6
instruments: 2590
base_eligible_rows: 6184
selected_in_play_momentum_candidate_rows: 69
selected_trade_station_like_profile_rows: 150
selected_das_research_profile_rows: 0
selected_without_50_move: 0
selected_without_tradability: 0
```

Runner smoke:

```text
run_id: daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d
root: C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_v0_3_runner_smoke_20250102_20250110_d/
status: completed
year_window_count: 1
elapsed_seconds: 24
full_universe_claim: false
```

## Promotion Gate

Antes de materializar 20y como candidato serio:

1. usar `scripts/run_daily_scanner_candidates_materialization_v0_3.ps1`;
2. validar `v0.3` contra rango mayor;
3. crear validator fisico para campos nuevos;
4. decidir si `daily_eod_proxy` es suficiente para el uso concreto;
5. construir builder intradia por segmentos antes de promocion para frontside
   intradia institucional;
6. mantener ML/RL/live flags en false hasta composition into state tables.

## Contract Stack

```text
scanner_framework: 01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_3.md
schema: 01_foundations/canonical_schemas/outputs/daily_scanner_candidates_table_schema_contract.md
dataset_contract: 01_foundations/contract_registry/dataset_contracts/daily_scanner_candidates_table_dataset_contract_v0_1.md
consumption_policy: 01_foundations/data_consumption_policies/daily_scanner_candidates_table_consumption_policy.md
registry: 01_foundations/dataset_registry/outputs/daily_scanner_candidates_table_registry_entry.yaml
validators: 01_foundations/validators/outputs/daily_scanner_candidates_table_validators.md
```
