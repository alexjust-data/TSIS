# Execution Protocol - EXP_DAS_FRONTSIDE_DISCOVERY_0002

Fecha: 2026-07-06
Estado: draft_operativo

## Objetivo Operativo

Ejecutar un experimento historico que mida, para cada ticker cazado por scanner, que ocurre despues del primer movimiento frontside:

```text
scanner gate
-> first push
-> first dip
-> recovery / no recovery
-> rebreak / fake rebreak
-> continuation / destruction
```

La ejecucion debe producir estadisticas, casos visuales auditables y tablas reproducibles.

## Fase 0 - Data Lineage Y Vista 1m

Antes de construir cualquier metrica:

```text
1. declarar fuente 1m usada
2. declarar repair/quote guard state
3. declarar si se usa tabla materializada o puente visual
4. bloquear casos con scale mismatch raw/quotes si no hay vista fiable
```

Orden de preferencia:

```text
1. master_intraday_bar_table_v0_2_candidate_quote_guarded si cubre ticker/sesion
2. raw ohlcv_1m + repair_manifest_lt1b_v0_1
3. puente visual raw + quotes q01/q99 con scale guard, solo para inspeccion
```

No se permite usar mechas raw sospechosas como verdad de first push, dip o rebreak.

## Fase 1 - Construccion Del Denominador

Para cada configuracion de scanner, construir el denominador completo:

```text
todos los tickers que el scanner captura
```

No filtrar solo supervivientes.

Columnas minimas:

```text
experiment_id
sweep_id
scanner_config_id
ticker
instrument_id
session_date
scanner_gate_ts_utc
scanner_gate_price
scanner_gate_prior_close_pct
scanner_gate_accumulated_volume
market_cap
price_gate_state
market_cap_gate_state
volume_gate_state
visual_price_source
lineage_manifest
```


### Implementacion Actual Del Denominador 2026

El primer builder operativo del denominador es:

```text
scripts/build_2026_scanner_from_quote_guarded_1m_v0_1.py
```

Principio obligatorio:

```text
nuevo scanner != candidate_events.parquet antiguo
nuevo scanner != copiar anchors DAS previos
nuevo scanner = filtros declarados + raw 1m + quote-guarded + lineage
```

El builder actual calcula solo `scanner_gate` y columnas de denominador. No calcula `first_push`, `first_dip`, `rebreak`, outcomes ni in-play.

Regla inicial de gate:

```text
reference_price = prior_close
scanner_gate_price = close quote-guarded de la vela 1m cerrada
threshold_pct = scanner_gate_price / prior_close - 1
volume_gate = volumen acumulado de la sesion premarket hasta el gate
price_gate = precio quote-guarded dentro del rango declarado
market_cap_gate = <100M con estado de fuente marcado
```

Esta separacion evita contaminar el denominador con detecciones estructurales posteriores.

## Fase 2 - Sweep De Threshold Inicial

Primer sweep obligatorio:

```text
threshold_pct = 20, 30, 40, 50, 70, 100
```

Variables constantes iniciales:

```text
reference_price = prior_close o segment_open, segun policy declarada
session_scope = premarket primero
market_cap_gate = <100M como filtro duro DAS
price_gate = declarar rango, no asumir optimo
volume_gate = baseline declarado o none, segun sweep
```

Pregunta del sweep:

```text
?como cambia la poblacion capturada y su comportamiento posterior cuando cambia el umbral de movimiento inicial?
```

No se debe promover un threshold solo por verse mejor en este sweep.

## Fase 3 - Anchors De Estructura

Para cada caso capturado, detectar y guardar anchors:

```text
scanner_gate
push_start
first_push_high
first_dip_low
recovery_attempt
rebreak
fake_rebreak
post_rebreak_high
failure_low
```

Cada anchor debe tener:

```text
anchor_id
anchor_type
ts_utc
bar_index
price
price_source
calculation_rule
visual_label_id
quality_state
```

Reglas conceptuales actuales:

```text
first push = primer tramo de expansion despues de despertar
first_push_high = maximo de ese primer tramo, puede estar en primera vela roja
first dip = primer retroceso real despues del first_push_high
first_dip_low = minimo del retroceso antes de recovery/rebreak
rebreak = recuperacion/ruptura valida de first_push_high segun regla candidata
fake_rebreak = intento de ruptura que no cumple regla candidata o falla rapidamente
```

Estas reglas son candidatas y deben auditarse visualmente.

## Fase 4 - Clasificacion De Trayectoria

Cada caso debe clasificarse sin mirar solo el resultado final:

```text
scanner_only_no_clean_push
first_push_no_clean_dip
first_push_dip_no_recovery
partial_recovery_no_rebreak
fake_rebreak
rebreak_confirmed
rebreak_then_failure
rebreak_then_continuation
data_quality_blocked
```

La clasificacion debe conservar tambien estados intermedios, no solo una etiqueta final.

## Fase 5 - Outcomes Desde Multiples Anchors

Calcular outcomes desde:

```text
scanner_gate
push_start
first_push_high
first_dip_low
rebreak
```

Horizontes iniciales:

```text
1m
2m
5m
10m
30m
end_of_premarket
regular_open_plus_5m cuando aplique
```

Metrica minima:

```text
MFE
MAE
return final
max_extension_pct
max_drawdown_pct
time_to_extension
time_to_failure
coverage_ratio
missing_bar_ratio
```

## Fase 6 - Recovery/Destruction Statistics

Agrupar por:

```text
threshold_pct
volume_gate
market_cap_bucket
price_bucket
time_bucket
premarket_phase
first_push_size_bucket
dip_depth_bucket
trend_context_bucket
```

Medir:

```text
case_count
recovery_rate
no_recovery_rate
rebreak_rate
fake_rebreak_rate
continuation_rate
destruction_rate
median_post_dip_mfe
median_post_dip_mae
median_post_rebreak_mfe
median_missed_move
```

## Fase 7 - Coste De Oportunidad

Para cada filtro o threshold medir:

```text
captured_case_count
lost_case_count_vs_looser_config
lost_recovery_cases
lost_continuation_cases
noise_reduction
opportunity_reduction
```

Ejemplo:

```text
volumen 500k puede limpiar basura, pero tambien puede perder movimientos buenos.
```

El output debe mostrar ese tradeoff, no solo la metrica ganadora.

## Fase 8 - Visual Audit

Todo caso usado para validar reglas de anchors debe tener imagen auditada o muestreo visual estratificado.

Obligatorio:

```text
label_id por metrica
anchor timestamp y precio
misma coordenada de calculo y pintado
visual_price_source
scale_guard_state
no marcas a ojo
```

Casos que requieren auditoria manual prioritaria:

```text
raw/quotes mismatch
rebreak dudoso
fake breakout dudoso
first dip ambiguo
mechas extremas
casos donde el algoritmo y el humano discrepan
```

## Fase 9 - Outputs Esperados

Outputs logicos esperados:

```text
das_frontside_scanner_denominator_v0_1
das_frontside_anchor_events_v0_1
das_frontside_dip_recovery_panel_v0_1
das_frontside_opportunity_decomposition_v0_1
das_frontside_threshold_sensitivity_report_v0_1
das_frontside_visual_inspection_manifest_v0_1
```

Estos nombres son candidatos. No son tablas oficiales hasta que tengan schema contract.

## Fase 10 - Decision Despues Del Experimento

Despues de ejecutar el primer sweep, no se promociona una estrategia.

Se decide una de estas rutas:

```text
1. ajustar anchors porque la deteccion no coincide con inspeccion humana
2. profundizar threshold sweep
3. abrir volume gate cost-of-opportunity sweep
4. abrir EXP_DAS_TICKER_INPLAY_0001
5. bloquear por data quality
```
