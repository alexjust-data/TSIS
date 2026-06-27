# Double Layer Resistance Strategy - Duxinator Source Draft v0.1

Fecha: 2026-06-27
Estado: source_note / strategy draft.
Fuente primaria: Steven Dux - Duxinator - `2 - Double Layer Resistance`.

## 1. Proposito

Este documento define la lectura inicial de TSIS para `Double Layer Resistance`
segun el material Duxinator.

No valida edge.
No crea parametros institucionales.
No autoriza operativa.

Su funcion es convertir la explicacion discrecional de Dux en una estrategia
medible que luego pueda producir:

```text
candidate_table
daily_resistance_map
intraday_resistance_crack_review
statistics_ledger
event_decomposition
```

## 2. Resumen tecnico

`Double Layer Resistance` no significa simplemente "hay resistencia".

Es una estrategia short para tickers crowded donde:

1. el ticker tiene una resistencia historica cercana;
2. el dia actual llega cerca de esa resistencia con volumen elevado;
3. el precio consolida intradia debajo o alrededor de esa zona;
4. esa consolidacion falla y rompe hacia abajo;
5. la resistencia historica y la consolidacion fallida pasan a actuar como dos
   capas de overhead supply.

La idea central es:

```text
resistencia historica cercana
+ consolidacion intradia rota
= doble capa de resistencia sobre el precio
```

Dux lo plantea como una adaptacion a tickers Nasdaq crowded, donde el volumen
intradia puede ser muy alto y la lectura de Level 2 o velas aisladas se vuelve
menos fiable.

## 3. Psicologia y microestructura propuesta

La tesis conductual de la estrategia es:

```text
cuando un ticker crowded falla justo debajo de una resistencia historica,
los compradores tardios y holders atrapados quedan encima del precio.
```

La primera capa es la resistencia historica:

- bagholders de sesiones anteriores;
- vendedores que ya defendieron el nivel;
- shorts que usan esa zona como referencia de riesgo;
- longs previos esperando salir en break-even.

La segunda capa aparece cuando la consolidacion intradia falla:

- compradores del breakout anticipado quedan atrapados;
- longs intradia que defendian la base pierden control;
- shorts nuevos usan el high de la consolidacion como riesgo;
- la zona de consolidacion rota se convierte en resistencia inmediata.

En lenguaje TSIS:

```text
historical_overhead_supply
+ failed_intraday_acceptance
= double_layer_overhead_supply
```

Esto debe tratarse como hipotesis observable, no como verdad garantizada.

## 4. Material fuente

Transcripcion usada:

```text
E:/04_Steven_Dux/Duxinator/Steven Dux - Duxinator - High Odds Penny Trading  [Hacksnation.com]/3 - Patterns And Factors  [Hacksnation.com]/transcripts/2 - Double Layer Resistance.md
```

La transcripcion automatica contiene fragmentos corruptos alrededor de
`03:22 - 03:24`. Esos fragmentos no se usan como autoridad semantica.

Timestamps importantes para capturas futuras:

```text
00:51 - 01:58  concepto de consolidation breakdown + double layer
03:53 - 06:40  ejemplo numerico de resistencia historica + consolidacion intradia
06:54 - 07:24  condicion de evitar tickers crowded sin resistencia
```

Imagenes fuente pendientes:

```text
source_assets/steven_dux/
```

Cuando existan capturas de esta leccion, deben insertarse aqui con lectura
visual precisa, igual que en `SHORT/stevenDux/First_Red_Day/STRATEGY.md`.

## 5. Condiciones minimas del setup

### 5.1. Crowded ticker

Dux usa el concepto de ticker crowded para describir acciones donde el volumen
actual es suficientemente alto como para que la lectura discrecional normal sea
mas dificil.

En la fuente, una referencia inicial es:

```text
premarket_volume >= 4,000,000 shares
```

Esto no es todavia un parametro institucional. Es un umbral fuente que TSIS
debe medir y someter a sensibilidad estadistica.

Campos candidatos:

```text
premarket_volume
premarket_dollar_volume
intraday_volume_to_resistance
relative_volume_vs_20d
crowding_bucket
```

### 5.2. Resistencia historica cercana

Debe existir una resistencia previa identificable.

Puede venir de:

- high historico reciente;
- high multi-day;
- zona previa de gran volumen;
- daily resistance;
- dollar block;
- prior failed breakout area.

La clave es que el precio actual se acerque a esa resistencia, pero no la rompa
de forma limpia antes del fallo.

Campos candidatos:

```text
historical_resistance_price
historical_resistance_date
historical_resistance_volume
resistance_source_type
distance_to_resistance_pct
```

### 5.3. Intraday consolidation near resistance

El ticker empuja hacia la resistencia y empieza a consolidar.

Dux describe un ejemplo:

```text
resistencia historica = 3.00
spike actual = 2.70
consolidacion intradia cerca de 2.70
```

La consolidacion es importante porque crea la segunda capa.

Mientras la consolidacion no rompa, el volumen intradia no debe sumarse como
resistencia confirmada.

Regla fuente:

```text
solo despues de que la consolidacion crackea,
la zona de consolidacion puede tratarse como nueva resistencia.
```

Campos candidatos:

```text
intraday_consolidation_high
intraday_consolidation_low
intraday_consolidation_mid
intraday_consolidation_start_ts
intraday_consolidation_end_ts
intraday_consolidation_volume
consolidation_range_pct
consolidation_distance_to_historical_resistance_pct
```

### 5.4. Consolidation breakdown

La entrada conceptual de Dux aparece despues del breakdown de la consolidacion.

En TSIS, esto debe modelarse como:

```text
consolidation_crack_candidate
```

No basta con que el precio este debajo de resistencia.

Debe haber una zona intradia que el mercado acepto temporalmente y luego perdio.

Campos candidatos:

```text
crack_ts
crack_price
crack_close
crack_below_consolidation_low_pct
crack_volume
crack_vwap_context
```

### 5.5. Doble capa activa

La doble capa queda activa cuando coexisten:

```text
historical_resistance_nearby = true
intraday_consolidation_failed = true
```

Desde ese momento hay dos zonas superiores relevantes:

```text
Layer 1: intraday failed consolidation
Layer 2: historical resistance
```

La calidad mejora cuando ambas capas estan cerca, porque el rango de riesgo es
mas estrecho.

Ejemplo fuente:

```text
intraday consolidation = 3.00
historical resistance = 3.10
risk layer width = 0.10
```

## 6. Formulas candidatas

### 6.1. Distancia a resistencia historica

```text
distance_to_resistance_pct =
  (historical_resistance_price / current_reference_price - 1) * 100
```

### 6.2. Anchura entre capas

```text
layer_width =
  historical_resistance_price - intraday_consolidation_high

layer_width_pct =
  layer_width / intraday_consolidation_high * 100
```

Interpretacion:

```text
layer_width_pct pequeno -> riesgo teorico mas compacto
layer_width_pct grande  -> peor estructura de double layer
```

### 6.3. Volumen de resistencia agregado

Dux propone sumar el volumen de la resistencia historica y el volumen de la
consolidacion intradia solo despues de que la consolidacion falle.

```text
double_layer_resistance_volume =
  historical_resistance_volume + intraday_consolidation_volume
```

Ejemplo fuente:

```text
historical_resistance_volume = 40,000,000
intraday_consolidation_volume = 20,000,000
double_layer_resistance_volume = 60,000,000
```

TSIS debe distinguir:

```text
share_volume_resistance
dollar_volume_resistance
```

porque el volumen en acciones no siempre representa la misma presion economica
cuando el precio cambia mucho.

### 6.4. Calidad de crack

```text
crack_depth_pct =
  (intraday_consolidation_low - crack_close) / intraday_consolidation_low * 100
```

### 6.5. Reward/risk inicial

Esta estrategia pertenece a Strategy Library, por tanto puede medir risk/reward
como hipotesis operativa.

```text
risk_to_upper_layer =
  historical_resistance_price - entry_reference_price

reward_to_prior_support =
  entry_reference_price - nearest_lower_support_price

reward_risk_ratio =
  reward_to_prior_support / risk_to_upper_layer
```

Dux menciona ejemplos conceptuales de:

```text
risk 0.10 para buscar 1.00 -> 1:10
```

TSIS no debe convertir esto en regla institucional hasta medir historicos.

## 7. Estados candidatos

El notebook no debe clasificar todo como `Double Layer Resistance` directamente.

Estados propuestos:

```text
crowded_gap_candidate
historical_resistance_nearby
resistance_approach_candidate
intraday_consolidation_near_resistance
consolidation_crack_candidate
double_layer_resistance_active
no_resistance_crowded_avoid
overwhelmed_resistance_invalid
invalid_double_layer_resistance
```

Definiciones:

| Estado | Significado |
|---|---|
| `crowded_gap_candidate` | Ticker con volumen premarket/intradia elevado. |
| `historical_resistance_nearby` | Existe resistencia previa cerca del precio actual. |
| `resistance_approach_candidate` | El precio se aproxima a la resistencia sin romperla limpiamente. |
| `intraday_consolidation_near_resistance` | Se forma una base o rango intradia cerca de la resistencia. |
| `consolidation_crack_candidate` | La base intradia falla hacia abajo. |
| `double_layer_resistance_active` | Resistencia historica + consolidacion fallida quedan encima del precio. |
| `no_resistance_crowded_avoid` | Hay crowding, pero no hay resistencia clara para definir riesgo. |
| `overwhelmed_resistance_invalid` | El volumen/impulso rompe resistencia y no deja fallo short. |
| `invalid_double_layer_resistance` | Falta alguna pieza estructural critica. |

## 8. Campos minimos para candidate_table

```text
candidate_id
ticker
exchange
company_name
session_date
premarket_volume
premarket_dollar_volume
intraday_volume_to_resistance
relative_volume_vs_20d
crowding_bucket
historical_resistance_price
historical_resistance_date
historical_resistance_volume
historical_resistance_dollar_volume
resistance_source_type
distance_to_resistance_pct
intraday_consolidation_start_ts
intraday_consolidation_end_ts
intraday_consolidation_high
intraday_consolidation_low
intraday_consolidation_mid
intraday_consolidation_volume
intraday_consolidation_dollar_volume
consolidation_range_pct
layer_width
layer_width_pct
crack_ts
crack_price
crack_close
crack_depth_pct
double_layer_resistance_volume
risk_to_upper_layer
nearest_lower_support_price
reward_to_prior_support
reward_risk_ratio
strategy_state
review_bucket
```

## 9. Charts requeridos para el notebook

### 9.1. Daily resistance map

Debe mostrar:

- resistencia historica;
- fecha de la resistencia;
- volumen del dia de resistencia;
- dollar volume si esta disponible;
- distancia del precio actual a esa resistencia;
- si la resistencia fue high aislado o zona multi-day.

### 9.2. Intraday approach and consolidation chart

Debe mostrar:

- premarket crowding;
- aproximacion a resistencia;
- consolidacion intradia;
- VWAP;
- EMA8/Wilder8 segun contrato visual general;
- volumen 1m;
- high/low de la consolidacion.

### 9.3. Crack detail chart

Debe mostrar:

- vela o secuencia de crack;
- linea de consolidation low;
- linea de historical resistance;
- ancho entre capas;
- volumen del crack;
- si el precio reclaimo la consolidacion despues del crack.

### 9.4. Outcome chart

Debe mostrar:

- fade posterior;
- reclaim/failure;
- soporte inferior mas cercano;
- max favorable excursion;
- max adverse excursion;
- si la resistencia historica o intradia fue rota despues.

## 10. No-trade / avoid cases segun fuente

Dux es explicito: si el ticker esta crowded pero no tiene resistencia clara,
no debe tratarse como este setup.

Caso fuente:

```text
first green day
premarket volume >= 4M
sin resistencia clara
```

Lectura:

```text
no hay nivel superior claro para risk-off
```

Estado TSIS:

```text
no_resistance_crowded_avoid
```

## 11. Diferencia con un evento

Este documento es de Strategy Library porque contiene respuesta operativa:

```text
buscar short despues de la ruptura bajista de una consolidacion intradia
cercana a una resistencia historica
```

Los eventos derivados se deben escribir despues en Event Library, por ejemplo:

```text
Crowded_Premarket_Volume_Context_Event
Historical_Resistance_Nearby_Event
Intraday_Consolidation_Near_Resistance_Event
Consolidation_Crack_Event
Double_Layer_Overhead_Supply_Event
No_Resistance_Crowded_Avoid_Context
```

La Event Library no debe contener entradas, stops ni sizing.

## 12. Failure modes

### 12.1. Confundir resistencia simple con double layer

No basta con que exista resistencia.

Debe existir:

```text
resistencia historica cercana
+ consolidacion intradia fallida
```

### 12.2. Sumar volumen intradia antes del crack

Dux no suma el volumen de la consolidacion como resistencia hasta que la
consolidacion falla.

Antes del crack, esa zona puede ser aceptacion.
Despues del crack, esa zona puede convertirse en resistencia.

### 12.3. Shortear un ticker crowded sin resistencia

Si no hay resistencia superior clara, el riesgo no esta definido.

### 12.4. Shortear demasiado pronto

Dux advierte no operar los primeros minutos solo porque el ticker esta crowded.

La estrategia espera que el precio alcance resistencia y forme/falle una
consolidacion.

### 12.5. Capas demasiado separadas

Si la resistencia historica esta muy lejos de la consolidacion intradia, el
riesgo puede ser demasiado ancho.

### 12.6. Resistencia sobrepasada por volumen

Si el volumen intradia rompe y acepta por encima de la resistencia historica,
la tesis de double layer short queda invalidada o degradada.

## 13. Preguntas para busqueda historica

El primer notebook debe responder:

```text
1. cuantas veces un ticker crowded se aproxima a resistencia historica cercana?
2. cuantas veces consolida debajo de esa resistencia?
3. cuantas veces crackea esa consolidacion?
4. cuantas veces el precio reclaima la consolidacion despues del crack?
5. como cambia el resultado segun layer_width_pct?
6. como cambia el resultado segun premarket_volume?
7. como cambia el resultado segun historical_resistance_volume?
8. que pasa si no hay resistencia historica clara?
```

## 14. Regla final

Double Layer Resistance, segun esta fuente, es una estrategia de overhead supply
compuesto.

La pregunta correcta no es:

```text
hay resistencia?
```

La pregunta correcta es:

```text
un ticker crowded fallo una consolidacion intradia justo debajo de una
resistencia historica cercana, creando dos capas medibles de resistencia sobre
el precio?
```
