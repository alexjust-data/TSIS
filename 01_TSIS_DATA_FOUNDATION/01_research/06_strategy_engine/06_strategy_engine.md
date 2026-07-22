Cada setup debe ser:

state machine

Ejemplo real:

Gap&Go

Estado:

```sh
PREMARKET_BUILDUP
↓
OPENING_EXPANSION
↓
FIRST_PULLBACK
↓
HOD_ATTACK
↓
PARABOLIC
↓
FAILURE
```

* La estrategia no es: “vela verde rompe high”
* La estrategia es: “transición probabilística entre estados”.

Ahí es donde realmente puedes empezar a usar matemática avanzada.


# 06_strategy_engine

## Objetivo

Construir setups y señales combinando eventos.

---

# Filosofía

Las estrategias NO operan directamente sobre velas.

Operan sobre:

eventos + estados + contexto.

---

# Ejemplos

## Gap&Go

EVENT_GAP_UP
+
EVENT_RVOL_EXPLOSION
+
EVENT_HOD_BREAK

---

# Outputs

## trade_signals.parquet

Señales teóricas NO ejecutadas.

---

# Qué define una estrategia

- setup
- entry
- stop
- target
- invalidación
- sizing
- filtros
- contexto

---

# Importante

Aquí todavía NO existe:

slippage real
fills reales
execution real

Eso pertenece al Execution Simulator.