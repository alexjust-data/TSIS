# 12_reporting

## Objetivo

Centralizar todos los informes, gráficos, dashboards y análisis finales del sistema.

Esta carpeta NO genera datos primarios.

Consume outputs de:

- backtests
- execution simulator
- edge analysis
- ML/RL
- regime modeling

---

# Qué va aquí

## Informes de estrategia

- performance por setup
- equity curves
- drawdowns
- profit factor
- expectancy
- winrate
- payoff ratio

## Informes de robustez

- walk-forward reports
- IS/OOS degradation
- parameter sensitivity
- stress testing
- slippage sensitivity

## Informes de ejecución

- MAE/MFE
- slippage realista
- spread impact
- partial fills
- capacity analysis

## Visualizaciones

- heatmaps
- histograms
- scatter plots
- regime charts
- trade distributions

---

# Ejemplos

equity_curve_gapgo_2021_2026.png  
gapgo_robustness_report.pdf  
mae_mfe_analysis.csv  
performance_by_float_bucket.parquet  
slippage_degradation_report.html  

---

# Filosofía

Reporting es la capa donde el sistema se vuelve interpretable.

Sirve para responder:

- qué funciona
- cuándo funciona
- cuándo falla
- por qué falla
- cuánto se degrada
- si el edge parece robusto

---

# Regla importante

Aquí NO se retocan estrategias.

Aquí se observan resultados.