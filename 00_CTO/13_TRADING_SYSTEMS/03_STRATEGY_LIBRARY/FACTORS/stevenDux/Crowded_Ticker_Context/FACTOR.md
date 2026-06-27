# Crowded Ticker Context Factor - Duxinator Advance Concepts Draft v0.1

Fecha: 2026-06-27
Estado: source_note / factor draft.
Fuente primaria:

```text
Steven Dux - Duxinator - 4 - Advance Concepts
8 - Characteristics of Crowded Tickers
```

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Crowded Ticker Context`.

No es una estrategia direccional.
No valida edge.
No autoriza operativa.

Es un factor de exclusion, degradacion y espera.

La pregunta central es:

```text
el ticker esta tan crowded hoy que el comportamiento intradia deja de ser
predecible y conviene esperar una oportunidad posterior?
```

## 2. Idea central

Dux describe que cuando demasiada gente mira y opera el mismo ticker, el
movimiento intradia puede volverse poco predecible.

Lectura fuente:

```text
si shorteas, sube;
si compras, baja;
el ticker hace lo contrario de lo esperado durante el dia.
```

Interpretacion TSIS:

```text
crowding degrada la calidad del setup intradia.
```

## 3. Crowding no siempre es malo

La idea importante es que un ticker crowded hoy puede crear oportunidad futura.

Lectura fuente:

```text
the more crowded today, the better for future resistance.
```

Traduccion TSIS:

```text
un dia crowded puede construir resistencia/volumen historico que luego alimenta
Bounce Short u otros fades en 2-3 semanas.
```

## 4. Estados del factor

```text
crowding_unknown
not_crowded
moderately_crowded
intraday_crowded_avoid
future_resistance_building
future_bounce_short_source
```

| Estado | Significado |
|---|---|
| `crowding_unknown` | Faltan inputs. |
| `not_crowded` | Volumen/atencion no sugieren crowding material. |
| `moderately_crowded` | Puede operar, pero requiere cautela. |
| `intraday_crowded_avoid` | El dia actual es demasiado competido. |
| `future_resistance_building` | El volumen actual puede construir resistencia futura. |
| `future_bounce_short_source` | Candidato a fuente historica para Bounce Short futuro. |

## 5. Variables candidatas

```text
premarket_volume
estimated_day_volume
session_volume_to_time
market_cap
float
estimated_float_rotation
social_attention_proxy
scanner_presence
intraday_fakeout_count
range_instability_pct
future_resistance_volume
```

## 6. Formulas candidatas

### 6.1. Crowding volume ratio

```text
crowding_volume_ratio =
  estimated_day_volume / float
```

Es equivalente a una estimacion de float rotation, pero aqui se usa como
contexto de crowding.

### 6.2. Intraday instability

Formula exploratoria:

```text
intraday_instability_score =
  fakeout_count + failed_breakout_count + failed_breakdown_count
```

### 6.3. Future resistance source

```text
future_resistance_volume =
  session_volume_in_crowded_day
```

```text
future_resistance_dollar_volume =
  sum(volume_i * price_i for crowded-day bars)
```

## 7. Uso correcto

### 7.1. Dia actual

Si el ticker esta crowded hoy:

```text
degradar o evitar la estrategia intradia.
```

### 7.2. Futuro

Guardar el dia crowded como:

```text
resistance source candidate
```

Despues, si el ticker vuelve a esa zona con menos volumen, puede alimentar:

```text
Bounce Short
Prior Volume Resistance
Dollar Block Resistance
```

## 8. Campos minimos para factor_table

```text
factor_id
ticker
exchange
company_name
session_date
strategy_context
market_cap
float
premarket_volume
estimated_day_volume
session_volume
estimated_float_rotation
crowding_volume_ratio
intraday_instability_score
crowding_state
future_resistance_price_zone_low
future_resistance_price_zone_high
future_resistance_volume
future_resistance_dollar_volume
review_required
```

## 9. Aplicacion por estrategia

### 9.1. Gap Up Short

Un ticker demasiado crowded puede invalidar el short intradia.

### 9.2. Bounce Short

El mismo dia crowded puede convertirse en fuente de resistencia futura.

### 9.3. Long momentum / DAS

Crowding puede indicar atencion y oportunidad, pero tambien fakeouts y rango
menos estable.

## 10. Chart requirements

Un notebook debe mostrar:

- volumen premarket;
- volumen esperado;
- float rotation estimada;
- si el dia esta marcado `intraday_crowded_avoid`;
- zona de precio donde se construyo resistencia futura;
- volumen/dollar-volume de esa zona.

## 11. Imagenes deseadas del propio video

No se deben insertar imagenes de otros videos.

Capturas deseadas:

```text
8 - Characteristics of Crowded Tickers:
00:00-00:45  crowding makes intraday unpredictable
00:45-01:30  mentality: do not overtrade crowded action
01:30-02:00  crowded today can create future opportunity
02:00-02:30  wait 2-3 weeks / short into built resistance
```

## 12. Regla final

Crowded Ticker Context no dice:

```text
operar ahora.
```

Dice:

```text
hoy puede ser demasiado impredecible,
pero el volumen de hoy puede crear la resistencia estadistica de manana.
```
