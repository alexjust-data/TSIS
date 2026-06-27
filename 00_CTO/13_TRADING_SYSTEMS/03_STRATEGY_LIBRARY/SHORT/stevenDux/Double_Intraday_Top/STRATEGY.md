# Double Intraday Top Strategy - Duxinator Source Draft v0.1

Fecha: 2026-06-27
Estado: source_note / strategy draft.
Fuente primaria: Steven Dux - Duxinator - `5 - Double Intra-day Top`.

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Double Intraday Top`
segun el material Duxinator.

No valida edge.
No crea parametros institucionales.
No autoriza operativa.

## 2. Resumen tecnico

`Double Intraday Top` es una estrategia short sobre multi-day runners que busca
esperar una segunda consolidacion/top intradia antes de shortear el crack.

La tesis:

```text
primer top intradia no se debe confiar
segundo top/consolidacion + red-day transition + volumen/cap maximo
= mejor candidato short
```

Dux la asocia a multi-day runners donde el volumen aumenta dia a dia y se acerca
a un maximo estadistico de participacion.

## 3. Condiciones minimas del setup

### 3.1. Multi-day runner

Fuente:

```text
first green day
second green day
third/fourth day with larger volume
```

### 3.2. Market cap inicial

Fuente:

```text
beginning market cap < 100M
```

### 3.3. Volumen creciente y maximo de volumen

Dux menciona ejemplos:

```text
day1 volume = 10M
day2 volume = 20M
day3 volume = 30M
day4 volume = 40M
```

Tambien menciona que en su estadistica el maximo visto suele estar alrededor de:

```text
100M-140M shares
```

### 3.4. Dollar cap

Dux propone convertir volumen maximo a dollar volume segun el precio medio de
consolidacion.

```text
max_dollar_cap = max_share_volume * average_consolidation_price
```

Luego aplica ese dollar cap a distintos precios para estimar cuantas shares
podrian representar saturacion.

### 3.5. Segundo top/consolidacion

La regla fuente es fuerte:

```text
never trust first intraday resistance
focus on second day consolidation
```

TSIS debe medir:

```text
first_intraday_top
second_intraday_top
top_distance_pct
second_top_crack_ts
```

### 3.6. Red transition

Dux quiere que el stock vaya rojo o este cerca de ir rojo al romper la segunda
consolidacion.

```text
distance_to_red_pct
red_transition_ts
```

## 4. Formulas candidatas

### 4.1. Max dollar cap

```text
max_dollar_cap =
  max_observed_share_volume * average_consolidation_price
```

### 4.2. Equivalent max shares at current price

```text
equivalent_max_shares =
  max_dollar_cap / current_consolidation_price
```

### 4.3. Distance to red

```text
distance_to_red_pct =
  (current_price / prior_close - 1) * 100
```

### 4.4. Second-top crack depth

```text
second_top_crack_depth_pct =
  (second_top_consolidation_low - crack_close) /
  second_top_consolidation_low * 100
```

## 5. Estados candidatos

```text
multi_day_runner_volume_ramp
max_volume_cap_approach
first_intraday_top_ignore
second_intraday_top_candidate
second_top_crack_candidate
red_transition_confirmed
double_intraday_top_active
invalid_first_top_only
invalid_no_red_transition
```

## 6. Campos minimos para candidate_table

```text
candidate_id
ticker
exchange
company_name
session_date
run_day_index
market_cap_at_run_start
daily_volume_sequence
daily_dollar_volume_sequence
max_dollar_cap
equivalent_max_shares
first_intraday_top_ts
first_intraday_top_price
second_intraday_top_ts
second_intraday_top_price
second_top_consolidation_low
second_top_crack_ts
distance_to_red_pct
red_transition_ts
strategy_state
review_bucket
```

## 7. Charts requeridos para notebook

### 7.1. Multi-day volume ramp chart

Debe mostrar:

- dias del runner;
- volumen diario;
- dollar volume;
- run day index;
- max dollar cap.

### 7.2. Intraday double-top chart

Debe mostrar:

- primer top intradia;
- segundo top intradia;
- crack de la segunda consolidacion;
- linea de prior close;
- transicion a rojo.

## 8. Diferencia con eventos

Este documento es Strategy Library porque contiene respuesta short.

Eventos futuros:

```text
Multi_Day_Runner_Volume_Ramp_Event
Max_Dollar_Cap_Approach_Event
Second_Intraday_Top_Event
Second_Top_Crack_Event
Red_Transition_After_Second_Top_Event
```

## 9. Imagenes deseadas del propio video

Solo se deben usar capturas de `5 - Double Intra-day Top`.

Capturas deseadas:

```text
00:19-01:15  multi-day runner con volumen creciente
01:20-03:25  max share volume y max dollar cap
04:11-04:45  primer intraday top que no debe confiarse
04:45-05:43  segundo top, crack y red transition
05:43-06:54  advertencia de no confiar en el primer top
```

## 10. Regla final

La pregunta correcta no es:

```text
hay un top intradia?
```

La pregunta correcta es:

```text
hay un multi-day runner saturado por volumen/dollar cap que forma segundo top
intradia y falla cerca de una transicion a rojo?
```
