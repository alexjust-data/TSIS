# Scanner Definitions: TradeStation-Like vs Broad Discovery v0.1

Fecha: 2026-06-30
Estado: candidate_policy

## 1. Decision

TSIS no tendra un unico scanner general.

La version v0.1 separa:

```text
trade_station_like_scanner_v0_1
broad_in_play_discovery_scanner_v0_1
```

Ambos producen candidatos.

Ninguno produce senales, labels, outcomes, rewards ni decisiones.

## 2. `trade_station_like_scanner_v0_1`

Pregunta:

```text
Que habria visto el operador en una hot list operativa similar a TradeStation?
```

Uso:

- reconstruir visibilidad humana historica;
- medir si una estrategia aparecia tarde para el operador;
- comparar research broad contra realidad operativa;
- construir un baseline operacional simple.

Forma conceptual:

```text
market_cap_usd < 100000000
volume_today > 500000
0.5 < last_price <= 20
rank by pct_chg_1d desc
top_n = 25
```

Limitacion:

```text
Puede llegar tarde para patrones tempranos como DAS/frontside.
```

## 3. `broad_in_play_discovery_scanner_v0_1`

Pregunta:

```text
Que tickers empezaban a estar vivos aunque todavia no cumplieran el scanner humano?
```

Uso:

- discovery amplio;
- detectar eventos tempranos;
- medir cuantos casos buenos habria perdido un scanner estrecho;
- crear denominadores mas honestos para research;
- alimentar futuras tablas experimentales de estado por estrategia.

Inclusion por razones:

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

Limitacion:

```text
No es una senal de trading ni un universo completo de oportunidad.
```

## 4. Diferencia clave

| Pregunta | Scanner |
| --- | --- |
| Que vio el humano? | `trade_station_like_scanner_v0_1` |
| Que estaba empezando a moverse? | `broad_in_play_discovery_scanner_v0_1` |
| Que estado real tenia el ticker? | `market_state` / `event_state` |
| Que hizo la estrategia? | strategy table / decision model |
| Que outcome ocurrio? | outcome table |

## 5. Por que esto importa para DAS

DAS puede activarse antes de que:

- `volume_today` alcance 500k;
- el ticker sea top 25 por `% change 1D`;
- el operador lo vea en una hot list estrecha.

Si TSIS solo conserva el scanner operativo, puede concluir falsamente que un
patron no existia o que no era observable.

Si TSIS solo conserva el scanner broad, puede olvidar la pregunta operacional:

```text
Lo habria visto realmente el operador?
```

Por eso ambos deben vivir juntos y compararse.

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
candidate_reasons
candidate_reason_count
rank_pct_chg_1d
rank_volume_acceleration
rank_dollar_volume_to_time
rank_rvol_to_time
rank_composite_in_play
selected_trade_station_like_top25
selected_broad_discovery
volume_tier
valid_for_event_discovery_candidate
valid_for_market_state_seed_candidate
valid_for_ml_feature_candidate = false by default
valid_for_rl_state_candidate = false by default
```

## 7. Regla de uso

```text
TradeStation-like reproduce la visibilidad operacional.
Broad discovery protege el research contra llegada tardia.
Ninguno reemplaza market_state.
```

