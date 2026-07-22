# 02_reference_layer

## Objetivo

Construir tablas maestras lentas y estructurales reutilizables por todo el sistema.

Estas tablas cambian lentamente y sirven como contexto permanente.

---

# Qué contiene

## Metadata de tickers

- exchange
- sector
- industry
- type

## Corporate actions

- splits
- reverse splits
- ticker changes

## Fundamentals

- market cap
- float
- shares outstanding

## Calendario

- trading sessions
- holidays
- half days

---

# Filosofía

Separar:

información estructural

de:

información dinámica intradía.

---

# Outputs principales

## ticker_master.parquet

1 fila por ticker.

## ticker_daily_reference.parquet

1 fila por ticker × día.

---

# Ejemplo de columnas

ticker
exchange
sector
market_cap
float
days_since_listing
reverse_split_recent

---

# Objetivo final

Centralizar toda la información estructural del mercado para reutilizarla en:

- universe builder
- feature engine
- event engine
- ML
- execution simulator