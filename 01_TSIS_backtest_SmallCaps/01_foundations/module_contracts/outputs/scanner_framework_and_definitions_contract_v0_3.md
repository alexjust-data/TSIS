# Scanner Framework And Definitions Contract v0.3

## Estado

Tipo: module contract.
Modulo: `01_TSIS_backtest_SmallCaps`.
Ambito: `CAPA 1 - DATA FOUNDATION`.
Status:

```text
builder_implemented_controlled_replay_not_official
```

## Cambio Frente A v0.2

`v0.2` mantenia un denominador llamado `base_in_play_universe_scanner_v0_2`,
pero su semantica real era `base_eligible_smallcap_denominator`.

`v0.3` corrige la ambiguedad:

```text
base_eligible_smallcap_denominator_v0_3
  -> in_play_momentum_candidate_denominator_v0_3
  -> strategy overlays
```

El denominador in-play ya no se define por DAS ni por un perfil broad. Se define
por:

```text
base elegible + movimiento fuerte + volumen/tradability minimo
```

## Configs Activas

```text
configs/data_foundation_outputs/scanner_definitions/base_eligible_smallcap_denominator_v0_3.yaml
configs/data_foundation_outputs/scanner_definitions/in_play_momentum_candidate_denominator_v0_3.yaml
configs/data_foundation_outputs/scanner_definitions/trade_station_like_profile_v0_3.yaml
```

## Base Eligible

```text
common_stock = true
market_cap_usd < 100000000
0.5 < last_price <= 20
data_quality in usable/review states
```

Esta base dice a quien se puede mirar. No prueba in-play.

## In-Play Momentum

Umbral inicial:

```text
minimum_push_move_pct = 50%
```

Replay diario/EOD controlado:

```text
daily_high_vs_prev_close_pct >= 50
OR pct_chg_1d >= 50
OR gap_pct >= 50
```

Gate de actividad:

```text
volume_today >= 500000
OR dollar_volume_today >= 250000
```

Output principal:

```text
selected_in_play_momentum_candidate
```

Compatibilidad:

```text
selected_any_profile = selected_in_play_momentum_candidate
selected_das_research_profile = false
```

## Segment Detection

La promocion intradia oficial requiere builder con extended hours:

```text
04:00-20:00 New York
premarket / regular / afterhours
```

Estado posterior a 2026-06-30:

```text
daily_scanner_candidates_table_v0_3 = daily_eod_proxy
intraday_scanner_candidates_table_v0_1 = controlled_replay_candidate_first_push_builder
```

El builder intradia inicial existe en:

```text
scripts/materialize_intraday_scanner_candidates_table_v0_1.py
```

Mientras no exista una materializacion oficial E-root de 20 anos, v0.1 sigue
siendo `controlled_replay_candidate`. Aun asi, para first-push timing debe
preferirse frente al proxy diario.

## Float

Float puede existir como columna informativa, pero no como filtro global hasta
tener fuente point-in-time auditada.

Dependencia pendiente:

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

Regla operativa:

```text
shares_outstanding no es float.
overview_weighted_shares_outstanding puede ser contexto provisional de shares
outstanding, pero no debe poblar float_shares ni activar filtros de float.
```

## Prohibited Uses

Queda prohibido:

- tratar base elegible como in-play;
- tratar TradeStation-like top 25 como denominador completo;
- usar DAS dentro del scanner global;
- usar float como filtro global sin source/as-of;
- entrenar ML/RL directamente con scanner rows como estado final;
- meter labels, rewards, fills, PnL o decisiones de estrategia en el scanner.

## Builder Y Tests

```text
builder: scripts/materialize_daily_scanner_candidates_table_v0_3.py
test: tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_3.py
long_run_runner: scripts/run_daily_scanner_candidates_materialization_v0_3.ps1
```

## Evidencia Controlada

```text
run_id: daily_scanner_candidates_replay_20250102_20250110_v0_3_0_in_play_momentum
root: C:/TSIS_Data/tests/test_runs/2026-06-30/daily_scanner_candidates_replay_20250102_20250110_v0_3_0_in_play_momentum/
rows: 15323
base_eligible_rows: 6184
selected_in_play_momentum_candidate_rows: 69
selected_trade_station_like_profile_rows: 150
selected_das_research_profile_rows: 0
selected_without_50_move: 0
selected_without_tradability: 0
min_selected_motion_pct: 50.2851
max_selected_motion_pct: 363.6408
```

Este replay es `controlled_replay_candidate`, no materializacion oficial E-root.

## Final Rule

```text
daily_scanner_candidates_table_v0_3 tells TSIS which smallcaps became in-play
under a declared momentum/tradability policy. It is still not market_state,
event_state, label, reward or strategy signal.
```
