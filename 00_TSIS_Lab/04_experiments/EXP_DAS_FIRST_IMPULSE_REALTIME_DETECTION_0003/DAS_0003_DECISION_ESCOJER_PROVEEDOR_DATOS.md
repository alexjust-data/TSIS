# DAS 0003 - Alineacion de investigacion y decision de proveedor de datos

**Experimento**: EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003  
**Version del contenido**: v0.2  
**Actualizado**: 2026-07-09  
**Alcance**: deteccion del primer impulso en eventos DAS de microcaps/smallcaps usando datos en tiempo real.  

---

# Decision central

El objetivo inmediato no es comprar desde el primer dia los datos de mercado mas profundos posibles.  

El objetivo inmediato es demostrar si el primer impulso DAS puede detectarse en tiempo real con una pila de datos mas barata y defendible:

```text
trades + BBO/TBBO/MBP-1 + status + features de estado L0/L1
```

Databento Standard parece adecuado para esta primera fase. No resuelve el problema final de microestructura institucional, porque no incluye MBP-10 live, MBO live ni Imbalance live en el paquete live base de Standard mostrado en la tabla de datos live de Databento.

Por tanto:

```text
Fase 1: Databento Standard para discovery live L1/tape y deteccion de eventos.
Fase 2: MBP-10 live solo si la Fase 1 muestra edge y necesita profundidad de libro.
Fase 3: MBO live solo si MBP-10 no basta o si la investigacion de ejecucion/cola/absorcion lo requiere.
```

Este es el camino practico para 0003.

---

# Por que existe este documento

El proyecto estaba inicialmente bloqueado por dos problemas distintos que se estaban mezclando.

## Problema A - Discovery / Scanner

Necesitamos descubrir tickers desconocidos en tiempo real cuando empiezan a despertar. El sistema no puede exigir que nos suscribamos manualmente a simbolos que todavia no conocemos.

DAS confirmo por email que DAS API no es viable para esto:

```text
- sin capacidad de scanner por API
- limite de simbolos simultaneos
- polling de todo el mercado en lotes de 100 simbolos es demasiado lento
- sin profundidad L2 real a traves de la API
- TotalView/ARCA Book no aplican a la API
- Fundamentals y News no estan soportados por la API
- Trade Signal y Scanner son solo del frontend
```

Decision:

```text
DAS API queda descartada como fuente de datos para 0003.
```

## Problema B - Modelado / Inferencia

Una vez detectado un ticker, necesitamos modelar si el primer impulso es un patron DAS valido o solo ruido erratico.

El sistema deseado no es una estrategia simple fija. Es reconocimiento de patrones en tiempo real:

```text
- una accion muerta despierta
- aparece el primer empuje rapido
- el tape confirma participacion
- el precio se expande con velocidad y fuerza
- el spread sigue siendo suficientemente operable
- BBO/MBP-1 confirma presion
- la estructura del primer dip/recovery se vuelve medible
- los casos erraticos malos siguen imprimiendose, pero no se fuerzan puntos/eventos
```

La pregunta clave de investigacion:

```text
Podemos detectar un primer impulso limpio usando L1/tape live antes de pagar por profundidad live?
```

---

# Databento Standard: interpretacion correcta

La pagina de precios y la tabla de datos live deben leerse por separado.

## Pagina de precios

Databento Standard aparece como:

```text
- 179 USD/mes
- live data
- sin license fees
- 16+ anos de historico L0
- 1 ano de historico L1
- 1 mes de historico L2 y L3
- pay as you go para mas historico
```

Esto es cierto, pero no significa que Standard incluya L2/L3 live.

## Tabla de datos live

La captura local revisada para datos live es:

```text
C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\databento\live_data.png
```

Segun esa tabla, Standard live incluye Databento US Equities Mini con:

```text
L0:
- OHLCV-1s/1m/1h/1d
- Definitions
- Statistics
- Status

L1:
- MBP-1
- TBBO
- BBO
- Trades
```

Segun esa misma tabla, Standard live no incluye:

```text
L2:
- MBP-10

L3:
- MBO
- Imbalance
```

Interpretacion correcta:

```text
Standard da L0/L1/tape live.
Standard da historico L2/L3 incluido de forma limitada.
Standard no da MBP-10/MBO/Imbalance live.
```

No hay contradiccion: `1 month L2 and L3 history` significa acceso historico, no entitlement de profundidad live.

---

# Es necesario MBP-10 / MBO live para 0003?

## Respuesta corta

No, no para la primera prueba.

Para la Fase 1 de 0003, MBP-10 live y MBO live no son obligatorios. El primer prototipo defendible puede construirse con:

```text
- trades
- BBO
- TBBO
- MBP-1
- status
- agregacion OHLCV/estado de 1 segundo
```

Esto nos permite construir un detector de primer impulso en tiempo real basado en tape, top-of-book, velocidad, spread y transiciones de estado.

## Que podemos medir con Standard

Desde trades:

```text
- tasa de prints por segundo
- aceleracion del conteo de trades
- volumen por segundo
- dollar volume por segundo
- frecuencia de prints grandes
- presion consecutiva de uptick/downtick
- aggressor side estimado usando BBO/TBBO
- estimacion de signed volume
- estimacion de buy/sell imbalance
- aproximacion de comportamiento tipo sweep a partir de prints y movimiento de BBO
```

Desde BBO/TBBO/MBP-1:

```text
- bid price
- ask price
- bid size
- ask size
- spread
- spread percent
- midprice
- imbalance de top-of-book
- velocidad del midprice
- tasa de actualizacion de quotes
- aproximacion de bid lifting / ask pressure
- aproximacion de replenishment de top-of-book
- operabilidad durante el empuje
```

Desde status/statistics/OHLCV:

```text
- contexto de halted/resumed/market status
- barras de 1 segundo
- VWAP rolling
- high/low rolling
- expansion de rango del dia del evento
- baseline previa de estado quieto
- actividad relativa frente a segundos/minutos previos
```

Esto basta para probar la pregunta principal:

```text
Puede una smallcap muerta/plana reconocerse como despertando antes o durante el primer empuje?
```

## Que no podemos medir con Standard live

Sin MBP-10 live, no podemos ver de forma fiable:

```text
- profundidad a traves de 10 niveles
- agotamiento del ask wall mas alla del top of book
- fortaleza del bid stack mas alla del best bid
- absorcion multinivel
- migracion de profundidad
- pendiente del order book
- precipicios de liquidez
```

Sin MBO live, no podemos ver:

```text
- ciclo de vida individual de cada orden
- add/modify/cancel/execute por order_id
- posicion real en cola
- edad de la orden
- oleadas de cancelacion por orden
- evidencia spoof-like por ciclo de vida
- absorcion fina por orden resting
```

Sin Imbalance live, no podemos ver streams de auction imbalance. Esto es menos critico para el primer impulso continuo, pero puede importar para apertura, reapertura tras halt o eventos especificos de subasta.

---

# Posicion practica de investigacion

## Fase 1 - Prototipo Standard / L1 Tape

Usar Databento Standard para responder:

```text
Pueden las features L1/tape separar primeros impulsos DAS validos de casos erraticos/sin empuje?
```

Esta fase debe construir:

```text
- discovery live de todo el mercado usando ALL_SYMBOLS o equivalente
- promocion de ticker cuando la actividad despierta
- tabla de estado de evento por simbolo segundo a segundo
- etiquetas de evento: dead_state, wakeup, first_push_candidate, first_push_confirmed, first_dip_candidate, invalid_erratic
- PNGs de auditoria visual que imprimen graficos incluso cuando no se detectan puntos/eventos
```

Importante: los tickers malos/erraticos no deben eliminarse del dataset. Deben permanecer en el universo de auditoria, pero el sistema debe poder emitir `NO_VALID_FIRST_IMPULSE` en lugar de forzar puntos verdes/rojos/negros.

## Fase 2 - Upgrade a MBP-10

Solo despues de que la Fase 1 muestre edge, probar si MBP-10 live aporta discriminacion significativa.

MBP-10 debe evaluarse para:

```text
- imbalance real del libro
- agotamiento multinivel del ask
- replenishment del bid despues del primer empuje
- estabilidad de spread/depth
- soporte de profundidad durante el primer dip
- deteccion de liquidity vacuum
```

Este es el primer upgrade pagado real que merece considerarse.

## Fase 3 - Upgrade a MBO

MBO no es el punto de partida. Es una capa avanzada de investigacion.

Usar MBO solo si necesitamos:

```text
- ciclo de vida de ordenes
- estado real de la cola
- intensidad de cancel/add
- evidencia de spoof/withdrawal
- modelado de calidad de ejecucion
- absorcion precisa y dinamica de cola
```

MBO es potente, pero caro y operativamente mas pesado. No debe comprarse antes de que el prototipo L1/tape demuestre que la deteccion del primer impulso DAS tiene señal.

---

# Objetivo de logica de eventos

El objetivo de evento no esta basado en velas. Las velas son solo una capa de visualizacion y auditoria.

El sistema en tiempo real debe inferir estados a partir de event streams:

## Estado 0 - Muerta / Dormida

Un ticker se considera dormido cuando muestra:

```text
- bajo conteo reciente de trades
- bajo dollar volume
- rango de precio comprimido
- bajo movimiento del midprice
- sin signed flow sostenido
- sin expansion significativa frente a su baseline reciente
```

## Estado 1 - Wakeup

Un wakeup empieza cuando el ticker rompe su baseline dormida:

```text
- se expande la tasa de prints
- acelera el dollar volume
- el midprice empieza a moverse
- el spread sigue sin ser imposible
- los trades se agrupan cerca/a traves del ask
- BBO/TBBO sugiere iniciacion compradora
```

## Estado 2 - First Push Candidate

Un candidato a primer empuje necesita persistencia, no un print aislado:

```text
- la velocidad de precio persiste durante varios segundos
- el signed volume permanece positivo
- los maximos siguen expandiendose
- los pullbacks son superficiales durante el burst inicial
- el spread no explota mas alla de limites operables
- la actividad es alta frente a la baseline pre-evento
```

## Estado 3 - First Push Confirmed

El empuje queda confirmado cuando el movimiento es suficientemente grande, rapido y limpio:

```text
- el movimiento porcentual desde la baseline pre-evento es significativo
- el volumen/dollar-volume es anormal
- el tape es sostenido
- la presion de top-of-book apoya el movimiento
- ningun colapso inmediato invalida el evento
```

## Estado 4 - First Dip Candidate

El primer dip no es simplemente la vela roja mas baja. Es el primer retroceso significativo despues del empuje:

```text
- la velocidad se desvanece
- el precio retrocede desde el maximo del primer empuje
- se forma un low antes del intento de recuperacion
- la recuperacion puede ocurrir via vela verde o recuperacion de mecha
- BBO/TBBO/trades muestran si el dip se defiende o se abandona
```

## Estado 5 - Invalid / Erratic

Un ticker puede estar activo pero ser invalido:

```text
- sin transicion limpia de dormido a wakeup
- prints aislados dispersos
- enorme distorsion de spread
- saltos iliquidos de quote
- sin tape sostenido
- spikes de precio sin continuidad
- movimiento demasiado erratico para definir limpiamente primer empuje/dip
```

Los casos invalidos permanecen en el dataset y en las auditorias PNG, pero no se fuerzan puntos/eventos.

---

# Relacion con tablas TSIS existentes

Las tablas TSIS existentes siguen siendo valiosas, pero no bastan para el detector final en tiempo real.

## master_daily_table

Rol:

```text
- contexto diario
- identidad/contexto del ticker
- contexto de prior close
- contexto de gap
- comportamiento historico
- sanity de split/corporate action
- filtrado de universo para investigacion
```

Uso en 0003:

```text
features de contexto y construccion de muestras
```

## master_intraday_bar_table

Rol:

```text
- baseline intradia 1m
- auditoria quote-guarded
- reconstruccion del dia del evento
- validacion de graficos
- revision historica de casos
```

Uso en 0003:

```text
auditoria visual y baseline offline, no inferencia final en tiempo real a nivel tick
```

## Nueva tabla requerida para 0003

0003 necesita una nueva familia de tablas:

```text
provider_microstructure_event_state_table
```

Los campos minimos deben incluir:

```text
symbol
session_date
ts_event
provider
schema
state_label
trade_count_1s
volume_1s
dollar_volume_1s
signed_volume_1s_est
print_rate_1s
spread_bps
bid_px
ask_px
bid_sz
ask_sz
mid_px
mid_return_1s
top_book_imbalance
quote_update_rate_1s
prior_dormant_baseline
wakeup_score
first_push_score
first_dip_score
invalid_reason
```

Si se agrega MBP-10 mas adelante, extender con:

```text
depth_bid_10
depth_ask_10
book_imbalance_10
ask_depletion_rate
bid_replenishment_rate
book_slope
liquidity_cliff_score
```

Si se agrega MBO mas adelante, extender con:

```text
add_count
cancel_count
modify_count
execute_count
order_lifetime_stats
queue_position_estimate
cancel_to_trade_ratio
resting_liquidity_age
```

---

# Decision de proveedor

## Databento Standard

Usar para la Fase 1 si el trial confirma acceso practico a:

```text
- US equities live L1/tape
- ALL_SYMBOLS o suscripcion equivalente de mercado amplio
- trades
- BBO/TBBO/MBP-1
- status
- OHLCV/statistics/definitions de 1s
- timestamps fiables
- ruta de export/replay para investigacion
```

Databento Standard no basta para modelado institucional final de profundidad, pero basta para el primer detector serio.

## Polygon/Massive

Util como complemento, no como sustituto de profundidad de microestructura.

Rol potencial:

```text
- snapshots amplios
- top movers
- reference data
- cobertura de trades/quotes
- amplitud de news/catalyst si el plan lo soporta
- capa de comparacion contra discovery de Databento
```

No resuelve MBO/L3 live.

## TradeStation

No elegir como proveedor core de datos de mercado para 0003 salvo que demuestren explicitamente:

```text
- scanner custom server-side de todo el mercado via API
- entrega programatica de eventos para tickers coincidentes
- cobertura premarket suficiente
- ausencia de limite impracticable de simbolos
- acceso a los datos especificos necesarios para las state tables
```

Sin esa prueba, TradeStation es candidato a broker/plataforma, no la columna vertebral de datos de investigacion.

## DAS API

Descartada para 0003.

---

# Preguntas que hacer a Databento antes de comprar

```text
1. Permite Standard live ALL_SYMBOLS o equivalente para discovery premarket de US equities?
2. Que dataset exacto debe usarse para discovery premarket de microcap/smallcap?
3. Incluye Standard live trades + BBO + TBBO + MBP-1 para el universo relevante?
4. Cuales son los limites de conexion/mensajes/rate para uso live con ALL_SYMBOLS?
5. Puede el stream empezar a las 04:00 ET para premarket de US equities?
6. Que plan/entitlement exacto se requiere para MBP-10 live?
7. Que plan/entitlement exacto se requiere para MBO live?
8. Que plan/entitlement exacto se requiere para Imbalance live?
9. Podemos comprar solo MBP-10/MBO historico para fechas/tickers seleccionados antes de comprar depth live?
10. Podemos exportar DBN/Parquet raw preservando orden de eventos y timestamps?
```

---

# Plan de investigacion actual

## Paso 1 - No comprar Plus todavia

No comprar Plus/Unlimited antes de tener evidencia de la Fase 1.

## Paso 2 - Construir detector L1/Tape

Usar datos de nivel Standard para construir:

```text
- discovery live de mercado amplio
- state table en tiempo real
- scoring de primer impulso
- clasificacion invalid/no-pattern
- generacion de auditorias PNG
```

## Paso 3 - Evaluar contra casos etiquetados por humanos

Comparar contra casos DAS revisados manualmente:

```text
- patron DAS limpio
- actividad erratica
- sin primer empuje real
- muerto y luego explosion
- spike y luego muerte
- primer dip defendido
- primer dip fallido
```

## Paso 4 - Decidir si MBP-10 es necesario

Comprar o probar MBP-10 solo si L1/tape no puede separar suficientes casos.

## Paso 5 - Decidir si MBO es necesario

Comprar o probar MBO solo si MBP-10 sigue siendo insuficiente o si el modelado de ejecucion/cola se convierte en el cuello de botella de investigacion.

---

# Posicion final

Para EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003, el encuadre correcto es:

```text
No intentamos comprar primero infraestructura HFT institucional.
Intentamos probar la senal del primer impulso DAS con la capa seria de observacion en tiempo real mas barata.
```

Databento Standard basta para empezar porque proporciona primitivas live L1/tape.  
Databento Standard no basta para modelado final de profundidad porque no incluye MBP-10/MBO/Imbalance live.  
MBP-10 es el primer upgrade significativo si hace falta.  
MBO es investigacion avanzada, no Fase 1.  
Auction Imbalance no es P0 para deteccion continua del primer impulso.  

La prueba cientifica principal queda clara:

```text
Pueden trades + BBO/TBBO/MBP-1 + status detectar primeros impulsos DAS validos y rechazar casos erraticos/no-pattern?
```

Si si, seguimos barato.  
Si no, sabemos exactamente que comprar despues: MBP-10 live para simbolos candidatos, no necesariamente MBO de universo completo.  

---

# Fuentes

- Email de DAS de Patrick Boyle: sin scanner API, limite de simbolos simultaneos, sin profundidad L2 real por API, fundamentals/news/scanner solo del frontend.
- Precios de Databento, US equities: Standard incluye live data, sin license fees, 16+ anos de historico L0, 1 ano de historico L1, 1 mes de historico L2/L3, pay as you go para mas historico.  
  https://databento.com/pricing#us-equities
- Captura de datos live de Databento usada para interpretar el entitlement live de Standard.  
  C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\databento\live_data.png
- Schema MBP-1 de Databento.  
  https://databento.com/docs/schemas-and-data-formats/mbp-1
- Schema MBP-10 de Databento.  
  https://databento.com/docs/schemas-and-data-formats/mbp-10
- Schema MBO de Databento.  
  https://databento.com/docs/schemas-and-data-formats/mbo
- Schema Imbalance de Databento.  
  https://databento.com/docs/schemas-and-data-formats/imbalance
- Ejemplo de stock screener en tiempo real de Databento.  
  https://databento.com/docs/examples/algo-trading/live-stock-screener
- Docs API de TradeStation.  
  https://api.tradestation.com/docs/
- Overview de acciones de Massive/Polygon.  
  https://massive.com/docs/rest/stocks/overview