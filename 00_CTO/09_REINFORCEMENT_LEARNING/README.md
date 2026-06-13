# Reinforcement Learning

## Objetivo

Aprender decisiones secuenciales.

## Preguntas

- ¿Cómo actuar dado un estado?
- ¿Cómo optimizar decisiones?

## Contenido esperado

- Offline RL
- Decision Transformers
- CQL
- IQL
- Behavior Cloning
- Policy Learning

## Resultado esperado

Políticas adaptativas para mercados dinámicos.



Ésta va aquí:

```text id="z4yq7n"
00_CTO/
└── 09_REINFORCEMENT_LEARNING/
```

Pero te diría algo importante:

**No la llamaría sólo Reinforcement Learning.**

La renombraría a:

```text id="j8v2m5"
09_DECISION_SYSTEMS/
```

o

```text id="f3r8k1"
09_REINFORCEMENT_LEARNING_AND_DECISION_MODELS/
```

Porque Decision Transformers ya no son RL clásico.

Y porque probablemente TSIS acabará mezclando:

```text id="c7n4p8"
Behavior Cloning
Offline RL
Decision Transformers
Imitation Learning
Policy Learning
```

---

# Cómo la estructuraría

```text id="p5k9v2"
09_REINFORCEMENT_LEARNING/
│
├── README.md
│
├── 01_FOUNDATIONS/
│
├── 02_BEHAVIOR_CLONING/
│
├── 03_OFFLINE_RL/
│
├── 04_DECISION_TRANSFORMERS/
│
├── 05_POLICY_REPRESENTATION/
│
├── 06_MARKET_STATE_REPRESENTATION/
│
├── 07_EVALUATION_AND_SAFETY/
│
├── 08_TSIS_RL_ROADMAP/
│
└── 09_RESEARCH_QUESTIONS/
```

---

# 01_FOUNDATIONS

Aquí:

```text id="r1m6q4"
MDP
State
Action
Reward
Policy
Value Function
```

Pregunta:

```text id="t8k2v7"
¿Qué significa aprender una decisión?
```

---

# 02_BEHAVIOR_CLONING

Esto para TSIS será el primer paso real.

```text id="q4n7x1"
Trader experto
↓
Dataset
↓
Aprender comportamiento
```

---

Aquí guardarías:

```text id="v9m3k6"
Imitation Learning
Behavior Cloning
Expert Demonstrations
Human Policies
```

---

Pregunta:

```text id="g2r8p5"
¿Puede TSIS aprender
de los mejores traders?
```

---

# 03_OFFLINE_RL

Aquí entra exactamente lo que has pegado.

```text id="n7v1q9"
CQL
IQL
BCQ
Offline RL
Dataset-Constrained Learning
```

---

Pregunta:

```text id="p3m6x8"
¿Puede aprender una política
sin interactuar con el mercado?
```

---

Y aquí pondría:

```text id="w5k2r4"
Offline_RL_Risks.md
```

porque distribution shift será probablemente el mayor enemigo de TSIS.

---

# 04_DECISION_TRANSFORMERS

Aquí:

```text id="j1n8v3"
Decision Transformer
Trajectory Modeling
Sequence Modeling
Return Conditioning
```

---

Pregunta:

```text id="f7p4m9"
¿Podemos tratar trading
como un problema secuencial?
```

---

Y sinceramente:

De todo el RL moderno aplicado a trading, ésta es probablemente la rama que más me interesa para TSIS.

---

# 05_POLICY_REPRESENTATION

MUY importante.

---

Porque aquí aparece la pregunta:

```text id="k9v5r2"
¿Qué aprende realmente el modelo?
```

---

Ejemplo:

```text id="d4m7q1"
Entrar
Salir
Esperar
Reducir tamaño
```

---

Pregunta:

```text id="z8n3p6"
¿Cómo representamos una política?
```

---

# 06_MARKET_STATE_REPRESENTATION

Y aquí está la bomba.

---

Ésta probablemente sea la carpeta más importante de RL.

```text id="x6p1v8"
06_MARKET_STATE_REPRESENTATION/
```

---

Porque:

```text id="c3m9r5"
RL
=
Estado
+
Acción
+
Reward
```

---

Si el estado es malo:

```text id="b7n2q4"
RL fracasa
```

---

Aquí conectarías:

* HFT
* López de Prado
* Causal Investing
* Meucci






---

# 07_EVALUATION_AND_SAFETY

MUY importante.

---

Aquí:

```text id="q2v8m4"
Walk Forward
Purged CV
Embargo
Robustness
Distribution Shift
```

---

Pregunta:

```text id="t5n1k7"
¿Cómo sabemos que la política
no está sobreoptimizando?
```

---

# 08_TSIS_RL_ROADMAP

Yo pondría exactamente esto:

```text id="m8r4q2"
Fase 1

Behavior Cloning

↓

Fase 2

Decision Transformer

↓

Fase 3

Offline RL Conservador

↓

Fase 4

CQL

↓

Fase 5

Adaptive Policies

↓

Fase 6

Research Agents + RL
```

---

# Pero te diré algo que creo que es importante para tu CTO

Si tuviera que ordenar las carpetas por importancia para TSIS:

```text id="h3p7v5"
04_MEMORY_AND_KNOWLEDGE

05_EVALUATION_SYSTEMS

08_MACHINE_LEARNING

06_MLOPS_AND_REPRODUCIBILITY

03_AGENT_ENGINEERING

09_REINFORCEMENT_LEARNING
```

---

Porque ahora mismo veo que mucha gente empieza por RL.

Y en realidad RL depende de:

```text id="n6m2q8"
Estado correcto
Memoria correcta
Evaluación correcta
Backtesting correcto
Trazabilidad correcta
```

Sin eso:

```text id="x1v9r4"
Offline RL
Decision Transformers
CQL
```

son simplemente formas muy sofisticadas de aprender ruido histórico.

Por eso en la visión que estás construyendo para TSIS, el documento que acabas de pegar iría en `09_REINFORCEMENT_LEARNING`, pero **no debería convertirse en una prioridad de implementación hasta que 04, 05, 06 y 08 estén muy maduras**. Esa es exactamente la secuencia que siguen los laboratorios serios cuando construyen sistemas de decisión.
