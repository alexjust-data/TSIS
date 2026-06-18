Yo **no la pondría dentro de Machine Learning**, ni dentro de Market Science, ni dentro de RL.

Porque las estrategias son el objeto principal que TSIS estudia.

---

Ahora mismo tienes esto:

```text
00_CTO
├── Research Philosophy
├── Systems Engineering
├── Agent Engineering
├── Memory
├── Evaluation
├── MLOps
├── Distributed Systems
├── ML
├── RL
├── Autonomous Research Systems
├── Market Science
├── TSIS Cognitive Architecture
```

Todo eso responde a:

```text
¿Cómo construimos TSIS?
```

Pero falta:

```text
¿Qué estudia TSIS?
```

---

Para mí falta una capa completa:

```text
13_TRADING_RESEARCH
```

o incluso mejor:

```text
13_TRADING_SYSTEMS
```

---

Y dentro:

```text
13_TRADING_SYSTEMS
│
├── 01_STRATEGY_LIBRARY
│
├── 02_SETUP_TAXONOMY
│
├── 03_EDGE_HYPOTHESES
│
├── 04_PATTERN_CATALOG
│
├── 05_EXECUTION_MODELS
│
├── 06_DISCRETIONARY_FRAMEWORKS
│
├── 07_STRATEGY_EVOLUTION
│
├── 08_STRATEGY_CLUSTERS
│
└── 09_SQUEEZE_RESEARCH
```

---

Porque una estrategia no es ML.

No es RL.

No es infraestructura.

No es arquitectura.

Es:

```text
Objeto de investigación.
```

---

# Lo que pondría en 01_STRATEGY_LIBRARY

Aquí sí irían tus documentos.

Por ejemplo:

```text
01_STRATEGY_LIBRARY
│
├── PM_Squeeze
│   ├── README.md
│   ├── setup_definition.md
│   ├── execution_rules.md
│   ├── examples
│   ├── charts
│   └── research_notes
│
├── First_Green_Day
│
├── First_Red_Day
│
├── VWAP_Reclaim
│
├── Gap_and_Go
│
├── ORB
│
├── SSR_Squeeze
│
└── Parabolic_Reversal
```

---

# Diferencia importante

Mucha gente mezcla:

```text
Estrategia
=
Código
```

Eso es un error.

---

La estrategia debería existir aunque no exista código.

---

Por ejemplo:

```text
PM_Squeeze
```

debería contener:

```text
Idea

Contexto

Psicología

Participantes

Microestructura

Reglas

Variantes

Casos límite

Ejemplos
```

---

Después ya aparece:

```text
TSIS Implementation
```

que viviría en:

```text
01_TSIS_Backtest
```

o

```text
Strategy Engine
```

---

# Otra carpeta que creo que te falta

Conociéndote, haría:

```text
13_TRADING_SYSTEMS
│
├── 01_STRATEGY_LIBRARY
│
├── 02_SETUP_TAXONOMY
```

---

Porque tú continuamente hablas de:

```text
Squeeze

Breakout

Pullback

Reclaim

Parabolic
```

Pero realmente son:

```text
Eventos de mercado
```

---

Por ejemplo:

```text
02_SETUP_TAXONOMY
│
├── Momentum_Setups
│
├── Squeeze_Setups
│
├── Reversal_Setups
│
├── Continuation_Setups
│
├── Liquidity_Events
│
└── Hybrid_Setups
```

---

# Donde pondría tu PM Squeeze

No aquí:

```text
08_MACHINE_LEARNING
```

Ni aquí:

```text
11_MARKET_SCIENCE
```

Ni aquí:

```text
09_REINFORCEMENT_LEARNING
```

Sino:

```text
13_TRADING_SYSTEMS
│
└── 01_STRATEGY_LIBRARY
    │
    └── PM_Squeeze
```

porque el PM Squeeze es:

```text
Conocimiento de dominio.
```

Y todo lo demás (Backtesting, Pattern Mining, ML, RL, AlphaEvolve) existe para estudiar, validar, mejorar y evolucionar ese conocimiento.

De hecho, si TSIS madura como imagino, **01_STRATEGY_LIBRARY** terminará siendo una de las carpetas más valiosas de todo el proyecto, porque será la traducción formal de 20 años de experiencia discrecional en small caps a conocimiento estructurado y reproducible.



# AlphaEvolve

Sí: **AlphaEvolve encaja**, pero no como “la IA que mira ticks y descubre todo sola”.

AlphaEvolve es más bien esto:

```text
LLM + código + evaluador + evolución
```

Google lo define como un agente que mejora algoritmos modificando código y recibiendo feedback de evaluadores programáticos. ([arXiv][1])

Para TSIS, la idea correcta sería:

```text
AlphaEvolve no busca directamente el trade.

AlphaEvolve busca mejores reglas, mejores features,
mejores detectores, mejores clusters y mejores evaluadores.
```

El punto clave: **AlphaEvolve necesita un evaluador objetivo**.

Ejemplo TSIS:

```text
Candidato generado por AlphaEvolve:

IF gap > 45%
AND float < 8M
AND pm_volume > 3M
AND first_push > 18%
AND pullback between 4% and 12%
AND volume_pullback < 60% of push_volume
THEN mark PM_Squeeze_Candidate
```

Luego tu harness lo evalúa:

```text
Walk-forward result
Profit factor
Max drawdown
Sharpe
Avg R
Top 5% squeeze capture
Stability across years
Parameter robustness
Cost/slippage
```

Si mejora, sobrevive. Si no, muere.

---

Para trading, yo lo colocaría así:

```text
Setup
    ↓
Contexto
    ↓
Cluster
    ↓
ML supervisado
    ↓
AlphaEvolve
```

Pero con una corrección importante:

**AlphaEvolve puede intervenir en todas las fases, pero no reemplaza las fases.**

Ejemplo:

```text
1. Setup
AlphaEvolve propone variantes de definición de setup.

2. Contexto
AlphaEvolve propone nuevas features.

3. Cluster
AlphaEvolve prueba formas distintas de agrupar eventos.

4. ML supervisado
AlphaEvolve busca mejores labels, thresholds y modelos.

5. Ejecución
AlphaEvolve busca mejores reglas de entrada/salida.
```

---

La arquitectura mental sería:

```text
Tú defines el fenómeno:
"PM Squeeze"

TSIS crea datasets:
daily + intraday + events + outcomes

AlphaEvolve propone código:
detectores, reglas, features, estrategias

Harness evalúa:
si realmente mejora fuera de muestra

Solo sobreviven las variantes robustas.
```

---

Entonces sí: **lo que tú imaginabas es correcto**, pero el orden no es:

```text
Le doy ticks a AlphaEvolve y descubre el edge.
```

El orden correcto es:

```text
Construyo el laboratorio evaluable.
Después AlphaEvolve evoluciona hipótesis dentro del laboratorio.
```

Google lo usó precisamente para problemas donde existe una métrica verificable: optimización de algoritmos, problemas matemáticos, infraestructura, kernels, etc. ([Google DeepMind][2])

En TSIS, tu métrica verificable sería:

```text
¿Esta variante mejora el edge
sin sobreoptimizar
y sobrevive fuera de muestra?
```

Ahí AlphaEvolve tiene muchísimo sentido.

[1]: https://arxiv.org/abs/2506.13131?utm_source=chatgpt.com "AlphaEvolve: A coding agent for scientific and algorithmic ..."
[2]: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/?utm_source=chatgpt.com "AlphaEvolve: A Gemini-powered coding agent for ..."
