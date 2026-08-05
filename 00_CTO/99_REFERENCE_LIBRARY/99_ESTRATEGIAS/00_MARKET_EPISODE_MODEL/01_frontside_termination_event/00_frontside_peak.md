Sí. **Creo que el final del frontside es detectable**, pero no de la misma manera que una figura técnica reconoce retrospectivamente el máximo.

La formulación correcta no sería:

> “Encontrar exactamente el top.”

Sería:

> **Detectar en tiempo real que el régimen comprador que sostenía el frontside está perdiendo persistencia, capacidad de desplazar el precio y resiliencia microestructural, y que la probabilidad de transición a backside acaba de aumentar materialmente.**

Eso sí es científicamente investigable y, con trades y quotes, potencialmente operable.

---

# 1. Primero: no existe un único “momento final”

Hay que separar cuatro timestamps:

| Timestamp                     | Significado                                                              | ¿Conocible en tiempo real? |
| ----------------------------- | ------------------------------------------------------------------------ | -------------------------: |
| `frontside_peak_timestamp`    | Máximo retrospectivo del episodio                                        |                         No |
| `termination_onset_timestamp` | Instante latente en que empieza a deteriorarse el régimen                |            No directamente |
| `termination_detected_at`     | Primer instante en que el sistema acumula evidencia suficiente           |                         Sí |
| `backside_confirmed_at`       | Instante en que la transición bajista ya está suficientemente confirmada |         Sí, pero más tarde |

Ejemplo:

```text
10:01:12  último máximo real
10:01:14  compradores empiezan a perder eficacia
10:01:19  detector eleva termination_risk
10:01:27  pérdida de soporte + failed reclaim
10:01:31  backside confirmado
```

El backtest no puede fingir que a las `10:01:12` sabía que ese sería el máximo.

Vuestra arquitectura ya contiene exactamente la distinción necesaria: un evento puede situarse retrospectivamente en `event_timestamp`, pero su identidad sólo puede utilizarse desde `event_detected_at`; además, las observaciones posteriores pueden ser válidas para investigación y, aun así, estar prohibidas como inputs predictivos. 

Por tanto, el objetivo no es adivinar retrospectivamente `frontside_peak_timestamp`, sino minimizar:

[
termination_detected_at
-----------------------

termination_onset_timestamp
]

manteniendo controlada la tasa de falsas alarmas.

---

# 2. La intuición económica tiene fundamento, pero no debe convertirse en una ley universal

Tu afirmación es razonable:

```text
gran extensión
+
micro/small cap
+
liquidez limitada
+
participación especulativa
→
alta propensión posterior a reversión
```

Pero no afirmaría todavía:

```text
cualquier extensión X%
→ necesariamente backside
```

La propensión dependerá de:

* Magnitud y calidad del catalizador.
* Float y capitalización.
* Dilución disponible.
* Volumen y turnover.
* Hora de la sesión.
* Número de halts.
* Liquidez.
* Duración del frontside.
* Participación institucional o predominantemente minorista.
* Magnitud de la extensión anterior.
* Capacidad de aparecer nuevo flujo comprador.

Existe evidencia general de reversión tras movimientos intradía extremos, y los valores más ilíquidos presentan con frecuencia mayor propensión a revertir. Un trabajo reciente específicamente sobre microcaps estadounidenses estudia 3.133 episodios con gaps extremos durante 2020–2024; es evidencia exploratoria muy próxima a vuestro universo, aunque se trata de una tesis reciente y no de una ley establecida. La literatura sobre *penny stocks* también documenta baja liquidez, elevados costes y reversals, mientras que estudios más generales encuentran reversión después de movimientos intradía extremos. ([Aaltodoc][1])

Esto justifica investigar el fenómeno, pero **TSIS debe estimar su propia distribución condicional**.

---

# 3. Por qué el final podría ser visible en microestructura

El frontside no es únicamente una trayectoria alcista de velas.

Es un régimen sostenido por una combinación de:

```text
compras agresivas
+
persistencia del order flow
+
liquidez disponible
+
retirada o consumo del ask
+
reposición del bid
+
aparición continua de nuevos participantes
```

El frontside termina cuando esa maquinaria cambia.

La investigación microestructural demuestra que, en horizontes muy cortos, los cambios de precio están más relacionados con el desequilibrio entre oferta y demanda en bid y ask que con el volumen aislado. También se ha observado poder predictivo en el queue imbalance, en los flujos de órdenes límite, en las tasas relativas de adiciones y cancelaciones y en la forma del libro. ([arXiv][2])

Además, el flujo de órdenes puede atravesar regímenes persistentes y esos cambios pueden detectarse online mediante métodos de *change-point detection*. Un estudio aplicado a Nasdaq encontró que incorporar el régimen del order flow mejora la predicción online del flujo y de su impacto sobre el precio. ([arXiv][3])

También existe una conexión económica importante: cuando finaliza una secuencia sostenida de compras, parte de su impacto empieza a relajarse. Esto se ha documentado en millones de metaórdenes institucionales; no demuestra directamente el comportamiento de una microcap especulativa, pero sí sustenta la idea de que **el final de un flujo persistente puede preceder a la relajación del precio**. ([arXiv][4])

---

# 4. La transición correcta no es `frontside → backside` de golpe

Propondría esta máquina de estados:

```text
FRONTSIDE_ACTIVE
        │
        │ aparecen señales de deterioro
        ▼
FRONTSIDE_STRESSED
        │
        ├──── recuperación del flujo ────→ FRONTSIDE_ACTIVE
        │
        │ deterioro multifuente
        ▼
TERMINATION_RISK_HIGH
        │
        ├──── nuevo impulso válido ──────→ FRONTSIDE_ACTIVE
        │
        │ ruptura + rechazo + flujo vendedor
        ▼
TERMINATION_DETECTED
        │
        ├──── reclaim válido ────────────→ FRONTSIDE_STRESSED
        │
        ▼
BACKSIDE_CONFIRMED
```

Esto es imprescindible porque, como señalas, durante un frontside válido puede haber:

* Breakouts bajistas de soportes.
* Pérdidas temporales de VWAP.
* Pullbacks profundos.
* Barridas de mínimos.
* Falsas rupturas.
* Consolidaciones largas.
* Reanudaciones después de halts.
* Rechazos del HOD que luego son recuperados.

Una pérdida de soporte **no es suficiente**.

El detector necesita distinguir:

```text
pullback que libera presión
```

de:

```text
deterioro estructural que destruye el régimen comprador
```

---

# 5. Las señales más prometedoras

No buscaría un único indicador. Buscaría una confluencia de fenómenos independientes.

## 5.1 Divergencia entre esfuerzo comprador y resultado

Esta probablemente sería una de las señales más importantes.

Durante el frontside:

```text
compras agresivas
→ el precio avanza
```

Cerca del agotamiento:

```text
más compras agresivas
→ cada vez menos avance
```

Representación:

[
BuyResponse_t =
\frac{\Delta midprice_t^{+}}
{AggressiveBuyDollar_t+\varepsilon}
]

Y su inversa:

[
BuyEffortPerProgress_t =
\frac{AggressiveBuyDollar_t}
{\Delta midprice_t^{+}+\varepsilon}
]

Señal de deterioro:

```text
aggressive_buy_dollar aumenta
buy_response disminuye
precio hace un nuevo máximo marginal
```

Esto es la traducción microestructural de:

> “Entra mucho volumen comprador, pero ya no sube.”

No debemos confundirlo con escasa liquidez:

```text
poquísimo volumen
+
movimiento enorme
```

Eso tampoco es necesariamente saludable. Puede ser un vacío de liquidez.

La zona favorable sería:

```text
participación amplia
+
impacto comprador consistente
+
progreso ordenado
```

---

## 5.2 Absorción en el ask

Una forma de terminación puede comenzar cuando la oferta empieza a absorber repetidamente las compras:

```text
se consume el ask
↓
aparece nuevamente oferta
↓
se vuelve a consumir
↓
el precio apenas progresa
```

Variables candidatas:

```text
ask_depletion_rate
ask_replenishment_rate
ask_replenishment_after_buy_burst
aggressive_buy_volume_without_tick_progress
repeated_trade_at_ask_without_ask_step_up
```

Métrica conceptual:

[
AskAbsorption =
\frac{\text{ask notional repuesto}}
{\text{ask notional consumido}+\varepsilon}
]

No toda reposición del ask es negativa. En un mercado sano debe existir liquidez. Lo preocupante sería:

```text
ask se repone
+
bid deja de avanzar
+
compras pierden impacto
+
aparecen rechazos repetidos
```

---

## 5.3 Pérdida de resiliencia del bid

En un frontside fuerte, después de una descarga vendedora suele ocurrir:

```text
sell burst
↓
bid absorbe
↓
bid se repone
↓
precio recupera
```

Cerca del final:

```text
sell burst similar
↓
bid desaparece
↓
no se repone
↓
el siguiente bid está mucho más abajo
```

Métrica:

[
BidResilience =
\frac{
\text{bid notional repuesto tras presión vendedora}
}{
\text{bid notional eliminado}+\varepsilon
}
]

Variables:

```text
bid_replenishment_rate
bid_hold_duration
bid_step_down_rate
time_to_bid_recovery
price_recovery_after_sell_burst
```

La pérdida de un nivel gráfico es más significativa cuando coincide con:

```text
bid resilience ↓
sell impact ↑
buy response ↓
```

---

## 5.4 Asimetría creciente del impacto

Esta es una señal especialmente interesante.

Durante el frontside:

```text
$50k compradores → +4%
$50k vendedores  → -1%
```

Cerca del final:

```text
$50k compradores → +0,5%
$50k vendedores  → -5%
```

Representación:

[
ImpactAsymmetry =
\frac{
|\Delta mid| / SellDollar
}{
\Delta mid^{+} / BuyDollar+\varepsilon
}
]

Cuando sube mucho:

```text
las compras requieren cada vez más esfuerzo
las ventas encuentran cada vez menos soporte
```

Esto puede aparecer antes de que el gráfico de un minuto muestre claramente el backside.

---

## 5.5 Cambio de régimen del order flow

El frontside suele tener persistencia:

```text
buy
buy
buy
pequeña venta
buy
buy
```

El final puede venir precedido por:

```text
menor autocorrelación compradora
más alternancia
clusters vendedores más largos
cambio de signo del OFI
```

Variables:

```text
trade_sign_autocorrelation
buy_run_length
sell_run_length
signed_dollar_imbalance
OFI
OFI_slope
buy_to_sell_intensity_ratio
Hawkes buy/sell intensity
```

No bastaría con un OFI negativo durante dos segundos. Lo relevante sería una transición:

```text
OFI muy positivo
→ OFI pierde intensidad
→ OFI neutral
→ OFI negativo persistente
```

Aquí puede entrar un `Bayesian Online Change-Point Detector`, un HMM/HSMM o, inicialmente, una regla secuencial interpretable.

---

## 5.6 Fallo de aceptación de nuevos máximos

No es suficiente tocar o superar el HOD.

Debemos medir si el mercado **acepta** el nuevo nivel.

[
HighAcceptance =
\frac{
\text{tiempo o eventos por encima del nivel}
}{
\text{ventana total}
}
]

Variables:

```text
time_above_prior_hod
events_above_prior_hod_ratio
bid_time_above_prior_hod
rejection_latency
distance_rejected_from_new_high
number_of_failed_high_tests
```

Secuencia terminal frecuente:

```text
nuevo HOD
+
muy poca aceptación
+
bid vuelve bajo el nivel
+
segundo intento más débil
+
venta con impacto elevado
```

Esto encaja conceptualmente con LIDR: rompe PMH y alcanza un máximo, pero el movimiento es rechazado violentamente. Sin trades y quotes no podemos afirmar qué ocurrió dentro de la microestructura, pero las hipótesis que habría que comprobar serían:

```text
buy effort sin progreso
aceptación muy baja
bid resilience colapsando
sell impact aumentando
```

---

## 5.7 Divergencia entre precio y participación

Un nuevo máximo no siempre tiene la misma calidad que el anterior.

Compararía cada burst con el burst previo:

[
BurstRenewal =
\frac{ActivityIntensity_{burst,2}}
{ActivityIntensity_{burst,1}}
]

Y:

[
ProgressRenewal =
\frac{PriceProgress_{burst,2}}
{PriceProgress_{burst,1}}
]

Ejemplo terminal:

```text
Burst 1:
+20%
1.000 trades
$1M
varios venues

Burst 2:
+3%
400 trades
$300k

Burst 3:
nuevo HOD marginal
120 trades
$80k
```

Variables:

```text
trade_rate_decay
dollar_volume_rate_decay
venue_breadth_decay
unique_participant_proxy_decay
quote_update_decay
new_high_progress_decay
```

No toda caída del volumen es terminal: las banderas sanas suelen tener contracción de actividad. La diferencia estaría en lo que sucede cuando se intenta reanudar el movimiento:

```text
pausa con volumen decreciente
+
ruptura con intensidad renovada
= continuación saludable
```

frente a:

```text
pausa
+
ruptura sin renovación
+
rechazo
= riesgo terminal
```

---

## 5.8 Degradación de la eficiencia direccional

[
DirectionalEfficiency =
\frac{
|mid_t-mid_{t-W}|
}{
\sum_{i\in W}|\Delta mid_i|
}
]

Puede ocurrir:

```text
precio todavía cerca del HOD
pero empieza a oscilar muchísimo
sin progreso neto
```

Eso puede representar:

* Distribución.
* Conflicto entre nuevos compradores y vendedores.
* Transición hacia mayor incertidumbre.
* Pérdida del régimen direccional.

Señal:

```text
volatilidad ↑
range ↑
directional efficiency ↓
price progress ↓
```

---

## 5.9 Fracaso de recuperación después de una venta

Durante el frontside:

```text
sell burst
→ recuperación rápida
→ nuevo máximo
```

Cerca del final:

```text
sell burst
→ recuperación lenta
→ lower high
→ nuevo sell burst
```

Variables:

```text
recovery_fraction_after_sell_burst
time_to_recover_drawdown
failed_reclaim_count
lower_high_distance
recovery_volume_quality
```

Esta familia es fundamental porque evita marcar como terminal el primer pullback.

El cambio no sería:

```text
rompe soporte
→ terminó
```

Sino:

```text
rompe soporte
+
no recupera con actividad válida
+
forma lower high
+
sell pressure reaparece
→ terminación mucho más probable
```

---

## 5.10 Eventos exógenos

La microestructura no es la única causa posible.

También pueden terminar el frontside:

```text
offering
ATM
warrants
SEC filing
nueva noticia
aclaración del catalizador
halt/resumption
cambio regulatorio
```

Estos eventos entrarían mediante:

```text
news_catalyst_context
fundamental_context
halt_context
```

No sustituirían el detector microestructural, pero podrían elevar drásticamente el riesgo.

---

# 6. La señal no debería ser binaria

No produciría inicialmente:

```text
frontside_ended = true/false
```

Produciría varias probabilidades:

```text
p_new_high_next_15s
p_new_high_next_60s
p_drawdown_5_before_new_high
p_drawdown_10_before_new_high
p_frontside_survival_30s
p_frontside_survival_120s
p_backside_confirmation_next_60s
```

La formulación más limpia sería un modelo de riesgo o *hazard*:

[
h_t(H,D,U)
==========

P(
\text{drawdown }D
\text{ antes de un nuevo máximo }U
\text{ durante }H
\mid S_{\le t}
)
]

Por ejemplo:

[
P(
-10%
\text{ antes de }+3%
\text{ en los próximos 60 s}
\mid MarketState_{\le t}
)
]

Esto es mucho mejor que preguntar:

> “¿Es este exactamente el top?”

También podemos plantearlo como **competing risks**:

```text
Riesgo A: nuevo máximo
Riesgo B: drawdown terminal
Riesgo C: halt
Riesgo D: pérdida de liquidez
Riesgo E: fin de sesión
```

---

# 7. Qué outputs debería emitir el detector

```text
FRONTSIDE_HEALTHY
FRONTSIDE_STRESSED
TERMINATION_WARNING
TERMINATION_RISK_HIGH
TERMINATION_DETECTED
BACKSIDE_CONFIRMED
```

Ejemplo:

```yaml
instrument_id: ABCD
decision_timestamp: 10:01:19.250

frontside_state: TERMINATION_RISK_HIGH
termination_probability_30s: 0.71
backside_probability_60s: 0.58

evidence:
  buy_response_decay: 0.82
  sell_impact_asymmetry: 2.7
  bid_resilience: 0.21
  high_acceptance_ratio: 0.08
  flow_regime_change_probability: 0.76
  participation_renewal_ratio: 0.34
```

Eso permite decisiones diferentes sin contaminar el estado.

---

# 8. Tres usos distintos: no son la misma estrategia

## Política 1: gestión del largo

```text
TERMINATION_WARNING
→ reducir tamaño

TERMINATION_RISK_HIGH
→ cerrar parte o ajustar stop

TERMINATION_DETECTED
→ cerrar largo
```

Su objetivo es evitar el *giveback*.

## Política 2: veto de nuevas entradas largas

```text
frontside_state >= TERMINATION_RISK_HIGH
→ no permitir nuevas entradas de continuación
```

Esta podría aportar valor incluso si el detector no acierta con precisión el máximo.

## Política 3: entrada short backside

No debería activar el short exactamente con la misma señal que cierra el largo.

```text
TERMINATION_RISK_HIGH
→ salir largo

TERMINATION_DETECTED
+
failed reclaim
+
liquidez suficiente
+
borrow disponible
→ candidato short

BACKSIDE_CONFIRMED
→ estrategia short confirmada
```

El largo y el short tienen costes y asimetrías diferentes:

* Disponibilidad y coste de borrow.
* Riesgo de nuevos halts.
* Squeezes.
* Partial fills.
* Volatilidad.
* Reanudación inesperada del frontside.

Por eso compartirían el mismo `Frontside State Tracker`, pero serían **estrategias y P&L separados**.

---

# 9. Cómo encaja en Market State y Event State

No introduciría una columna canónica llamada:

```text
frontside_is_over
```

dentro de Market State.

## Market State conservaría observaciones

```text
trading_activity:
    trade_rate
    dollar_volume_rate
    burst_decay
    participation_breadth

liquidity:
    spread
    bid_depth
    ask_depth
    bid_resilience
    ask_replenishment

order_flow_pressure:
    OFI
    aggressor_buy_ratio
    signed_dollar_imbalance

price_movement:
    velocity
    acceleration
    directional_efficiency
    buy_response
    sell_response

market_microstructure_state:
    impact_asymmetry
    high_acceptance
    quote_to_trade_conversion

price_location:
    distance_to_hod
    distance_to_activation_vwap
    drawdown_from_hod
```

## Event State contextualizaría respecto al wake-up

```text
event_type = wake_up_event
time_from_wake_up
time_from_first_impulse
frontside_phase
number_of_bursts
number_of_halts
current_drawdown_from_event_hod
```

Y más adelante podría existir un evento candidato:

```text
event_type:
market_microstructure:frontside_termination_detected
```

Pero debe distinguir:

```text
termination_event_timestamp
termination_detected_at
state_available_at
```

La arquitectura multirresolución y las extensiones microestructurales pesadas por evento o ventana ya están previstas en vuestro diseño, sin necesidad de convertir Market State en una megatabla universal.

Actualmente ese nuevo Event Type sería sólo un candidato científico, no un evento institucionalmente admitido.

---

# 10. Cómo definir el outcome sin engañarnos

Necesitamos etiquetar retrospectivamente el final para poder investigar, pero sin utilizar esa etiqueta como input.

Una definición candidata:

```text
frontside_peak =
último máximo antes de un drawdown D
que no recupera ese máximo
antes de H segundos/minutos
```

Ejemplo:

```text
D = 10%
H = 15 minutos
```

Pero no congelaría directamente esos valores.

Crearía varias definiciones:

```text
D = 5%, 10%, 15%, 20%
H = 30s, 60s, 5m, 15m, fin de sesión
recovery_tolerance = 0%, 2%, 5%
```

Después buscaríamos señales que sean estables frente a varias definiciones.

También diferenciaría:

```text
local_frontside_failure
session_frontside_termination
full_backside_transition
complete_reversion_to_prior_close
```

Porque no son el mismo outcome.

---

# 11. Cómo evitar que el modelo aprenda simplemente “ha subido mucho”

El modelo podría descubrir una regla trivial:

```text
cuanto mayor es la extensión,
más probable es que revierta
```

Eso puede ser cierto y útil, pero no demostraría que la microestructura anticipa el momento.

El benchmark obligatorio sería:

```text
BASELINE 1
sólo extensión desde prior close

BASELINE 2
extensión + tiempo de sesión

BASELINE 3
extensión + volumen acumulado

BASELINE 4
precio y OHLCV subminuto
```

Después:

```text
MODEL MICROSTRUCTURE
baseline
+
order flow
+
liquidity
+
resilience
+
impact asymmetry
+
acceptance
```

La pregunta científica sería:

> ¿La microestructura aporta información incremental sobre el momento de terminación una vez que ya conocemos extensión, hora, gap y volumen?

Si no mejora al baseline, no hemos descubierto microestructura predictiva; sólo hemos redescubierto que los movimientos extendidos revierten.

---

# 12. Métricas para evaluar el detector

No empezaría por P&L.

## Calidad del evento

```text
median_detection_delay
median_lead_time_before_large_drawdown
false_termination_rate
recovery_after_warning_rate
missed_termination_rate
new_high_after_warning_rate
```

## Utilidad para el largo

```text
giveback avoided
upside sacrificed
percentage of true tops exited within X%
average distance from HOD at exit
```

## Utilidad para short

```text
MAE after short signal
MFE after short signal
time to drawdown
borrow-adjusted expectancy
halt-adjusted risk
fill probability
```

La métrica especialmente importante sería:

[
GivebackAvoided
---------------

UpsideSacrificed
]

Un detector que sale siempre tras +50% puede evitar muchos drawdowns, pero también abandonar prematuramente SGN y otros grandes runners.

---

# 13. Qué empezar a construir

Propondría cuatro componentes:

```text
TSIS_FRONTSIDE_PHASE_TRACKER_V0_1
```

Mantiene:

```text
impulse
pullback
reacceleration
stress
recovery
termination risk
backside
```

```text
TSIS_FRONTSIDE_TERMINATION_HAZARD_V0_1
```

Estima:

```text
probabilidad de drawdown
probabilidad de nuevo HOD
probabilidad de supervivencia del frontside
```

```text
TSIS_LONG_GIVEBACK_CONTROL_POLICY_V0_1
```

Decide:

```text
mantener
reducir
salir
```

```text
TSIS_BACKSIDE_ENTRY_POLICY_V0_1
```

Decide separadamente:

```text
no short
watch short
short eligible
```

---

# Conclusión

**Sí, hay una posibilidad real de detectar el final del frontside**, pero no como una vela mágica, un soporte roto o una figura chartista aislada.

La hipótesis fuerte sería:

> El final del frontside aparece cuando el flujo comprador pierde capacidad de producir avance, la liquidez del bid deja de recuperarse, la oferta empieza a absorber, el impacto se vuelve asimétrico a favor de las ventas, los nuevos máximos dejan de ser aceptados y el régimen de order flow cambia de persistencia compradora a neutral o vendedora.

En forma compacta:

[
\text{Buy effort} \uparrow
\quad
\text{Price progress} \downarrow
]

[
\text{Bid resilience} \downarrow
\quad
\text{Ask absorption} \uparrow
]

[
\text{Sell impact} \uparrow
\quad
\text{High acceptance} \downarrow
]

[
\Rightarrow
P(\text{frontside termination}) \uparrow
]

La misma arquitectura que detecta el despertar puede detectar el final:

```text
DORMANT
→ actividad aparece
→ participación se organiza
→ frontside se sostiene
→ participación pierde eficacia
→ liquidez cambia
→ frontside termina
→ backside se confirma
```

No serían dos problemas independientes. Serían **los dos extremos de una misma máquina de estados microestructural**.

[1]: https://aaltodoc.aalto.fi/items/5b3e64f3-8b86-4808-b9ea-1e47fd21aa24?utm_source=chatgpt.com "Intraday price reversals after extreme run-ups in U.S. ..."
[2]: https://arxiv.org/abs/1011.6402 "[1011.6402] The Price Impact of Order Book Events"
[3]: https://arxiv.org/abs/2307.02375 "[2307.02375] Online Learning of Order Flow and Market Impact with Bayesian Change-Point Detection Methods"
[4]: https://arxiv.org/abs/1901.05332 "Slow decay of impact in equity markets: insights from the ANcerno database"
