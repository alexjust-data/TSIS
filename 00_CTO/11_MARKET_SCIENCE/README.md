Son sobre la **ciencia del mercado** que TSIS necesita aprender.

AlphaEvolve es un método para descubrir cosas.

Los libros son el conocimiento de dominio que determina qué merece la pena descubrir.

---

# Libro 1

High Frequency Trading

```text
11_MARKET_SCIENCE/
└── 01_MICROSTRUCTURE/
```

porque realmente habla de:

```text
order flow
liquidez
market microstructure
event time
toxicity
execution
```

No habla de ML.

No habla de AlphaEvolve.

Habla de cómo funciona el mercado.

---

Ejemplo:

```text
01_MICROSTRUCTURE/
│
├── Event_Time.md
├── Liquidity_Dynamics.md
├── Order_Flow.md
├── Toxicity.md
├── Market_Making.md
└── Notes_HFT_Book.md
```

---

# Libro 2

Advances in Financial Machine Learning



Este es probablemente el libro más importante para TSIS.

Lo separaría completamente:

```text
11_MARKET_SCIENCE/
└── 02_FINANCIAL_ML/
```

porque aquí aparecen:

```text
meta-labeling
triple barrier
purged CV
embargo
fractional differentiation
feature importance
information bars
```

---

Ejemplo:

```text
02_FINANCIAL_ML/
│
├── Information_Bars.md
├── Triple_Barrier.md
├── Meta_Labeling.md
├── Purged_CV.md
├── Fractional_Differentiation.md
├── Feature_Importance.md
└── Notes_Lopez_De_Prado.md
```

---

# Libro 3

Causal Factor Investing



Éste NO lo metería en ML.

Lo pondría aquí:

```text
11_MARKET_SCIENCE/
└── 03_CAUSALITY/
```

porque la idea central es:

```text
causalidad
confounders
causal graphs
do-calculus
type A spuriousness
type B spuriousness
```

---

Ejemplo:

```text
03_CAUSALITY/
│
├── Causal_Graphs.md
├── Confounders.md
├── Market_Causality.md
├── TypeA_Spuriousness.md
├── TypeB_Spuriousness.md
└── Notes_Causal_Factor_Investing.md
```

---

# Libro 4

Risk and Asset Allocation



Yo lo colocaría aquí:

```text
11_MARKET_SCIENCE/
└── 04_INVARIANTS_AND_RISK/
```

porque realmente habla de:

```text
invariants
uncertainty
hidden states
risk
robustness
bayesian thinking
estimation risk
```

---

Ejemplo:

```text
04_INVARIANTS_AND_RISK/
│
├── Invariants.md
├── Hidden_States.md
├── Estimation_Risk.md
├── Robustness.md
├── Bayesian_Thinking.md
└── Notes_Meucci.md
```

---

# Lo que haría después

probablemente la más importante de todas:

```text
11_MARKET_SCIENCE/
└── 05_MARKET_STATE_REPRESENTATION/
```

Porque cuando juntas los 4 libros aparece una pregunta común:

```text
¿Cómo representamos el estado real del mercado?
```

Ahí convergen:

### HFT

```text
event time
order flow
liquidez
```

### López de Prado

```text
information bars
meta-labeling
features
```

### Causal Investing

```text
causal graphs
hidden mechanisms
```

### Meucci

```text
invariants
latent states
uncertainty
```

---

Y sinceramente, si me preguntas cuál es el tema más importante de TSIS durante los próximos 2 años, no diría RL.

No diría AlphaEvolve.

Diría:

```text
Market State Representation
```

Porque:

```text
Universe Builder
      ↓
Features
      ↓
Events
      ↓
Market State Representation
      ↓
Strategy
      ↓
Execution
      ↓
Evaluation
```

Y una vez tengas una representación del estado del mercado realmente buena, entonces sí tiene sentido hablar de:

```text
AlphaEvolve
Offline RL
Decision Transformers
Research Agents
```

porque todos ellos dependerán de esa representación para aprender algo útil.



Ésta es probablemente una de las ideas más importantes de toda la IA moderna, RL, AlphaGo, AlphaEvolve y también de TSIS.

Voy a intentar explicarlo desde cero.

---

# ¿Qué es un estado?

Imagina que juegas al ajedrez.

La pregunta es:

```text
¿Qué necesita ver AlphaZero
para decidir el siguiente movimiento?
```

No necesita ver:

```text
últimos 1000 movimientos
```

Necesita ver:

```text
posición actual del tablero
```

Eso es el estado.

---

Formalmente:

```text
State =
Representación de todo lo necesario
para tomar una decisión óptima.
```

---

## En AlphaGo

El estado es:

```text
posición de las piedras
en el tablero
```

---

## En un coche autónomo

El estado es:

```text
posición
velocidad
distancia a obstáculos
carriles
```

---

## En trading

Aquí empieza el problema.

---

La mayoría cree que el estado es:

```text
precio
```

o

```text
vela de 5 minutos
```

---

Pero científicamente eso es absurdo.

Porque dos gráficos idénticos pueden significar cosas totalmente distintas.

---

Ejemplo:

Ticker A

```text
Gap 50%
News FDA
Float 3M
RVOL 20
SSR
```

---

Ticker B

```text
Gap 50%
Sin news
Float 500M
RVOL 1.2
```

---

Misma vela.

Mismo precio.

Estado completamente diferente.

---

## Entonces

La pregunta científica es:

```text
¿Qué información describe
realmente el mercado?
```

Eso es Market State Representation.

---

## Representación pobre

La mayoría del retail usa:

```text
state =
OHLCV
```

---

o

```text
state =
OHLCV
+
RSI
+
MACD
```

---

Eso es una representación extremadamente pobre.

Porque ignora:

```text
catalyst
float
spread
SSR
halt
order flow
liquidez
atención
régimen
```

---

## Representación mejor

Podría ser:

```text
state =

Catalyst_Type
Float
Market_Cap
Premarket_Volume
Gap_Size
RVOL
Spread
Volatility
SSR
Sector
Time_Of_Day
```

---

Ya describe mejor la realidad.

---

## Representación avanzada

Aquí es donde van los libros que has subido.

---

High Frequency Trading



te dice:

```text
añade:

order flow
toxicity
liquidity
event time
```

---

López de Prado



te dice:

```text
añade:

information bars
meta-labeling
feature engineering
```

---

Causal Factor Investing



te dice:

```text
añade:

causal structure
confounders
hidden mechanisms
```

---

Meucci



te dice:

```text
añade:

invariants
hidden states
uncertainty
```

---

## Lo que TSIS intenta realmente

Mucha gente cree que TSIS es:

```text
Backtester
```

---

Yo no lo veo así.

Lo veo como:

```text
Sistema para descubrir
una representación útil
del estado del mercado.
```

---

Porque una vez tienes el estado...

Todo lo demás es relativamente fácil.

---

## Ejemplo brutal

Supongamos que definimos:

```text
Estado 173
```

como:

```text
Biotech
Float < 5M
Gap > 50%
RVOL > 10
Spread estrecho
Premarket fuerte
SSR OFF
```

---

Y analizamos:

```text
10.000 casos históricos
```

---

Podemos descubrir:

```text
Estado 173

Win Rate = 67%
Expectancy = 0.42R
```

---

Ahora imagina:

```text
Estado 174
```

idéntico salvo:

```text
Spread ancho
```

---

Y obtenemos:

```text
Win Rate = 42%
Expectancy = -0.18R
```

---

Acabas de descubrir que:

```text
spread
forma parte del estado
```

---

## Por qué AlphaGo fue tan revolucionario

Porque DeepMind encontró una representación útil del tablero.

---

## Por qué AlphaEvolve funciona

Porque encuentra representaciones útiles del problema matemático.

---

## Por qué RL funciona

Porque encuentra políticas sobre estados.

---

La ecuación fundamental es:

```text
Estado
   ↓
Política
   ↓
Acción
   ↓
Resultado
```

---

#3 La pregunta más importante de TSIS

No es:

```text
¿Qué modelo uso?
```

Ni:

```text
¿Qué RL uso?
```

Ni:

```text
¿Qué LLM uso?
```

Es:

```text
¿Cómo represento el estado real
de una microcap?
```

Porque si el estado está mal representado:

```text
RL falla
ML falla
AlphaEvolve falla
Backtesting engaña
```

---

Si me preguntas qué creo que acabará siendo la carpeta más importante de todo TSIS, sería algo como:

```text
00_CTO/
└── 11_MARKET_SCIENCE/
    └── 05_MARKET_STATE_REPRESENTATION/
```

Porque ahí estás atacando la pregunta científica central:

> **¿Cuál es la mínima representación del mercado que conserva toda la información necesaria para tomar decisiones óptimas?**

Esa pregunta conecta directamente microestructura, causalidad, ML, RL, AlphaEvolve y prácticamente todo lo que has estado investigando durante los últimos meses.






