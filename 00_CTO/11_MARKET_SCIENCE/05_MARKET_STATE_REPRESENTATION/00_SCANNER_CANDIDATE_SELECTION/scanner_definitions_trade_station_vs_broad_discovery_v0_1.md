# Scanner Definitions v0.1 Historical Note

Fecha: 2026-06-30
Estado: historical_reference

## 1. Nota de revision 2026-06-30

Este documento conservaba la definicion v0.1:

```text
trade_station_like_scanner_v0_1
broad_in_play_discovery_scanner_v0_1
```

Esa lectura queda degradada a referencia historica del primer replay
controlado.

La decision activa vive en:

```text
scanner_base_universe_and_profiles_contract_v0_2.md
```

La arquitectura activa es:

```text
base_in_play_universe_scanner_v0_2
-> profiles / views / rankings
```

No se deben crear dos universos de scanner independientes salvo experimento
versionado y justificado.

## 2. Scanner base v0.2

Pregunta:

```text
Que instrumentos pertenecen a la poblacion smallcap/microcap observable que TSIS
debe considerar para candidate selection?
```

Hard filters:

```text
common_stock = true
market_cap_usd < 100000000
0.5 < last_price <= 20
data_quality in usable/review
```

No son hard filters universales:

```text
volume_today >= 500000
pct_chg_1d top 25
relative_volume threshold
float threshold
news present
afterhours breakout present
premarket new high present
```

## 3. Perfiles activos

| Perfil | Pregunta | Seleccion / ranking | Uso |
| --- | --- | --- | --- |
| `trade_station_like_profile_v0_2` | Que habria visto el operador? | `volume_today >= 500k`, rank `% change 1D`, top 25 | Visibilidad operativa humana |
| `relative_volume_profile_v0_2` | Que esta acelerando actividad? | `rvol_to_time`, `volume_acceleration`, volume tiers | Timing, attention proxy, discovery temprano |
| `percent_change_profile_v0_2` | Que es visible por movimiento porcentual? | `pct_chg_1d`, gap/range expansion | Momentum/hot-list visibility |
| `dollar_volume_tradability_profile_v0_2` | Que parece operable? | dollar volume, liquidity/tradability tiers | Execution realism y risk gates |
| `das_research_profile_v0_2` | Que candidatos merecen reconstruccion DAS/frontside? | flags/reasons sobre el base universe | Denominador experimental DAS, no senal |

## 4. TradeStation-like profile

Forma conceptual:

```text
base_in_play_universe_scanner_v0_2
+ volume_today >= 500000
+ rank by pct_chg_1d desc
+ top_n = 25
```

Uso:

- reconstruir visibilidad humana historica;
- medir si una estrategia aparecia tarde para el operador;
- comparar research contra realidad operativa;
- construir un baseline operacional simple.

Limitacion:

```text
Puede llegar tarde para patrones tempranos como DAS/frontside.
```

## 5. Broad discovery v0.1 como concepto historico

La idea v0.1 de `broad_in_play_discovery_scanner_v0_1` no se elimina: se
descompone en perfiles y razones.

Razones que sobreviven como features/ranks/flags:

```text
reason_pct_chg_1d_move
reason_gap_pct_move
reason_volume_acceleration
reason_rvol_to_time
reason_afterhours_breakout
reason_premarket_new_high
reason_prior_day_high_reclaim
reason_unusual_range_expansion
reason_news_context
reason_halt_or_reopen_context
```

Regla:

```text
Una razon in-play no crea un universo alternativo; etiqueta una fila del
universo base.
```

## 6. Columnas que deben sobrevivir

El output debe preservar, como minimo:

```text
scanner_definition_id
scanner_definition_version
scanner_run_id
session_date
as_of_utc
ticker / instrument_id
population_denominator_count
evaluated_candidate_count
selected_candidate_count
profile_ids
candidate_reasons
candidate_reason_count
rank_pct_chg_1d
rank_volume_acceleration
rank_dollar_volume_to_time
rank_rvol_to_time
rank_composite_in_play
selected_trade_station_like_top25
selected_relative_volume_profile
selected_percent_change_profile
selected_dollar_volume_tradability_profile
selected_das_research_profile
volume_tier
float_available_point_in_time
float_source_id
valid_for_event_discovery_candidate
valid_for_market_state_seed_candidate
valid_for_ml_feature_candidate = false by default
valid_for_rl_state_candidate = false by default
```

## 7. Regla de uso

```text
El scanner base crea el denominador.
Los perfiles crean formas reproducibles de mirar ese denominador.
Ninguno reemplaza market_state.
```
