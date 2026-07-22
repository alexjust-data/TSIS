# 15_exports

## Objetivo

Guardar salidas finales listas para usar, compartir, revisar o importar en otras herramientas.

Esta carpeta es la capa de entrega del sistema.

---

# Qué va aquí

## CSVs finales

- mejores trades
- resultados filtrados
- tablas resumidas
- rankings de setups

## Datasets preparados

- datasets para ML
- datasets para Offline RL
- snapshots de estados
- muestras reducidas para análisis externo

## Informes exportables

- PDFs
- HTML reports
- Excel reports
- presentaciones
- archivos para compartir

## Outputs para otras herramientas

- TradeStation
- Excel
- dashboards
- notebooks
- BI tools

---

# Ejemplos

best_gapgo_trades_2020_2026.csv  
offline_rl_dataset_v12.parquet  
meta_labeling_training_sample.csv  
edge_map_low_float.xlsx  
final_strategy_report.pdf  

---

# Filosofía

Exports contiene productos finales.

No debe ser la fuente de verdad del sistema.

La fuente de verdad está en las capas internas del pipeline.

---

# Regla importante

Todo export debe poder reconstruirse desde:

- raw data
- configs
- código
- logs
- outputs internos

---

# Objetivo final

Facilitar consumo externo sin contaminar el pipeline interno.