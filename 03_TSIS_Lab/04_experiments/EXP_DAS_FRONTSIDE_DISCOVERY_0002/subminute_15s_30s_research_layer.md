# Subminute 15s/30s Research Layer - EXP_DAS_FRONTSIDE_DISCOVERY_0002

Fecha: 2026-07-06
Estado: draft_operativo

## Pregunta

```text
?Podemos construir velas o barras de 15s/30s para estudiar mejor el momentum antes del first push?
```

Respuesta corta:

```text
Desde 1m no podemos crear velas reales de 15s/30s.
Desde quotes/trades si podemos construir barras 15s/30s.
```

## Regla Base

No se permite partir una vela 1m en cuatro velas de 15s.

Eso inventaria el camino intraminuto:

```text
open -> high -> low -> close
```

y no sabemos el orden real dentro de la vela 1m.

Por tanto:

```text
1m -> no genera 15s/30s reales
quotes/trades -> si pueden generar barras 15s/30s
```

## Fuentes Disponibles

Fuentes detectadas en el proyecto:

```text
D:/quotes
E:/TSIS/data/trades_ticks_prod_2005_2026
```

Ejemplo auditado:

```text
INM 2024-08-20
D:/quotes/INM/year=2024/month=08/day=20/quotes.parquet
rows = 198,658
rango NY = 04:00:00 a 19:59:59
rows entre 07:00 y 10:00 NY = 110,994
```

Esto demuestra que, al menos para este caso, quotes tienen granularidad suficiente para construir barras sub-1m.

## Que Podemos Construir Con Quotes

Con quotes podemos construir barras de estado top-of-book, no velas de trades.

Ejemplos:

```text
15s/30s bid bar
15s/30s ask bar
15s/30s midpoint bar
spread
spread_bps
quote_count
quote_rate
bid_size
ask_size
top_size
quote_staleness
locked_crossed_state
missing_quote_interval
```

Esto sirve para estudiar:

```text
si el midpoint avanza limpio
si el spread se abre demasiado
si hay aceleracion de quotes
si el book se vuelve fragil
si el push nace con continuidad
si el movimiento de la vela 1m era real o ruido de mecha
```

## Que Podemos Construir Con Trades

Con trades, si hay cobertura premarket, podemos construir barras negociadas.

Ejemplos:

```text
15s/30s trade OHLC
trade_volume
trade_dollar_volume
trade_count
trade_vwap
avg_trade_size
max_trade_size
odd_lot_ratio si existe
trade_intensity
```

Esto se parece mas a una vela real.

Pero debe auditarse cobertura, porque en algunos casos puede no haber trades premarket disponibles aunque si haya quotes.

Si no hay trades premarket:

```text
execution_truth = unavailable
```

No se debe inferir ejecucion real solo desde quotes u OHLC 1m.

## Por Que Puede Ser Util Para DAS/frontside

Para estrategias frontside, 1m puede ser demasiado grueso.

Dentro de una vela 1m se pueden mezclar:

```text
despertar
aceleracion
primera absorcion
primer micro pullback
primer squeeze
primer stall
```

Con 15s/30s podemos estudiar mejor lo que ocurre antes del `first_push_high`:

```text
si el impulso empieza limpio
si hay micro dips recuperados rapidamente
si el spread se rompe
si el volumen entra antes del scanner gate
si la accion ya estaba in-play antes del rebreak 1m
si el primer dip empieza dentro de la propia vela 1m
```

## Relacion Con EXP_DAS_FRONTSIDE_DISCOVERY_0002

Esta capa no sustituye al experimento principal.

La lectura correcta es:

```text
EXP_DAS_FRONTSIDE_DISCOVERY_0002
= poblacion, recovery/destruction, thresholds y coste de oportunidad usando anchors 1m auditables

subminute_15s_30s_research_layer
= capa exploratoria para entender si el edge aparece antes o dentro de los anchors 1m
```

## Hipotesis

```text
H1: algunos tickers que recuperan el first dip muestran se?ales sub-1m antes de que la vela 1m confirme.
```

```text
H2: algunos fake breakouts 1m pueden detectarse antes por spread, midpoint o falta de trade confirmation.
```

```text
H3: algunas oportunidades long existen antes del first_push_high/rebreak, pero requieren validacion de ejecucion y microestructura.
```

```text
H4: 15s/30s puede reducir el coste de oportunidad frente a esperar confirmacion 1m, pero puede aumentar ruido y falsos positivos.
```

## Auditoria De Cobertura Antes De Construir Barras

Antes de crear cualquier dataset 15s/30s, auditar para los casos DAS:

```text
quotes disponibles 07:00-10:00 NY
trades disponibles 07:00-10:00 NY
numero de intervalos 15s esperados
numero de intervalos 15s observados
numero de intervalos 30s esperados
numero de intervalos 30s observados
missing_quote_intervals
missing_trade_intervals
scale mismatch raw/quotes
spread extremo
locked/crossed quotes
stale quotes
```

El output candidato:

```text
das_subminute_coverage_audit_v0_1
```

## Datasets Candidatos

Si la cobertura es suficiente, construir:

```text
das_quote_bars_15s_30s_candidate
```

con:

```text
bid/ask/mid OHLC
spread/spread_bps
quote_count
quote_rate
bid_size/ask_size
staleness
quality flags
```

Y, solo cuando trades cubran la ventana:

```text
das_trade_bars_15s_30s_candidate
```

con:

```text
trade OHLC
volume
dollar_volume
trade_count
vwap
trade intensity
quality flags
```

## Mediciones Iniciales Desde Scanner Gate

Desde `scanner_gate` medir:

```text
midpoint_MFE_15s_30s
midpoint_MAE_15s_30s
trade_MFE_15s_30s si trades existen
trade_MAE_15s_30s si trades existen
spread_expansion
quote_acceleration
trade_volume_acceleration
time_to_first_impulse
time_to_first_stall
time_to_first_micro_pullback
```

## Relacion Con Opportunity Decomposition

La capa sub-1m puede ayudar a separar:

```text
scanner_to_inplay_opportunity
post_inplay_opportunity
missed_move
tradable_after_inplay
```

Pero con una advertencia:

```text
subminute opportunity no equivale automaticamente a ejecucion real
```

Para llamarlo tradable se necesita:

```text
quotes/trades suficientes
spread aceptable
slippage proxy
entry policy
exit policy
latencia/cutoff declarados
```

## No-Goals

Esta capa no debe:

```text
inventar barras 15s desde OHLC 1m
validar estrategia completa
promocionar tablas oficiales de estado
asumir fills reales sin trades/quotes suficientes
mezclar quotes midpoint con trade OHLC sin declarar fuente
```

## Siguiente Paso Propuesto

Primer paso tecnico:

```text
crear das_subminute_coverage_audit_v0_1 para los casos DAS
```

Preguntas que debe responder:

```text
cuantos casos tienen quotes suficientes
cuantos casos tienen trades suficientes
cuantos casos pueden soportar 15s
cuantos casos pueden soportar 30s
cuantos casos quedan bloqueados por scale mismatch
```

Solo despues construir barras 15s/30s candidatas.



---- 


La regla queda así:

15s/30s no se audita contra todo el universo todavía.
15s/30s se audita solo cuando exista una lista de eventos capturados:
ticker + fecha + evento + anchors.

Primero necesitamos producir la tabla/panel de eventos de EXP_DAS_FRONTSIDE_DISCOVERY_0002:

das_frontside_scanner_denominator_v0_1
das_frontside_anchor_events_v0_1
das_frontside_dip_recovery_panel_v0_1

Luego, para cada fila:

ticker
session_date
scanner_gate_ts
first_push_high_ts
first_dip_low_ts
rebreak_ts / fake_rebreak_ts

recién ahí se pide sub-1m:

quotes/trades 15s/30s alrededor de ese evento concreto

El orden corregido:

1. Construir denominador scanner
2. Detectar anchors 1m auditables
3. Clasificar recovery/destruction/rebreak/fake
4. Generar event panel ticker+fecha+anchors
5. Solo entonces auditar 15s/30s por evento
6. Construir subminute windows por evento

Así no gastamos tiempo auditando granularidad donde todavía no sabemos si hay evento que estudiar. El 15s/30s queda como capa
posterior por evento, no como primer paso.