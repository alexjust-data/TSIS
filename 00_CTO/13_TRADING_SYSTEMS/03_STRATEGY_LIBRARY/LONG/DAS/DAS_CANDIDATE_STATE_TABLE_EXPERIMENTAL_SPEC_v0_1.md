# DAS Candidate State Table Experimental Spec v0.1

Fecha: 2026-06-29  
Estado: `draft_experimental_spec`  
Scope: `03_STRATEGY_LIBRARY/LONG/DAS/`  

Documento relacionado:

- `STRATEGY.md`  
- `DAS_FRONTSIDE_STATE_AND_ALPHAEVOLVE_RESEARCH_PLAN_v0_1.md`  
- `DAS_SCANNER_USAGE_AND_OVERLAY_RUNBOOK_v0_1.md`

Run inicial de trabajo:

```text
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z
```

## 1. Proposito

Este documento define la primera especificacion de
`das_candidate_state_table_experimental`.

La tabla tiene un objetivo pragmatico:

```text
convertir los candidatos DAS visuales en filas medibles,
con estados, features, labels humanos, outcomes y lineage separados.
```

No es una tabla institucional.
No sustituye a Data Foundation.
No crea `market_state_table`.
No crea `event_state_table`.
No valida una estrategia.

Sirve para aprender, medir patrones y preparar un futuro builder mas serio.

## 2. Posicion en la arquitectura

El encaje correcto es:

```text
daily_scanner_candidates_table
-> das_candidate_state_table_experimental
-> future market_state_table / event_state_table
```

Lectura:

```text
daily_scanner_candidates_table
= denominador general / donde mirar

das_candidate_state_table_experimental
= lectura DAS/frontside sobre esos candidatos o sobre un run DAS actual

market_state_table / event_state_table
= futura capa institucional gobernada
```

Mientras el scanner general no este materializado, esta tabla puede construirse
desde runs DAS existentes, pero sus estadisticas deben declararse como:

```text
conditional_on_current_das_detector
```

No como:

```text
population_statistics_over_all_in_play_tickers
```

## 3. Unidad de fila

Una fila representa:

```text
un candidato DAS/frontside para un ticker en una session_date concreta,
detectado por un run DAS experimental.
```

La fila puede estar en varios estados:

- scanner_only;
- momentum_triggered;
- first_push_detected;
- first_dip_detected;
- rebreak_confirmed;
- active_frontside;
- backside_damaged;
- failed_candidate;
- human_rejected;
- manual_review_required.

La tabla no representa:

- una orden;
- un fill;
- una posicion;
- un PnL real;
- una estrategia institucional;
- una decision automatica.

## 4. Identidad logica

Identidad propuesta:

```text
logical_dataset_id = das_candidate_state_table_experimental
logical_version = 0.1.0
status = experimental
```

Clave conceptual:

```text
das_candidate_id
```

Debe derivarse de forma estable desde:

```text
source_run_id
ticker
session_date
scanner__trigger_ts or frontside__momentum_trigger_ts
frontside__rebreak_ts when available
detector_version
```

Ejemplo:

```text
das_candidate_id =
das_scanner_appearance_20260628T114046Z::SYRA::2024-02-08::2024-02-08T09:09:00-05:00
```

## 5. Inputs permitidos para esta fase

### 5.1. Inputs operativos actuales

| Input | Uso |
| --- | --- |
| `das_scanner_appearance_*` run | Fuente de candidatos iniciales. |
| `E:\TSIS\data\ohlcv_1m` | Fuente 1m full-universe actual para reconstruir precio/volumen. |
| `E:\TSIS\data\reference\overview` | Exchange, nombre de compania y market cap cuando exista. |
| imagenes exportadas del run | Evidencia visual y labels humanos. |

### 5.2. Inputs Data Foundation que pueden enriquecer despues

| Input | Uso futuro |
| --- | --- |
| `instrument_master` | Identidad canonica del instrumento. |
| `market_calendar` | Sesiones, horarios y calendario. |
| `corporate_actions_table` | Splits, reverse splits y eventos corporativos. |
| `master_daily_table` | Contexto diario y niveles previos. |
| `halts_table` | Halts cercanos al frontside. |
| `fundamentals_asof_table` | Market cap/float si esta disponible as-of. |
| `news_context_table` | Catalysts y atencion externa. |
| `short_context_table` | Contexto short, si el scope lo permite. |
| `regime_context_table` | Estado de mercado, si esta materializado y permitido. |

### 5.3. Inputs no asumidos todavia

No asumir como base primaria final:

- `market_state_table`;
- `event_state_table`;
- `short_sale_constraints_table`;
- `master_intraday_bar_table` si sigue scoped/pilot;
- microstructure como fuente completa si solo existe seed/candidate.

## 6. Regla temporal

Toda columna debe declarar si se conoce:

```text
before_scanner_trigger
at_scanner_trigger
between_scanner_and_momentum
at_momentum_trigger
between_momentum_and_rebreak
at_rebreak
after_rebreak
end_of_window
future_outcome
human_after_review
```

Regla:

```text
Una columna future_outcome o human_after_review no puede entrar como feature.
```

## 7. Namespaces

La tabla debe usar namespaces explicitos:

```text
identity__
source__
scanner__
daily__
afterhours__
premarket__
frontside__
das__
vwap__
ema_wilder__
quality__
human_label__
outcome__
export__
```

## 8. Columnas identity__

Columnas minimas:

```text
identity__das_candidate_id
identity__logical_dataset_id
identity__logical_version
identity__status
identity__ticker
identity__primary_exchange
identity__tradingview_symbol
identity__company_name
identity__session_date
identity__timezone
identity__canonical_security_id
identity__symbol_identity_quality
```

Notas:

- `tradingview_symbol` debe tener formato `EXCHANGE:TICKER` cuando sea posible.
- `canonical_security_id` puede estar vacio en fase experimental, pero debe existir como columna.
- `symbol_identity_quality` debe indicar si la identidad fue resuelta, aproximada o desconocida.

## 9. Columnas source__

Columnas minimas:

```text
source__run_id
source__run_dir
source__candidate_file
source__data_root
source__reference_overview_root
source__price_view
source__detector_version
source__builder_version
source__notebook_path
source__build_commit
source__created_at_utc
source__config_json
source__launcher_command
```

Regla:

```text
Cada fila debe poder reconstruirse desde run_dir + config + data_root.
```

## 10. Columnas scanner__

Estas columnas describen cuando el ticker habria aparecido para el humano o para
el scanner experimental.

```text
scanner__definition_id
scanner__mode
scanner__trigger_ts
scanner__trigger_price
scanner__trigger_gap_pct_from_prior_close
scanner__trigger_pct_from_premarket_open
scanner__trigger_volume_today
scanner__trigger_dollar_volume_today
scanner__trigger_rank
scanner__trigger_reason
scanner__trigger_reasons_json
scanner__top_n_inclusion
scanner__eligible_before_momentum
scanner__late_vs_momentum_trigger
scanner__minutes_after_momentum_trigger
scanner__volume_threshold_reached_ts
scanner__volume_threshold_reached_before_entry_zone
```

Interpretacion:

- `scanner__trigger_ts` no es necesariamente el primer momento de oportunidad.
- `scanner__late_vs_momentum_trigger = true` indica que el scanner llego tarde frente al movimiento.
- `scanner__trigger_volume_today` debe ser acumulado hasta ese timestamp, no volumen final del dia.

## 11. Columnas daily__

Contexto diario minimo:

```text
daily__prior_close
daily__prior_open
daily__prior_high
daily__prior_low
daily__prior_volume
daily__current_day_open_0400
daily__gap_pct_from_prior_close_at_0400
daily__gap_pct_from_prior_close_at_scanner
daily__prior_high_reclaim_before_trigger
daily__multi_day_extension_count
daily__days_since_last_major_extension
daily__daily_resistance_nearby
daily__daily_breakout_context
daily__daily_chart_context_quality
```

Uso:

Estas columnas permiten responder si el DAS aparece dentro de una estructura
diaria mayor, por ejemplo:

- primer dia fuerte;
- continuacion multi-day;
- ruptura de maximos diarios;
- extension tardia;
- rebote despues de varios dias de bajada.

## 12. Columnas afterhours__

After-hours puede explicar parte del frontside de premarket.

Columnas iniciales:

```text
afterhours__prev_session_has_activity
afterhours__prev_session_high
afterhours__prev_session_low
afterhours__prev_session_close
afterhours__prev_session_volume
afterhours__breakout_above_prior_regular_high
afterhours__breakout_held_into_premarket
afterhours__failed_breakout_before_premarket
afterhours__exhaustion_flag
afterhours__structure_highs_lows_json
```

Regla:

```text
No tratar premarket como ventana aislada si after-hours contiene estructura
relevante.
```

## 13. Columnas premarket__

Columnas de ventana premarket:

```text
premarket__window_start_ts
premarket__window_end_ts
premarket__open_price
premarket__open_ts
premarket__high
premarket__high_ts
premarket__low
premarket__low_ts
premarket__volume_total
premarket__dollar_volume_total
premarket__range_pct_from_open
premarket__first_liquid_bar_ts
premarket__minutes_from_open_to_scanner
premarket__minutes_from_open_to_momentum_trigger
premarket__minutes_from_open_to_first_push_high
premarket__minutes_from_open_to_rebreak
```

Regla:

```text
Las extensiones porcentuales DAS deben medirse al alza.
```

Si el movimiento principal detectado es bajista, la fila debe marcarse como:

```text
quality__direction_mismatch = true
das__state = human_rejected or failed_candidate
```

## 14. Columnas frontside__

Este namespace es el centro de la tabla.

Columnas iniciales:

```text
frontside__momentum_trigger_ts
frontside__momentum_trigger_price
frontside__momentum_trigger_gap_pct_from_prior_close
frontside__momentum_trigger_pct_from_premarket_open
frontside__momentum_trigger_volume_today

frontside__first_push_start_ts
frontside__first_push_start_price
frontside__first_push_high_ts
frontside__first_push_high_price
frontside__first_push_pct_from_premarket_open
frontside__first_push_pct_from_prior_close
frontside__first_push_duration_minutes
frontside__first_push_volume
frontside__first_push_dollar_volume
frontside__first_push_bar_count
frontside__first_push_red_bar_high_to_break

frontside__first_dip_start_ts
frontside__first_dip_low_ts
frontside__first_dip_low_price
frontside__first_dip_depth_pct
frontside__first_dip_holds_vwap
frontside__first_dip_holds_higher_low
frontside__first_dip_duration_minutes

frontside__rebreak_ts
frontside__rebreak_price
frontside__rebreak_type
frontside__rebreak_above_first_push_high
frontside__rebreak_above_red_bar_high
frontside__rebreak_volume
frontside__rebreak_minutes_after_first_push_high

frontside__max_momentum_high_ts
frontside__max_momentum_high_price
frontside__max_momentum_pct_from_premarket_open
frontside__max_momentum_pct_from_prior_close
frontside__minutes_to_max_momentum_high

frontside__backside_damage_ts
frontside__backside_damage_reason
frontside__frontside_duration_minutes
frontside__new_lows_after_rebreak_count
frontside__higher_high_count_after_rebreak
frontside__higher_low_count_after_rebreak
```

Lectura:

- `first_push_pct` mide el primer tramo.
- `max_momentum_pct` mide el techo de toda la extension frontside.
- `first_dip_depth_pct` mide cuanto retrocede sin destruir estructura.
- `rebreak_type` explica como se supera el primer push.

Valores iniciales permitidos para `frontside__rebreak_type`:

```text
single_candle_rebreak
red_bar_high_break
green_wick_reclaim
vwap_reclaim_rebreak
ascending_flag_break
multi_candle_flag_break
prior_high_reclaim
unclear
none
```

## 15. Columnas das__

Estado DAS interpretado:

```text
das__state
das__variant
das__sequence_index
das__is_first_das
das__active_sequence_started_ts
das__active_sequence_ended_ts
das__entry_zone_observed
das__entry_zone_type
das__entry_zone_ts
das__entry_zone_price_low
das__entry_zone_price_high
das__invalidated_ts
das__invalidation_reason
das__pattern_family
```

Valores iniciales para `das__variant`:

```text
A_plus_continuation
early_red_high_break
green_wick_reactivation
vwap_dip_reclaim
flag_break_after_first_push
late_scanner_but_valid
pattern_n_one_shot
deep_dip_reclaim
reject_after_rebreak
backside_false_positive
unclear
```

Nota:

`entry_zone_*` no significa orden ejecutada. Significa zona visual donde el
humano marco una oportunidad de estudio.

## 16. Columnas vwap__

La tabla debe permitir comparar VWAP calculado y VWAP original si existe en la
fuente.

```text
vwap__source_selected
vwap__calculated_available
vwap__raw_available
vwap__at_scanner
vwap__at_momentum_trigger
vwap__at_first_push_high
vwap__at_first_dip_low
vwap__at_rebreak
vwap__price_above_vwap_at_scanner
vwap__price_above_vwap_at_momentum_trigger
vwap__first_dip_holds_vwap
vwap__vwap_reclaim_before_rebreak
vwap__vwap_loss_after_rebreak_ts
```

Valores de `vwap__source_selected`:

```text
calculated
raw_source
unknown
```

## 17. Columnas ema_wilder__

Indicadores de momentum intradia usados en los charts:

```text
ema_wilder__ema8_at_scanner
ema_wilder__wilder8_at_scanner
ema_wilder__state_at_scanner
ema_wilder__ema8_at_momentum_trigger
ema_wilder__wilder8_at_momentum_trigger
ema_wilder__state_at_momentum_trigger
ema_wilder__ema8_at_rebreak
ema_wilder__wilder8_at_rebreak
ema_wilder__state_at_rebreak
ema_wilder__bullish_spread_at_rebreak
ema_wilder__bearish_flip_ts
ema_wilder__bullish_duration_minutes
```

Valores de estado:

```text
bullish
bearish
flat
unknown
```

Regla:

```text
EMA/Wilder describe estado de momentum; no valida por si sola una entrada.
```

## 18. Columnas quality__

Calidad tecnica y semantica:

```text
quality__state
quality__manual_review_required
quality__missing_1m_bars
quality__missing_premarket_window
quality__suspicious_wicks
quality__direction_mismatch
quality__split_or_reverse_split_nearby
quality__halt_overlap
quality__market_cap_missing
quality__identity_unresolved
quality__scanner_late
quality__insufficient_volume_at_scanner
quality__candidate_from_partial_run
quality__notes
```

Valores de `quality__state`:

```text
good_candidate
review_candidate
degraded_candidate
failed_candidate
invalid_candidate
```

## 19. Columnas human_label__

Labels humanos y anotaciones manuales:

```text
human_label__grade
human_label__folder_source
human_label__tags
human_label__annotator
human_label__label_ts
human_label__discretionary_entry_notes
human_label__discretionary_stop_notes
human_label__why_good
human_label__why_bad
human_label__pattern_name_manual
human_label__image_annotation_path
```

Valores iniciales para `human_label__grade`:

```text
A_plus
good
regular
bad
worst
pattern_n
unlabeled
```

Regla critica:

```text
human_label__ no es feature.
```

Puede usarse para:

- auditoria visual;
- entrenamiento supervisado posterior con contrato anti-leakage;
- calibrar detectores;
- explicar falsos positivos.

No puede usarse como input directo de decision historica.

## 20. Columnas outcome__

Outcomes posteriores para medir que paso despues.

```text
outcome__max_high_after_scanner
outcome__max_high_after_scanner_ts
outcome__max_extension_pct_after_scanner
outcome__max_high_after_momentum_trigger
outcome__max_extension_pct_after_momentum_trigger
outcome__max_high_after_rebreak
outcome__max_extension_pct_after_rebreak
outcome__minutes_to_max_high_after_rebreak
outcome__drawdown_after_rebreak_pct
outcome__vwap_loss_after_rebreak
outcome__first_lower_low_after_rebreak_ts
outcome__backside_confirmed
outcome__backside_confirmed_ts
outcome__failed_to_hold_first_push_high
outcome__failed_to_hold_vwap
outcome__close_vs_rebreak_pct
outcome__close_vs_premarket_open_pct
```

Regla critica:

```text
outcome__ no es feature.
```

Los outcomes sirven para:

- medir continuacion;
- medir fallo;
- comparar variantes;
- construir fitness de credibilidad;
- entrenar labels futuros con separacion temporal.

No sirven para decidir en el mismo timestamp que se esta evaluando.

## 21. Columnas export__

Lineage visual:

```text
export__chart_01_interactive_available
export__chart_02_three_day_overview_path
export__chart_03_event_day_premarket_detail_path
export__chart_04_event_day_until_1600_path
export__chart_daily_context_path
export__chart_export_root
export__chart_export_manifest_path
export__chart_export_created_at_utc
```

Uso:

Estas columnas permiten enlazar una fila con las imagenes revisadas por el
humano.

## 22. Clasificacion anti-leakage

Cada columna debe clasificarse en una de estas categorias:

```text
observable_before_scanner
observable_at_scanner
observable_at_momentum_trigger
observable_at_rebreak
derived_without_future
human_label_after_review
outcome_after_event
forbidden_for_model
```

Reglas:

- `observable_*` puede alimentar analisis temporal si respeta su timestamp.
- `derived_without_future` puede alimentar investigacion si no mira adelante.
- `human_label_after_review` no es feature.
- `outcome_after_event` no es feature.
- `forbidden_for_model` queda fuera de ML/RL/AlphaEvolve.

## 23. Materializacion experimental propuesta

Ruta propuesta para el primer builder:

```text
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\<run_id>\state_tables\
```

Outputs:

```text
das_candidate_state_table_experimental_v0_1.parquet
das_candidate_state_table_experimental_v0_1.csv
das_candidate_state_table_experimental_v0_1_manifest.json
das_candidate_state_table_experimental_v0_1_summary.md
```

El manifest debe incluir:

- run original;
- comando launcher;
- data roots;
- version de builder;
- fecha de build;
- numero de candidatos;
- columnas generadas;
- columnas con missingness;
- warnings de calidad;
- git commit si esta disponible.

## 24. Builder experimental: responsabilidades

El builder debe:

1. Leer candidatos del run DAS.
2. Resolver ticker, fecha y timestamps clave.
3. Cargar velas 1m necesarias.
4. Reconstruir premarket, after-hours cercano y regular session.
5. Calcular scanner trigger sin mirar el final del dia.
6. Calcular momentum trigger.
7. Calcular first push, first dip, rebreak y max momentum.
8. Calcular VWAP segun source seleccionada.
9. Calcular EMA8/Wilder8.
10. Enlazar imagenes exportadas si existen.
11. Separar features, labels y outcomes.
12. Escribir tabla, manifest y resumen.

El builder no debe:

- optimizar entradas;
- decidir stops;
- seleccionar targets;
- promocionar la estrategia;
- crear state tables institucionales;
- ocultar filas malas.

## 25. Estadisticas iniciales que queremos medir

Primera tanda:

```text
distribution(frontside__first_push_pct_from_premarket_open)
distribution(frontside__max_momentum_pct_from_premarket_open)
distribution(frontside__first_dip_depth_pct)
distribution(frontside__rebreak_minutes_after_first_push_high)
distribution(scanner__minutes_after_momentum_trigger)
distribution(scanner__trigger_volume_today)
distribution(vwap__first_dip_holds_vwap)
distribution(ema_wilder__state_at_rebreak)
```

Cruces:

```text
human_label__grade x first_push_pct
human_label__grade x first_dip_depth_pct
human_label__grade x rebreak_type
human_label__grade x scanner_late
human_label__grade x vwap_hold
human_label__grade x ema_wilder_state
human_label__grade x afterhours_breakout_held
```

Outcomes:

```text
max_extension_after_rebreak by das__variant
backside_confirmed rate by das__variant
failed_to_hold_first_push_high rate by first_dip_depth_bucket
continuation rate by rebreak_type
money_fail rate by scanner_late
```

## 26. Preguntas estadisticas para AlphaEvolve

AlphaEvolve no debe recibir solo PnL.

Debe poder proponer hipotesis sobre estructuras como:

```text
Si first_push_pct esta entre A y B,
y first_dip_depth_pct esta entre C y D,
y first_dip_holds_vwap = true,
y rebreak_type in {...},
y scanner_late = false,
entonces la probabilidad de continuation frontside aumenta.
```

Tambien debe poder penalizar:

```text
one_shot_pattern
late_scanner
deep_dip_without_vwap_reclaim
direction_mismatch
backside_damage_before_rebreak
afterhours_exhaustion
```

Fitness futuro recomendado:

```text
credibility_fitness =
  outcome_quality
+ temporal_stability
+ variant_stability
+ neighbour_robustness
+ out_of_sample_survival
- complexity_penalty
- leakage_penalty
- data_quality_penalty
```

## 27. Criterio de terminado v0.1

Esta spec se considera suficientemente implementada cuando podamos responder,
para el run DAS actual:

1. Cuantos candidatos hay.
2. Que porcentaje son scanner_only, rebreak_confirmed, failed, review.
3. Donde salto el scanner respecto al momentum trigger.
4. Cual fue el first push pct.
5. Cual fue el max momentum pct.
6. Si el primer dip aguanto VWAP.
7. Como se produjo el rebreak.
8. Que labels humanos tienen.
9. Que outcomes posteriores tuvieron.
10. Que filas no deben usarse por calidad o leakage.

## 28. No-goals

Este documento no:

- define un backtest;
- define una entrada obligatoria;
- define stops o targets finales;
- valida edge;
- crea una tabla institucional;
- crea un scanner general;
- sustituye contratos de Data Foundation;
- autoriza ML/RL directo.

## 29. Regla final

La tabla experimental DAS debe ayudarnos a aprender.

No debe fingir que ya sabemos.
