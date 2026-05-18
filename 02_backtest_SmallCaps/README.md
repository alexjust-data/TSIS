ejemplos:

# Trading Backtester (Quant-grade, reproducible)

## Setup
1) Create venv & install deps (uv)
- Install uv: https://github.com/astral-sh/uv
- Then:

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env
# backtest_SmallCaps
```

Sí. La dirección es MUY correcta.

Pero yo lo reorganizaría un poco para que refleje realmente el flujo de investigación cuantitativa.

Ahora mismo mezclas:

* datos
* features
* eventos
* estrategias
* ML
* ejecución

Y más adelante eso crea caos.

Yo lo estructuraría así:

```text id="33n72t"
C:\TSIS_Data\02_backtest_SmallCaps\
│
├── 00_raw_polygon
├── 01_data_auditoria_polygon
├── 02_reference_layer
├── 03_universe_builder
├── 04_feature_engine
├── 05_event_engine
├── 06_strategy_engine
├── 07_execution_simulator
├── 08_research_backtests
├── 09_edge_statistico
├── 10_regime_modeling
├── 11_ml_offline_rl
├── 12_reporting
├── 13_configs
├── 14_logs
└── 15_exports
```

Y te explico por qué.

---

# 00_raw_polygon

```text id="8bdbcf"
SOLO RAW
```

Nunca tocar.

Aquí:

```text id="wnm0xa"
ohlcv_1m
ohlcv_daily
quotes
trades
reference
halts
financial
```

Exactamente como vienen.

---

# 01_data_auditoria_polygon

Aquí validas:

* parquet corruptos
* gaps
* timestamps
* duplicates
* bad ticks
* splits raros
* days inválidos
* missing sessions

Esto es:

```text id="xv89dy"
control de calidad
```

NO lógica de trading.

---

# 02_reference_layer

Esto es MUY importante y mucha gente no lo separa.

Aquí construyes:

```text id="jxh7bk"
tablas maestras lentas
```

Ejemplo:

* ticker metadata
* exchanges
* splits normalizados
* corporate actions
* market holidays
* sessions
* float history
* market cap history
* ticker changes

---

# Por qué separarlo

Porque esto cambia lento.

Y lo reutilizarás en TODO.

---

# 03_universe_builder

Aquí construyes:

```text id="q9rz9j"
qué tickers existían y eran elegibles cada día
```

Resultado:

```text id="0xpl5u"
universe_daily.parquet
```

1 fila:

```text id="4y7i6j"
ticker × día
```

---

# Columnas

```text id="3m9nlk"
date
ticker
active
market_cap
exchange
sector
float
days_since_listing
reverse_split_recent
```

---

# 04_feature_engine

Aquí empieza el núcleo cuantitativo.

Esto NO son eventos todavía.

Son:

```text id="l6z0e9"
features matemáticas
```

---

# Desde 1m

Construyes:

```text id="br1hvp"
gap_pct
rvol
pm_volume
range_expansion
intraday_extension
close_near_hod
vwap_distance
spread
```

---

# Resultado

```text id="n4hlgo"
master_daily_table.parquet
```

y luego:

```text id="d32zv8"
master_intraday_features.parquet
```

---

# IMPORTANTÍSIMO

Aquí NO decides setups.

Solo describes el mercado.

---

# 05_event_engine

Aquí transformas features → eventos.

Esto ya es:

```text id="ud6pkq"
semántica de mercado
```

---

# Ejemplos

```text id="7cbv0k"
EVENT_GAP_UP
EVENT_RVOL_EXPLOSION
EVENT_FIRST_PULLBACK
EVENT_VWAP_RECLAIM
EVENT_HOD_BREAK
EVENT_PARABOLIC
EVENT_FAILED_BREAKOUT
```

---

# Resultado

```text id="5q5avl"
event_table.parquet
```

---

# 06_strategy_engine

Aquí:

```text id="wg4xiu"
combinas eventos
```

para crear setups.

---

# Ejemplo

```text id="8a1hmo"
Gap&Go
=
EVENT_GAP_UP
+
EVENT_RVOL_EXPLOSION
+
EVENT_HOD_BREAK
+
NOT EVENT_OFFERING
```

---

# Resultado

```text id="cl2wqe"
trade signals
```

NO trades ejecutados todavía.

---

# 07_execution_simulator

Aquí viene:

```text id="v40mqg"
la realidad
```

---

# Inputs

* quotes
* trades
* spread
* liquidity
* halts
* SSR

---

# Decide

```text id="5j41sl"
entry fill
slippage
partial fills
stop execution
halt behavior
```

---

# Resultado

```text id="4mwq8h"
executed_trades.parquet
```

---

# 08_research_backtests

Aquí haces:

* grids
* walk-forward
* robustness
* CPCV
* IS/OOS
* parameter sweeps

---

# Resultado

```text id="2q1b7q"
research experiments
```

---

# 09_edge_statistico

Aquí analizas:

```text id="4o4txv"
dónde existe edge REAL
```

---

# Ejemplos

* por régimen
* por float
* por hora
* por market cap
* por spread
* por época
* por tipo de catalyst

---

# Resultado

```text id="tdm7z5"
edge maps
```

---

# 10_regime_modeling

Aquí ya entra:

* HMM
* clustering
* embeddings
* switching models
* drift detection

---

# Objetivo

NO:

```text id="83m4x9"
predecir precio
```

Sino:

```text id="e6bvxz"
inferir contexto oculto
```

---

# 11_ml_offline_rl

Aquí sí:

* CatBoost
* LightGBM
* transformers
* offline RL
* IQL
* CQL

---

# IMPORTANTE

Esto debe venir DESPUÉS de:

* features
* eventos
* ejecución
* edge

---

# Porque si no:

RL aprenderá basura.

---

# 12_reporting

Aquí centralizas:

* MAE/MFE
* equity curves
* reports
* heatmaps
* degradation
* robustness
* dashboards

---

# 13_configs

MUY importante.

Aquí:

```text id="6sivg9"
yaml/json/toml
```

con:

* parámetros
* universos
* sesiones
* costes
* setups

---

# 14_logs

Todo:

* pipelines
* errores
* experimentos
* timings

---

# 15_exports

Aquí:

* CSVs
* reports
* datasets finales
* snapshots

---

# La clave conceptual

Tu proyecto realmente tiene 3 niveles distintos:

---

# Nivel 1 — Infraestructura

```text id="9zfd9o"
datos
universo
features
eventos
```

---

# Nivel 2 — Trading

```text id="yzlvkz"
setups
ejecución
riesgo
backtests
```

---

# Nivel 3 — IA / investigación avanzada

```text id="9bx90n"
régimen
representación
offline RL
adaptación
```

---

# Y esto es IMPORTANTÍSIMO

NO mezcles:

```text id="v3l39f"
eventos
```

con:

```text id="gvsvv5"
estrategias
```

Porque un mismo evento puede alimentar:

* Gap&Go
* Gap extension
* short squeeze
* failed breakout
* momentum continuation

---

# La arquitectura correcta es:

```text id="y66bq8"
mercado
→ features
→ eventos
→ setups
→ ejecución
→ estadísticas
→ modelos
```

NO:

```text id="8hzxgl"
precio → estrategia directamente
```

Porque eso te limita muchísimo más adelante.
