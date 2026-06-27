# Volume Prediction Factor - Duxinator Advance Concepts Draft v0.1

Fecha: 2026-06-27
Estado: source_note / factor draft.
Fuente primaria:

```text
Steven Dux - Duxinator - 4 - Advance Concepts
1 - Volume Prediction Intraday
2 - Scenarios of Intraday Volume Prediction
3 - Volume Prediction Pre-Market
```

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Volume Prediction` segun
los tres primeros transcripts de `Advance Concepts`.

No es una estrategia direccional.
No valida edge.
No autoriza operativa.

Es un factor transversal que ayuda a decidir si una estrategia candidata tiene
contexto estadistico suficiente o si debe ser descartada por:

- volumen demasiado bajo;
- volumen demasiado crowded;
- float rotation excesiva;
- resistencia historica neutralizada;
- resistencia historica todavia dominante.

La pregunta central es:

```text
cuanto volumen es probable que negocie el ticker durante el dia,
y como compara ese volumen contra float, resistencia historica y crowding?
```

## 2. Por que importa

Dux usa la prediccion de volumen para responder preguntas practicas:

```text
el ticker esta perdiendo equity?
puedo mantener hasta el final del dia?
debo cubrir en mitad de una consolidacion?
el ticker se volvera demasiado crowded?
hay tan poco volumen que no merece operar?
la resistencia historica puede aguantar?
el volumen actual puede romper o neutralizar esa resistencia?
```

Para TSIS, este factor debe existir antes de optimizar estrategias porque muchas
estructuras visuales cambian completamente de significado segun el volumen
esperado del dia.

## 3. Relacion con otros factores

Este factor esta conectado con:

```text
FACTORS/stevenDux/Float_Rotation/FACTOR.md
FACTORS/stevenDux/Pattern_Variation_Acceptable_Range/FACTOR.md
```

Regla:

```text
Volume Prediction estima cuanto volumen puede aparecer.
Float Rotation mide cuantas veces ese volumen renueva el float.
Pattern Variation decide si una ruptura o variacion sigue siendo aceptable.
```

## 4. Formulas fuente

### 4.1. Prediccion desde premarket

Formula fuente aproximada:

```text
estimated_day_volume_from_premarket =
  premarket_volume * 10
```

Ejemplo:

```text
premarket_volume = 2M
estimated_day_volume_from_premarket = 20M
```

### 4.2. Prediccion desde primera hora

Formula fuente alternativa:

```text
estimated_day_volume_from_first_hour =
  first_hour_volume * 4
```

Uso:

```text
si la prediccion desde premarket no parece estable,
usar primera hora como segunda estimacion.
```

### 4.3. Rango de prediccion

TSIS no debe asumir una sola prediccion puntual.

Campos recomendados:

```text
estimated_day_volume_low
estimated_day_volume_mid
estimated_day_volume_high
```

Ejemplo inicial:

```text
estimated_day_volume_low  = premarket_volume * 5
estimated_day_volume_mid  = premarket_volume * 10
estimated_day_volume_high = first_hour_volume * 4
```

La fuente usa multiplicadores simples. TSIS debera medir despues si esos
multiplicadores sobreviven por ano, market cap, float, precio, sector y hora.

## 5. Limite critico: microfloat y float rotation

Dux advierte que la prediccion de volumen no debe interpretarse igual cuando el
float rota muchas veces.

Ejemplo fuente:

```text
float = 2M
estimated_day_volume = 20M
estimated_float_rotation = 10x
```

Lectura:

```text
cuando el float rota demasiado, entran compradores nuevos y la resistencia
historica puede perder capacidad predictiva.
```

Regla TSIS:

```text
Volume Prediction no debe usarse sola en microfloat o high-rotation names.
```

Debe combinarse con:

```text
float
float_rotation
market_cap
resistance_volume
resistance_dollar_volume
crowding_state
```

## 6. Escenarios contra resistencia historica

La aplicacion mas importante del factor es comparar volumen esperado actual
contra volumen historico de resistencia.

### 6.1. Current volume overwhelms resistance

Condicion conceptual:

```text
estimated_day_volume > resistance_volume
```

Lectura:

```text
el volumen actual puede neutralizar la resistencia historica.
```

Consecuencia:

```text
shorting against resistance becomes risky.
```

Estado:

```text
resistance_volume_overwhelmed
```

### 6.2. Current volume close to resistance

Condicion conceptual:

```text
estimated_day_volume ~= resistance_volume
```

Lectura:

```text
la resistencia puede romper o fallar; el caso requiere gestion estricta.
```

Consecuencia:

```text
do not size aggressively.
```

Estado:

```text
resistance_volume_near_match
```

### 6.3. Current volume below resistance

Condicion conceptual:

```text
estimated_day_volume < resistance_volume
```

Lectura:

```text
la resistencia historica todavia domina al volumen actual.
```

Consecuencia:

```text
bounce short / resistance fade context improves.
```

Estado:

```text
resistance_volume_dominant
```

## 7. Resistance volume quality

Dux sugiere que la resistencia necesita volumen material.

Lectura fuente:

```text
resistance_volume > 20M shares = usable resistance context
resistance_volume < 10M shares = weaker / less tradable for bounce short
```

TSIS debe tratar estos valores como fuente inicial, no como regla final.

Campos:

```text
resistance_volume
resistance_volume_bucket
resistance_volume_quality
```

## 8. Premarket volume buckets

Los buckets siguientes vienen del transcript `Volume Prediction Pre-Market`.

No son parametros institucionales finales.

| Premarket volume | Lectura fuente | Uso TSIS inicial |
|---|---|---|
| `< 1M` | Poco probable que este crowded. Puede ser bueno para Bounce Short o Gap Up Short. | `premarket_not_crowded` |
| `1M-1.5M` | Puede empezar a crowded, pero todavia puede ser trade candidate. | `premarket_moderate_attention` |
| `1.5M-2M` | Alta probabilidad de morning spike porque aparece en scanners. | `morning_spike_likely` |
| `> 4M` | Muy crowded; Dux sugiere evitar el dia actual en muchos casos. | `premarket_crowded_avoid` |

Regla:

```text
premarket volume debe leerse junto a float y market cap.
```

Ejemplo:

```text
4M shares en float 700k no significa lo mismo que 4M shares en float 50M.
```

## 9. Morning spike logic

Cuando el premarket volume esta en zona de alta atencion, Dux espera que muchos
compradores entren al open.

Lectura fuente:

```text
1.5M-2M premarket volume -> likely morning spike
```

Consecuencia para shorts:

```text
no perseguir short en open sin esperar el spike/momentum shift.
```

Consecuencia para longs:

```text
puede haber quick long context si no hay warrants, resistencia o bloque historico.
```

TSIS debe modelarlo como contexto, no como entrada:

```text
morning_spike_likelihood_context
```

## 10. Crowding logic

Dux trata el volumen premarket muy alto como posible senal de crowding.

Lectura:

```text
premarket_volume > 4M
-> estimated_day_volume puede superar 40M
-> el ticker puede volverse muy competido
-> patrones pueden volverse raros / fakeouts
```

Estado:

```text
crowded_volume_context
```

Consecuencia:

```text
No descartar automaticamente todos los casos,
pero no clasificarlos como clean setup sin revisar float, market cap, resistance
y comportamiento posterior al open.
```

## 11. Estados del factor

```text
volume_prediction_unavailable
premarket_not_crowded
premarket_moderate_attention
morning_spike_likely
premarket_crowded_avoid
resistance_volume_dominant
resistance_volume_near_match
resistance_volume_overwhelmed
high_rotation_invalidates_volume_resistance
microfloat_volume_prediction_degraded
```

| Estado | Significado |
|---|---|
| `volume_prediction_unavailable` | Faltan inputs para estimar volumen. |
| `premarket_not_crowded` | Premarket volume bajo; menos crowding inicial. |
| `premarket_moderate_attention` | Atencion suficiente pero no extrema. |
| `morning_spike_likely` | El volumen premarket sugiere spike al open. |
| `premarket_crowded_avoid` | Volumen premarket alto; riesgo de crowding/fakeouts. |
| `resistance_volume_dominant` | La resistencia historica domina al volumen esperado. |
| `resistance_volume_near_match` | Volumen actual y resistencia estan cerca. |
| `resistance_volume_overwhelmed` | El volumen actual puede neutralizar la resistencia. |
| `high_rotation_invalidates_volume_resistance` | Float rotation excesiva degrada la lectura de resistencia. |
| `microfloat_volume_prediction_degraded` | Microfloat hace que la prediccion sea menos fiable por rotacion rapida. |

## 12. Campos minimos para factor_table

```text
factor_id
ticker
exchange
company_name
session_date
strategy_context
market_cap
float
price_reference
premarket_volume
first_hour_volume
session_volume_to_time
estimated_day_volume_from_premarket
estimated_day_volume_from_first_hour
estimated_day_volume_low
estimated_day_volume_mid
estimated_day_volume_high
premarket_volume_bucket
estimated_float_rotation
observed_float_rotation_to_time
resistance_volume
resistance_dollar_volume
current_vs_resistance_volume_ratio
resistance_vs_current_volume_ratio
volume_prediction_state
crowding_state
review_required
```

## 13. Formulas candidatas

### 13.1. Current vs resistance ratio

```text
current_vs_resistance_volume_ratio =
  estimated_day_volume_mid / resistance_volume
```

### 13.2. Resistance pressure ratio

```text
resistance_vs_current_volume_ratio =
  resistance_volume / estimated_day_volume_mid
```

### 13.3. Estimated float rotation

```text
estimated_float_rotation =
  estimated_day_volume_mid / float
```

### 13.4. Observed float rotation to time

```text
observed_float_rotation_to_time =
  session_volume_to_time / float
```

## 14. Aplicacion por estrategia

### 14.1. Gap Up Short

Usar para:

- medir si el gap esta demasiado crowded;
- estimar volumen diario;
- marcar `morning_spike_likely`;
- evitar short temprano cuando el volumen premarket sugiere squeeze.

### 14.2. Bounce Short

Usar para:

- comparar volumen actual contra resistencia historica;
- decidir si la resistencia sigue siendo dominante;
- marcar si un retest tiene volumen suficiente para absorber bagholders.

### 14.3. First Red Day

Usar para:

- comparar volumen del dia actual contra dias previos;
- decidir si el movimiento sigue ganando volumen o empieza a perder calidad;
- segmentar por market cap/float.

### 14.4. DAS / long momentum

Usar con cautela:

- volumen creciente puede confirmar atencion;
- volumen excesivo en microfloat puede significar crowding;
- no debe sustituir la lectura de estructura, VWAP y momentum.

## 15. Chart requirements

Un notebook que use este factor debe imprimir en charts o summary panel:

```text
premarket_volume
first_hour_volume
estimated_day_volume_from_premarket
estimated_day_volume_from_first_hour
estimated_float_rotation
resistance_volume if available
current_vs_resistance_volume_ratio
volume_prediction_state
```

Para casos de resistencia, el chart debe mostrar:

- zona de resistencia;
- volumen historico que la crea;
- volumen actual acumulado;
- prediccion de volumen final;
- si la resistencia esta dominante, near match u overwhelmed.

## 16. Imagenes deseadas del propio video

No se deben insertar imagenes de otros videos.

Capturas deseadas:

```text
1 - Volume Prediction Intraday:
00:34-00:56  definicion de day volume prediction y float rotation
01:20-01:42  advertencia sobre flow rotation y resistencia
01:42-02:10  formulas premarket volume * 10 y first hour volume * 4

2 - Scenarios of Intraday Volume Prediction:
00:05-00:55  current volume overwhelms resistance
00:56-01:43  current volume close to resistance
01:43-02:13  current volume under resistance
03:21-05:31  tres escenarios contra resistencia 20M
06:16-06:26  volumen como indicador de win-rate

3 - Volume Prediction Pre-Market:
00:00-00:23  buckets under 1M y 1M-1.5M
00:23-00:58  1.5M-2M y morning spike risk
00:58-02:10  over 4M crowded / avoid
02:10-02:46  comfort zone 1M-2M, quick long context and filters
```

## 17. Regla final

Volume Prediction no dice:

```text
entra long o short.
```

Dice:

```text
el volumen esperado del dia favorece, neutraliza o invalida la lectura
estadistica de la estrategia candidata?
```

Si un notebook Dux-style no calcula volumen proyectado, float rotation y ratio
contra resistencia cuando aplica, no esta usando correctamente este bloque de
`Advance Concepts`.
