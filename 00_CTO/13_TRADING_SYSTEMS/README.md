# 13_TRADING_SYSTEMS

## Propósito

Esta carpeta representa el **conocimiento de dominio de trading** que TSIS estudia, valida, evoluciona y explota.

Mientras que otras áreas del proyecto se centran en:

* Ingeniería de sistemas
* Machine Learning
* Reinforcement Learning
* Infraestructura
* Agentes
* MLOps

`13_TRADING_SYSTEMS` responde a una pregunta diferente:

> ¿Qué sabemos realmente sobre el mercado?

Aquí viven las hipótesis, estrategias, patrones, modelos mentales y marcos de decisión que constituyen el conocimiento operativo del sistema.

---

# 01_STRATEGY_LIBRARY

## Objetivo

Repositorio maestro de estrategias.

Cada estrategia debe existir como un objeto de conocimiento independiente de cualquier implementación.

Una estrategia debe poder entenderse completamente sin leer una sola línea de código.

---

## Contenido esperado

Ejemplos:

```text
PM_Squeeze/
Gap_and_Go/
First_Green_Day/
VWAP_Reclaim/
SSR_Squeeze/
Parabolic_Reversal/
```

Cada estrategia debería incluir:

```text
README.md
setup_definition.md
market_context.md
execution_rules.md
examples/
charts/
research_notes/
```

---

## Preguntas que responde

```text
¿Qué es esta estrategia?

¿Por qué debería funcionar?

Quiénes son los participantes implicados?

Qué ineficiencia explota?

Cuáles son sus variantes?
```

---

# 02_SETUP_TAXONOMY

## Objetivo

Crear una clasificación formal de todos los setups observados en el mercado.

Una estrategia puede contener múltiples setups.

Un setup puede aparecer dentro de múltiples estrategias.

---

## Ejemplos

```text
Momentum_Setups/
Continuation_Setups/
Squeeze_Setups/
Reversal_Setups/
Liquidity_Events/
News_Driven_Setups/
```

---

## Ejemplos concretos

```text
Break_PM_High
ORB
Micro_Pullback
VWAP_Reclaim
SSR_Squeeze
Parabolic_Extension
Failed_Breakout
```

---

## Preguntas que responde

```text
Qué tipo de evento de mercado estoy observando?

A qué familia pertenece?

Qué otros setups son similares?
```

---

# 03_EDGE_HYPOTHESES

## Objetivo

Repositorio de hipótesis de ventaja estadística.

No contiene estrategias completas.

Contiene explicaciones sobre por qué una ventaja podría existir.

---

## Ejemplos

```text
Short_Seller_Trap.md

Low_Float_Inefficiency.md

News_Repricing_Delay.md

Liquidity_Vacuum.md

Retail_FOMO_Cascade.md

Market_Maker_Hedging.md
```

---

## Ejemplos de hipótesis

```text
Los floats extremadamente bajos generan squeezes más violentos.

Los shorts atrapados producen aceleraciones no lineales.

Los gaps con noticia positiva presentan persistencia intradía.
```

---

## Pregunta principal

```text
¿Por qué debería existir el edge?
```

---

# 04_PATTERN_CATALOG

## Objetivo

Base de conocimiento de patrones descubiertos mediante investigación.

Aquí no viven las hipótesis humanas.

Aquí viven los patrones encontrados en los datos.

---

## Fuentes

```text
Backtesting
Pattern Mining
Machine Learning
Clustering
Análisis estadístico
```

---

## Ejemplos

```text
Pattern_001.md

Pattern_002.md

Pattern_003.md
```

---

## Ejemplo de patrón

```text
83% de los movimientos >80%

ocurren cuando:

Float < 5M
PM Volume > 3M
Gap > 40%
```

---

## Pregunta principal

```text
¿Qué patrones aparecen realmente en los datos?
```

---

# 05_EXECUTION_MODELS

## Objetivo

Documentar cómo se ejecutan las operaciones.

Dos traders pueden utilizar la misma estrategia y ejecutar de forma completamente distinta.

---

## Ejemplos

```text
Aggressive_Breakout.md

Passive_Pullback.md

Scale_In.md

Scale_Out.md

Momentum_Chase.md

Confirmation_Entry.md
```

---

## Variables estudiadas

```text
Entradas

Salidas

Stops

Gestión parcial

Escalado

Gestión de riesgo
```

---

## Pregunta principal

```text
¿Cómo se ejecuta el trade?
```

---

# 06_DISCRETIONARY_FRAMEWORKS

## Objetivo

Capturar conocimiento discrecional difícil de formalizar.

Representa cómo piensa un trader experto.

---

## Ejemplos

```text
Tape_Reading/

Level2_Interpretation/

Market_Psychology/

Momentum_Assessment/

Context_Recognition/
```

---

## Contenido esperado

```text
Casos reales

Diagramas

Capturas DAS

Análisis de tape

Lecturas de L2

Estudios subjetivos
```

---

## Pregunta principal

```text
¿Qué observa un trader experto que todavía no está modelado?
```

---

# 07_STRATEGY_EVOLUTION

## Objetivo

Historial evolutivo de las estrategias.

Permite entender cómo una estrategia cambia a lo largo del tiempo.

---

## Ejemplos

```text
PM_Squeeze/
    v1/
    v2/
    v3/
```

---

## Información almacenada

```text
Cambios

Motivación

Resultados

Mejoras

Regresiones
```

---

## Pregunta principal

```text
¿Cómo ha evolucionado esta estrategia?
```

---

# 08_STRATEGY_CLUSTERS

## Objetivo

Agrupar eventos de mercado similares.

No agrupa tickers.

No agrupa empresas.

Agrupa comportamientos.

---

## Ejemplos

```text
Cluster_001_Explosive_Squeezes/

Cluster_002_Slow_Grinders/

Cluster_003_Parabolic_Runners/

Cluster_004_Failed_Breakouts/
```

---

## Fuentes

```text
K-Means

HDBSCAN

UMAP

Hierarchical Clustering

Representation Learning
```

---

## Pregunta principal

```text
Qué familias de comportamiento existen?
```

---

# 09_SQUEEZE_RESEARCH

## Objetivo

Área especializada para el fenómeno más importante del proyecto.

Estudio sistemático de:

```text
Short Squeezes

Momentum Squeezes

Low Float Runners

Intraday Expansions

Liquidity Vacuums
```

---

## Posibles secciones

```text
01_Theory

02_Microstructure

03_Historical_Cases

04_Tape_and_L2

05_Pattern_Mining

06_ML_Research

07_Offline_RL

08_Squeeze_Dataset
```

---

## Preguntas principales

```text
Qué genera un squeeze?

Cómo nace?

Cómo evoluciona?

Qué variables predicen su magnitud?

Qué diferencia un squeeze mediocre de uno explosivo?

Cuál es el retroceso óptimo?

Qué estados de mercado preceden los mayores runners?
```

---

# Relación con TSIS

```text
Strategy Library
        ↓
Setup Taxonomy
        ↓
Edge Hypotheses
        ↓
Backtesting
        ↓
Pattern Catalog
        ↓
Strategy Clusters
        ↓
Machine Learning
        ↓
Offline RL
        ↓
Strategy Evolution
```

Esta carpeta representa la capa de conocimiento financiero de TSIS. Todo el resto del sistema existe para estudiar, validar, explicar y evolucionar los conceptos almacenados aquí.
