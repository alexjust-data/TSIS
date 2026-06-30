# Dip Buying Multi-Day Runner Strategy - Duxinator Source Draft v0.1

Fecha: 2026-06-27
Estado: source_note / strategy draft.
Fuente primaria: Steven Dux - Duxinator - `7 - Dip Buying Multi-day Runner`.

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Dip Buying Multi-Day
Runner` segun el material Duxinator.

No valida edge.
No crea parametros institucionales.
No autoriza operativa.

## 2. Resumen tecnico

Dux distingue entre dip buying malo y dip buying viable.

La tesis:

```text
dip buying en OTC/microcap inactivo suele ser peligroso
dip buying en Nasdaq/high cap activo/multi-day runner puede tener soporte real
```

La estrategia viable requiere:

1. market cap alto relativo;
2. volumen masivo;
3. multi-day runner;
4. soporte o consolidacion clara;
5. panic medible;
6. bounce esperado como fraccion del panic.

## 3. No-goal: OTC dip buy

Dux lo desaconseja, especialmente si:

```text
stock no activo
menos de 10M shares diarios
no multi-day runner
crack 30%-50% sin soporte claro
ejecucion OTC lenta
```

TSIS debe conservar esta parte como avoid context.

## 4. Condiciones para Nasdaq/high-cap dip buy

### 4.1. Market cap

Fuente:

```text
market_cap >= 500M
```

### 4.2. Volumen masivo

Fuente:

```text
100M-140M shares on the day
```

### 4.3. Multi-day runner

Debe ser ticker activo, con hype y continuidad previa.

### 4.4. Most consolidation / support

El dip debe llegar a una zona de soporte o consolidacion previa.

Sin soporte:

```text
avoid
```

## 5. Bounce target

Dux menciona:

```text
average bounce ~= 50% of entire panic
maximum bounce ~= 75% of entire panic
```

Toma parcial sugerida por fuente:

```text
empezar a tomar beneficios cuando profit > 20%
al menos tomar half
evitar esperar mas alla de 75% del panic
```

## 6. Formulas candidatas

### 6.1. Panic range

```text
panic_range = panic_start_price - panic_low_price
panic_pct = panic_range / panic_start_price * 100
```

### 6.2. Bounce levels

```text
half_panic_bounce_price =
  panic_low_price + 0.50 * panic_range

max_panic_bounce_price =
  panic_low_price + 0.75 * panic_range
```

### 6.3. Support distance

```text
distance_to_support_pct =
  (entry_reference_price / support_price - 1) * 100
```

## 7. Estados candidatos

```text
otc_dip_buy_avoid
inactive_microcap_dip_avoid
nasdaq_highcap_dip_candidate
multi_day_runner_dip_candidate
panic_into_support_candidate
half_panic_bounce_target
max_panic_bounce_zone
no_support_invalid
```

## 8. Campos minimos para candidate_table

```text
candidate_id
ticker
exchange
company_name
session_date
market_cap
daily_volume
multi_day_runner_flag
panic_start_ts
panic_start_price
panic_low_ts
panic_low_price
panic_pct
support_price
support_source_type
distance_to_support_pct
half_panic_bounce_price
max_panic_bounce_price
actual_bounce_high
actual_bounce_pct_of_panic
strategy_state
review_bucket
```

## 9. Charts requeridos para notebook

### 9.1. Multi-day runner context

Debe mostrar:

- dias previos;
- volumen;
- market cap;
- si es active runner.

### 9.2. Panic into support detail

Debe mostrar:

- panic start;
- panic low;
- soporte/consolidacion;
- bounce 50%;
- bounce 75%;
- volumen.

### 9.3. Avoid microcap chart

Debe mostrar:

- gap microcap que pierde 75%-100% del gain;
- ausencia de soporte;
- no comeback.

## 10. Diferencia con eventos

Este documento es Strategy Library porque contiene decision long y profit
management.

Eventos futuros:

```text
Multi_Day_Runner_Panic_Event
Panic_Into_Support_Event
Half_Panic_Bounce_Event
Microcap_No_Support_Dip_Avoid_Context
```

## 11. Imagenes deseadas del propio video

Solo se deben usar capturas de `7 - Dip Buying Multi-day Runner`.

Capturas deseadas:

```text
00:18-03:27  OTC dip buy avoid y ejecucion lenta
03:39-05:29  Nasdaq/high-cap active runner criteria
05:29-06:24  50% y 75% del panic como bounce levels
07:03-08:54  microcap gap que pierde 75%-100% y no vuelve
```

## 12. Regla final

La pregunta correcta no es:

```text
ha caido mucho?
```

La pregunta correcta es:

```text
es un runner activo de suficiente calidad que esta haciendo panic hacia soporte
real, o es un microcap destruido sin soporte ni comeback estadistico?
```
