# EduTrades Long Plays Source Event Index v0.1

Fecha: 2026-06-21
Estado: `source_note` estructurado para Event Library.
Orientacion del material fuente: `long plays discrecionales`.

Nota de autoridad:

```text
La orientacion long solo describe el origen didactico del material.
No convierte este documento en Strategy Library.
```

Fuente textual externa:

```text
C:\TSIS_SmallCaps\00_data_governance\00_papers\EduTrades\07_Long_plays.md
```

Fuente textual copiada al repo:

```text
source_assets/edu_trades/07_Long_plays.md
```

Imagenes fuente copiadas al repo:

```text
source_assets/edu_trades/
```

Nota de ingesta:

```text
No se localizo un PDF EduTrades operativo en las rutas revisadas durante esta
ingesta. Este source-note se basa en 07_Long_plays.md y en las imagenes
disponibles bajo source_assets/edu_trades/.
```

## 1. Proposito

Este documento extrae fenomenos observables desde material discrecional de
EduTrades y los convierte en eventos candidatos que luego puedan buscarse en
historico con Python.

No basta con decir "Breakout" o "VWAP Bounce". Para TSIS, cada evento debe
dejar claro:

```text
que ocurre
que secuencia observable lo forma
donde empieza
donde termina
que features permitirian encontrar candidatos
que casos deben excluirse
```

Este documento no autoriza entradas, stops, targets, sizing ni salidas. Es un
source-note operativo para Event Research: preserva imagenes, lenguaje del
trader y una primera traduccion a busquedas historicas.

La prioridad del documento es doble:

```text
1. preservar el contexto visual y textual del material fuente;
2. dejar suficiente estructura para que un agente futuro pueda escribir
   un detector exploratorio sin reinterpretar el evento desde cero.
```

## 2. Guardrail de Event Library

Segun `TSIS_LAB_ARCHITECTURE.md`, la Event Library responde:

```text
Que eventos existen?
Que ocurrio en el mercado?
```

No responde:

```text
Que debo hacer?
Donde entro?
Donde pongo stop?
Que target busco?
Con que size actuo?
```

El documento fuente habla de long plays discrecionales. TSIS los descompone:

```text
play discrecional
-> eventos observables
-> filtros de contexto
-> hipotesis de mecanismo
-> decision operativa futura, fuera de este documento
```

Event Library solo conserva los eventos observables y los filtros necesarios
para encontrarlos sin contaminar la definicion con accion operativa.

Ejemplo:

```text
Breakout discrecional
!=
Daily_Resistance_Volume_Breakout_Event

Breakout discrecional puede estar compuesto por:
  Daily_Resistance_Volume_Breakout_Event
  Breakout_First_Dip_Hold_Event
  catalyst/no-dilution filters
  risk rules fuera de Event Library
```

La estrategia pertenece a otra capa. El evento responde:

```text
Que ocurrio en el mercado?
```

## 3. Plantilla para eventos buscables

Cada evento de este documento usa esta estructura:

1. `Que ocurre`: definicion concreta del fenomeno.
2. `Imagenes fuente`: evidencia visual asociada.
3. `Texto del trader`: explicacion contextual del documento fuente.
4. `Definicion observable v0`: secuencia minima, inicio, fin y unidad.
5. `Busqueda historica v0`: campos, features, thresholds iniciales y exclusiones.
6. `Composicion observable no operativa`: marcos donde puede aparecer como pieza.
7. `No es estrategia`: frontera explicita.

Los thresholds de este documento son semillas de investigacion. No son
parametros promovidos.

### 3.1. Contrato minimo para busqueda historica

Cada evento debe poder traducirse despues a una funcion exploratoria de Python
con esta forma conceptual:

```text
inputs -> window builder -> event predicate -> feature extraction -> candidate row
```

Cada bloque debe permitir derivar, como minimo:

```yaml
event_name:
event_family_candidate:
search_grain:
session_scope:
temporal_anchor:
start_condition_seed:
end_condition_seed:
required_price_fields:
required_volume_fields:
candidate_features:
candidate_thresholds:
exclusion_flags:
review_flags:
expected_event_table_fields:
```

Esto no es todavia un detector promovido. Es solo el puente entre source note y
detector candidate.

## 4. Eventos candidatos identificados

1. [`Daily_Resistance_Volume_Breakout_Event`](#5-daily_resistance_volume_breakout_event): ruptura de resistencia daily relevante con volumen confirmatorio.
2. [`Breakout_First_Dip_Hold_Event`](#6-breakout_first_dip_hold_event): primer retroceso posterior al breakout que respeta el nivel roto.
3. [`Red_To_Green_Level_Reclaim_Event`](#7-red_to_green_level_reclaim_event): recuperacion del nivel red-to-green con volumen despues de abrir rojo.
4. [`Red_Base_Volume_Ramp_Event`](#8-red_base_volume_ramp_event): base en rojo con perdida de presion vendedora y rampa de volumen comprador.
5. [`VWAP_Bounce_After_Extension_Event`](#9-vwap_bounce_after_extension_event): retroceso de una accion verde extendida hacia VWAP, seguido de rebote.
6. [`VWAP_Reclaim_Control_Event`](#10-vwap_reclaim_control_event): recuperacion de VWAP tras perdida temporal, con volumen superior al retroceso.
7. [`Panic_Dip_Reversal_Event`](#11-panic_dip_reversal_event): caida rapida extrema que deja de acelerar y revierte con volumen comprador.
8. [`First_Green_Day_High_Close_Event`](#12-first_green_day_high_close_event): primer dia verde con volumen historico y cierre cerca del HOD.
9. [`First_Day_Runner_Frontside_Dip_Event`](#13-first_day_runner_frontside_dip_event): dip en frontside durante el primer dia de runner, con estructura alcista viva.
10. [`First_Green_Day_Bounce_Event`](#14-first_green_day_bounce_event): primer rebote verde despues de una destruccion parcial del runner.
11. [`Gap_And_Grab_Reversal_Event`](#15-gap_and_grab_reversal_event): apertura roja, base tipo V y recuperacion agresiva de resistencias.
12. [`Gap_And_Go_Premarket_High_Breakout_Event`](#16-gap_and_go_premarket_high_breakout_event): ruptura del premarket high durante apertura con volumen y continuacion.

Mapa de busqueda inicial:

| Evento | Familia candidata | Grano | Ancla temporal | Observables primarios |
| --- | --- | --- | --- | --- |
| `Daily_Resistance_Volume_Breakout_Event` | `RESISTANCE_AND_BREAKOUTS` | `ticker_day + intraday_window` | primera vela que cierra sobre resistencia | nivel, close sobre nivel, volumen de ruptura |
| `Breakout_First_Dip_Hold_Event` | `RESISTANCE_AND_BREAKOUTS` | `event_interval` | primer low del dip posterior al breakout | profundidad del dip, distancia al nivel roto, cierres bajo nivel |
| `Red_To_Green_Level_Reclaim_Event` | `INTRADAY_REVERSALS` | `ticker_session` | vela que recupera `prior_close` | gap rojo, minutos bajo prior close, volumen de reclaim |
| `Red_Base_Volume_Ramp_Event` | `INTRADAY_REVERSALS` | `intraday_window` | low inicial de la base roja | duracion de base, lower lows, decay de venta, rampa de volumen |
| `VWAP_Bounce_After_Extension_Event` | `VWAP_CONTROL` | `ticker_session` | touch/aproximacion a VWAP tras extension | distancia high-VWAP, low-VWAP, hold/rebote |
| `VWAP_Reclaim_Control_Event` | `VWAP_CONTROL` | `intraday_window` | cierre que recupera VWAP | duracion bajo VWAP, volumen de reclaim, hold posterior |
| `Panic_Dip_Reversal_Event` | `INTRADAY_REVERSALS` | `intraday_window` | low de panico o primera vela de reversa | drop pct, duracion del drop, reversal volume, no break del low |
| `First_Green_Day_High_Close_Event` | `RUNNER_LIFECYCLE` | `ticker_day` | cierre de sesion | daily return, volume rank, close location, VWAP relation |
| `First_Day_Runner_Frontside_Dip_Event` | `RUNNER_LIFECYCLE` | `ticker_session` | low del dip frontside | day gain, pullback depth, VWAP hold, higher low |
| `First_Green_Day_Bounce_Event` | `RUNNER_LIFECYCLE` | `ticker_day` | cierre del primer dia verde tras drawdown | runner high, drawdown, retained gain, reversal volume |
| `Gap_And_Grab_Reversal_Event` | `INTRADAY_REVERSALS` | `ticker_session` | low de V o primera vela de pickup | gap down, V depth, sell volume decay, resistance reclaim |
| `Gap_And_Go_Premarket_High_Breakout_Event` | `MOMENTUM_EXPANSION` | `ticker_session` | vela regular que rompe PMH | gap, PM volume, PMH break, breakout volume, hold sobre PMH |

La tabla no sustituye la definicion de cada evento. Su funcion es orientar el
primer detector exploratorio y la UI de notebook.

## 5. Daily_Resistance_Volume_Breakout_Event

### Que ocurre

El precio rompe una resistencia daily visible y lo hace con volumen
anormalmente alto. El evento no es "precio sube"; es la combinacion de:

```text
nivel historico relevante
-> consolidacion o rechazo previo bajo ese nivel
-> vela que cierra por encima
-> volumen superior al contexto anterior
```

### Imagenes fuente

<img src="source_assets/edu_trades/000_breakout.png" width="760" alt="000 - Breakout diario con resistencia y volumen">

<img src="source_assets/edu_trades/001_breakout.png" width="760" alt="001 - Breakout intradia y niveles de riesgo">

### Texto del trader

El documento fuente presenta el Breakout como una ruptura de resistencia clave
con volumen confirmatorio. La resistencia puede ser maximo del dia anterior,
52-week high o una zona donde el precio fallo antes. El trader advierte que el
volumen valida la demanda y que una ruptura vertical sin estructura previa
puede ser fakeout.

### Definicion observable v0

Unidad de busqueda:

```text
ticker_day + intraday confirmation
```

Secuencia minima:

```text
1. existe resistance_level calculable desde daily o premarket/dia previo
2. precio cotiza bajo o cerca del nivel antes de romperlo
3. una vela cierra por encima de resistance_level
4. volumen de la vela o ventana de ruptura > volumen promedio reciente
```

Inicio conceptual:

```text
primera vela que cierra por encima de resistance_level
```

Fin conceptual:

```text
fin de la ventana de confirmacion o primer pullback posterior
```

### Busqueda historica v0

Inputs esperados:

```text
daily OHLCV
1m/5m OHLCV
session calendar
```

Features candidatas:

```text
resistance_level
resistance_source = previous_day_high | 52w_high | multi_day_high
close_above_level_pct
breakout_volume_ratio
bars_below_level_before_break
prior_consolidation_minutes
breakout_followthrough_5m_pct
```

Thresholds semilla:

```text
close >= resistance_level * 1.002
breakout_volume_ratio >= 2.0
prior_consolidation_minutes >= 5
```

Excluir o marcar `review_event` si:

```text
breakout ocurre sin volumen
spread extremo
vela rompe y cierra inmediatamente por debajo
gap abre muy por encima del nivel sin interaccion local
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `Breakout`;
- `Gap and Go`;
- `First Green Day`;
- `High of Day Breakout`.

Composicion didactica:

```text
Daily_Resistance_Volume_Breakout_Event
+ Breakout_First_Dip_Hold_Event
+ VWAP_Bounce_After_Extension_Event
```

### No es estrategia

No define actuar sobre la ruptura ni sobre el dip posterior. Solo marca que una
resistencia fue rota con volumen.

## 6. Breakout_First_Dip_Hold_Event

### Que ocurre

Despues de un breakout confirmado, el precio retrocede hacia el nivel roto y no
lo destruye. El evento mide si el antiguo techo empieza a comportarse como zona
de aceptacion o soporte.

### Imagenes fuente

<img src="source_assets/edu_trades/001_breakout.png" width="760" alt="001 - Entradas ideales en niveles de breakout">

<img src="source_assets/edu_trades/013_gapandgo.png" width="760" alt="013 - Dip luego del breakout del premarket high">

### Texto del trader

El texto dice que en Breakout no se busca necesariamente la vela exacta de la
ruptura, sino el primer dip posterior a la confirmacion. Para TSIS, esa frase
describe un retest: el mercado prueba si el nivel roto se acepta o si la
ruptura fue falsa.

### Definicion observable v0

Unidad de busqueda:

```text
event_interval despues de Daily_Resistance_Volume_Breakout_Event
```

Secuencia minima:

```text
1. existe breakout previo
2. precio retrocede desde el high posterior al breakout
3. low del dip se acerca al nivel roto
4. el precio no cierra claramente por debajo del nivel
5. aparece vela de estabilizacion o recuperacion
```

Inicio conceptual:

```text
primera vela despues del breakout cuyo low retrocede hacia el nivel roto
```

Fin conceptual:

```text
vela que confirma hold/reclaim o cierre bajo invalidation_level
```

### Busqueda historica v0

Features candidatas:

```text
breakout_level
post_breakout_high
dip_low
dip_depth_from_high_pct
dip_low_to_breakout_level_pct
closes_below_level_count
recovery_close_above_level
volume_on_dip_vs_breakout
```

Thresholds semilla:

```text
dip_low <= breakout_level * 1.03
closes_below_level_count <= 1
recovery_close_above_level = true
```

Excluir o marcar `invalid_event` si:

```text
dip rompe el nivel y no recupera
dip ocurre muchas horas despues sin relacion con breakout
breakout previo no tuvo volumen
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `Breakout`;
- `Gap and Go`;
- `First Pullback Continuation`;
- `VWAP Bounce`.

### No es estrategia

No dice actuar sobre el pullback. Describe que el mercado testeo y sostuvo la zona
rota.

## 7. Red_To_Green_Level_Reclaim_Event

### Que ocurre

La accion abre por debajo del cierre anterior y durante la sesion recupera ese
nivel. El evento es el cambio de estado de rojo a verde, confirmado por volumen
o aceptacion sobre el nivel.

### Imagenes fuente

<img src="source_assets/edu_trades/003_redtogreen.png" width="760" alt="003 - Nivel del R/G e incremento de volumen">

<img src="source_assets/edu_trades/0004_redtogreen.png" width="760" alt="0004 - Spike del open, posterior G/R y gran volumen">

### Texto del trader

El documento fuente define Red to Green como una accion que abre roja y logra
girarse a verde durante el dia. La confirmacion llega cuando cruza el nivel
red-to-green con volumen mayor al promedio de las velas anteriores.

### Definicion observable v0

Unidad de busqueda:

```text
ticker_session
```

Secuencia minima:

```text
1. open < prior_close
2. precio permanece bajo prior_close durante una fase inicial
3. precio cruza prior_close al alza
4. la vela de reclaim muestra volumen superior al contexto inmediato
5. al menos una vela posterior sostiene el nivel o no lo destruye
```

Inicio conceptual:

```text
primera vela que cruza/cierra sobre prior_close
```

Fin conceptual:

```text
confirmacion de hold sobre prior_close o perdida inmediata del nivel
```

### Busqueda historica v0

Features candidatas:

```text
prior_close
open_gap_pct
minutes_red_before_reclaim
reclaim_ts
reclaim_close_above_prior_close_pct
reclaim_volume_ratio
post_reclaim_hold_minutes
vwap_relation_at_reclaim
```

Thresholds semilla:

```text
open_gap_pct < 0
reclaim_close >= prior_close
reclaim_volume_ratio >= 1.5
post_reclaim_hold_minutes >= 3
```

Excluir o marcar `review_event` si:

```text
reclaim ocurre en una sola wick y cierra debajo
prior_close no es fiable
accion ya abrio verde
```

### Composicion observable no operativa

Puede aparecer como pieza observable dentro de:

- `Red to Green`;
- `Gap and Grab Reversal`;
- `First Green Day Bounce`;
- `VWAP Reclaim`.

### No es estrategia

No define accion sobre el cruce ni sobre el dip posterior. Solo detecta la
recuperacion del nivel que cambia el color del dia.

