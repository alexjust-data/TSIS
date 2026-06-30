# DAS Frontside State and AlphaEvolve Research Plan v0.1

Fecha: 2026-06-29

Estado: `draft_research_protocol`

Ruta:

```text
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\DAS_FRONTSIDE_STATE_AND_ALPHAEVOLVE_RESEARCH_PLAN_v0_1.md
```

Este documento no promociona una estrategia institucional.

Su funcion es dejar por escrito el marco de investigacion para estudiar DAS como estrategia long de frontside momentum, usando:

- accion de precio 1m;
- contexto after-hours y premarket;
- componentes de estado de Data Foundation;
- estadistica historica;
- y, mas adelante, generacion de hipotesis con AlphaEvolve bajo validacion estricta.

---

## 1. Proposito

DAS se esta investigando como una estrategia long aplicada al frontside de movimientos extremos en small caps y microcaps.

El objetivo no es optimizar un backtest clasico desde el inicio.

El objetivo es:

1. entender con precision que es frontside;
2. separar frontside de backside;
3. identificar las ventanas temporales donde existe oportunidad real;
4. identificar las ventanas donde el movimiento ya esta degradado;
5. medir variantes buenas, malas y ambiguas;
6. construir features y estados que permitan buscar patrones historicos;
7. preparar un espacio de hipotesis que AlphaEvolve pueda explorar sin fabricar overfitting.

La pregunta central no es:

```text
Que regla exacta gana mas?
```

La pregunta central es:

```text
Que estados del frontside producen oportunidades robustas, y bajo que contexto fallan?
```

---

## 2. Separacion conceptual

DAS pertenece a `Strategy Library`, no a `Event Library`.

Por tanto, puede hablar de:

- entradas;
- stops;
- invalidacion;
- secuencias operables;
- gestion del riesgo;
- salida;
- degradacion de calidad.

Pero no debe redefinir:

- semantica de datasets;
- contratos de Data Foundation;
- definiciones oficiales de eventos;
- outcomes institucionales;
- rewards RL.

Regla:

```text
Event Library describe que ocurre.
Strategy Library estudia que hacer frente a eso.
Data Foundation gobierna la semantica de los datos.
Outcome Research mide que paso despues.
AlphaEvolve propone hipotesis, no decide promocion.
```

---

## 3. DAS como estrategia de frontside

El DAS que estamos investigando no es simplemente:

```text
comprar un dip despues de una subida
```

DAS requiere una secuencia mas concreta:

```text
scanner/momentum aparece
-> primer push expansivo
-> primer retroceso o dip
-> la estructura no se destruye
-> el precio vuelve a romper o reactivar momentum
-> la secuencia sigue viva mientras el frontside no este dañado
```

La idea practica es operar o estudiar los dips que aparecen mientras el movimiento sigue en frontside.

Si el movimiento ya entro en backside, el mismo patron visual deja de ser DAS long de calidad.

---

## 4. Frontside y backside

### 4.1. Frontside

Frontside es el tramo donde el mercado sigue aceptando precios crecientes y los retrocesos no destruyen la estructura alcista.

Sintomas de frontside:

- nuevos highs relevantes despues del primer push;
- dips que retienen parte significativa de la extension;
- reclaim de VWAP o respeto dinamico de VWAP;
- EMA8/Wilder8 en estado bullish o recuperandose;
- volumen suficiente durante reactivaciones;
- shorts presionados por falta de fallo claro;
- estructura de lows no rota de forma decisiva;
- el movimiento todavia tiene posibilidad de nuevos breakouts.

### 4.2. Backside

Backside es el tramo donde el mercado deja de aceptar precios crecientes y los intentos de reactivacion fallan o solo producen rebotes de menor calidad.

Sintomas de backside:

- fallo claro despues del primer push;
- no hay rebreak del high relevante;
- se pierde VWAP y no se recupera;
- EMA8/Wilder8 pasan a estado bearish y no se recomponen;
- se rompen lows estructurales;
- el precio empieza a formar lower highs/lower lows;
- el volumen de venta domina la recuperacion;
- los dips dejan de ser oportunidad long y pasan a ser trampas.

Regla de investigacion:

```text
DAS debe medirse dentro del frontside.
Los mismos dibujos fuera del frontside deben etiquetarse como failure, backside o review.
```

---

## 5. Ventanas temporales obligatorias

Hasta ahora el trabajo se centro demasiado en:

```text
04:00 - 09:30 New York
```

Eso es insuficiente.

La premarket window sigue siendo central, pero no explica todo.

Para DAS hay que estudiar cuatro ventanas:

| Ventana | Uso |
| --- | --- |
| `previous_regular_session` | Contexto del dia anterior: high, low, close, volumen, rango, tendencia previa. |
| `previous_afterhours` | Puede contener breakout, primera aceptacion, fallo, acumulacion o extension previa. |
| `overnight_to_premarket` | Transicion entre after-hours y premarket; posible continuidad o reset. |
| `current_premarket` | Ventana principal de scanner, primer push, dip y rebreak antes del open. |
| `regular_open` | Confirmacion, extension, fallo o cambio a backside tras 09:30. |

Regla:

```text
No estudiar DAS solo como un evento aislado de premarket.
El contexto after-hours puede explicar por que el frontside existe o por que ya esta agotado.
```

---

## 6. Por que after-hours importa

After-hours puede crear informacion estructural antes de premarket:

- ruptura de high previo;
- nuevo high after-hours;
- aceptacion de precio elevado;
- fallo de breakout after-hours;
- volumen anormal previo;
- primeras capas de shorts atrapados;
- niveles que luego gobiernan el premarket;
- extension que hace que el scanner de premarket llegue tarde.

Casos a medir:

| Estado after-hours | Hipotesis |
| --- | --- |
| `ah_breakout_held` | El frontside de premarket puede empezar con estructura previa ya aceptada. |
| `ah_breakout_failed` | El premarket puede estar intentando recuperar una estructura fallida. |
| `ah_high_near_pm_trigger` | El trigger de premarket puede ser realmente un rebreak de after-hours. |
| `ah_volume_expansion` | Puede anticipar atencion antes de la Hot List. |
| `ah_exhaustion` | El premarket puede ser continuacion tardia, no oportunidad temprana. |

---

## 7. Estado operativo actual de Data Foundation

Lectura realizada sobre:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\graphify-out\leaf_slices\data_foundation_outputs_topology_20260629\
E:\TSIS\data\data_foundation_outputs\
C:\TSIS_Data\tests\test_runs\
```

Conclusion principal:

```text
Las tablas materializadas son componentes de estado.
No son todavia un market_state_table final ni un event_state_table final.
```

### 7.1. Tablas materializadas utiles como componentes

| Tabla | Uso posible para DAS |
| --- | --- |
| `instrument_master` | Identidad, exchange, market cap de referencia, LT1B operational context. |
| `market_calendar` | Sesiones, horarios, early close, timezone. |
| `corporate_actions_table` | Splits, dividends, ticker changes, eventos que contaminan comparaciones. |
| `dataset_certification_matrix` | Gates de consumo por familia. |
| `expected_data_calendar` | Ausencias esperadas/no esperadas de datos. |
| `master_daily_table` | Contexto daily, previous close, daily ranges, gap, rvol daily. |
| `halts_table` | Halts como eventos/regime interrupts. |
| `event_windows_table` | Ventanas de eventos halt-derived. |
| `fundamentals_asof_table` | Contexto as-of, no como causalidad directa. |
| `news_context_table` | Catalyst context con published_utc y attribution state. |
| `short_context_table` | Short interest/short volume source-scoped context. |
| `regime_context_table` | Regime proxy session-level, no intraday causal truth. |

### 7.2. Tablas existentes pero no listas como base primaria DAS

| Tabla | Restriccion |
| --- | --- |
| `master_intraday_bar_table` | Existe como scoped pilot: 8 tickers, no full-universe. No sustituye `E:\TSIS\data\ohlcv_1m` para busqueda DAS global. |
| `microstructure_features_table_v0_1` | Seed smoke: 1 row. No usar como fuente primaria. |
| `microstructure_features_table_v0_2_candidate` | Candidate controlled: 50 rows. No usar como institucional para DAS full-universe. |
| `outcomes_table` | Puede servir como label/outcome research. Prohibido usarlo como feature pre-event. |

### 7.3. Tablas no materializadas

Estas tablas tienen contrato/esqueleto, pero no existen como outputs finales:

| Tabla | Estado |
| --- | --- |
| `market_state_table` | No materializada final. Hay skeleton tests y fixture loop. |
| `event_state_table` | No materializada final. Hay skeleton tests y fixture loop. |
| `short_sale_constraints_table` | No materializada. Bloqueada por borrow/locate/SSR/as-of constraints. |

Regla:

```text
DAS puede disenar features que un futuro market_state/event_state deberia contener.
Pero no puede afirmar que esas tablas ya existen como source of truth final.
```

---

## 8. Fuente operativa 1m actual

Para buscar DAS full-universe hoy, la base operativa sigue siendo:

```text
E:\TSIS\data\ohlcv_1m
```

Motivo:

```text
master_intraday_bar_table no es full-universe.
ohlcv_1m_split_normalized no debe tratarse como full-universe si solo existe en scope piloto.
```

Regla de consumo:

- usar `ohlcv_1m` para scanner y geometria intradia full-universe actual;
- marcar riesgo de splits/corporate actions cuando haya comparaciones cross-session;
- cruzar con `corporate_actions_table` para flags;
- migrar a una version intraday gobernada full-scope cuando exista.

---

## 9. Maquina de estados DAS/frontside

Propuesta de estados para estudio:

| Estado | Descripcion |
| --- | --- |
| `D0_dormant` | Ticker sin actividad relevante. |
| `F1_scanner_eligible` | Cumple universo operativo: market cap, price, volume, ranking/momentum. |
| `F2_momentum_trigger` | Aparece momentum antes o durante el scanner; puede ser anterior al trigger TradeStation. |
| `F3_first_push_expansion` | Primer push relevante desde apertura/arranque de sesion. |
| `F4_first_dip_retention` | Primer retroceso no destruye la estructura. |
| `F5_rebreak_confirmation` | El precio rompe high relevante del primer push o estructura local. |
| `F6_active_frontside` | La secuencia queda activa para estudiar DAS posteriores. |
| `F7_mature_frontside` | El movimiento sigue vivo, pero con riesgo creciente y peor calidad relativa. |
| `B1_frontside_damage` | Primer dano serio: VWAP/estructura/lows/EMA-Wilder dañados. |
| `B2_backside_confirmed` | La estrategia DAS long deja de tener contexto primario. |

No todos los estados son entradas.

Son estados de investigacion para medir:

- donde aparece la oportunidad;
- cuando se vuelve tarde;
- cuando se degrada;
- cuando se invalida.

---

## 10. Trigger de scanner vs trigger de momentum

Hay que separar dos cosas:

| Concepto | Definicion |
| --- | --- |
| `scanner_trigger` | Momento en que el ticker cumple el screener tipo TradeStation Hot List. |
| `momentum_trigger` | Momento temprano donde la accion ya muestra momentum estructural medible. |

El screener humano actual:

```text
Universe: Equities
Exchange: ALL
Activity: % Gainers - 1 Day
Results: 25

Filters:
Market Cap M < 100
Volume Today > 500000
Last <= 20
Last > 0.5
```

Replica conceptual en Python:

```python
df["pct_chg_1d"] = (df["last"] - df["prev_close"]) / df["prev_close"] * 100
screen = (
    df[
        (df["market_cap"] < 100_000_000) &
        (df["volume_today"] > 500_000) &
        (df["last"] <= 20) &
        (df["last"] > 0.5)
    ]
    .sort_values("pct_chg_1d", ascending=False)
    .head(25)
)
```

Problema detectado:

```text
scanner_trigger puede llegar tarde.
momentum_trigger puede existir mucho antes.
```

Por eso el notebook debe medir ambos.

---

## 11. Mediciones obligatorias por candidato

Cada candidato DAS debe medir, como minimo:

### 11.1. Referencias temporales

- `previous_close_ts`;
- `previous_regular_high_ts`;
- `previous_afterhours_start_ts`;
- `previous_afterhours_high_ts`;
- `premarket_start_ts`;
- `scanner_trigger_ts`;
- `momentum_trigger_ts`;
- `first_push_start_ts`;
- `first_push_high_ts`;
- `first_dip_low_ts`;
- `first_rebreak_ts`;
- `frontside_high_ts`;
- `backside_damage_ts`;

### 11.2. Porcentajes clave

- `pm_open_to_momentum_trigger_pct`;
- `pm_open_to_scanner_trigger_pct`;
- `pm_open_to_first_push_high_pct`;
- `pm_open_to_frontside_high_pct`;
- `scanner_to_frontside_high_pct`;
- `momentum_trigger_to_frontside_high_pct`;
- `first_dip_depth_pct`;
- `first_push_retention_pct`;
- `frontside_drawdown_after_entry_candidate_pct`;

### 11.3. Volumen

- `volume_at_scanner_trigger`;
- `volume_at_momentum_trigger`;
- `volume_to_first_push_high`;
- `volume_to_first_rebreak`;
- `session_volume_to_time`;
- `relative_volume_proxy`;
- `volume_expansion_vs_prior_window`;

### 11.4. Estructura

- `first_push_duration_minutes`;
- `first_push_candle_count`;
- `higher_high_count_after_rebreak`;
- `higher_low_count_after_rebreak`;
- `breakout_count_frontside`;
- `failed_breakout_count_frontside`;
- `lowest_low_after_first_push`;
- `vwap_state_at_dip`;
- `ema8_wilder8_state_at_dip`;
- `ema8_wilder8_state_at_rebreak`;

### 11.5. Contexto after-hours

- `ah_volume`;
- `ah_high`;
- `ah_low`;
- `ah_close_location`;
- `ah_breakout_held`;
- `ah_breakout_failed`;
- `ah_high_reclaimed_in_pm`;
- `ah_extension_already_exhausted`;

---

## 12. Money windows y money fail windows

### 12.1. Money window candidate

Ventana donde DAS podria tener oportunidad robusta.

Sintomas:

- trigger temprano;
- push inicial claro;
- dip controlado;
- estructura no destruida;
- VWAP respetado o recuperado;
- EMA8/Wilder8 bullish o reclaim rapido;
- rebreak claro;
- continuidad posterior medible;
- suficiente volumen y rango para ejecucion realista.

### 12.2. Money fail window

Ventana donde el chart puede parecer operable, pero estadisticamente debe tratarse como peligro o review.

Sintomas:

- scanner muy tarde;
- primer push ya hizo la mayor parte del movimiento;
- dip destruye estructura;
- no hay rebreak del high relevante;
- hay solo una vela o dos de extension y luego fade;
- VWAP se pierde y no se recupera;
- EMA8/Wilder8 pasan bearish;
- after-hours ya mostro agotamiento;
- el movimiento entra rapido en backside.

---

## 13. Patrones iniciales observados en DAS

Estos patrones salen de la lectura humana de imagenes y del run DAS:

```text
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\DAS_VISUAL_CASEBOOK\img\archive
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\DAS_VISUAL_CASEBOOK\img\human_good_cases
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\DAS_VISUAL_CASEBOOK\img\human_bad_cases
```

### 13.1. A_plus_Continuation_DAS

Movimiento ideal:

- primer push potente;
- dip que respeta estructura;
- rebreak;
- nuevos breakouts;
- frontside largo;
- no hay colapso inmediato.

Hipotesis:

```text
La calidad no viene solo del dip.
Viene de la combinacion: trigger temprano + estructura retenida + rebreak + continuidad.
```

### 13.2. Pattern_N_One_Shot

Movimiento vertical de 1-3 velas que puede dar oportunidad rapida, pero no sostiene estructura.

Sintomas:

- push muy vertical;
- poca aceptacion posterior;
- no hay secuencia limpia de nuevos breakouts;
- el precio cae suavemente o se degrada tras la extension.

Uso:

```text
Puede ser una variante de scalp, pero no debe contaminar DAS frontside robusto.
```

### 13.3. Late_Scanner

El scanner detecta el ticker cuando gran parte del movimiento ya ocurrio.

Medicion critica:

```text
scanner_delay_pct = pm_open_to_scanner_trigger_pct - pm_open_to_momentum_trigger_pct
```

Si el scanner llega tarde, la estrategia debe medir si aun queda frontside real o solo persecucion tardia.

### 13.4. Deep_Dip_Reclaim

El primer dip parece profundo, pero puede seguir siendo util si:

- VWAP se recupera;
- EMA8/Wilder8 vuelven bullish;
- el precio rompe high relevante;
- no hay breakdown estructural confirmado.

### 13.5. Reject_DAS

Casos que el codigo debe aprender a excluir o marcar como malos:

- primer push destruido;
- no hay rebreak real;
- el high de la ultima vela roja del primer push no se supera;
- el precio cae por debajo de VWAP sin reclaim;
- el movimiento venia ya extendido de antes;
- no existe continuation, solo fade.

---

## 14. Componentes de estado para AlphaEvolve

AlphaEvolve no debe limitarse a precio.

Debe poder proponer hipotesis sobre:

- accion de precio;
- estructura temporal;
- contexto daily;
- after-hours;
- premarket;
- volumen;
- VWAP/EMA/Wilder;
- catalyst;
- short context;
- regime context;
- corporate actions;
- halts;
- calidad de datos.

Pero cada componente debe respetar su disponibilidad real.

### 14.1. Componentes permitidos hoy para research

| Componente | Fuente |
| --- | --- |
| Identidad, exchange, LT1B | `instrument_master` |
| Sesiones y timezone | `market_calendar` |
| Previous close, daily gap, daily rvol | `master_daily_table` |
| Splits/dividends/ticker changes | `corporate_actions_table` |
| News/catalyst context | `news_context_table`, con `published_utc` |
| Short context source-scoped | `short_context_table` |
| Regime proxy | `regime_context_table` |
| Halt context | `halts_table` |
| Raw 1m full-universe scanner | `E:\TSIS\data\ohlcv_1m` con flags |

### 14.2. Componentes no permitidos como verdad final hoy

| Componente | Motivo |
| --- | --- |
| `market_state_table` | No materializada final. |
| `event_state_table` | No materializada final. |
| `short_sale_constraints_table` | No materializada. |
| `microstructure_features_table` | Seed/candidate, no full-universe. |
| `master_intraday_bar_table` | Scoped pilot, no full-universe. |
| `outcomes_table` como feature | Leakage. Solo labels/outcome research. |

---

## 15. Gramática de hipótesis para AlphaEvolve

AlphaEvolve debe proponer hipotesis estructurales, no solo parametros.

Formato conceptual:

```yaml
hypothesis:
  state_window:
    previous_regular:
    previous_afterhours:
    current_premarket:
    regular_open:

  eligibility:
    market_cap:
    price:
    session_volume_to_time:
    pct_chg_1d_rank:
    catalyst_context:
    short_context:

  frontside_definition:
    momentum_trigger:
    first_push:
    first_dip:
    rebreak:
    active_frontside:
    backside_damage:

  das_candidate:
    entry_zone_family:
    invalidation_family:
    continuation_expectation:
    failure_mode:

  validation:
    train_period:
    validation_period:
    holdout_period:
    regime_split:
    data_quality_filters:
    leakage_checks:
```

AlphaEvolve puede variar:

- definicion de momentum trigger;
- definicion de primer push;
- profundidad aceptable del dip;
- retencion minima del primer push;
- condicion de rebreak;
- uso de VWAP/EMA/Wilder;
- uso de after-hours;
- degradacion por tiempo;
- degradacion por numero de breakouts;
- exclusion de Pattern_N;
- exclusion de late scanner.

AlphaEvolve no puede variar:

- contratos de datos despues de ver resultados;
- outputs de outcome como features;
- periodos de validacion para elegir a posteriori;
- source of truth;
- reglas de as-of;
- restricciones de leakage.

---

## 16. Fitness como credibilidad, no como maximo local

El objetivo de AlphaEvolve no debe ser:

```text
maximizar PnL historico
```

Debe ser:

```text
maximizar probabilidad de que la hipotesis sea robusta y no sobreajustada
```

Fitness recomendado:

```text
credibility_fitness =
    expectancy
  + stability
  + frontside_state_precision
  + neighbour_parameter_robustness
  + walk_forward_survival
  + regime_robustness
  + data_quality_survival
  + execution_realism_penalty
  - complexity_penalty
  - leakage_risk_penalty
  - late_scanner_penalty
  - pattern_n_false_positive_penalty
```

Regla:

```text
AlphaEvolve propone.
Validation Engine acepta, rechaza o manda a review.
```

---

## 17. Validacion minima futura

Ninguna hipotesis DAS debe tratarse como fuerte sin:

- split temporal train/validation/holdout;
- walk-forward;
- purged CV cuando aplique;
- embargo temporal si hay overlap;
- estabilidad por año;
- estabilidad por rango de precio;
- estabilidad por market cap;
- estabilidad por hora de trigger;
- estabilidad por regimen;
- sensibilidad a volumen;
- sensibilidad a scanner delay;
- degradacion por slippage/spread;
- revision de falsos positivos visuales;
- separacion clara entre labels y features.

---

## 18. Reglas anti-leakage

Prohibido usar como feature:

- high futuro del movimiento;
- frontside high si ocurre despues del punto de decision;
- outcome labels;
- datos publicados despues del timestamp de decision;
- corporate actions no conocidas en ese momento;
- fundamentals sin filtro as-of;
- news sin `published_utc` anterior al evento;
- short data sin lag/availability semantics;
- cualquier tabla marcada como no materializada final.

---

## 19. Implicacion para el notebook DAS

El notebook DAS debe evolucionar hacia dos capas:

### 19.1. Discovery/visual layer

Sirve para:

- detectar candidatos;
- exportar imagenes;
- comparar buenos/malos;
- revisar visualmente frontside/backside;
- marcar variantes humanas.

### 19.2. Statistics/state layer

Debe producir tablas de investigacion con:

- una fila por candidato;
- una fila por trigger;
- una fila por posible DAS dentro del frontside;
- features pre-event;
- state labels;
- outcome labels separados;
- metadata del run;
- version de codigo;
- version de datasets;
- flags de calidad.

Regla:

```text
Las imagenes ayudan a definir.
Las tablas permiten medir.
```

---

## 20. Relacion con daily scanner general

El `daily_scanner_candidates_table` debe construirse antes de usar DAS como
estadistica institucional de universo.

Motivo:

```text
Sin scanner general no sabemos que tickers estaban realmente in-play cada dia.
Sin ese denominador, un run DAS solo contiene lo que el detector DAS ya supo encontrar.
```

Por tanto, la separacion correcta es:

```text
daily_scanner_candidates_table
= capa comun de tickers in-play

das_candidate_state_table_experimental
= lectura DAS/frontside sobre esos tickers
```

Tambien puede construirse temporalmente sobre el universo encontrado por la
busqueda DAS 2025/2026 existente, siempre que quede marcado como estadistica
condicionada al detector actual.

El scanner general responde:

```text
Que tickers estaban vivos, visibles o in-play en cada fecha/as-of?
```

DAS responde:

```text
Dentro de esos tickers in-play, cuales desarrollaron frontside,
primer push, dip, rebreak, continuation, failure o backside?
```

### 20.1. Por que no crear primero un scanner especifico DAS

Un scanner especifico DAS puede servir como detector exploratorio, pero no debe
ser el denominador estadistico principal.

Si se usa como denominador, se pierden:

- tickers in-play que no hicieron DAS;
- tickers que hicieron DAS pero el scanner llego tarde;
- tickers que parecian DAS y fallaron;
- tickers que fueron `A_plus`;
- tickers que nunca debimos mirar;
- falsos negativos del detector actual.

Regla:

```text
Primero scanner general para saber donde mirar.
Despues DAS state table para saber que paso dentro de lo que miramos.
```

### 20.2. Que puede hacerse antes de que exista el scanner general

No hace falta esperar al scanner general para avanzar.

Con los runs DAS actuales se puede trabajar en:

- definicion de estados DAS/frontside;
- clasificacion visual de buenos, malos, regulares y pattern_n;
- metricas internas por candidato detectado;
- refactor del detector para mejorar precision;
- diseño de features;
- definicion de failure modes;
- especificacion de `das_candidate_state_table_experimental`;
- lectura de imagenes A+/D/malas para crear reglas candidatas.

Pero esas estadisticas deben marcarse como:

```text
conditional_on_current_das_detector
```

No como:

```text
population_statistics
```

### 20.3. Que debe esperar al scanner general

Debe esperar al scanner general cualquier afirmacion sobre:

- frecuencia real de DAS en el universo;
- probabilidad de que un ticker in-play genere DAS;
- ranking comparativo entre DAS y otros patrones;
- falsos negativos del detector DAS;
- valor del scanner como filtro operativo;
- distribucion real de oportunidad por dia;
- expectativa institucional del setup.

Regla:

```text
El run DAS actual sirve para aprender la forma y depurar el detector.
El scanner general sirve para medir la poblacion completa.
```

---

## 21. Tabla experimental DAS y frontera con state tables

El siguiente artefacto operativo para DAS no debe ser `market_state_table` ni
`event_state_table`.

Debe ser una tabla experimental local:

```text
das_candidate_state_table_experimental
```

Su papel:

```text
leer DAS/frontside sobre candidatos del scanner general,
o sobre la busqueda DAS 2025/2026 mientras el scanner general no exista.
```

La relacion correcta es:

```text
daily_scanner_candidates_table
-> das_candidate_state_table_experimental
-> future market_state_table / event_state_table
```

Donde:

```text
daily_scanner_candidates_table
= denominador general / donde mirar

das_candidate_state_table_experimental
= lectura DAS/frontside sobre esos candidatos o sobre el run DAS actual

market_state_table / event_state_table
= futura capa institucional gobernada
```

### 21.1. Diferencia semantica

`daily_scanner_candidates_table` dice:

```text
este ticker estaba in-play en este momento/as-of
```

`das_candidate_state_table_experimental` dice:

```text
dentro de este ticker in-play, que estados DAS/frontside aparecieron?
```

`market_state_table` futuro dira:

```text
que sabia TSIS del mercado/ticker en ese timestamp, de forma gobernada?
```

`event_state_table` futuro dira:

```text
que evento o transicion de estado ocurrio, con que contexto, calidad y lineage?
```

Regla:

```text
DAS puede prototipar estados.
Data Foundation debe gobernar estados institucionales.
```

### 21.2. Namespaces de la tabla experimental

`das_candidate_state_table_experimental` debe usar namespaces explicitos:

```text
scanner__
daily__
afterhours__
premarket__
frontside__
das__
vwap__
ema_wilder__
quality__
human_label__
outcome__
```

Ejemplos:

```text
scanner__trigger_ts
scanner__gap_pct_at_trigger
scanner__volume_at_trigger

afterhours__high
afterhours__breakout_held
afterhours__exhaustion_flag

frontside__first_push_start_ts
frontside__first_push_high_pct
frontside__first_dip_depth_pct
frontside__rebreak_ts
frontside__backside_damage_ts

das__state
das__variant
das__quality_label
```

### 21.3. Features, labels y outcomes

La tabla debe separar de forma explicita:

- columnas observables antes o en el timestamp de decision;
- columnas de estado calculadas sin mirar futuro;
- etiquetas humanas;
- outcomes posteriores;
- columnas prohibidas para ML/RL por leakage.

Regla critica:

```text
outcome__ y human_label__ no son features.
```

Sirven para:

- analisis;
- scoring;
- auditoria visual;
- entrenamiento supervisado posterior si el contrato de features/labels lo
  permite.

No sirven como input directo de decision, ML, RL o AlphaEvolve fitness sin
separacion temporal estricta.

### 21.4. Estadisticas permitidas antes del scanner general

Mientras no exista el scanner general completo, las estadisticas DAS solo son:

```text
estadisticas condicionadas al universo DAS buscado
```

No son todavia:

```text
estadisticas sobre todo el mercado in-play
```

Esto debe aparecer en cualquier summary, chart export, notebook o tabla
experimental que derive de los runs DAS actuales.

---

## 22. Siguiente trabajo recomendado

1. Crear una tabla `das_candidate_state_table_experimental` desde el ultimo run.
2. Enriquecer cada candidato con contexto daily, after-hours y premarket.
3. Separar `momentum_trigger` de `scanner_trigger`.
4. Calcular `frontside_state` y `backside_damage_reason`.
5. Crear labels humanos iniciales:
   - `A_plus`;
   - `good`;
   - `regular`;
   - `bad`;
   - `pattern_n`;
   - `late_scanner`;
   - `reject_no_rebreak`;
   - `backside`;
6. Medir estadisticas por grupo.
7. Crear una primera lista de hipotesis candidatas para AlphaEvolve.
8. Solo despues, refactorizar el scanner DAS v2.

---

## 23. No-goals

Este documento no:

- valida DAS como edge;
- define estrategia institucional;
- define execution model;
- crea event_state_table;
- crea market_state_table;
- promociona AlphaEvolve;
- sustituye Data Foundation;
- autoriza usar outcomes como features;
- autoriza usar microstructure seed/candidate como core.

---

## 24. Regla final

DAS no debe investigarse como un dibujo.

DAS debe investigarse como una secuencia de estados:

```text
atencion -> scanner/momentum -> primer push -> dip retenido -> rebreak -> frontside activo -> degradacion o continuacion
```

Y esa secuencia debe medirse con:

- datos;
- contexto;
- estados;
- validacion;
- y separacion estricta entre hipotesis, feature, label, decision y outcome.
