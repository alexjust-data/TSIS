# README — Event Library

## Objetivo

La Event Library es el núcleo conceptual de TSIS.

Su función es representar fenómenos observables del mercado de forma estructurada, independiente de cualquier decisión operativa.

La librería de eventos existe para responder:

```text
¿Qué está ocurriendo?
```

No para responder:

```text
¿Qué debería hacer?
```

Esa segunda pregunta pertenece a las capas posteriores del sistema.

---

## Filosofía

TSIS no está diseñado para estudiar estrategias.  
TSIS está diseñado para estudiar el mercado.

Por tanto:

```text
Evento ≠ Estrategia
```

Un evento representa:

```text
Fenómeno observable
```

Una estrategia representa:

```text
Respuesta operativa
```

Ejemplo:

Evento:

```text
VWAP_Reclaim_Event
```

Estrategias posibles:

```text
Break VWAP
First Pullback
Higher Low
Tape Confirmation
```

Todas pueden operar exactamente el mismo evento.


## Principio fundamental

La Event Library es la fuente de verdad para:

```text
Outcome Research
Pattern Discovery
Clustering
Machine Learning
Decision Models
AlphaEvolve
Offline RL
```

Si la definición de los eventos es incorrecta:

```text
Todo el sistema será incorrecto.
```



## Estructura General

```text
01_EVENT_LIBRARY
│
├── 01_MOMENTUM_EXPANSION
│
├── 02_VWAP_CONTROL
│
├── 03_INTRADAY_REVERSALS
│
├── 04_MOMENTUM_EXHAUSTION
│
├── 05_RUNNER_LIFECYCLE
│
├── 06_RESISTANCE_AND_BREAKOUTS
│
├── 07_SHORT_SQUEEZE_DYNAMICS
│
└── 99_EXPERIMENTAL
```



## ¿Por qué organizar por familias?

No organizamos por estrategias.  
No organizamos por entradas.  
No organizamos por setups.  

Organizamos por:

```text
Fenómenos de mercado
```

Porque los fenómenos son mucho más estables que las estrategias.

Ejemplo:

```text
VWAP Bounce
VWAP Reclaim
VWAP Rejection
```

son manifestaciones distintas de:

```text
VWAP Control
```



# Familia 01 — Momentum Expansion

**Pregunta**

```text
¿La demanda domina el mercado?
```

**Fenómeno**

Movimientos explosivos impulsados por:

```text
Catalizador
Short Squeeze
Volumen
FOMO
Desequilibrio oferta/demanda
```

**Eventos iniciales**

```text
PM_Squeeze_Event
Gap_And_Go_Event
Opening_Drive_Event
Parabolic_Expansion_Event
```


# Familia 02 — VWAP Control

**Pregunta**

```text
¿Quién controla la acción alrededor del VWAP?
```

**Fenómeno**

Cambio de control entre:

```text
Longs
Shorts
```

alrededor del VWAP.

**Eventos iniciales**

```text
VWAP_Bounce_Event
VWAP_Reclaim_Event
VWAP_Loss_Event
VWAP_Rejection_Event
```


# Familia 03 — Intraday Reversals

**Pregunta**

```text
¿Está cambiando el control intradía?
```

**Fenómeno**

Reversión de dirección dentro de la misma sesión.

**Eventos iniciales**

```text
Red_To_Green_Event
Green_To_Red_Event
Gap_And_Crap_Reversal_Event
```


# Familia 04 — Momentum Exhaustion

**Pregunta**

```text
¿Se está agotando el movimiento?
```

**Fenómeno**

Pérdida progresiva de momentum.

**Eventos iniciales**

```text
Bull_Trap_Event
Failed_Breakout_Event
Late_Day_Fade_Event
Parabolic_Top_Event
```

# Familia 05 — Runner Lifecycle

**Pregunta**

```text
¿En qué fase del ciclo de vida está el runner?
```

**Fenómeno**

Las Small Caps suelen seguir un ciclo recurrente:

```text
Dormida
↓
Runner
↓
Euforia
↓
Destrucción
↓
Primer rebote
↓
Muerte
```

**Eventos iniciales**

```text
First_Green_Day_Event
First_Red_Day_Event
Runner_Continuation_Event
Runner_Collapse_Event
Multi_Day_Runner_Event
```

Esta familia es especialmente importante para TSIS.


# Familia 06 — Resistance & Breakouts

**Pregunta**

```text
¿Cómo interactúa el precio con niveles relevantes?
```

**Fenómeno**

Lucha alrededor de:

```text
Previous Day High
Daily Levels
Premarket High
Resistance Zones
```

**Eventos iniciales**

```text
Previous_Day_High_Breakout_Event
PMH_Breakout_Event
Resistance_Test_Event
Daily_Level_Breakout_Event
```



# Familia 07 — Short Squeeze Dynamics

**Pregunta**

```text
¿Existe presión estructural sobre los vendedores en corto?
```

**Fenómeno**

Eventos relacionados con:

```text
SSR
Short Interest
Forced Covering
Liquidity Vacuum
```

**Eventos iniciales**

```text
SSR_Triggered_Event
Short_Squeeze_Event
Forced_Covering_Event
High_Short_Interest_Event
```


# Familia 99 — Experimental

Zona de investigación.

Aquí se almacenan:

```text
Eventos descubiertos por Pattern Mining
Eventos descubiertos por Clustering
Eventos descubiertos por AlphaEvolve
Hipótesis nuevas
```

No deben promoverse a producción sin validación.

---

# Estructura de un Evento

Cada evento debe existir como archivo independiente.

Ejemplo:

```text
02_VWAP_CONTROL
│
└── VWAP_Reclaim_Event.yaml
```


## Plantilla de Evento

```yaml
event_name: VWAP_Reclaim_Event

family: VWAP_CONTROL

status: human_hypothesis_v1

description: >
  Price recovers VWAP after trading below it.

phenomenon: >
  Shift of intraday control from sellers to buyers.

conditions:

  - price_below_vwap_prior
  - cross_above_vwap
  - volume_expansion
  - hold_above_vwap

features:

  - gap_pct
  - float
  - market_cap
  - reclaim_volume
  - reclaim_time
  - distance_to_hod
  - spread
  - rvol

notes:

  - Not a strategy
  - No entries
  - No exits
  - No stop loss
```



# Reglas para Humanos

Cuando diseñes un nuevo evento:

Pregunta siempre:

```text
¿Qué está ocurriendo?
```

Nunca:

```text
¿Dónde entro?
```


# Reglas para Agentes

Antes de crear un evento:

Verificar:

```text
1. Describe un fenómeno observable
2. Puede detectarse automáticamente
3. No contiene entradas
4. No contiene stops
5. No contiene targets
6. No contiene gestión de posición
```

Si contiene cualquiera de los elementos anteriores:

```text
NO ES UN EVENTO
```

Es una estrategia.


# Evolución de Eventos

Los eventos humanos son únicamente el punto de partida.

Versionado esperado:

```text
VWAP_Reclaim_Event_v1
VWAP_Reclaim_Event_v2
VWAP_Reclaim_Event_v3
VWAP_Reclaim_Event_AlphaEvolve_17
```

La definición inicial no se considera definitiva.


# Relación con el resto de TSIS

```text
Data Foundation
        ↓

Event Library = Definiciones
        ↓

Event Engine = Detector
        ↓

event_table
        ↓

Outcome Engine
        ↓

outcome_table
        ↓

Event Analytics
        ↓

 ┌─────────────────────┐
 │ Pattern Discovery   │
 └─────────────────────┘

 ┌─────────────────────┐
 │ Cluster Discovery   │
 └─────────────────────┘
        ↓

Feature Library
        ↓

Machine Learning
        ↓

Decision Models
        ↓

Evolution Systems
```

# Ciclo de vida de un evento

```
Hipótesis Humana
        ↓

Event Definition
        ↓

Event Engine
        ↓

event_table
        ↓

Outcome Engine
        ↓

outcome_table
        ↓

Event Analytics
        ↓

Pattern Discovery
        ↓

Clustering
        ↓

Promoción / Evolución
```


# Principio Final

TSIS no aprende estrategias.

TSIS aprende fenómenos.

Las estrategias son simplemente una posible respuesta a esos fenómenos.

Por tanto:

```text
Evento primero.
Estrategia después.
```

Toda la arquitectura del laboratorio depende de mantener esta separación de forma estricta.
