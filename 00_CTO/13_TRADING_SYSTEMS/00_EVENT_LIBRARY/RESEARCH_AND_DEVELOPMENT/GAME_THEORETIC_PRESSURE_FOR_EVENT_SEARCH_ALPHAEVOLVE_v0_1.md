# Game-Theoretic Pressure For Event Search And AlphaEvolve v0.1

Fecha: 2026-06-22
Estado: research_and_development_note
Scope: `00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/`

Este documento clona la respuesta conceptual inicial sobre como tratar
`Game-theoretic pressure` de forma matematica dentro de Event Library, y anade
referencias bibliograficas para investigacion posterior.

No define estrategia.
No define entradas.
No define stops.
No define targets.
No define sizing.

Su objetivo es preparar definiciones de eventos que puedan ser evolucionadas
por AlphaEvolve sin contaminar la busqueda del evento con PnL o reglas
operativas.

---

Si: tienes razon. En ese documento `Game-theoretic pressure` esta demasiado
narrativo. Si hablamos de teoria de juegos, debe quedar como:

```text
jugadores
acciones
informacion observable
payoffs/incentivos
restricciones
nivel que cambia incentivos
proxies medibles
falsificacion
```

Propongo tres enfoques matematicos.

## 1. Pressure Payoff Model

Modelo local de presion por payoff.

Para cada grupo de participantes `g`:

```text
g = shorts_recientes, longs_tempranos, momentum_buyers, sellers, liquidity_providers
```

Definimos:

```text
side_g = +1 long, -1 short
entry_proxy_g
p_t = precio actual
L_g(t) = perdida latente aproximada
C_g(t) = constraint/riesgo de actuar forzado
```

Ejemplo para shorts:

```text
loss_short(t) = (p_t - entry_proxy_short) / entry_proxy_short
pressure_short(t) = sigmoid((loss_short(t) - threshold_short) / k)
```

Luego:

```text
game_pressure_score(t) =
  short_pressure(t)
  * level_breach_strength(t)
  * volume_acceleration(t)
  / liquidity_proxy(t)
```

Uso para eventos:

```text
push -> dip -> shorts entran proxy -> rebreak -> pressure_score sube
```

AlphaEvolve podria evolucionar:

- como estimar `entry_proxy_short`;
- que nivel importa: HOD, shelf high, PMH, VWAP, prior high;
- umbral de perdida latente;
- formula de `liquidity_proxy`;
- combinacion de volumen, rango y velocidad.

Esto convierte "shorts asustados" en una variable latente medible.

## 2. Sequential Trigger Game

Modelo de juego secuencial por fases.

El evento se modela como estados:

```text
S0: neutral
S1: initial_push
S2: dip_or_pause
S3: defended_level
S4: rebreak
S5: forced_reaction / continuation
S6: failure
```

En cada estado, los grupos tienen acciones posibles:

```text
shorts: add_short | hold | cover
longs: hold | sell | add
momentum: wait | chase
liquidity: provide | withdraw
```

La clave es el cambio de incentivos al romper un nivel:

```text
Delta_U_short(t) =
  U_short_hold(t) - U_short_cover(t)
```

Cuando `Delta_U_short` cae por debajo de cero, cubrir se vuelve mas racional
que mantener.

Proxies:

```text
breach_strength = (close_t - level) / level
time_underwater_short_proxy
failed_dip_breakdown
rebreak_volume_ratio
post_rebreak_speed
```

Probabilidad de reaccion forzada:

```text
P(forced_cover_t) =
  sigmoid(
    b0
    + b1 * breach_strength
    + b2 * failed_breakdown
    + b3 * rebreak_volume_ratio
    + b4 * time_underwater_proxy
    - b5 * liquidity_proxy
  )
```

AlphaEvolve podria evolucionar:

- la maquina de estados;
- que transicion define el evento;
- pesos `b`;
- reglas de invalidacion;
- ventanas temporales por fase.

Esto serviria muy bien para DAS, rebreaks, shelf breaks y failed bear attacks.

## 3. Mean-Field Feedback Game

Modelo agregado de masa/crowd.

Aqui no intentamos identificar a cada trader. Modelamos presion agregada:

```text
price_change(t+1) =
  impact(t) * net_aggressive_flow(t) + noise
```

Donde:

```text
net_aggressive_flow =
  momentum_demand
  + short_covering_pressure
  - profit_taking_pressure
  - seller_absorption
```

Y:

```text
impact(t) = 1 / liquidity_proxy(t)
```

El evento se vuelve peligroso/interesante cuando el feedback se vuelve
reflexivo:

```text
K(t) =
  attention(t)
  * pressure_density(t)
  * impact(t)
```

Lectura:

```text
si K(t) > 1, el movimiento tiende a autoalimentarse
si K(t) < 1, el movimiento tiende a absorberse o fallar
```

Proxies:

```text
attention = RVOL, PM volume, gap, news flag
pressure_density = participantes atrapados proxy
impact = rango por unidad de volumen, spread, candle body efficiency
seller_absorption = dips rechazados, lows no rotos, closes fuertes
```

AlphaEvolve podria evolucionar:

- definicion de `K(t)`;
- que proxies entran;
- pesos;
- umbrales;
- penalizacion por falsos positivos;
- separacion entre eventos parecidos.

Este modelo es util para distinguir:

```text
spike sin masa
vs
squeeze con feedback real
```

## Mi recomendacion

Usaria los tres, en capas:

```text
1. Pressure Payoff Model
   mide presion local de un grupo.

2. Sequential Trigger Game
   mide cambio de incentivos por fases.

3. Mean-Field Feedback Game
   mide si la masa/liquidez crea autoalimentacion.
```

Para AlphaEvolve, no le daria "encuentra DAS" como texto. Le daria una funcion
objetivo:

```text
maximizar:
  coherencia de fases
  separacion frente a ventanas aleatorias
  estabilidad por anos
  calidad visual revisada
  baja tasa de falsos positivos
  claridad del event_start y event_end

sin usar:
  PnL
  entradas
  stops
  targets
  sizing
```

Asi AlphaEvolve evoluciona la definicion del evento, no una estrategia.

---

## Referencias bibliograficas y enlaces de interes

Estas referencias no convierten ninguna hipotesis de TSIS en evidencia
institucional. Sirven como base de investigacion para formalizar mecanismos,
proxies y tests falsables.

### Teoria de juegos, informacion e incentivos

- Kyle, A. S. (1985). "Continuous Auctions and Insider Trading." Econometrica.
  DOI: https://doi.org/10.2307/1913210
  Uso TSIS: base conceptual para order flow, market depth, informacion
  asimetrica y price impact.

- Glosten, L. R., & Milgrom, P. R. (1985). "Bid, Ask and Transaction Prices in
  a Specialist Market with Heterogeneously Informed Traders." Journal of
  Financial Economics.
  DOI: https://doi.org/10.1016/0304-405X(85)90044-3
  Uso TSIS: marco para spreads, adverse selection, trade direction y
  microestructura informacional.

- Morris, S., & Shin, H. S. (2003). "Global Games: Theory and Applications."
  En Advances in Economics and Econometrics.
  DOI: https://doi.org/10.1017/CCOL0521806501.003
  Uso TSIS: cambios de coordinacion cuando los participantes observan senales
  publicas imperfectas.

### Feedback, bubbles y presion endogena

- De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990).
  "Positive Feedback Investment Strategies and Destabilizing Rational
  Speculation." Journal of Finance.
  DOI: https://doi.org/10.1111/j.1540-6261.1990.tb03795.x
  Uso TSIS: formalizacion de feedback positivo y persecucion de momentum.

- Abreu, D., & Brunnermeier, M. K. (2003). "Bubbles and Crashes."
  Econometrica.
  DOI: https://doi.org/10.1111/1468-0262.00412
  Uso TSIS: coordinacion temporal, retraso en atacar una burbuja y colapso
  por sincronizacion.

- Brunnermeier, M. K., & Pedersen, L. H. (2005). "Predatory Trading."
  Journal of Finance.
  DOI: https://doi.org/10.1111/j.1540-6261.2005.00781.x
  Uso TSIS: participantes que explotan constraints de otros participantes y
  presion de liquidacion/cobertura.

- Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market Liquidity and Funding
  Liquidity." Review of Financial Studies.
  DOI: https://doi.org/10.1093/rfs/hhn098
  Uso TSIS: liquidez, espirales de liquidez y fragilidad cuando se retira
  absorcion.

### Herding, cascadas y atencion colectiva

- Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). "A Theory of Fads,
  Fashion, Custom, and Cultural Change as Informational Cascades." Journal of
  Political Economy.
  DOI: https://doi.org/10.1086/261849
  Uso TSIS: cascadas informacionales y decisiones secuenciales observables.

- Bikhchandani, S., Hirshleifer, D., Tamuz, O., & Welch, I. (2021).
  "Information Cascades and Social Learning."
  arXiv: https://arxiv.org/abs/2105.11044
  Uso TSIS: revision moderna de cascadas y aprendizaje social.

- Shiller, R. J. (2000). "Measuring Bubble Expectations and Investor
  Confidence." Journal of Psychology and Financial Markets.
  DOI: https://doi.org/10.1207/S15327760JPFM0101_05
  Uso TSIS: expectativas, narrativa y comportamiento de masas en burbujas.

### Limites al arbitraje, shorts y constraints

- Shleifer, A., & Vishny, R. W. (1997). "The Limits of Arbitrage." Journal of
  Finance.
  DOI: https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
  Uso TSIS: por que agentes racionales pueden no corregir precios de inmediato
  cuando tienen constraints.

- Ofek, E., Richardson, M., & Whitelaw, R. F. (2004). "Limited Arbitrage and
  Short Sales Restrictions: Evidence from the Options Markets." Journal of
  Financial Economics.
  DOI: https://doi.org/10.1016/S0304-405X(03)00198-9
  Uso TSIS: restricciones de shorting y limites a la correccion de precios.

- SEC Regulation SHO overview.
  Link: https://www.sec.gov/investor/pubs/regsho.htm
  Uso TSIS: contexto regulatorio para short sales, locate, close-out y
  restricciones que pueden afectar eventos de presion short.

### Microestructura y order flow

- O'Hara, M. (1995). "Market Microstructure Theory." Blackwell.
  Link: https://onlinelibrary.wiley.com/doi/book/10.1002/9780470757719
  Uso TSIS: marco general para bid/ask, dealers, order flow, informacion y
  liquidez.

- Hasbrouck, J. (2007). "Empirical Market Microstructure." Oxford University
  Press.
  Link: https://global.oup.com/academic/product/empirical-market-microstructure-9780195301649
  Uso TSIS: medicion empirica de microestructura, price impact y datos de alta
  frecuencia.

## Research queue futura

Preguntas que deben investigarse antes de promover claims fuertes:

1. Que proxy estima mejor `entry_proxy_short` en datos 1m sin tape completo?
2. Que nivel cambia mas los incentivos: HOD, VWAP, PMH, shelf high o prior high?
3. Como separar short covering de chase de momentum usando solo OHLCV 1m?
4. Que metricas de liquidez pueden aproximarse sin order book completo?
5. Puede `K(t)` separar spikes falsos de feedback loops sostenidos?
6. Que funciones objetivo son apropiadas para AlphaEvolve sin introducir PnL?
7. Que eventos se degradan si el modelo matematico de presion no aumenta en la
   fase esperada?
