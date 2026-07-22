# 04_ohlcv_1m_closeout

## Objetivo

Este documento acompana al cierre de `ohlcv_1m` y fija la lectura ejecutiva final tras abrir `schema` y `vw`.

## Diagnostico final

`ohlcv_1m` no presenta un unico problema. La lectura correcta queda separada en tres capas:

- `schema` = anomalia estructural conocida
- `vw` = problema economico dominante
- `parse/price invalid` = nucleo duro pequeno

## Politica good review bad

- `good`
  - `RESCUE_SCHEMA_ONLY`
  - `vw_mild_low_ratio`
- `review`
  - `vw_moderate_ratio`
  - `vw_severe_tiny_base`
  - `vw_severe_small_mass`
- `bad`
  - `vw_severe_large_mass_diffuse`
  - `vw_severe_large_mass_persistent`
  - `QUARANTINE_PARSE_INVALID`
  - `QUARANTINE_PRICE_INVALID`

## Uso operativo

### Backtesting

- `good`: entra en el core dataset
- `review`: solo en sensitivity runs
- `bad`: fuera del universo principal

### ML IA

- `good`: base principal
- `review`: usar con flag o menor peso
- `bad`: fuera del train principal; util para anomalia y monitoring

## Estado de cierre

`ohlcv_1m` queda cerrado a nivel de auditoría operativa.

La parte conceptual ya queda cerrada y la parte ejecutiva también:

- `03_ohlcv_1m_root_cause_audit_notebook.ipynb` queda como notebook metodológico
- `04_ohlcv_1m_closeout.ipynb` queda como notebook ejecutivo final
- el `closeout` fue corregido para leer los manifests reales de validación y materialización
- el `closeout` fue validado ejecutando sus celdas contra los artifacts actuales

El siguiente paso ya no es seguir refinando `ohlcv_1m`, sino consumir esta política en backtesting y modelado. Si se quiere ampliar algo más, sería solo una capa adicional de inspección raw puntual sobre casos `vw_severe_large_mass_persistent`.
