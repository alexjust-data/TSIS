# 14_logs

## Objetivo

Guardar la memoria operativa del sistema.

Aquí se registran ejecuciones, errores, advertencias, tiempos de proceso y resultados técnicos.

---

# Qué va aquí

## Logs de pipelines

- descarga de datos
- auditoría
- feature engine
- event engine
- backtests
- ML training
- RL training

## Logs de errores

- archivos faltantes
- schemas incompatibles
- tickers sin datos
- sesiones incompletas
- fallos de ejecución

## Logs de experimentos

- fecha de ejecución
- config usada
- dataset usado
- versión del código
- duración
- resultado técnico

---

# Ejemplos

feature_engine_2026_05_16.log  
audit_missing_sessions_2021.log  
backtest_gapgo_grid_004.log  
offline_rl_training_epoch_012.log  
execution_simulator_errors.log  

---

# Filosofía

Si algo cambia o falla, debe poder rastrearse.

Los logs permiten responder:

- qué se ejecutó
- cuándo
- con qué parámetros
- sobre qué datos
- qué errores aparecieron
- cuánto tardó

---

# Regla importante

No guardar aquí datasets finales.

Sólo trazabilidad técnica.