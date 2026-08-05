Sí, **mantengo la tesis principal de la respuesta anterior**, pero la ajustaría de manera importante a los datos que realmente tiene TSIS:

> Para detectar el nacimiento del movimiento no necesitamos inventar velas de menos de un minuto como fuente primaria.
> Necesitamos un **scanner event-driven sobre trades y quotes**, que produzca eventos y estados. Las velas de 1 s, 5 s, 15 s o 30 s pueden derivarse después como vistas auxiliares.

El movimiento seguiría siendo:

[
\text{DORMANT}
\rightarrow
\text{ACTIVATION}
\rightarrow
\text{IMPULSE}
\rightarrow
\text{FIRST PULLBACK}
\rightarrow
\text{CONTINUATION}
\rightarrow
\text{FRONTSIDE TERMINATED}
]

El Donchian, PMH, HOD, VWAP reclaim o ruptura de bandera continuarían siendo **triggers internos**, no la estrategia completa.

---

# 1. Qué cambia al conocer vuestra data

TSIS dispone físicamente de:

```text
OHLCV diario
OHLCV 1m
trades tick-by-tick
quotes
news
halts
reference
fundamentals
short-side context
corporate actions y soporte de identidad
```

Además, el árbol físico `ohlcv_1m_quote_guarded_full_universe_v0_1` ya existe para 2005–2026. No está promovido globalmente y conserva restricciones institucionales, pero 2024, 2025 y 2026 figuran con materialización completa y sin *failed tickers*. Por tanto, es una base válida para investigación acotada si declaramos que sigue siendo `candidate_not_official`. 

La materialización 1m está precisamente diseñada para alimentar scanners, experimentos DAS, *state builders* y ventanas de eventos, sin obligar a cada consumidor a reconstruir el overlay `quote_guarded`. Pero el propio documento distingue correctamente:

```text
1m quote-guarded
= dato intradía observable

state table
= fotografía legal del mundo observable en t
```



Por tanto, propondría este reparto:

| Fuente             | Uso correcto                                                        |
| ------------------ | ------------------------------------------------------------------- |
| 1m quote-guarded   | Descubrimiento histórico, candidatos, contexto, labels preliminares |
| Trades ticks       | Velocidad, volumen, intensidad y precio del primer movimiento       |
| Quotes             | Midprice, spread, NBBO, presión y calidad ejecutable                |
| News               | Canal causal de activación                                          |
| Halts/LULD         | Disponibilidad real y estado regulatorio                            |
| Reference          | Universo, precio, market cap, identidad                             |
| Daily              | Prior close, gap, contexto histórico                                |
| Fundamentals/short | Condicionantes del episodio, no detector de milisegundos            |

La consecuencia es importante:

> **No os faltan necesariamente las velas inferiores a un minuto. Os falta convertir trades y quotes en un replay event-driven gobernado.**

Podemos generar velas de 1 s o 5 s para gráficos, comparaciones y un primer backtest convencional. Pero el motor científicamente correcto debería consumir los eventos originales.

---

# 2. Lo que revela el ZIP sobre vuestro scanner actual

He revisado el manifiesto incluido en el ZIP.

Hay una primera minucia: el run no utilizó un volumen mínimo de **500 millones**, sino:

```text
--min-session-volume 500000.0
```

Es decir, **500.000 acciones acumuladas desde el comienzo del premarket**. También usó:

```text
market cap < $100M
price entre $0.50 y $20
session_scope = premarket
push_label = 20%
dip_label = 3%
price_view = raw
años = 2024, 2025, 2026
```

## El filtro de 500.000 acciones funciona, pero llega tarde

Sobre los 679 casos exportados:

| Precio recorrido desde apertura PM cuando aparece en scanner |   Resultado |
| ------------------------------------------------------------ | ----------: |
| Mediana                                                      | **+17,97%** |
| Percentil 75                                                 | **+34,06%** |
| Percentil 90                                                 | **+60,24%** |
| Máximo                                                       | **+337,5%** |
| Detectados antes de +10%                                     |   **32,1%** |
| Detectados antes de +20%                                     |   **54,2%** |

Esto confirma tu intuición:

> El volumen acumulado de 500.000 acciones sirve para declarar que una acción está **in play**, pero no es un buen detector del instante en que despierta.

Aun así, después de aparecer en el scanner, la subida restante mediana hasta el máximo fue aproximadamente **+30%**. En torno al 69% de los casos todavía recorrieron más de un 20% desde el punto de aparición.

Por tanto, el scanner actual no es inútil. Simplemente tiene otro rol:

```text
500k accumulated volume scanner
=
established in-play / continuation scanner
```

No:

```text
first-seconds activation scanner
```

## El ZIP tiene además un sesgo importante

Aunque comentas que contiene buenos y fallidos, el manifiesto formal de los 679 eventos los clasifica a todos como:

```text
das_state = rebreak_confirmed
```

Y todos han sido seleccionados después de haber alcanzado al menos un push del 20% y un dip del 3%.

Es decir, este ZIP es muy útil para estudiar:

* Cómo son los movimientos que sí llegaron a activarse.
* Qué tipos de pullback y rebreak aparecen.
* Cómo varía su recorrido.
* Dónde llegaba tarde el scanner.

Pero no sirve todavía para aprender a separar activaciones reales de falsas porque no contiene formalmente:

```text
scanner_only
activity_burst_failed
push_detected_without_continuation
failed_before_rebreak
dead-stock false alarm
one-print anomaly
```

Algunas curvas pueden acabar mal después del rebreak, pero no hay una etiqueta formal equilibrada de “éxito frente a fracaso”.

Eso debe corregirse antes de entrenar cualquier clasificador.

---

# 3. No reemplazaría vuestro scanner: añadiría otro delante

La arquitectura debería contener dos scanners diferentes.

```text
┌───────────────────────────────────────┐
│ SCANNER 0 — STATIC UNIVERSE           │
│ MCap < $100M · $0.50–$20 · elegible   │
└──────────────────┬────────────────────┘
                   ↓
┌───────────────────────────────────────┐
│ SCANNER 1 — WAKE-UP                   │
│ Detecta el cambio en segundos         │
│ trades · dollar volume · precio       │
└──────────────────┬────────────────────┘
                   ↓
┌───────────────────────────────────────┐
│ ACTIVE SYMBOL SET                     │
│ Observación microestructural intensa  │
└──────────────────┬────────────────────┘
                   ↓
┌───────────────────────────────────────┐
│ SCANNER 2 — ESTABLISHED IN-PLAY       │
│ 500k volume · gap · VWAP · PMH · HOD  │
└──────────────────┬────────────────────┘
                   ↓
┌───────────────────────────────────────┐
│ STRATEGY STATE MACHINE                │
│ impulse · pullback · continuation     │
└───────────────────────────────────────┘
```

El scanner de 500.000 acciones permanecería. Su trabajo sería confirmar:

* Que existe participación real.
* Que hay suficiente liquidez o capacidad.
* Que la acción sigue siendo relevante.
* Que puede aparecer una segunda oportunidad de continuación.

El nuevo scanner `WAKE-UP` se ocuparía del instante inicial.

---

# 4. Qué filtro usaría para detectar el primer movimiento

No usaría un único umbral de volumen acumulado.

Utilizaría cuatro condiciones:

[
\text{elegibilidad}
\times
\text{shock relativo}
\times
\text{actividad absoluta}
\times
\text{respuesta del precio}
]

## 4.1 Universo estático

Se calcula antes de abrir la sesión:

```text
market_cap_PIT < $100M
0.50 <= price <= 20
instrumento elegible
ticker activo
sin problemas graves de identidad
```

La market cap debe ser *point-in-time*. No deberíamos usar la capitalización conocida años después.

Este filtro no se recalcula con cada trade.

## 4.2 Shock relativo de actividad

Una acción muerta puede negociar 30.000 acciones en cinco segundos y eso ser extraordinario. Otra acción puede negociar lo mismo continuamente y no significar nada.

Por eso calcularía:

```text
trade_rate_1s / expected_trade_rate
trade_rate_5s / expected_trade_rate
dollar_volume_rate_5s / expected_dollar_volume_rate
quote_update_rate_5s / expected_quote_update_rate
```

El denominador debe depender de:

```text
ticker
franja horaria
sesión
historia reciente
```

No usaría media y desviación estándar simples. En microcaps hay muchos ceros y distribuciones extremadamente asimétricas. Empezaría con:

```text
log1p(variable)
mediana histórica
MAD o cuantiles empíricos
```

## 4.3 Suelo absoluto

El ratio relativo no basta.

Una acción que pasa de un trade cada diez minutos a dos trades por segundo tiene una aceleración enorme, pero puede continuar siendo inoperable.

Necesitamos un mínimo absoluto:

```text
número de trades
dollar volume
número de actualizaciones de quote
desplazamiento ejecutable del bid/ask
```

Preferiría **dollar volume** al volumen en acciones.

El umbral de 500.000 acciones tiene significados muy diferentes:

```text
500.000 acciones × $0,50 = $250.000
500.000 acciones × $20   = $10.000.000
```

La variable más comparable es:

[
\text{dollar volume}*W =
\sum*{i\in W} price_i \times size_i
]

También podemos utilizar:

[
\text{float turnover}_W =
\frac{\text{shares traded}_W}{\text{float shares}}
]

pero inicialmente lo dejaría como información contextual porque la cobertura histórica del float y su validez PIT deben comprobarse.

## 4.4 Respuesta del precio

No queremos alertar únicamente porque apareció un bloque grande.

Debe existir alguna respuesta ejecutable:

```text
midprice return
ask progression
nuevos máximos
rangos recorridos
eficiencia direccional
```

El precio principal del detector no debería ser siempre el último trade. Un único print erróneo, atrasado o fuera de mercado puede engañarlo. Preferiría, cuando sea legal según el contrato de quotes:

```text
mid = (best_bid + best_ask) / 2
microprice
executable ask
```

---

# 5. Una primera regla piloto concreta

No propongo estos números como parámetros definitivos. Los utilizaría como **grid experimental inicial**.

### Canal rápido: 3–5 segundos

```python
absolute_activity = (
    trades_5s >= 8
    and dollar_volume_5s >= 25_000
)

relative_shock = (
    trade_rate_ratio_5s >= 10
    or dollar_volume_ratio_5s >= 10
)

price_response = (
    mid_return_5s >= 0.01
    or executable_ask_return_5s >= 0.015
)

wake_up = (
    eligible_universe
    and absolute_activity
    and relative_shock
    and price_response
)
```

### Canal algo más lento: 15 segundos

```python
wake_up_15s = (
    trades_15s >= 20
    and dollar_volume_15s >= 50_000
    and (
        trade_rate_ratio_15s >= 8
        or dollar_volume_ratio_15s >= 8
    )
    and mid_return_15s >= 0.02
)
```

### Grid que probaría

| Variable           | Valores iniciales               |
| ------------------ | ------------------------------- |
| Ventana            | 1 s, 3 s, 5 s, 10 s, 15 s, 30 s |
| Nº trades          | 5, 8, 12, 20                    |
| Dollar volume      | $10k, $25k, $50k, $100k         |
| Retorno mid/ask    | 0,5%, 1%, 2%, 3%                |
| Actividad relativa | 5×, 10×, 20×, percentil 99,5    |
| Persistencia       | 1, 2 o 3 ventanas consecutivas  |

La condición no debería exigir que todos los parámetros sean altos simultáneamente. Podría haber varios canales:

```text
trade burst
quote burst
price jump
news event
halt resumption
```

Cualquiera de ellos puede despertar el ticker.

---

# 6. Cómo evitar las alertas falsas

Hay varios eventos que parecen activaciones, pero no lo son.

## Un único bloque

```text
1 trade de 300.000 acciones
sin movimiento del NBBO
sin nuevos trades
```

No debería activar el símbolo como frontside.

Exigiría:

```text
varios trades
distribuidos en varios timestamps
persistencia mínima
movimiento del bid/ask
```

## Prints atrasados o condiciones especiales

Debemos verificar que los ticks contengan:

```text
trade conditions
correcciones
cancelaciones
out-of-sequence flags
exchange timestamp
sequence
```

No se puede afirmar desde el README que todo esto exista y esté validado. El README confirma presencia física de `trades_ticks_prod_2005_2026`, pero recuerda que la autoridad semántica está en los contratos, no en el nombre de la carpeta. 

## Un precio que sube sin liquidez negociable

Puede haber un print alto, pero el ask real estar mucho más arriba o desaparecer.

El detector debe guardar:

```text
last trade
midprice
best ask
best bid
spread bps
displayed size
quote age
```

## Ruptura sin progreso

Una variable especialmente importante sería:

[
\text{price progress efficiency}
================================

\frac{\Delta midprice}
{\text{aggressive dollar volume}}
]

Por ejemplo:

```text
entran muchas compras agresivas
pero el precio deja de progresar
        ↓
absorción o agotamiento posible
```

La evidencia de microestructura pública muestra que, en intervalos muy cortos, el desequilibrio entre oferta y demanda en el bid y ask explica mejor los cambios de precio que el volumen negociado aislado. ([arXiv][1])

---

# 7. Scanner no significa entrada

El primer `wake_up` sólo debería decir:

```yaml
event_type: market_activity:abnormal_activation_detected
ticker: XYZ
event_timestamp: ...
detector_version: ...
evidence:
  trade_rate_5s: ...
  dollar_volume_5s: ...
  mid_return_5s: ...
  quote_update_rate_5s: ...
```

Después comienza una observación más cara:

```text
WAKE_UP
   ↓
ACTIVE OBSERVATION
   ↓
IMPULSE CONFIRMED
   ↓
FIRST PULLBACK
   ↓
CONTINUATION READY
```

Esta separación resuelve una confusión habitual:

> No necesitamos saber en el primer segundo si será SGN o será un fracaso. Necesitamos detectar tempranamente que merece observación.

El sistema puede producir tres decisiones distintas:

```text
WATCH
ENTER
DISCARD
```

El `WAKE_UP` produce `WATCH`, no necesariamente `ENTER`.

---

# 8. Cómo discrimina HFT miles de acciones

La respuesta directa es:

> HFT sí realiza cálculos y sí tiene latencia. Lo que no hace es recorrer todos los tickers, leer ficheros y recalcular todas las ventanas desde cero.

## No escanea el universo en un bucle

No funciona así:

```python
for ticker in 5000_tickers:
    read_database(ticker)
    recalculate_everything(ticker)
```

El feed entrega mensajes:

```text
trade de XYZ
quote de ABC
cancelación de DEF
```

Cada mensaje ya viene identificado por instrumento. En feeds directos como Nasdaq ITCH, los mensajes están secuenciados, utilizan identificadores compactos del instrumento y timestamps expresados en nanosegundos desde medianoche. ([Nasdaq Trader][2])

El procesamiento es:

```python
event = next_market_message()
state = states[event.instrument_id]
state.update(event)
```

Si una acción está totalmente muerta y no recibe eventos, prácticamente no consume cálculo.

## Estado incremental O(1)

Para cada símbolo se conservan contadores en memoria:

```text
trades últimos 1/5/15/60 segundos
shares últimos 1/5/15/60 segundos
dollar volume
último bid/ask
máximo y mínimo
quote updates
retorno
```

Cuando entra un nuevo evento:

```text
se suma el evento nuevo
se elimina el bucket expirado
```

No se vuelven a leer todos los trades de los últimos 60 segundos.

## Cascada barato → caro

```text
Todos los símbolos
    ↓ filtro extremadamente barato
20 símbolos despertados
    ↓ microestructura más detallada
5 símbolos relevantes
    ↓ modelo de estrategia y ejecución
1 o 2 decisiones
```

Los modelos complejos, Hawkes, ML o clasificación de noticias no se ejecutan obligatoriamente sobre los miles de símbolos con cada mensaje. Los procesos Hawkes pueden modelar la autoexcitación de trades y movimientos, pero los reservaría para investigación posterior, no para la primera versión del scanner. ([arXiv][3])

## Infraestructura

Los participantes que compiten en microsegundos utilizan conexiones directas, colocación cercana a los mercados y, en algunos casos, FPGA para reducir la latencia de recepción y procesamiento. Nasdaq ofrece colocación para reducir latencia y complejidad de red, y publica métricas de conectividad de decenas de microsegundos para determinados servicios. ([Nasdaq][4])

También existen implementaciones académicas y profesionales donde parte del *feed handling* y del libro se procesa en FPGA. ([IEEE Xplore][5])

TSIS no necesita competir en ese juego para esta estrategia.

Nuestro objetivo realista sería:

```text
no capturar el primer milisegundo
sino detectar en 1–5 segundos
y modelar la primera continuación operable
```

---

# 9. Arquitectura concreta para TSIS

```text
┌────────────────────────────────────────────┐
│ PRESESSION UNIVERSE TABLE                  │
│ market cap · price · exchange · identity   │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ STREAM ROUTER                              │
│ trades · quotes · news · halts             │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ LIGHTWEIGHT WAKE-UP DETECTOR               │
│ O(1) rolling counters per symbol           │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ ACTIVE SYMBOL REGISTRY                     │
│ priority score · TTL · reason              │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ EVENT STATE BUILDER                        │
│ snapshots at t and bounded windows         │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ FRONTSIDE STATE MACHINE                    │
│ impulse · pullback · rebreak · exhaustion  │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ EXECUTION SIMULATOR                        │
│ quotes · latency · spread · partial fills  │
└────────────────────────────────────────────┘
```

## Eventos mínimos

```text
abnormal_activity_detected
price_expansion_started
impulse_confirmed
first_pullback_started
first_pullback_completed
continuation_breakout
frontside_failure
frontside_terminated
halt_started
halt_resumed
```

## Ventanas de estado

En cada evento guardaría ventanas como:

```text
[-300s, -60s]  baseline dormant
[-60s, -15s]   preactivation
[-15s, 0s]     immediate activation
[0s, +5s]      initial response
[0s, +15s]     confirmation
[0s, +60s]     impulse development
```

Los outcomes futuros se escriben en otra capa, nunca dentro del estado observable.

---

# 10. Cómo haría el backtest

## Fase 1: descubrimiento con 1m

La vista 1m quote-guarded sirve para:

```text
localizar episodios
crear casepacks
descubrir patrones
seleccionar días y tickers
definir ventanas de replay
```

El materializador está concebido precisamente para que scanners y *state builders* consuman esa vista sin reconstruir reparaciones en cada consulta. 

## Fase 2: replay de trades y quotes

Para cada ticker/día seleccionado:

```text
leer trades y quotes ordenados temporalmente
reproducir evento por evento
actualizar estados incrementales
emitir wake-up sin mirar el futuro
registrar decision_timestamp
```

## Fase 3: ejecución

No rellenaría la orden al precio que originó la señal.

```text
decision_timestamp
    +
latencia modelada
    ↓
primera quote elegible posterior
```

Hay que considerar:

```text
bid/ask
spread
displayed size
partial fill
slippage
halt/LULD
trade conditions
```

## Vistas subminuto

Podemos derivar:

```text
1s
5s
15s
30s
event bars
volume bars
dollar-volume bars
```

Pero deben ser vistas derivadas del tape:

```text
trades/quotes
    ↓
subminute views
```

No una nueva fuente de verdad.

Para los gráficos y una primera estrategia convencional, las velas de 5 s pueden ser muy útiles. Para validar el primer impulso, no bastan por sí solas.

---

# 11. Lo que debemos comprobar antes de declarar viable el replay

La presencia física de trades y quotes no demuestra todavía que estén preparados para este uso.

Hay que confirmar:

| Trades                     | Quotes                            |
| -------------------------- | --------------------------------- |
| Resolución del timestamp   | NBBO o quotes por venue           |
| Secuencia                  | Bid/ask y tamaños                 |
| Trade conditions           | Timestamp y secuencia             |
| Correcciones/cancelaciones | Locked/crossed markets            |
| Premarket incluido         | Premarket incluido                |
| Odd lots                   | Frecuencia de snapshots o updates |
| Symbol mapping             | Calidad/staleness                 |

También necesitamos saber:

```text
exchange timestamp o vendor timestamp
timezone
orden estable entre trades y quotes
cobertura real por año
latencia histórica disponible
```

Sin ese contrato no afirmaría todavía que TSIS posee un replay microestructural listo. Afirmaría algo más preciso:

> **TSIS parece disponer de las familias físicas necesarias, pero falta cerrar su admisibilidad para este uso concreto.**

---

# 12. Mi propuesta final de detector

Mantendría el scanner actual y crearía:

```text
TSIS_MICROCAP_WAKEUP_DETECTOR_V0_1
```

Su lógica inicial:

```text
GATE A — eligible universe
MCap < $100M
$0.50 <= executable price <= $20

GATE B — absolute activity
minimum trades
minimum dollar volume
minimum quote updates

GATE C — relative shock
trade-rate anomaly
dollar-volume-rate anomaly
quote-rate anomaly

GATE D — price response
mid/ask progression
directional efficiency

OUTPUT
WATCH event, not automatic BUY
```

Después:

```text
TSIS_FRONTSIDE_STATE_TRACKER_V0_1
```

clasificaría:

```text
impulse
single-candle rebreak
ascending flag
multi-candle flag
flat shelf
VWAP reclaim
last-red-high break
failure/exhaustion
```

Esas categorías ya aparecen en vuestro propio manifiesto del ZIP. Por tanto, no impondría un único Donchian a todas. Construiría una ontología de estados y permitiría que varios triggers operaran dentro de ella.

La conclusión ajustada es:

> **El filtro de 500.000 acciones debe conservarse como confirmación “in play”. Para descubrir el despertar en segundos necesitamos un nuevo filtro basado en velocidad de trades, velocidad de dollar volume, cambio relativo respecto al estado dormido y respuesta del bid/ask. La fuente primaria debe ser el stream de trades y quotes; las velas subminuto son vistas derivadas.**

Y el objetivo no debería ser comprar en el primer tick:

[
\text{detectar pronto}
\rightarrow
\text{observar intensamente}
\rightarrow
\text{clasificar el estado}
\rightarrow
\text{entrar sólo cuando exista una oportunidad ejecutable}
]

[1]: https://arxiv.org/abs/1011.6402?utm_source=chatgpt.com "The Price Impact of Order Book Events"
[2]: https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf?utm_source=chatgpt.com "Nasdaq TotalView-ITCH 5.0"
[3]: https://arxiv.org/abs/1502.04592?utm_source=chatgpt.com "Hawkes processes in finance"
[4]: https://www.nasdaq.com/solutions/nasdaq-co-location?utm_source=chatgpt.com "Stock Exchange Co-Location - Data Center & Trading"
[5]: https://ieeexplore.ieee.org/document/6868785/?utm_source=chatgpt.com "Low latency book handling in FPGA for high frequency ..."
