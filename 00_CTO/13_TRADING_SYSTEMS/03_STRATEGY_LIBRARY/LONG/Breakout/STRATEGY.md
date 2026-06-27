# Breakout - Initial Strategy Definition v0.1

Fecha: 2026-06-23  
Estado: `initial_strategy_definition`  
Scope: `03_STRATEGY_LIBRARY/LONG/Breakout/`

Este documento define inicialmente que entendemos por `Breakout` long en TSIS.

No es un backtest.
No valida edge.
No define todavia una estrategia institucional.

Su funcion es servir como primera definicion tecnica para buscar muestras,
visualizarlas en notebook y despues desgranar los eventos que componen la
estrategia.

## 1. Definicion corta

`Breakout` es una estrategia long basada en la ruptura alcista de un nivel
relevante de resistencia.

No es simplemente que el precio suba.

El evento operativo de interes aparece cuando el mercado supera un nivel que
otros participantes podian estar observando, y esa ruptura produce expansion,
aceptacion o fallo medible.

En una frase:

```text
Breakout =
nivel relevante +
presion contra el nivel +
ruptura alcista +
volumen o expansion +
aceptacion o fallo posterior.
```

## 2. Naturaleza de la estrategia

Breakout no es un evento atomico.

Es una estrategia compuesta.

Puede contener:

```text
contexto
-> nivel relevante
-> compresion o aproximacion al nivel
-> ruptura
-> volumen
-> aceptacion sobre el nivel
-> continuacion o fallo
```

Por eso el primer trabajo no es optimizar entrada, stop o target.

El primer trabajo es:

```text
encontrar muestras historicas
-> ver graficos
-> etiquetar que nivel fue roto
-> separar fenomenos observables
-> escribir eventos v0 en Event Library
```

## 3. Relacion con patrones bullish

Breakout puede aparecer dentro de patrones de continuacion o de reversal.

Material visual de referencia:

- `00_EVENT_LIBRARY/source_assets/patrones/105_continuation.png`
- `00_EVENT_LIBRARY/source_assets/patrones/106_reversal.png`

Estos assets son contexto visual, no detector logic.

Lectura para TSIS:

```text
Un breakout puede ser continuacion bullish cuando rompe despues de consolidar
una expansion previa.

Un breakout puede ser reversal bullish cuando rompe despues de absorber oferta
o invalidar una presion bajista previa.
```

## 4. Arbol conceptual inicial

Propuesta de descomposicion:

```text
Breakout_Strategy
  -> Relevant_Level_Context
  -> Level_Approach_Event
  -> Compression_Or_Pressure_Event
  -> Breakout_Event
  -> Breakout_Acceptance_Event
  -> Breakout_Followthrough_Event
  -> Breakout_Failure_Event
```

Esta lista no es definitiva. Sirve para empezar a mirar la estrategia como un
conjunto de piezas observables.

## 5. Explicacion de cada componente

### 5.1. `Relevant_Level_Context`

Contexto donde existe un nivel que puede actuar como resistencia visible.

Un nivel relevante no es cualquier precio.

Debe tener alguna razon observable:

- high anterior;
- rango previo;
- numero psicologico;
- VWAP;
- trendline;
- high de varias sesiones;
- nivel marcado con volumen;
- zona donde el precio fue rechazado antes.

En TSIS este componente responde:

```text
Que nivel esta intentando romper el mercado?
```

### 5.2. `Level_Approach_Event`

Evento donde el precio se acerca al nivel.

Debe medir:

- distancia al nivel;
- velocidad de aproximacion;
- volumen de aproximacion;
- si hay rechazo previo;
- si hay lows ascendentes;
- si hay compresion del rango.

En TSIS este evento responde:

```text
El precio esta presionando el nivel o solo lo toca de forma aislada?
```

### 5.3. `Compression_Or_Pressure_Event`

Evento donde antes de romper se acumula presion.

Puede verse como:

- rango estrecho bajo resistencia;
- lows ascendentes;
- volumen creciente;
- menor capacidad de los vendedores para tirar el precio;
- candles que cierran cerca de highs;
- varios ataques al mismo nivel.

En TSIS este evento responde:

```text
Hay evidencia de presion acumulada contra la resistencia?
```

### 5.4. `Breakout_Event`

Evento donde el precio rompe el nivel relevante.

Debe medir:

- timestamp de ruptura;
- si el high supera el nivel;
- si el close supera el nivel;
- porcentaje por encima del nivel;
- volumen relativo;
- tipo de nivel;
- si es primera ruptura o rebreak;
- si la ruptura aparece en premarket, regular o afterhours.

En TSIS este evento responde:

```text
El mercado rompio el nivel de forma observable?
```

### 5.5. `Breakout_Acceptance_Event`

Evento posterior a la ruptura que mide si el precio acepta operar por encima
del nivel.

Debe medir:

- si el precio sostiene el nivel;
- si retestea y aguanta;
- cuanto tiempo permanece por encima;
- si VWAP acompana;
- si el volumen posterior sostiene o se seca;
- si la ruptura falla rapidamente.

En TSIS este evento responde:

```text
Despues de romper, el mercado acepto el nuevo precio?
```

### 5.6. `Breakout_Followthrough_Event`

Evento donde la ruptura produce continuacion.

No implica entrada ni target.

Debe medir:

- extension despues de romper;
- max favorable movement;
- velocidad de continuacion;
- continuidad de volumen;
- numero de velas verdes;
- si crea nuevos highs sin crear nuevos lows relevantes.

En TSIS este evento responde:

```text
La ruptura genero desplazamiento posterior?
```

### 5.7. `Breakout_Failure_Event`

Evento donde la ruptura no se sostiene.

Debe medir:

- retorno bajo el nivel;
- tiempo hasta fallo;
- volumen de rechazo;
- perdida de VWAP;
- lower high posterior;
- si el fallo invalida la estructura o solo genera retest.

En TSIS este evento responde:

```text
La ruptura fue aceptada o fue rechazada?
```

## 6. Taxonomia inicial de niveles

El notebook de Breakout debe etiquetar el nivel roto.

Un candidato puede tener varios tags, pero debe tener un nivel primario:

```text
primary_level_type
primary_level_value
breakout_level_tags[]
```

### 6.1. Niveles premarket

`premarket_high`

High del premarket.

`premarket_shelf_high`

Techo de una meseta o rango en premarket.

`premarket_range_high`

High de un rango premarket mas amplio.

`premarket_volume_node_high`

Zona alta asociada a volumen visible en premarket.

### 6.2. Niveles intradia

`high_of_day`

High del dia hasta ese momento.

`opening_range_high_1m`

High del primer minuto regular.

`opening_range_high_5m`

High de los primeros cinco minutos regulares.

`opening_range_high_15m`

High de los primeros quince minutos regulares.

`intraday_consolidation_high`

Techo de una consolidacion intradia.

`bull_flag_high`

Techo de una bandera alcista.

`prior_impulse_high`

High de un impulso previo dentro de la misma sesion.

### 6.3. Niveles de sesion previa

`previous_day_high`

High del dia anterior.

`previous_day_close`

Cierre del dia anterior.

`previous_regular_session_high`

High de la sesion regular anterior.

`previous_afterhours_high`

High del afterhours anterior.

### 6.4. Niveles multi-day

`two_day_high`

High de las dos sesiones previas.

`three_day_high`

High de las tres sesiones previas.

`five_day_high`

High de las cinco sesiones previas.

`ten_day_high`

High de las diez sesiones previas.

`twenty_day_high`

High de las veinte sesiones previas.

`multi_day_range_high`

Techo de un rango de varios dias.

`prior_runner_high`

High relevante de una corrida previa.

### 6.5. Niveles daily/weekly

`daily_resistance`

Resistencia visible en grafico diario.

`weekly_high`

High semanal.

`monthly_high`

High mensual.

`fifty_two_week_high`

Maximo de 52 semanas.

`all_time_high`

Maximo historico disponible en la data.

### 6.6. Niveles psicologicos

`whole_dollar`

Numero entero: 1.00, 2.00, 3.00, etc.

`half_dollar`

Medio dolar: 1.50, 2.50, 3.50, etc.

`major_round_number`

Nivel redondo de mayor importancia visual: 5.00, 10.00, 20.00, etc.

### 6.7. Niveles dinamicos o de control

`VWAP`

Precio medio ponderado por volumen de la sesion.

`anchored_VWAP_from_push`

VWAP anclado desde un push o evento relevante.

`trendline_resistance`

Linea descendente o diagonal que actua como resistencia.

`descending_resistance_line`

Resistencia descendente formada por highs decrecientes.

### 6.8. Niveles especiales

`IPO_high`

High relevante asociado a una IPO reciente.

`post_split_reference_high`

High relevante posterior a split/reverse split.

`offering_price_level`

Precio de offering o financing si esta documentado.

`prior_halt_high`

High marcado antes o despues de un halt.

## 7. Relacion con DAS

DAS y Breakout se solapan, pero no son lo mismo.

En DAS, el nivel principal es:

```text
first_push_high
```

En Breakout, el nivel principal puede venir de muchas fuentes.

Por tanto:

```text
DAS puede contener un breakout del first_push_high.
Breakout puede existir sin DAS.
```

La pregunta de Breakout es:

```text
Que resistencia relevante rompio el precio?
```

La pregunta de DAS es:

```text
El primer push aguanto su primer dip y recupero/rompio su propio high?
```

## 8. Condiciones iniciales para buscar muestras

Estas condiciones son parametros de busqueda, no reglas finales.

```yaml
search_seed:
  session_scope:
    - premarket
    - regular
    - afterhours
  allowed_level_types:
  min_level_age_minutes:
  min_touch_count:
  max_distance_to_level_before_break_pct:
  min_break_close_above_level_pct:
  min_breakout_volume_ratio:
  max_failure_minutes:
  min_price:
  max_market_cap:
  require_vwap_context:
  pattern_context:
    - continuation
    - reversal
    - unclear
```

## 9. Explicacion de parametros

### 9.1. `allowed_level_types`

Lista de tipos de nivel que el buscador puede considerar.

Ejemplo:

```text
premarket_high, high_of_day, previous_day_high, whole_dollar
```

### 9.2. `min_level_age_minutes`

Tiempo minimo que debe existir el nivel antes de ser roto.

Sirve para excluir highs creados y rotos en la misma vela sin estructura.

### 9.3. `min_touch_count`

Numero minimo de aproximaciones o rechazos previos al nivel.

Sirve para diferenciar una resistencia visible de un high aislado.

### 9.4. `max_distance_to_level_before_break_pct`

Distancia maxima permitida antes de la ruptura.

Sirve para detectar presion cerca del nivel, no solo impulsos que llegan desde
muy lejos.

### 9.5. `min_break_close_above_level_pct`

Porcentaje minimo de cierre por encima del nivel.

Sirve para separar ruptura real de toque minimo.

### 9.6. `min_breakout_volume_ratio`

Multiplicador minimo de volumen en la ruptura frente a volumen reciente.

Puede ponerse a cero si en una fase exploratoria no queremos filtrar por
volumen.

### 9.7. `max_failure_minutes`

Ventana para medir si la ruptura falla pronto.

No es filtro de entrada. Es etiqueta de calidad posterior.

### 9.8. `pattern_context`

Clasificacion aproximada del patron antes de romper:

```text
continuation
reversal
unclear
```

## 10. Visualizacion requerida en notebook

El notebook de Breakout debe reutilizar la calidad visual del notebook de Gap
and Go.

Debe incluir:

- chart interactivo con ventana amplia;
- chart estatico de contexto;
- chart estatico del dia del evento hasta las 16:00 NY;
- velas de 1m;
- VWAP;
- volumen en panel inferior;
- velas verdes para candles alcistas;
- velas rojas para candles bajistas;
- volumen verde/rojo segun vela;
- sesiones sombreadas;
- crosshair y hover con OHLCV y hora NY;
- `EXCHANGE:TICKER` visible y copiable;
- nombre completo de compania si existe;
- exportacion PNG de los charts estaticos.

Capas especificas Breakout:

- linea del nivel primario;
- etiqueta del tipo de nivel;
- marcador circular en la vela de ruptura;
- zona de aceptacion o fallo posterior;
- tags secundarios si existen;
- panel o tabla con `breakout_level_tags`.

## 11. Casos que NO son Breakout claro

No son Breakout claros:

- vela aislada que marca high sin nivel previo;
- ruptura por una wick sin cierre ni aceptacion;
- movimiento vertical sin resistencia reconocible;
- ruptura con datos de baja calidad;
- fake print;
- gap directo sobre el nivel sin negociacion util alrededor;
- continuation que no puede asociarse a ningun nivel.

Estos casos pueden guardarse como muestras ambiguas, pero no deben contaminar
las muestras buenas.

## 12. Relacion con eventos v0 en Event Library

Eventos candidatos que podrian derivarse de esta estrategia:

```text
Relevant_Level_Defined_Event
Level_Pressure_Event
Breakout_Event
Breakout_Acceptance_Event
Breakout_Followthrough_Event
Breakout_Failure_Event
Rebreak_Event
```

Estos nombres son provisionales.

Los eventos finales deben escribirse primero en Event Library como:

```text
00_EVENT_LIBRARY/001.md
00_EVENT_LIBRARY/002.md
00_EVENT_LIBRARY/003.md
```

y solo despues, cuando esten claros, se moveran a su familia final.

## 13. Notebook plan

El notebook de Breakout debe permitir:

1. elegir tipos de nivel;
2. elegir filtros;
3. imprimir el comando terminal reproducible;
4. lanzar busqueda o cargar un run existente;
5. refrescar resultados parciales;
6. ordenar candidatos;
7. renderizar charts;
8. exportar PNGs;
9. clasificar muestras como buenas, regulares, malas o peores;
10. guardar metadata del run y parametros usados;
11. dejar claro que los outputs son exploratorios.

Campos esperados iniciales:

```text
ticker
exchange
company_name
date
primary_level_type
primary_level_value
breakout_level_tags
level_age_minutes
touch_count
retest_count
confluence_count
break_ts
break_close_above_level_pct
breakout_volume_ratio
held_after_break
failed_after_break
pattern_type
rebreak_or_first_break
followthrough_5m_pct
failure_window_minutes
quality_bucket_human
```

## 14. Estado actual

`Breakout` queda definido como estrategia inicial de investigacion long.

No queda validado.
No queda institucionalizado.
No queda convertido en evento.

El siguiente paso operativo, despues de DAS, sera construir un notebook
exploratorio adaptado a:

- taxonomia de niveles;
- ruptura;
- aceptacion;
- fallo;
- clasificacion continuation/reversal/unclear.

## 15. Regla final

Breakout no significa "precio subiendo".

Breakout significa que el precio supera un nivel relevante y que esa ruptura
puede describirse, etiquetarse y medirse sin depender todavia de una decision
operativa.
