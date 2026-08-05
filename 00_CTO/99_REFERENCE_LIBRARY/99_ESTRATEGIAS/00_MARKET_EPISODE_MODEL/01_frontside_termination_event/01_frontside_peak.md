Sí. **Con los datos de TSIS podemos modelar una parte muy importante de ese proceso**, incluida la transición desde un frontside sano hasta un riesgo elevado de terminación. Pero debemos distinguir entre:

1. Lo que podemos observar directamente.
2. Lo que sólo podemos representar mediante proxies.
3. Lo que no podemos saber con nuestros datos.

Y una precisión importante:

> Las variables que propuse en los puntos 5.x son hipótesis de ingeniería de características de nivel profesional, respaldadas parcialmente por la literatura de microestructura. Pero todavía no constituyen un modelo excelente hasta que estén definidas físicamente, validadas temporalmente y demuestren información incremental en microcaps.

La sofisticación matemática ayuda. La excelencia científica procede de que el modelo no se engañe.

---

# 1. Overhead, resistencias e historial del ticker deben incorporarse

Tienes razón: la lista anterior estaba incompleta.

Además del catalizador, float, dilución, extensión, liquidez, halts, actividad y duración del frontside, debemos representar:

```text
Overhead histórico
Resistencias estructurales
Zonas de volumen previas
Niveles de antiguas diluciones u offerings
Comportamiento histórico del ticker
Propensión histórica a revertir gaps
Respuesta histórica ante tipos equivalentes de catalizador
```

No los trataría como líneas visuales arbitrarias. Los convertiría en información cuantificable.

## Overhead como masa de oferta potencial

Cuando un ticker negoció anteriormente mucho volumen en una zona superior al precio actual, puede haber participantes atrapados esperando recuperar su precio de entrada.

No sabemos cuántos continúan manteniendo sus acciones. Por eso no lo llamaría “oferta real”, sino:

```text
historical_overhead_supply_proxy
```

Una representación posible:

[
OverheadDensity_t(q)=
\frac{
\sum_{s<t}
DollarVolume_s,
\mathbf{1}
\left(
P_s\in[P_t,P_t(1+q)]
\right)
w(age_s)
}{
FloatDollarValue_t+\varepsilon
}
]

Donde:

* (q) puede ser 5%, 10%, 20%.
* `w(age)` reduce el peso de operaciones antiguas.
* Los precios históricos deben estar correctamente normalizados por splits.
* Sólo utilizamos datos anteriores a `t`.

Variables candidatas:

```text
overhead_dollar_volume_5pct
overhead_dollar_volume_10pct
overhead_float_turnover_10pct
distance_to_nearest_high_volume_node
distance_to_nearest_unretested_gap_high
age_of_nearest_overhead_zone
number_of_prior_rejections_in_next_10pct
```

Con trades históricos podemos construir volumen por precio con bastante precisión. Con barras de un minuto sería sólo una aproximación.

## Overhead no visitado

Podemos dar más importancia a zonas que:

1. Se formaron con gran volumen.
2. Quedaron por encima del precio.
3. No fueron revisitadas posteriormente.
4. Coinciden con un antiguo gap, offering o máximo significativo.

Por ejemplo:

```text
unretested_overhead_mass_10pct
```

Eso expresa mejor la intuición discrecional:

> “Aquí arriba todavía debe quedar mucha gente atrapada.”

No sabemos si realmente sigue atrapada. Pero preservamos la evidencia observable que hace plausible esa presión.

---

# 2. Clusters de resistencias, no una única resistencia

Una línea individual puede tener poco valor. Varias referencias próximas pueden formar una zona más relevante:

```text
antiguo HOD
+
máximo de un gap anterior
+
nodo de volumen
+
precio de offering
+
número redondo
+
máximo de 52 semanas
```

Podemos construir:

[
ResistanceCluster_t =
\sum_j
w_j
K
\left(
\frac{L_j-P_t}{\sigma_t}
\right)
]

Donde:

* (L_j) es cada nivel histórico.
* (w_j) depende de su naturaleza, volumen, antigüedad y número de rechazos.
* (K) permite que dos niveles próximos formen una zona.
* (\sigma_t) adapta la distancia a la volatilidad actual.

Variables:

```text
resistance_cluster_score_5pct
resistance_cluster_score_10pct
number_of_reference_levels_5pct
distance_to_strongest_cluster
historical_rejection_count_at_cluster
historical_break_acceptance_rate_at_cluster
```

Esto encajaría dentro de los objetos ya existentes:

```text
price_location
price_movement
trading_activity
```

No necesitamos crear un nuevo Information Object llamado `Overhead`. El documento de TSIS establece precisamente que el objeto semántico permanece estable mientras pueden evolucionar sus modelos de representación y variables físicas. 

---

# 3. El “carácter histórico” del ticker también puede modelarse

Tu ejemplo es muy bueno:

```text
El ticker ha tenido cinco gaps.
Los cinco revirtieron completamente.
```

Eso es información relevante, pero hay que evitar concluir:

```text
probabilidad de reversión = 100%
```

Cinco observaciones son muy pocas.

## Representación bayesiana del historial

Podemos modelar la propensión de reversión del ticker:

[
p_i \sim Beta(\alpha_g,\beta_g)
]

[
y_{ij}\sim Bernoulli(p_i)
]

Donde:

* (i) identifica el ticker.
* (j) identifica cada episodio histórico.
* (g) es su grupo comparable: market cap, precio, float, sector, tipo de catalizador.
* (y=1) significa reversión completa.

Si el ticker tiene 5 de 5 reversiones, su estimación se combina con la distribución de tickers semejantes. Esto se llama *shrinkage*: evita tratar una muestra minúscula como certeza absoluta.

Guardaríamos:

```text
ticker_gap_full_reversion_posterior_mean
ticker_gap_full_reversion_posterior_uncertainty
ticker_median_time_to_frontside_peak
ticker_median_frontside_duration
ticker_median_drawdown_after_peak
ticker_new_hod_after_first_failure_rate
ticker_same_catalyst_reversion_probability
ticker_historical_halt_count_per_episode
```

El modelo no recibe simplemente:

```text
5 de 5 = 100%
```

Recibe:

```text
probabilidad posterior
+
incertidumbre de esa estimación
+
número de episodios
```

Eso es bastante más sólido.

## Lo que no podemos afirmar

No podemos concluir directamente:

> “Los owners venden cada vez que sube.”

Eso es una posible explicación económica, pero no es una observación.

Podemos observar:

* Ofertas históricas.
* Registros S-1/S-3.
* 424B5.
* ATMs conocidos.
* Warrants.
* Convertibles.
* Aumentos de acciones en circulación.
* Form 4 o transacciones publicadas.
* Reversión repetida tras gaps.

Pero una venta contemporánea de accionistas o del emisor puede no conocerse en tiempo real. Por tanto, construiría:

```text
historical_issuer_supply_behavior
```

no:

```text
owners_are_selling_now
```

---

# 4. Eventos exógenos en tiempo real

Esta capa es crucial porque puede cambiar instantáneamente el hazard de terminación.

## Eventos candidatos

```text
offering anunciado
ATM activado o actualizado
warrant exercise
S-1/S-3 effectiveness
424B5
8-K material
nueva nota de prensa
aclaración o desmentido del catalizador
halt por news pending
halt por actividad extraordinaria
reanudación de cotización
riesgo de incumplimiento o delisting
```

El registro del evento debe contener:

```text
source_timestamp
received_at
available_at
event_type
event_subtype
source
materiality
dilution_direction
novelty
confidence
instrument_mapping_quality
```

No basta con guardar la hora escrita dentro del documento. Necesitamos saber cuándo llegó realmente al sistema.

La SEC indica que sus APIs de EDGAR se actualizan en tiempo real a medida que se difunden los filings, con un retraso habitual inferior a un segundo para la API de submissions. Nasdaq ofrece información de halts y pausas mediante sus páginas y un RSS específico. Eso hace técnicamente posible una capa rápida de filings y halts, aunque para noticias corporativas de muy baja latencia normalmente necesitaríamos un proveedor dedicado. ([SEC][1])

Un evento de dilución podría actuar así:

[
\lambda_{\text{termination},t}^{new}
====================================

\lambda_{\text{termination},t}^{base}
\times
EventRiskMultiplier_t
]

Pero no necesariamente debería ordenar una venta automática. Puede:

```text
elevar riesgo
vetar una entrada larga
reducir tamaño
exigir confirmación adicional
```

---

# 5. Qué podemos modelar con los datos de TSIS

## Bastante bien modelable

| Fenómeno                        | Datos                      |
| ------------------------------- | -------------------------- |
| Tape speed e interarrival times | Trades                     |
| Volumen y dollar volume         | Trades                     |
| Signed order flow aproximado    | Trades + quotes            |
| Spread y evolución del NBBO     | Quotes                     |
| Top-of-book imbalance           | Bid/ask size               |
| OFI de mejor bid/ask            | Quote updates              |
| Resiliencia del bid             | Quotes + trades            |
| Absorción aproximada del ask    | Quotes + trades            |
| Impacto comprador/vendedor      | Trades + midprice          |
| Aceptación de nuevos máximos    | Trades + quotes            |
| Volumen por precio histórico    | Trades                     |
| Overhead y resistencias         | Trades + OHLCV + reference |
| Comportamiento histórico        | Episodios anteriores       |
| News, filings y halts           | News + SEC + halts         |
| Contexto de float/dilución      | Fundamentals + filings     |

La relación entre order-flow imbalance y cambios cortos de precio está bien documentada en datos de acciones estadounidenses. También existe evidencia de que el desequilibrio entre las colas del mejor bid y ask contiene información sobre el siguiente movimiento del midprice. Estos resultados proceden principalmente de acciones líquidas; son fundamento metodológico, no prueba de que el mismo edge sobreviva automáticamente en microcaps. ([arXiv][2])

## Modelable mediante proxies

```text
absorción real
liquidez oculta
reposición de órdenes
participación institucional
metaórdenes
amplitud de participantes
```

Por ejemplo, podemos inferir absorción cuando:

```text
mucho volumen comprador se ejecuta
+
el ask reaparece
+
el precio no progresa
```

Pero sin datos order-by-order no sabemos si:

* Es la misma orden.
* Son distintos participantes.
* Es un iceberg.
* Se canceló y sustituyó.
* Se desplazó liquidez entre venues.

## No modelable directamente con top-of-book

Salvo que vuestros contratos de quotes contengan profundidad multinivel y mensajes de órdenes:

```text
posición exacta en la cola
libro completo
cancelaciones por orden individual
identidad del participante
icebergs verdaderos
quién está vendiendo
metaórdenes reales
```

Éste es un punto crítico.

Con NBBO, trades y tamaños del mejor bid/ask podemos crear un modelo microestructural valioso. Pero no debemos llamarlo “modelo completo del order book”.

---

# 6. Cómo lo modelaría profesionalmente

No puedo saber qué fórmulas exactas emplea un hedge fund concreto. El alpha es propietario. Lo que sí puede reconstruirse a partir de la literatura y de arquitecturas cuantitativas serias es el tipo de sistema.

No sería un único Random Forest que dice:

```text
TOP / NO TOP
```

Sería una arquitectura jerárquica.

## Estado observable

En cada instante:

[
x_t=
[
C_i,,
H_i,,
O_t,,
E_t,,
M_t,,
P_t
]
]

Donde:

```text
C_i = contexto estructural
      float, market cap, dilución, precio

H_i = comportamiento histórico
      gaps, reversiones, halts, duración típica

O_t = overhead y estructura de precio
      resistencias, volumen por precio, niveles

E_t = eventos exógenos
      news, filings, halts

M_t = microestructura
      OFI, spread, resiliencia, absorción, impacto

P_t = trayectoria del episodio
      extensión, burst, pullback, HOD, tiempo
```

Esto se alinea perfectamente con TSIS: `Market State` conserva el estado observable; `Event State` añade posición temporal y contexto respecto al episodio, sin inventar un segundo mercado. Además, la arquitectura admite representaciones multirresolución y extensiones microestructurales materializadas sólo para las ventanas necesarias. 

## Estado latente del frontside

El estado que realmente queremos conocer no es observable directamente:

[
z_t \in
{
HEALTHY,
STRESSED,
WARNING,
RISK_HIGH,
TERMINATED,
BACKSIDE
}
]

Estimamos:

[
P(z_t\mid x_{\leq t})
]

Y las transiciones:

[
P(z_t\mid z_{t-1},x_t,\Delta t)
]

Esto puede implementarse inicialmente mediante:

* Máquina de estados probabilística.
* HMM.
* HSMM para representar explícitamente la duración de cada fase.
* Filtro bayesiano.
* Gradient boosting sobre secuencias resumidas.

No empezaría por una red neuronal.

---

# 7. Change-point detection

El cambio de:

```text
flujo comprador persistente
```

a:

```text
flujo neutral, absorbido o vendedor
```

encaja de forma natural con detección online de cambios.

Podemos observar una secuencia:

[
y_t=
[
OFI_t,
BuyResponse_t,
SellImpact_t,
BidResilience_t,
Acceptance_t
]
]

Y estimar:

[
P(\text{change point at }t\mid y_{\leq t})
]

La investigación con datos Nasdaq ha utilizado Bayesian Online Change-Point Detection para identificar cambios de régimen del order flow en tiempo real, encontrando que incorporar esa información mejora las predicciones online de flujo e impacto frente a modelos que ignoran los regímenes. ([arXiv][3])

Para TSIS, el cambio relevante podría ser:

```text
REGIME 1
compras persistentes con impacto positivo

REGIME 2
compras persistentes sin impacto

REGIME 3
flujo neutral con volatilidad alta

REGIME 4
ventas con impacto creciente
```

La transición 1 → 2 puede generar:

```text
FRONTSIDE_STRESSED
```

La transición 2/3 → 4 puede generar:

```text
TERMINATION_RISK_HIGH
```

---

# 8. El modelo central debería ser de supervivencia y riesgos competitivos

Ésta sería, en mi opinión, la formulación matemática más adecuada.

No preguntamos:

> “¿Éste es el máximo?”

Preguntamos:

> “¿Qué eventos pueden ocurrir a partir de este estado y cuánto falta para cada uno?”

## Riesgos

```text
K1 = nuevo HOD
K2 = drawdown terminal
K3 = pérdida de liquidez ejecutable
K4 = halt
K5 = fin de sesión sin resolución
```

Para cada riesgo:

[
\lambda_k(t\mid x_{\leq t})
===========================

P(
T=t,,
K=k
\mid
T\geq t,,
x_{\leq t}
)
]

El output puede ser:

```text
P(nuevo HOD antes de 30s)
P(drawdown 10% antes de nuevo HOD)
P(drawdown 20% durante 60s)
P(halt antes de poder salir)
P(frontside superviviente 5m)
```

Los modelos de supervivencia con riesgos competitivos están diseñados precisamente para estimar tiempo y tipo de evento cuando existen varios desenlaces posibles; DeepHit es un ejemplo de arquitectura que aprende conjuntamente la distribución del tiempo y la causa del evento. No propongo comenzar con DeepHit, sino utilizar esa formulación como referencia matemática. ([AAAI][4])

## Combinación elegante

[
P(K=k\mid x_{\leq t})
=====================

\sum_z
P(K=k\mid z_t=z,x_t)
P(z_t=z\mid x_{\leq t})
]

Es decir:

1. Estimamos la fase latente del frontside.
2. Estimamos el riesgo condicionado a esa fase.
3. La política decide mantener, reducir, salir o preparar short.

Esto es mucho más sólido que intentar encontrar una vela terminal universal.

---

# 9. ¿Son los puntos 5.x matemáticamente excelentes?

Son un punto de partida **muy bueno**, pero debemos distinguir:

## Respaldados directamente por microestructura

```text
order-flow imbalance
queue imbalance
spread
depth
trade intensity
impacto respecto a profundidad
persistencia del order flow
```

## Ingenierías plausibles que debemos demostrar en microcaps

```text
bid resilience
ask absorption
buy effort per price progress
sell/buy impact asymmetry
high acceptance
burst renewal
participation decay
failed recovery
```

Estas últimas no son ocurrencias arbitrarias. Son traducciones cuantitativas de fenómenos microestructurales razonables. Pero la fórmula exacta, horizonte y normalización son nuestras hipótesis.

La literatura sobre DeepLOB demuestra que modelos CNN-LSTM pueden extraer relaciones espaciales y temporales de secuencias completas del limit order book. Sin embargo, esa arquitectura requiere datos LOB suficientemente profundos y homogéneos; si TSIS dispone sólo del mejor bid y ask, no debemos simular que tenemos la misma representación. ([arXiv][5])

El orden profesional para TSIS sería:

```text
1. Features interpretable
2. Modelos estadísticos simples
3. Gradient boosting / survival forests
4. Modelos de régimen
5. Secuencias profundas sólo si aportan valor OOS
```

Un modelo matemáticamente complicado que no mejora a una regresión logística fuera de muestra no es excelente. Es decoración.

---

# 10. El caso extremo: +70% y después −90% dentro de un minuto

Sí, el enfoque puede modelarlo, pero **no desde la vela de un minuto**.

Una barra OHLCV no revela:

* Si primero ocurrió el máximo o el mínimo.
* Cuántos halts hubo.
* Qué spread existía.
* Si era posible entrar o salir.
* Qué volumen había en el bid.
* Si el movimiento fue un trade aislado.
* Cuánto tardó en colapsar.
* Qué señales aparecieron antes del máximo.

Necesitamos replay de trades y quotes.

## Relojes necesarios

```text
Tiempo cronológico:
100 ms, 250 ms, 1 s, 3 s, 5 s

Tiempo de eventos:
últimos 10, 25, 50, 100 trades

Tiempo económico:
últimos $10k, $25k, $100k negociados
```

En un ticker que hace +70% y −90%, cinco segundos pueden ser demasiado lentos. Una ventana de los últimos 25 trades puede tener más sentido que una vela fija.

## Outcomes de primera pasada

En vez de una única etiqueta, guardaría:

[
MFE_t(H)=
\max_{0<u\leq H}
\frac{P_{t+u}-P_t}{P_t}
]

[
MAE_t(H)=
\min_{0<u\leq H}
\frac{P_{t+u}-P_t}{P_t}
]

[
\tau_D(t)=
\inf
{
u>0:
Bid_{t+u}\leq HOD_t(1-D)
}
]

[
\tau_U(t)=
\inf
{
u>0:
Mid_{t+u}>HOD_t
}
]

Esto conserva:

```text
cuánto subió
cuánto cayó
qué ocurrió primero
cuánto tardó
si era ejecutable
```

Para construir estados utilizaríamos midprice o referencias gobernadas. Para resultados de una política larga utilizaríamos el bid ejecutable posterior a la decisión, no el máximo o mínimo teórico.

Los halts deben aparecer como evento competitivo, no como tiempo continuo imaginario.

---

# 11. Cómo definir `frontside_peak` sin sobreoptimizar D y H

La definición:

```text
último máximo antes de un drawdown D
que no recupera el máximo antes de H
```

es correcta para etiquetar retrospectivamente, pero sería peligroso hacer esto:

```text
Pruebo 500 combinaciones D/H
↓
elijo la que produce mejor Sharpe
↓
digo que ésa es la definición científica del frontside
```

## D y H no deben elegirse por P&L

Primero deben tener significado económico.

### Familia D

```text
5%  = deterioro temprano
10% = drawdown operativo relevante
15% = fallo fuerte
20% = transición severa
```

También podemos tener versiones normalizadas:

```text
D / spread
D / microvolatilidad
D / rango del impulso
```

### Familia H

```text
15s  = riesgo inmediato
30s  = microestructura
60s  = continuación rápida
5m   = estructura intradía
15m  = supervivencia del episodio
fin de sesión = reversión completa
```

El objetivo no es descubrir “el D/H verdadero”. No existe necesariamente uno.

Construimos una **familia de outcomes**.

---

# 12. Usar toda la superficie D × H

En lugar de seleccionar una celda:

```text
D = 10%
H = 60s
```

el modelo produce una superficie:

|        | 15 s | 30 s | 60 s | 5 m | 15 m |
| ------ | ---: | ---: | ---: | --: | ---: |
| DD 5%  |    P |    P |    P |   P |    P |
| DD 10% |    P |    P |    P |   P |    P |
| DD 15% |    P |    P |    P |   P |    P |
| DD 20% |    P |    P |    P |   P |    P |

Y debe respetar coherencia:

[
P(DD\geq20%\text{ en }H)
\leq
P(DD\geq10%\text{ en }H)
]

[
P(DD\geq10%\text{ en }30s)
\leq
P(DD\geq10%\text{ en }5m)
]

Así no “optimizamos la definición”. Modelamos toda la distribución del riesgo.

## Qué significa estabilidad frente a definiciones

Una feature sería especialmente convincente si:

```text
buy_response_decay
```

mejora la predicción de:

```text
DD 5% en 30s
DD 10% en 60s
DD 15% en 5m
DD 20% en 15m
```

No necesariamente con idéntica intensidad, pero sí de manera coherente.

Sería sospechoso que sólo funcionase para:

```text
D = 13%
H = 47 segundos
```

La robustez debe aparecer como una región continua, no como una celda aislada.

---

# 13. Protocolo para no sobreoptimizar

## Paso 1 — Congelar la ontología de outcomes

Antes de mirar el rendimiento de las estrategias:

```text
OutcomeDefinitionFamily v0.1
D = {5,10,15,20}
H = {15s,30s,60s,5m,15m,session}
recovery_tolerance = {0,2,5}
```

## Paso 2 — Mantener todos los outcomes

No eliminar los que dan peores resultados.

## Paso 3 — Separar episodios completos

El mismo frontside no puede aparecer parcialmente en entrenamiento y test.

La unidad de separación debe ser:

```text
ticker + session + frontside_episode
```

No filas individuales.

## Paso 4 — Purge y embargo

Si las ventanas futuras de dos observaciones se solapan, no pueden contaminar train y test.

## Paso 5 — Outer test intocable

El test final no participa en:

* Selección de D/H.
* Selección de features.
* Selección de modelo.
* Selección del umbral de política.

## Paso 6 — Registrar todos los intentos

Cada variante de:

```text
feature
modelo
label
ventana
policy
```

debe entrar en un trial ledger.

La literatura sobre backtest overfitting muestra que seleccionar la mejor estrategia entre muchas variantes puede producir resultados extraordinarios dentro de muestra y débiles fuera de ella. PBO intenta cuantificar ese riesgo y DSR corrige la inflación del Sharpe debida a selección múltiple y distribuciones no normales. ([SSRN][6])

---

# 14. ¿Estoy hablando de ML o de backtest clásico?

De ambos, pero en fases distintas.

## La definición del outcome no es ML ni estrategia

Es una pieza del:

```text
Outcome Engine
```

Produce hechos retrospectivos:

```text
MFE
MAE
time_to_new_high
time_to_drawdown
frontside_peak research label
full_reversion
```

Esos outcomes son `research_only` u `outcome_adjacent`. No pueden entrar como features predictivas. Esta separación coincide con la arquitectura TSIS: Event State puede contener estados posteriores para investigación, pero su legalidad de consumo debe impedir que lleguen a una decisión anterior. 

## Backtest clásico

Podemos comenzar con reglas interpretables:

```text
buy_response_decay > percentil 90
AND
bid_resilience < percentil 20
AND
sell_impact_asymmetry > 2
AND
high_acceptance < 10%
```

Y medir:

```text
nuevo HOD
drawdown
giveback evitado
upside sacrificado
```

Esto permite comprobar si la hipótesis económica existe sin esconderla dentro de un modelo complejo.

## Machine Learning

Después:

```text
logistic regression
gradient boosting
random forest
survival forest
discrete-time hazard model
HMM / HSMM
BOCPD
```

El ML no inventa el estado. Consume la secuencia de Market States y estima probabilidades.

## Deep Learning

Sólo más tarde:

```text
TCN
LSTM
Transformer
DeepHit-like competing risks
LOB model
```

Siempre comparados contra los baselines simples.

## Finalmente, backtest de política

La predicción no es el P&L.

```text
Market State
↓
Frontside model
↓
probabilidades
↓
long management policy
↓
execution model
↓
fills
↓
ledger
```

Y separadamente:

```text
probabilidades
↓
backside short policy
↓
borrow + execution + halts
↓
PnL short
```

---

# 15. Arquitectura concreta para TSIS

```text
MARKET_STATE_PRICE_STRUCTURE_EXTENSION_V0_1
```

Contendría:

```text
overhead density
unretested volume zones
resistance clusters
distance to offering levels
prior rejection history
```

```text
MARKET_STATE_TICKER_BEHAVIOR_EXTENSION_V0_1
```

Contendría:

```text
reversion posterior
incertidumbre
historical frontside duration
historical drawdown distribution
catalyst-conditioned behavior
```

```text
MARKET_STATE_MICROSTRUCTURE_EXTENSION_V0_1
```

Contendría:

```text
OFI
buy response
sell response
impact asymmetry
bid resilience
ask absorption proxy
high acceptance
burst renewal
```

```text
MARKET_STATE_EVENT_RISK_EXTENSION_V0_1
```

Contendría eventos ya conocidos y legalmente disponibles:

```text
filings
news
halts
dilution events
```

Después:

```text
FRONTSIDE_PHASE_FILTER_V0_1
```

Estimaría:

```text
HEALTHY
STRESSED
WARNING
RISK_HIGH
TERMINATED
BACKSIDE
```

Y:

```text
FRONTSIDE_COMPETING_RISK_MODEL_V0_1
```

Produciría:

```text
new-high probabilities
drawdown surface
survival curves
halt probability
liquidity-failure probability
```

Finalmente las tres políticas:

```text
LONG_GIVEBACK_CONTROL_POLICY
LONG_ENTRY_VETO_POLICY
BACKSIDE_ENTRY_POLICY
```

Dado el estado institucional reflejado en vuestro documento, estas piezas deben considerarse candidatos científicos: el Event Type de terminación todavía tendría que pasar por admisión y el consumo de State Replay continúa sujeto a sus gates y manifests autorizados. 

---

# Mi conclusión

Sí: **con los datos que tenéis, más una ingeniería de características rigurosa, se puede construir un modelo profesional de terminación del frontside**.

Pero no podremos observar perfectamente:

```text
la intención real
la identidad del comprador
la identidad del vendedor
los owners vendiendo ahora
los icebergs reales
la cola completa
```

Podremos observar su huella:

```text
mucho esfuerzo comprador
pero poco progreso

oferta que se repone
bid que pierde resiliencia

ventas con impacto creciente
nuevos máximos sin aceptación

overhead próximo
historial de reversiones

evento dilutivo o halt
```

Y modelarlo como:

[
\text{estado latente}
+
\text{cambio de régimen}
+
\text{riesgos competitivos}
+
\text{políticas separadas}
]

El resultado más valioso quizá no sea localizar el máximo exacto. Puede ser algo más operable:

> Detectar diez o veinte segundos antes que continuar largo ya no compensa el riesgo; impedir nuevas entradas; reducir el giveback; y esperar una confirmación distinta antes de abrir un short.

Eso sería un edge mucho más realista y defendible que afirmar que hemos aprendido a predecir todos los tops.

[1]: https://www.sec.gov/search-filings/edgar-application-programming-interfaces?utm_source=chatgpt.com "EDGAR Application Programming Interfaces (APIs)"
[2]: https://arxiv.org/abs/1011.6402?utm_source=chatgpt.com "[1011.6402] The Price Impact of Order Book Events"
[3]: https://arxiv.org/abs/2307.02375?utm_source=chatgpt.com "Online Learning of Order Flow and Market Impact with Bayesian Change-Point Detection Methods"
[4]: https://ojs.aaai.org/index.php/AAAI/article/view/11842?utm_source=chatgpt.com "DeepHit: A Deep Learning Approach to Survival Analysis ..."
[5]: https://arxiv.org/abs/1808.03668?utm_source=chatgpt.com "DeepLOB: Deep Convolutional Neural Networks for Limit Order Books"
[6]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253&utm_source=chatgpt.com "The Probability of Backtest Overfitting"
