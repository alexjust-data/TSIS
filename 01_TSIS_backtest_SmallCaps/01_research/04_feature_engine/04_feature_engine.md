Aquí está el edge.

NO trabajaría directamente sobre “velas”.

Trabajaría sobre:

eventos

Ejemplos:

```sh
EVENT_GAP_UP
EVENT_RVOL_EXPLOSION
EVENT_FIRST_PM_BREAK
EVENT_HOD_BREAK
EVENT_VWAP_RECLAIM
EVENT_PARABOLIC_EXTENSION
EVENT_OFFERING_DROP
EVENT_HALTED
EVENT_SSR
```

Eso convierte el mercado en una secuencia de estados/eventos.

Y eso es MUCHO más compatible con ML/RL después.


---


# 04_feature_engine

## Objetivo

Transformar datos de mercado en features cuantitativas utilizables.

---

# Filosofía

Aquí NO existen todavía:

- setups
- señales
- estrategias

Sólo descripción matemática del mercado.

---

# Inputs

- ohlcv
- quotes
- trades
- reference_layer
- universe_builder

---

# Features típicas

## Momentum

- gap_pct
- intraday_extension
- close_near_hod

## Liquidez

- volume
- dollar_volume
- rvol

## Volatilidad

- ATR
- range_expansion
- volatility

## Microestructura

- spread
- imbalance
- quote_velocity

---

# Outputs principales

## master_daily_table.parquet

1 fila:

ticker × día

## master_intraday_features.parquet

features intradía multi-timeframe.

---

# Filosofía importante

El Feature Engine NO toma decisiones.

Sólo representa el estado observable del mercado.