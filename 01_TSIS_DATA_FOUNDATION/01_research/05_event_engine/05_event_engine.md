# 05_event_engine

## Objetivo

Transformar features cuantitativas en eventos semánticos de mercado.

---

# Filosofía

El mercado se modela como:

eventos y transiciones

NO sólo velas temporales.

---

# Ejemplos de eventos

EVENT_GAP_UP  
EVENT_RVOL_EXPLOSION  
EVENT_HOD_BREAK  
EVENT_VWAP_RECLAIM  
EVENT_PARABOLIC  
EVENT_FAILED_BREAKOUT  

---

# Inputs

- master_daily_table  
- intraday features  
- microstructure features  

---

# Outputs

## event_table.parquet

1 fila:

evento × timestamp

---

# Objetivo final

Convertir el mercado en una secuencia interpretable de estados/eventos.

Base fundamental para:

- estrategias
- ML
- RL
- state machines