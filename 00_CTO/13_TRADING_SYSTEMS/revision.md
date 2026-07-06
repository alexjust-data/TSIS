Yo **no la pondrÃ­a dentro de Machine Learning**, ni dentro de Market Science, ni dentro de RL.

Porque las estrategias son el objeto principal que TSIS estudia.

---

Ahora mismo tienes esto:

```text
00_CTO
â”œâ”€â”€ Research Philosophy
â”œâ”€â”€ Systems Engineering
â”œâ”€â”€ Agent Engineering
â”œâ”€â”€ Memory
â”œâ”€â”€ Evaluation
â”œâ”€â”€ MLOps
â”œâ”€â”€ Distributed Systems
â”œâ”€â”€ ML
â”œâ”€â”€ RL
â”œâ”€â”€ Autonomous Research Systems
â”œâ”€â”€ Market Science
â”œâ”€â”€ TSIS Cognitive Architecture
```

Todo eso responde a:

```text
Â¿CÃ³mo construimos TSIS?
```

Pero falta:

```text
Â¿QuÃ© estudia TSIS?
```

---

Para mÃ­ falta una capa completa:

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
â”‚
â”œâ”€â”€ 01_STRATEGY_LIBRARY
â”‚
â”œâ”€â”€ 02_SETUP_TAXONOMY
â”‚
â”œâ”€â”€ 03_EDGE_HYPOTHESES
â”‚
â”œâ”€â”€ 04_PATTERN_CATALOG
â”‚
â”œâ”€â”€ 05_EXECUTION_MODELS
â”‚
â”œâ”€â”€ 06_DISCRETIONARY_FRAMEWORKS
â”‚
â”œâ”€â”€ 07_STRATEGY_EVOLUTION
â”‚
â”œâ”€â”€ 08_STRATEGY_CLUSTERS
â”‚
â””â”€â”€ 09_SQUEEZE_RESEARCH
```

---

Porque una estrategia no es ML.

No es RL.

No es infraestructura.

No es arquitectura.

Es:

```text
Objeto de investigaciÃ³n.
```

---

# Lo que pondrÃ­a en 01_STRATEGY_LIBRARY

AquÃ­ sÃ­ irÃ­an tus documentos.

Por ejemplo:

```text
01_STRATEGY_LIBRARY
â”‚
â”œâ”€â”€ PM_Squeeze
â”‚   â”œâ”€â”€ README.md
â”‚   â”œâ”€â”€ setup_definition.md
â”‚   â”œâ”€â”€ execution_rules.md
â”‚   â”œâ”€â”€ examples
â”‚   â”œâ”€â”€ charts
â”‚   â””â”€â”€ research_notes
â”‚
â”œâ”€â”€ First_Green_Day
â”‚
â”œâ”€â”€ First_Red_Day
â”‚
â”œâ”€â”€ VWAP_Reclaim
â”‚
â”œâ”€â”€ Gap_and_Go
â”‚
â”œâ”€â”€ ORB
â”‚
â”œâ”€â”€ SSR_Squeeze
â”‚
â””â”€â”€ Parabolic_Reversal
```

---

# Diferencia importante

Mucha gente mezcla:

```text
Estrategia
=
CÃ³digo
```

Eso es un error.

---

La estrategia deberÃ­a existir aunque no exista cÃ³digo.

---

Por ejemplo:

```text
PM_Squeeze
```

deberÃ­a contener:

```text
Idea

Contexto

PsicologÃ­a

Participantes

Microestructura

Reglas

Variantes

Casos lÃ­mite

Ejemplos
```

---

DespuÃ©s ya aparece:

```text
TSIS Implementation
```

que vivirÃ­a en:

```text
01_TSIS_Backtest
```

o

```text
Strategy Engine
```

---

# Otra carpeta que creo que te falta

ConociÃ©ndote, harÃ­a:

```text
13_TRADING_SYSTEMS
â”‚
â”œâ”€â”€ 01_STRATEGY_LIBRARY
â”‚
â”œâ”€â”€ 02_SETUP_TAXONOMY
```

---

Porque tÃº continuamente hablas de:

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
â”‚
â”œâ”€â”€ Momentum_Setups
â”‚
â”œâ”€â”€ Squeeze_Setups
â”‚
â”œâ”€â”€ Reversal_Setups
â”‚
â”œâ”€â”€ Continuation_Setups
â”‚
â”œâ”€â”€ Liquidity_Events
â”‚
â””â”€â”€ Hybrid_Setups
```

---

# Donde pondrÃ­a tu PM Squeeze

No aquÃ­:

```text
08_MACHINE_LEARNING
```

Ni aquÃ­:

```text
11_MARKET_SCIENCE
```

Ni aquÃ­:

```text
09_REINFORCEMENT_LEARNING
```

Sino:

```text
13_TRADING_SYSTEMS
â”‚
â””â”€â”€ 01_STRATEGY_LIBRARY
    â”‚
    â””â”€â”€ PM_Squeeze
```

porque el PM Squeeze es:

```text
Conocimiento de dominio.
```

Y todo lo demÃ¡s (Backtesting, Pattern Mining, ML, RL, AlphaEvolve) existe para estudiar, validar, mejorar y evolucionar ese conocimiento.

De hecho, si TSIS madura como imagino, **01_STRATEGY_LIBRARY** terminarÃ¡ siendo una de las carpetas mÃ¡s valiosas de todo el proyecto, porque serÃ¡ la traducciÃ³n formal de 20 aÃ±os de experiencia discrecional en small caps a conocimiento estructurado y reproducible.



# AlphaEvolve

SÃ­: **AlphaEvolve encaja**, pero no como â€œla IA que mira ticks y descubre todo solaâ€.

AlphaEvolve es mÃ¡s bien esto:

```text
LLM + cÃ³digo + evaluador + evoluciÃ³n
```

Google lo define como un agente que mejora algoritmos modificando cÃ³digo y recibiendo feedback de evaluadores programÃ¡ticos. ([arXiv][1])

Para TSIS, la idea correcta serÃ­a:

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

Luego tu harness lo evalÃºa:

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

Para trading, yo lo colocarÃ­a asÃ­:

```text
Setup
    â†“
Contexto
    â†“
Cluster
    â†“
ML supervisado
    â†“
AlphaEvolve
```

Pero con una correcciÃ³n importante:

**AlphaEvolve puede intervenir en todas las fases, pero no reemplaza las fases.**

Ejemplo:

```text
1. Setup
AlphaEvolve propone variantes de definiciÃ³n de setup.

2. Contexto
AlphaEvolve propone nuevas features.

3. Cluster
AlphaEvolve prueba formas distintas de agrupar eventos.

4. ML supervisado
AlphaEvolve busca mejores labels, thresholds y modelos.

5. EjecuciÃ³n
AlphaEvolve busca mejores reglas de entrada/salida.
```

---

La arquitectura mental serÃ­a:

```text
TÃº defines el fenÃ³meno:
"PM Squeeze"

TSIS crea datasets:
daily + intraday + events + outcomes

AlphaEvolve propone cÃ³digo:
detectores, reglas, features, estrategias

Harness evalÃºa:
si realmente mejora fuera de muestra

Solo sobreviven las variantes robustas.
```

---

Entonces sÃ­: **lo que tÃº imaginabas es correcto**, pero el orden no es:

```text
Le doy ticks a AlphaEvolve y descubre el edge.
```

El orden correcto es:

```text
Construyo el laboratorio evaluable.
DespuÃ©s AlphaEvolve evoluciona hipÃ³tesis dentro del laboratorio.
```

Google lo usÃ³ precisamente para problemas donde existe una mÃ©trica verificable: optimizaciÃ³n de algoritmos, problemas matemÃ¡ticos, infraestructura, kernels, etc. ([Google DeepMind][2])

En TSIS, tu mÃ©trica verificable serÃ­a:

```text
Â¿Esta variante mejora el edge
sin sobreoptimizar
y sobrevive fuera de muestra?
```

AhÃ­ AlphaEvolve tiene muchÃ­simo sentido.

[1]: https://arxiv.org/abs/2506.13131?utm_source=chatgpt.com "AlphaEvolve: A coding agent for scientific and algorithmic ..."
[2]: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/?utm_source=chatgpt.com "AlphaEvolve: A Gemini-powered coding agent for ..."
> Estado: source note historica.
>
> Este archivo conserva una propuesta previa de estructura para
> `13_TRADING_SYSTEMS/`. No es la arquitectura vigente. La arquitectura activa
> vive en `README.md`, `../TSIS_LAB_ARCHITECTURE_v3.md` y
> `C:/TSIS_Data/00_TSIS_Lab/README.md`. El plan de refactor anterior esta
> archivado en `_archive/superseded_architecture_2026_07_05/`.
>
> Muchas rutas mencionadas aqui son anteriores al refactor event-first ejecutado
> el 2026-06-18.

