# Bounce Plus Gap Up Short Strategy - Duxinator Source Draft v0.1

Fecha: 2026-06-27
Estado: source_note / strategy draft.
Fuente primaria: Steven Dux - Duxinator - `3 - Bounce Short plus Gap Up Short`.

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Bounce Plus Gap Up Short`
segun el material Duxinator.

No valida edge.
No crea parametros institucionales.
No autoriza operativa.

Su funcion es separar tres ideas que Dux presenta juntas:

```text
Gap Up Short
Bounce Short
Bounce Plus Gap Up Short
```

La estrategia combinada nace cuando un ticker esta rebotando hacia una
resistencia previa y ademas gapea en premarket hacia esa zona.

## 2. Resumen tecnico

`Bounce Plus Gap Up Short` no es cualquier gap.

Es una combinacion short donde:

1. existe una resistencia previa dentro del ultimo ano;
2. el ticker rebota o gapea hacia esa resistencia;
3. el gap premarket es suficientemente grande;
4. el volumen estimado del dia no supera la resistencia de volumen previa;
5. el float no es demasiado pequeno;
6. al llegar a resistencia, el ticker tiende a fallar.

La idea central es:

```text
gap fuerte hacia resistencia previa
+ volumen actual insuficiente frente a resistencia historica
= mayor probabilidad de rechazo/fade
```

## 3. Componentes de la fuente

### 3.1. Gap Up Short individual

Dux describe `Gap Up Short` como un gap sin resistencia cercana, donde el ticker
empuja un porcentaje medio y luego tiende a crackear.

Lectura aproximada de la fuente:

```text
low float extremo -> push medio 25%-30% o mas
float 3M-10M/30M -> push medio 20%-25%
```

TSIS debe tratar estos porcentajes como etiquetas de fuente, no como reglas
institucionales.

### 3.2. Bounce Short individual

`Bounce Short` aparece cuando un ticker tiene resistencia dentro del ultimo ano,
rebota hacia esa resistencia y falla al llegar.

La tesis conductual:

```text
bagholders previos venden cerca de break-even cuando el precio vuelve a su zona
```

### 3.3. Combinacion Bounce Plus Gap

La combinacion ocurre cuando el ticker:

```text
rebota hacia resistencia
+ gapea en premarket hacia esa resistencia
```

Ejemplo fuente:

```text
resistencia = 3.00
gap premarket cerca de 2.80
```

## 4. Condiciones minimas del setup

### 4.1. Market cap

Fuente:

```text
market_cap < 100M
```

### 4.2. Float

Fuente:

```text
float > 2M
```

Dux evita floats demasiado pequenos para esta combinacion porque pueden romper
la resistencia con menos volumen.

### 4.3. Gap premarket

Fuente:

```text
premarket_gap_pct >= 50%
```

Si el gap es inferior a 50%, la fuente no lo llama `Bounce Plus Gap` limpio.

### 4.4. Resistencia previa

Debe existir resistencia previa relevante dentro de aproximadamente un ano.

Campos candidatos:

```text
resistance_price
resistance_date
resistance_age_days
resistance_volume
resistance_dollar_volume
resistance_source_type
```

### 4.5. Ratio volumen actual vs resistencia

Dux insiste en comparar el volumen estimado actual contra el volumen de la
resistencia previa.

```text
current_estimated_volume / resistance_volume
```

La fuente menciona:

```text
1:10 -> mejor caso
1:3  -> peor que 1:10
1:1  -> minimo aceptable / frontera
```

Si el volumen actual empieza a superar la resistencia, la tesis short se
degrada.

## 5. Formulas candidatas

### 5.1. Gap premarket

```text
premarket_gap_pct =
  (premarket_reference_price / prior_close - 1) * 100
```

### 5.2. Estimacion de volumen del dia

Dux usa heuristicas de volumen premarket para estimar volumen diario.

```text
estimated_day_volume =
  premarket_volume * volume_projection_multiplier
```

La fuente usa ejemplos tipo:

```text
1M premarket -> 10M estimated day volume
```

### 5.3. Ratio contra resistencia

```text
volume_resistance_ratio =
  estimated_day_volume / resistance_volume
```

Interpretacion inicial:

```text
ratio <= 0.10 -> resistencia domina mucho mas que el volumen actual
ratio <= 1.00 -> criterio fuente minimo
ratio > 1.00  -> volumen actual puede estar sobrepasando la resistencia
```

### 5.4. Fade objetivo de mitad del gap

Dux menciona que cuando funciona, suele perder alrededor de la mitad de su
ganancia.

```text
gap_range = gap_reference_price - prior_close
half_gap_fade_price = gap_reference_price - 0.50 * gap_range
```

## 6. Estados candidatos

```text
gap_up_short_component
bounce_short_component
bounce_plus_gap_candidate
resistance_volume_dominant
resistance_volume_overwhelmed
straight_dump_open_risk
push_into_resistance_short_candidate
invalid_bounce_plus_gap
```

| Estado | Significado |
|---|---|
| `gap_up_short_component` | Gap fuerte con extension esperada, sin validar resistencia. |
| `bounce_short_component` | Rebote hacia resistencia previa. |
| `bounce_plus_gap_candidate` | Gap fuerte hacia resistencia previa. |
| `resistance_volume_dominant` | El volumen estimado actual es menor que el volumen de resistencia. |
| `resistance_volume_overwhelmed` | El volumen actual puede superar la resistencia y degradar la tesis short. |
| `straight_dump_open_risk` | El ticker cae directo al abrir y no ofrece push/risk-reward limpio. |
| `push_into_resistance_short_candidate` | Hay push hacia resistencia, que Dux considera mejor para risk/reward. |
| `invalid_bounce_plus_gap` | Falta gap, resistencia, float o ratio. |

## 7. Campos minimos para candidate_table

```text
candidate_id
ticker
exchange
company_name
session_date
market_cap
float
prior_close
premarket_reference_price
premarket_gap_pct
premarket_volume
estimated_day_volume
volume_projection_multiplier
resistance_price
resistance_date
resistance_age_days
resistance_volume
resistance_dollar_volume
volume_resistance_ratio
gap_range
half_gap_fade_price
push_into_resistance_ts
push_into_resistance_price
open_dump_flag
strategy_state
review_bucket
```

## 8. Charts requeridos para notebook

### 8.1. Daily resistance chart

Debe mostrar:

- resistencia previa;
- volumen de la resistencia;
- edad de la resistencia;
- zona de bagholders.

### 8.2. Premarket gap into resistance chart

Debe mostrar:

- prior close;
- gap premarket;
- volumen premarket;
- resistencia previa;
- distancia a resistencia.

### 8.3. Open / push / dump detail

Debe mostrar:

- si hubo push hacia resistencia;
- si hubo straight dump;
- half-gap fade level;
- volumen 1m;
- VWAP;
- EMA8/Wilder8 overlay si aplica.

## 9. Diferencia con eventos

Este documento es de Strategy Library porque contiene respuesta operativa short.

Eventos futuros derivados:

```text
Premarket_Gap_Into_Resistance_Event
Resistance_Volume_Dominance_Context
Bounce_To_Prior_Resistance_Event
Straight_Dump_After_Gap_Event
Half_Gap_Fade_Event
```

## 10. Imagenes deseadas del propio video

Solo se deben usar capturas de `3 - Bounce Short plus Gap Up Short`.

Capturas deseadas:

```text
00:20-01:12  ratio de volumen actual vs volumen de resistencia
01:29-01:59  explicacion visual de Gap Up Short individual
01:59-02:44  explicacion visual de Bounce Short individual y bagholders
03:04-03:52  ejemplo resistencia 3.00 y gap cerca de 2.80
04:05-04:58  push into resistance, straight dump y half-gap fade
05:09-06:33  lista final de criterios: market cap, float, gap, ratio
```

## 11. Regla final

La pregunta correcta no es:

```text
hay un gap fuerte?
```

La pregunta correcta es:

```text
el ticker gapea hacia una resistencia previa cuyo volumen historico sigue
dominando al volumen estimado actual?
```
