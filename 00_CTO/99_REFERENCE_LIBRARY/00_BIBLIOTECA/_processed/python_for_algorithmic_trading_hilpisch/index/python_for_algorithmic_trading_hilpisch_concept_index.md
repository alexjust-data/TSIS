# Concept Index - Python for Algorithmic Trading

**book_id:** `python_for_algorithmic_trading_hilpisch`  
**Uso:** localizar conceptos de infraestructura Python, datos, backtesting, streaming y automatizacion.

| Concepto | Seccion | Paginas PDF | Importancia TSIS | Notas |
|---|---|---:|---|---|
| Python infrastructure | Ch. 2 | 57-93 | Alta | Entornos reproducibles |
| Conda environment | Ch. 2 | 60-74 | Media | Registrar environment en manifest |
| Docker container | Ch. 2 | 74-82 | Media | Reproducibilidad/despliegue |
| Cloud instance | Ch. 2 | 82-92 | Media | Deployment remoto |
| Financial data types | Ch. 3 | 95-96 | Alta | Historico/real-time, structured/unstructured |
| CSV/pandas IO | Ch. 3 | 97-105 | Media | Basico, no final TSIS |
| Data APIs | Ch. 3 | 105-126 | Media | Ejemplos Quandl/Eikon |
| HDF5/HDFStore | Ch. 3 | 126-133 | Media | Sustituible por Parquet |
| Time series storage | Ch. 3 | 133-140 | Alta | Particion temporal |
| SQLite storage | Ch. 3 | 140-143 | Media | Consultas SQL simples |
| Vectorization | Ch. 4 | 147-158 | Alta | Research rapido |
| SMA vectorized backtest | Ch. 4 | 158-178 | Media | Prototipo simple |
| Momentum vectorized backtest | Ch. 4 | 178-196 | Media | Prototipo simple |
| Mean reversion vectorized backtest | Ch. 4 | 196-207 | Media | Prototipo simple |
| Data snooping | Ch. 4 | 207-210 | Alta | Conectar con validacion avanzada |
| Overfitting | Ch. 4 | 207-210 | Alta | No confiar en brute force |
| ML prediction | Ch. 5 | 223-310 | Media | Pipeline modelo -> posicion |
| Regression backtesting | Ch. 5 | 225-248 | Media | Ejemplo research |
| Classification backtesting | Ch. 5 | 253-274 | Media | Direction prediction |
| Deep learning backtesting | Ch. 5 | 281-302 | Baja-media | Aplazar |
| Event-based backtesting | Ch. 6 | 314-345 | Critica | Backtesting con loops e incrementalidad |
| Lookahead in vectorized systems | Ch. 6 | 314-315 | Alta | Razones para event-based |
| Path dependency | Ch. 6 | 315-316 | Alta | Estado recursivo |
| BacktestBase | Ch. 6 | 317-324 | Alta | Base class pedagogica |
| Fixed transaction costs | Ch. 6 | 318-328 | Alta | `ftc` |
| Proportional transaction costs | Ch. 6 | 318-328 | Alta | `ptc` |
| Buy/sell methods | Ch. 6 | 320-322 | Alta | Separar en Order/Fill en TSIS |
| Close out position | Ch. 6 | 322-323 | Alta | Final liquidation/accounting |
| Long-only backtest | Ch. 6 | 325-329 | Media | Smoke test |
| Long-short backtest | Ch. 6 | 329-335 | Alta | Position transitions |
| ZeroMQ | Ch. 7 | 348-357 | Media | Streaming pattern |
| PUB-SUB sockets | Ch. 7 | 348-357 | Alta | Live data adapter pattern |
| Tick server/client | Ch. 7 | 350-357 | Alta | Real-time ingestion |
| Online algorithm | Ch. 7 | 358-362 | Critica | Solo conoce pasado/presente |
| Resampling tick to bars | Ch. 7 | 358-360 | Alta | Streaming state |
| Streaming visualization | Ch. 7 | 362-370 | Media | Monitoring |
| Broker API historical data | Ch. 8-9 | 376-444 | Media | Oanda/FXCM examples |
| Market orders via API | Ch. 8-9 | 402-406, 439-442 | Media | BrokerAdapter examples |
| Kelly criterion | Ch. 10 | 446-463 | Media | Capital management, usar con cautela |
| ML-based live strategy | Ch. 10 | 463-491 | Alta | Offline -> online pattern |
| Spread as transaction cost | Ch. 10 | 464-465 | Alta | Cost model |
| Risk analysis | Ch. 10 | 478-483 | Alta | Drawdown, VaR |
| Persisted model object | Ch. 10 | 483-486 | Alta | Model + normalization |
| Deployment | Ch. 10 | 491-504 | Media | Cloud setup |
| Logging | Ch. 10 | 491-495 | Alta | Audit trail |
| Monitoring | Ch. 10 | 491-509 | Alta | Live observability |
