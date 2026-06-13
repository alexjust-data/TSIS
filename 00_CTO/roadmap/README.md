`00_CTO/roadmap/` es:

```text
la capa de dirección estratégica del proyecto
```

NO es código.

NO es research técnico.

NO es documentación genérica.

Es:

```text
hacia dónde va el sistema
```

---

# CTO = Chief Technical Office

Esa carpeta representa:

```text
la mente arquitectónica del proyecto
```

---

# Qué NO debe ir aquí

NO:

* scripts
* notebooks
* datasets
* código experimental
* outputs
* parquet
* logs

---

# Qué SÍ debe ir aquí

Todo lo relacionado con:

```text
decisiones estratégicas futuras
```

---

# Ejemplo REAL de contenido

```text
00_CTO/
│
├── roadmap/
│   ├── roadmap_master.md
│   ├── roadmap_2026_q2.md
│   ├── roadmap_backtesting.md
│   ├── roadmap_live_trading.md
│   ├── roadmap_offline_rl.md
│   ├── milestones.md
│   └── technical_debt.md
```

---

# Qué contiene cada uno

---

# roadmap_master.md

La visión completa.

Ejemplo:

```text
FASE 1
Data audit + universe builder

FASE 2
Feature engine robusto

FASE 3
Event engine

FASE 4
Execution simulator realista

FASE 5
Research-grade validation

FASE 6
Meta-labeling baseline

FASE 7
Realtime websocket infra

FASE 8
Behavioral cloning

FASE 9
Offline RL

FASE 10
Production deployment
```

---

# roadmap_2026_q2.md

Roadmap trimestral concreto.

Ejemplo:

```text
Objetivos mayo-junio:

- terminar master_daily_table
- definir schemas oficiales
- construir event taxonomy
- crear slippage model v1
- validar walk-forward baseline
```

---

# roadmap_backtesting.md

TODO lo relacionado con:

```text
01_TSIS_backtest_SmallCaps
```

---

# roadmap_live_trading.md

TODO lo relacionado con:

```text
02_TSIS_webSocket_SmallCaps
```

---

# roadmap_offline_rl.md

TODO lo relacionado con:

```text
03_TSIS_Offline_RL
```

---

# milestones.md

Hitos oficiales del proyecto.

Ejemplo:

```text
[v0.3.0]
Universe Builder operativo

[v0.4.0]
Feature Engine estable

[v0.5.0]
Primer backtest reproducible

[v0.8.0]
Purged CV implementado

[v1.0.0]
Primer sistema institutional-grade
```

---

# technical_debt.md

MUY importante.

Aquí documentas:

```text
cosas mal hechas temporalmente
```

para NO olvidarlas.

Ejemplo:

```text
- quotes parser demasiado lento
- schemas inconsistentes entre daily y intraday
- event engine aún acoplado
- hardcoded exchange mapping
```

---

# Lo MÁS importante

Esta carpeta sirve para separar:

```text
estrategia del proyecto
```

de:

```text
implementación diaria
```

---

# Esto es MUY profesional

Porque cuando el proyecto crezca muchísimo:

* agentes
* tú
* futuros colaboradores

necesitarán entender:

```text
hacia dónde va el sistema
```

NO sólo:

```text
qué código existe hoy
```

---

# Cómo interactúan los agentes aquí

Un agente puede leer:

```text
00_CTO/roadmap/
```

y entender:

* prioridades
* fases
* arquitectura futura
* objetivos pendientes
* deuda técnica
* milestones

---

# Entonces el agente deja de trabajar “a ciegas”

y empieza a trabajar:

```text
alineado con la dirección estratégica
```

# esta carpeta acabará siendo IMPORTANTÍSIMA

Porque ahí vivirán:

```text
las decisiones de más alto nivel del sistema
```

