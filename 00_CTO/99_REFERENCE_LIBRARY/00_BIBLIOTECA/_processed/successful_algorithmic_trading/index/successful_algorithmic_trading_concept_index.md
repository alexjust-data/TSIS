# Concept Index - Successful Algorithmic Trading

**book_id:** `successful_algorithmic_trading`  
**Uso:** localizar rapidamente conceptos del libro y su encaje en TSIS.

| Concepto | Seccion | Paginas PDF | Importancia TSIS | Notas |
|---|---|---:|---|---|
| Algorithmic trading system | Ch. 1-2 | 12-20 | Media | Contexto general y enfoque Python |
| Scientific method | Ch. 2 | 18 | Media | Base mental para research reproducible |
| Backtesting | Ch. 3 | 24-25 | Alta | Verificacion historica de estrategias |
| Optimisation bias | Ch. 3 | 25 | Alta | Registrar variantes y parametros |
| Lookahead bias | Ch. 3 | 25-26 | Alta | Prohibir estado futuro en decisiones |
| Survivorship bias | Ch. 3 | 26 | Alta | Especialmente critico en small caps |
| Cognitive bias | Ch. 3 | 26-27 | Media | Riesgo humano durante drawdowns |
| Order types | Ch. 3 | 27 | Media | Base para `Order` |
| Shorting constraints | Ch. 3 | 28 | Alta | Necesario para small caps y shorts |
| Commission | Ch. 3 | 28 | Alta | Cost model minimo |
| Slippage | Ch. 3 | 28-29 | Alta | Fill model minimo |
| Market impact | Ch. 3 | 29 | Alta | Aplazable en v0.1, obligatorio antes de edge |
| Event-driven backtesting | Ch. 4, Ch. 14 | 32, 138-164 | Critica | Patron central del motor |
| Code reuse backtest/live | Ch. 14 | 139, 144, 170 | Critica | Misma interfaz historico/live |
| Event queue | Ch. 14 | 140-164 | Critica | Routing temporal de eventos |
| MarketEvent | Ch. 14 | 140-141 | Critica | Evento de nueva data |
| SignalEvent | Ch. 14 | 141 | Critica | Separar decision de orden |
| OrderEvent | Ch. 14 | 142 | Critica | Orden teorica |
| FillEvent | Ch. 14 | 142-143 | Critica | Ejecucion y contabilidad |
| DataHandler | Ch. 14 | 144-149 | Critica | Interfaz historico/live |
| HistoricCSVDataHandler | Ch. 14 | 146-149 | Media | Sustituir por Parquet/DuckDB/Polars |
| Strategy interface | Ch. 14 | 149-151 | Critica | Genera signals, no fills |
| Portfolio | Ch. 14 | 151-158 | Alta | Mantiene posiciones/holdings y genera ordenes |
| ExecutionHandler | Ch. 14 | 159-170 | Critica | Simulado o broker |
| Backtest loop | Ch. 14 | 161-164 | Critica | Heartbeat y routing |
| Broker adapter | Ch. 14 | 164-170 | Alta | Ejemplo IB; TSIS usara DAS |
| Securities master | Ch. 7 | 56-69 | Alta | Identidad, vendor, exchange, precios |
| Corporate actions | Ch. 7 | 59 | Alta | Splits/dividends point-in-time |
| Holidays | Ch. 7 | 59 | Media | Calendarios y missing-data checks |
| Data automation | Ch. 7 | 60 | Alta | Ingestion reproducible |
| Data frequency | Ch. 8 | 72-73 | Alta | Daily/minute/tick condicionan arquitectura |
| Tick data | Ch. 8 | 73 | Alta | Futura capa trades/quotes |
| Order book | Ch. 8 | 73 | Alta | No v0.1, si para microestructura |
| Data cleaning | Ch. 8 | 83-84 | Alta | Validacion previa al backtest |
| Statistical learning | Ch. 9 | 90-94 | Media | Research/model layer |
| ADF test | Ch. 10 | 96-98 | Media | Mean reversion screening |
| Hurst exponent | Ch. 10 | 98-100 | Media | Trending vs mean reversion |
| Cointegration | Ch. 10 | 100-105 | Media | Pairs trading |
| Forecasting | Ch. 11 | 106-115 | Media | Feature/model examples |
| Hit rate | Ch. 11 | 106-107 | Media | Model metric, no suficiente para P&L |
| Confusion matrix | Ch. 11 | 107 | Media | Directional classifier diagnostics |
| Equity curve | Ch. 12 | 121 | Alta | Output minimo |
| Sharpe ratio | Ch. 12 | 122-125 | Media | Basico, no DSR |
| Drawdown | Ch. 12 | 126-127 | Alta | Metrica critica |
| Strategy risk | Ch. 13 | 128-129 | Alta | Risk model |
| Portfolio risk | Ch. 13 | 129 | Alta | Exposure/factor risk |
| Operational risk | Ch. 13 | 130 | Alta | Arquitectura y SPOF |
| Kelly Criterion | Ch. 13 | 130-132 | Baja-media | Sizing avanzado, usar con cautela |
| VaR | Ch. 13 | 132-133 | Media | Riesgo portfolio |
| Moving average crossover | Ch. 15 | 172-176 | Alta | Smoke test simple |
| Forecasting strategy | Ch. 15 | 177-181 | Media | Predictor integrado en Strategy |
| Mean-reverting pairs | Ch. 15 | 181-188 | Media | Ejemplo intradia |
| Strategy optimisation | Ch. 16 | 190-203 | Alta | Experiment runner |
| Cross-validation | Ch. 16 | 192-198 | Media | Modernizar con time-series CV |
| Grid search | Ch. 16 | 198-203 | Alta | Parameter sweep |
| Overfitting | Ch. 16 | 190-197 | Alta | Conectar con Lopez de Prado |
