Esto probablemente es más importante que el propio modelo.

Porque tu edge vive en:

* compañías “muertas”
* low float
* despertadores de atención
* pumps
* squeezes
* news spikes

Entonces tu universo debe reconstruirse exactamente como existía cada día.

Tu reference/all_tickers y reference/events son oro aquí.

Yo construiría diariamente:

```sh
ticker
date
active
market_cap
float
split_recent
reverse_split_recent
days_since_listing
sector
exchange
```

Y luego encima:

```sh
gap
relative_volume
premarket_volume
dollar_volume
spread
volatility
halt_recent
```


---


# 03_universe_builder

## Objetivo

Reconstruir históricamente el universo elegible de trading para cada día.

---

# Pregunta que responde

¿Qué tickers existían y eran tradeables este día?

---

# Importancia

Evita:

- survivorship bias
- delisted bias
- universe leakage

---

# Inputs

- reference_layer
- ticker metadata
- listing data
- delisting data

---

# Outputs

## universe_daily.parquet

1 fila:

ticker × día

---

# Ejemplo de columnas

date
ticker
active
exchange
market_cap
float
days_since_listing

---

# Uso posterior

El universo define:

- qué tickers pueden participar
- qué activos entran al backtest
- qué empresas eran realmente visibles en cada época

---

# Filosofía

NO describe comportamiento.

Sólo elegibilidad estructural.
