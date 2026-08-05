## Respuesta central

Lo que quieres construir **no es realmente un Donchian aplicado a microcaps**.

El nombre técnico más aproximado sería:

> **Estrategia event-driven de expansión de volatilidad y continuación del momentum frontside.**

El Donchian, el *premarket high*, el *high of day*, una bandera o el *opening range breakout* serían únicamente **posibles disparadores de entrada** dentro de esa estrategia.

En el documento, el Donchian se presenta como una ruptura mecánica del máximo de los últimos (X) cierres. Eso puede servir en mercados líquidos y tendenciales, pero no describe adecuadamente una microcap que pasa de estar muerta a subir un 50% en un minuto. 

La arquitectura correcta sería:

[
\text{candidato}
\times
\text{detección de activación}
\times
\text{estado frontside}
\times
\text{trigger estructural}
\times
\text{ejecución}
\times
\text{salida}
]

No:

[
\text{rompe PMH} \Rightarrow \text{comprar}
]

---

# Qué enseñan tus dos gráficos

## SGN

En SGN se observa esta secuencia:

```text
Activo prácticamente muerto
        ↓
Aparición súbita de volumen
        ↓
Primer impulso vertical
        ↓
Pullback
        ↓
Bandera / consolidación
        ↓
Ruptura de la bandera
        ↓
Nueva expansión hacia PMH
        ↓
Ruptura posterior de PMH
```

El movimiento frontside **no empieza en la ruptura del PMH**.

Cuando rompe PMH, la acción ya ha:

* Multiplicado su precio.
* Generado varios impulsos.
* Construido una bandera.
* Confirmado interés especulativo.
* Realizado una parte importante del recorrido.

En este caso, el punto marcado como `banderita rota` probablemente representa una familia de entrada más interesante que el PMH:

> **First-pullback continuation breakout.**

## LIDR

LIDR muestra el problema contrario:

```text
Gap
  ↓
Movimiento premarket
  ↓
Consolidación
  ↓
Ruptura de PMH a las 09:36
  ↓
Pequeña extensión
  ↓
Colapso violento
```

Un sistema puro:

```python
if price > premarket_high:
    buy()
```

habría comprado precisamente en el círculo azul y habría sufrido la caída posterior.

Por tanto, los dos gráficos demuestran algo fundamental:

> **El nivel roto no contiene por sí solo el edge. El edge está en el estado del episodio cuando se rompe ese nivel.**

PMH es el mismo tipo de trigger en ambos casos, pero la dinámica posterior es completamente diferente.

---

# Qué utilizan realmente los profesionales

Las reglas exactas de cada fondo son propietarias. Lo que permite ver la literatura pública es que no suelen depender de una única figura chartista, sino de varias familias de señales combinadas.

## 1. Estrategias event-driven: detectar la causa antes que el gráfico

Son las más cercanas a “capturar el minuto en el que empieza todo”.

El sistema consume en tiempo real:

* Noticias corporativas.
* Comunicados de prensa.
* SEC filings.
* Resultados clínicos.
* Aprobaciones regulatorias.
* Contratos comerciales.
* Ofertas, *reverse splits* o financiación.
* Cambios de dirección.
* Halts y reanudaciones.
* Redes sociales o fuentes alternativas, cuando son legalmente utilizables.

El algoritmo no analiza solamente si la noticia es positiva o negativa. Intenta extraer:

```text
tipo de evento
sorpresa
materialidad
novedad
credibilidad de la fuente
dilución potencial
magnitud económica
edad de la noticia
ambigüedad
```

La investigación pública muestra sistemas que detectan eventos corporativos en noticias con marcas temporales de minuto y los relacionan con movimientos posteriores. También existe evidencia de que noticias no programadas pueden estar asociadas con saltos intradía. ([arXiv][1])

Esta es la vía más rápida, pero también la más difícil. Cuando el mercado empieza a subir, los participantes que procesaron primero una noticia legible por máquinas pueden llevar segundos de ventaja; la velocidad alrededor de anuncios es una parte importante de este tipo de estrategias. ([SSRN][2])

### Qué puede capturar

```text
Noticia a las 10:00:00
        ↓
Clasificación del evento
        ↓
Orden a las 10:00:01
        ↓
Primer impulso
```

Para esto, una vela de un minuto es demasiado lenta.

---

## 2. Detectores de activación o de salto

Estos algoritmos no necesitan conocer la noticia. Detectan que el comportamiento estadístico de la acción acaba de cambiar.

No preguntan inicialmente:

> “¿Ha roto PMH?”

Preguntan:

> “¿Ha dejado de pertenecer al régimen inactivo en el que estaba hace treinta segundos?”

Las variables habituales serían:

* Retorno normalizado.
* Velocidad y aceleración del precio.
* Volumen anormal.
* Aceleración del *dollar volume*.
* Número de trades por segundo.
* Tamaño de los trades.
* Reducción repentina de la liquidez del ask.
* Expansión del spread.
* Cambios en profundidad.
* Desequilibrio entre compras y ventas agresivas.
* Distancia recorrida respecto a su volatilidad previa.
* Cambio estructural en la distribución de retornos.

Una investigación con Level 2 de 1.271 acciones estudió precisamente la predicción de saltos en los siguientes cinco minutos utilizando medidas de liquidez e indicadores técnicos. Es evidencia de que este problema puede formularse mediante ML, aunque no prueba directamente que el mismo modelo funcione en microcaps estadounidenses. ([arXiv][3])

Esto puede implementarse mediante:

```text
CUSUM
Bayesian change-point detection
jump tests
Isolation Forest
Random Forest
gradient boosting
modelos de estados ocultos
redes temporales
```

Aquí el objetivo no es todavía comprar, sino producir un evento como:

```yaml
event_type: volatility_expansion_activated
subject: SGN
decision_timestamp: 2025-05-28T...
confidence: 0.94
```

---

## 3. Order-flow momentum

Una vez activada la acción, los participantes de alta frecuencia observan cómo se está consumiendo la liquidez.

Un indicador simplificado sería:

[
OFI_t =
\text{presión compradora}
-------------------------

\text{presión vendedora}
]

Pero un sistema profesional no mira solamente la cantidad mostrada en Level 2. Considera:

* Órdenes añadidas.
* Órdenes canceladas.
* Trades ejecutados contra el ask.
* Trades ejecutados contra el bid.
* Desplazamiento del NBBO.
* Profundidad disponible.
* Recuperación de la liquidez después de una agresión.
* Impacto conseguido por cada unidad comprada.
* Absorción.

La investigación con NYSE TAQ encontró una relación aproximadamente lineal entre cambios de precio y desequilibrio del flujo de órdenes, y que esta relación era más robusta que usar solamente volumen negociado. ([arXiv][4])

Un ejemplo importante:

```text
Muchísimas compras agresivas
pero el precio deja de subir
        ↓
Absorción / agotamiento potencial
```

Eso podría haber ayudado a reconocer que el breakout de LIDR estaba perdiendo eficacia, aunque el gráfico de velas por sí solo no permite demostrar qué ocurrió exactamente dentro del libro.

---

## 4. Modelos de intensidad autoexcitada

En un movimiento explosivo, cada trade puede generar nuevos trades:

```text
Compra agresiva
    ↓
Rompe un nivel
    ↓
Activa stops y breakout traders
    ↓
Aumenta el volumen
    ↓
Atrae scanners
    ↓
Genera nuevas compras
```

Los procesos de Hawkes modelan precisamente esta propiedad: la llegada de un evento eleva temporalmente la probabilidad de que lleguen más eventos. Se han utilizado para representar la interacción entre trades, movimientos de precios, impacto y actividad de alta frecuencia. ([arXiv][5])

En nuestro caso podrían servir para estimar:

```text
intensidad de compras agresivas
intensidad de ventas agresivas
probabilidad de continuación de la cascada
velocidad de decaimiento del impulso
```

No sería necesario empezar con Hawkes. Primero habría que demostrar que variables más sencillas de intensidad contienen información.

---

## 5. Breakouts estructurales

Aquí sí entra Donchian, pero como una familia más.

Los triggers públicos más próximos a lo que muestras son:

| Trigger                    | Qué rompe                                |
| -------------------------- | ---------------------------------------- |
| Opening Range Breakout     | Máximo de los primeros X minutos         |
| PMH breakout               | Premarket high                           |
| HOD breakout               | High of day                              |
| First-pullback breakout    | Máximo de la primera consolidación       |
| Breakout-retest            | Nivel roto después de un retest          |
| VWAP reclaim               | Recuperación de VWAP                     |
| Halt-resumption breakout   | Rango formado tras una reanudación       |
| Event-conditioned Donchian | Máximo rolling después de una activación |

Las estrategias ORB han sido investigadas públicamente en acciones estadounidenses, pero eso no significa que una ruptura simple sea suficiente en microcaps ni que los resultados se transfieran directamente a este universo. ([SSRN][6])

El equivalente más adecuado para SGN sería:

> **Event-conditioned first-pullback breakout.**

No un Donchian de veinte barras ejecutado durante todo el día.

---

# Las tres maneras de entrar en el frontside

Hay tres relojes diferentes.

## A. Antes del movimiento: reloj causal

```text
noticia → clasificación → entrada
```

Ventaja:

* Puede capturar el primer impulso.

Problema:

* Competencia por latencia.
* Riesgo de interpretar mal el evento.
* Spreads y falta de liquidez.
* La noticia puede ser positiva superficialmente y dilutiva realmente.

## B. Durante el primer impulso: reloj de activación

```text
volumen + trades + aceleración + order flow → entrada
```

Ventaja:

* No necesita conocer la causa.
* Puede incorporarse relativamente pronto.

Problema:

* Muchos falsos positivos.
* Ejecución muy sensible al spread y al *slippage*.
* Necesita trades y quotes, no sólo velas.

## C. Después del impulso: reloj estructural

```text
impulso → pullback → bandera → breakout
```

Ventaja:

* Más observable.
* Más fácil de validar.
* Permite definir un stop estructural.

Problema:

* Sacrifica la primera parte del movimiento.
* Puede entrar en una fase ya agotada.

Para TSIS, la vía C combinada con parte de B parece el punto de partida más científico y realizable:

> Detectar la activación y operar la primera continuación estructurada.

No intentar ganar una carrera de microsegundos contra sistemas de noticias.

---

# Estrategia TSIS que encajaría con este movimiento

## `FRONTSIDE_EXPANSION_CONTINUATION_V0_1`

### Máquina de estados

```text
DORMANT
   │
   │ actividad anormal
   ▼
ACTIVATED
   │
   │ expansión direccional
   ▼
IMPULSE
   │
   │ retroceso controlado
   ▼
FIRST_PULLBACK
   │
   │ compresión + higher low
   ▼
CONTINUATION_READY
   │
   │ rompe nivel con renovación del flujo
   ▼
FRONTSIDE_ACTIVE
   │
   ├── continuación
   │
   └── fallo / agotamiento
             ▼
       FRONTSIDE_TERMINATED
```

### La entrada no sería una única condición

Conceptualmente:

```python
entry_allowed = (
    candidate_is_in_play
    and state == CONTINUATION_READY
    and structural_breakout
    and renewed_activity
    and execution_quality_is_acceptable
    and not_exhausted
)
```

El breakout podría ser:

```python
structural_breakout = (
    price > first_pullback_high
    or price > premarket_high
    or price > opening_range_high
)
```

Pero sería el **último predicado**, no toda la estrategia.

---

# Objetos de información relevantes

Para este caso, tus objetos actuales encajan bastante bien:

```text
price_movement
trading_activity
volatility_range_state
liquidity
market_microstructure_state
order_flow_pressure
price_location_intraday
news_catalyst_context
fundamental_context
short_side_context
halt_context
```

Las representaciones candidatas incluirían:

### Activación

```text
return_5s / 15s / 60s
price_velocity
price_acceleration
trade_count_acceleration
dollar_volume_acceleration
relative_volume
float_turnover
```

### Calidad del impulso

```text
progress_per_dollar_volume
green_volume_ratio
ask_lift_rate
pullback_depth
time_to_new_high
wick_ratio
spread_normalized
depth_depletion
```

### Localización

```text
distance_to_VWAP
distance_to_PMH
distance_to_HOD
distance_to_LULD_upper_band
distance_from_impulse_base
extension_from_last_consolidation
```

### Agotamiento

```text
aggressive_buying_without_price_progress
failed_breakout_count
price_acceleration_decay
spread_expansion
upper_wick_cluster
VWAP_loss
failed_VWAP_reclaim
lower_high_confirmation
```

No significa convertir inmediatamente cada variable en un filtro. Primero deben tratarse como información observable y estudiar cuáles aportan realmente capacidad discriminatoria.

---

# Aplicación a SGN y LIDR

## SGN

Las posibles oportunidades serían:

```text
1. Activación inicial
   Muy difícil de ejecutar con 1m

2. Primer pullback
   Mejor relación entre observabilidad y precocidad

3. Ruptura de la bandera
   Trigger estructural claro

4. Ruptura de PMH
   Entrada de continuación más tardía
```

La estrategia que más se parece a lo señalado en la imagen es:

> **Volatility activation + first flag breakout + order-flow renewal.**

## LIDR

El PMH breakout se produjo, pero no hubo continuidad sostenible.

El sistema tendría que evaluar antes de entrar:

* Cuánto recorrido ya llevaba.
* Cuánta expansión quedaba hasta LULD.
* Si el flujo comprador seguía produciendo avance.
* Si aparecía absorción.
* Si el spread estaba deteriorándose.
* Si la ruptura mantenía el nivel.
* Si el nuevo máximo era aceptado o inmediatamente rechazado.

La diferencia entre SGN y LIDR no se resuelve cambiando Donchian de 20 a 10 barras. Se resuelve representando el **estado del episodio**.

---

# Requisitos del backtest

Para investigar candidatos y dibujar episodios pueden servir barras de un minuto.

Para probar entradas dentro de una vela que sube 20%, 30% o 50%, **una vela de un minuto no es suficiente**. No permite saber:

* En qué orden ocurrieron máximo y mínimo.
* Qué ask existía al dispararse la señal.
* Cuánto volumen había disponible.
* Si habría habido fill completo.
* Cuál era el spread.
* Si entró en estado LULD.
* Si se produjo un halt entre ambos precios.

El sistema de Limit Up-Limit Down utiliza bandas dinámicas basadas en precios recientes y contempla estados límite, pausas y procesos específicos de reapertura. Por eso el estado LULD y los eventos de halt deben formar parte del replay, no ser una anotación posterior. ([SEC][7])

La base mínima debería separar:

```text
1m bars
    → selección de candidatos y contexto

trades + NBBO quotes
    → decisiones y ejecución

halts + LULD
    → disponibilidad real del mercado

news point-in-time
    → contexto causal sin anticipación

reference + float point-in-time
    → universo y capacidad
```

Además, la liquidez de las microcaps es especialmente problemática: la SEC señala que sus bajos volúmenes pueden dificultar las salidas y que una operación de cierto tamaño puede tener un gran impacto porcentual en el precio. Esto implica que la capacidad será pequeña y que este nicho encaja más naturalmente —como inferencia— en firmas propietarias o fondos especializados pequeños que en fondos gigantescos. ([SEC][8])

---

# Cómo llamaría a la estrategia

Evitaría el término **momentum ignition**, porque regulatoriamente suele referirse a intentar provocar artificialmente un movimiento mediante órdenes o trades, una conducta potencialmente manipuladora. Nuestro sistema observa y sigue una activación natural; no intenta crearla. ([Finra][9])

Un nombre científicamente más preciso sería:

```text
Event-Conditioned Frontside Expansion Strategy
```

o:

```text
Catalyst and Activity Conditioned
Intraday Momentum Continuation
```

La conclusión práctica es:

> **Donchian, PMH, HOD o una bandera no son estrategias completas. Son triggers. La estrategia profesional consiste en determinar cuándo una acción ha cambiado de régimen, si todavía está en frontside, si la presión compradora continúa siendo efectiva y si la ruptura puede ejecutarse con liquidez y riesgo aceptables.**

Para empezar TSIS, no intentaría capturar el primer 50% invisible. Modelaría primero el tramo que aparece claramente en SGN:

[
\text{activación}
\rightarrow
\text{primer impulso}
\rightarrow
\text{primer pullback}
\rightarrow
\text{ruptura de continuación}
]

Ese episodio es suficientemente temprano para conservar una parte importante del movimiento y suficientemente observable para construir un backtest científicamente defendible.

[1]: https://arxiv.org/abs/2105.12825 "Trade the Event: Corporate Events Detection for News-Based Event-Driven Trading"
[2]: https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2174901_code356671.pdf?abstractid=2174901&mirid=1&utm_source=chatgpt.com "Speed, Algorithmic Trading, and Market Quality around ..."
[3]: https://arxiv.org/abs/1912.07165 "[1912.07165] Predicting intraday jumps in stock prices using liquidity measures and technical indicators"
[4]: https://arxiv.org/abs/1011.6402 "The Price Impact of Order Book Events"
[5]: https://arxiv.org/abs/1301.1135 "Hawkes model for price and trades high-frequency dynamics"
[6]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284&utm_source=chatgpt.com "A Profitable Day Trading Strategy For The U.S. Equity Market"
[7]: https://www.sec.gov/files/rules/sro/nms/2026/34-105596.pdf "Notice of Filing of the Twenty-Seventh Amendment to the National Market System Plan to Address Extraordinary Market Volatility to Establish Temporary Price Band Protections in Overnight Trading"
[8]: https://www.sec.gov/oiea/investor-alerts-bulletins/ib_microcap_1.html "Investor Bulletin: Microcap Stock Basics (Part 1 of 3: General Information) | Investor.gov"
[9]: https://www.finra.org/rules-guidance/guidance/reports/2024-finra-annual-regulatory-oversight-report/manipulative-trading?utm_source=chatgpt.com "Manipulative Trading | FINRA.org"
