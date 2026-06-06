# Ohlcv 1m Split-Normalized - Final Readout `v0_1`

## 1. Rol

Este documento cierra el paquete inspector de:

- `ohlcv_1m_split_normalized`

No sustituye:

- el contrato;
- el piloto semantico;
- ni los readouts detallados caso por caso.

Los integra en una lectura final unica para inspector.

## 2. Que estamos auditando

La pregunta no es:

- "se reescalaron precios?"

La pregunta correcta es:

- la capa reescala solo donde la logica temporal del split lo exige?
- deja neutro lo que debe quedar neutro?
- y, cuando un consumidor real compara sesiones, evita falsos gaps y falsos shocks de regimen?

## 3. Artefactos principales

### Contrato y semantica

- [ohlcv_1m_split_normalized_dataset_contract_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md>)
- [ohlcv_1m_split_normalized_operational_landing_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md>)
- [ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md>)

### Piloto semantico de la capa

- [ohlcv_1m_split_normalized_semantic_pilot_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_semantic_pilot_v0_1.md>)
- [ohlcv_1m_split_normalized_pilot_results_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_results_v0_1.md>)
- [ohlcv_1m_split_normalized_pilot_readout_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_pilot_readout_v0_1.md>)
- [ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_inspection_notebook_v0_1.ipynb>)
- [ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1.md>)
- [ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_full_universe_audit_notebook_v0_1.ipynb>)

### Consumidor minimo de validacion

- [intraday_regime_features_consumer_contract_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/intraday_regime_features_consumer_contract_v0_1.md>)
- [intraday_regime_features_semantic_pilot_results_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/intraday_regime_features_semantic_pilot_results_v0_1.md>)
- [intraday_regime_features_semantic_pilot_readout_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md>)

## 4. Semantica contractual que debe cumplirse

La capa no pretende ser:

- una serie economica completa ajustada por dividendos;
- ni una sustitucion de `1m raw`.

Pretende exactamente esto:

- reexpresar observaciones anteriores a un split futuro en la escala posterior al split

mediante la regla:

- `px_split_normalized = px_raw * future_split_factor`

donde:

- `future_split_factor(date_t) = producto de todos los split_ratio con execution_date > date_t`

## 5. Resumen cuantitativo del piloto de capa

Universo piloto materializado:

- `10` casos `ticker-month`
- `4` reverse splits
- `4` forward splits
- `2` controles

Hechos importantes observados:

- `BXRX 2022-12` -> `rows = 7424`, `split_non1_rows = 0`
- `COSM 2022-12` -> `16986`, `9929`
- `CEI 2022-12` -> `15660`, `10956`
- `BNGO 2025-01` -> `10560`, `9256`
- `LIVE 2014-02` -> `7038`, `7038`
- `BXRX 2022-11` control pre-evento -> `3801`, `3801`
- `BNGO 2025-02` control post-evento -> `2724`, `0`

## 6. Lectura tecnica del piloto de capa

### Que demuestra

- un evento al inicio del mes puede dar `0` filas reescaladas sin contradiccion;
- un evento tardio puede dejar `>80%` del mes reescalado;
- un control pre-evento puede ser `100%` no neutro en factor;
- y un control post-evento puede ser `100%` neutro.

### Que significa

Esto demuestra que la capa no esta aplicando una regla superficial del tipo:

- "mes con split = tocar siempre"

La regla que si estamos viendo en los datos es:

- "toda observacion anterior al split futuro debe reescalarse, y ninguna posterior debe arrastrar ese factor"

## 7. Paso fuerte de auditoria: consumidor real minimo

La auditoria no se cierra solo mirando precios.

Se cierra cuando una comparacion downstream sensible al problema deja de contaminarse.

Para eso se construyo el consumidor minimo:

- `intraday_regime_features`

No como sistema de alpha ni de estrategia final, sino como prueba de uso real para features cross-session.

## 8. Resumen cuantitativo del consumidor

Comparando las mismas features cross-session calculadas:

- con `1m raw` como contrafactual
- frente a `1m_split_normalized` como vista contractual

se obtiene:

### Casos positivos fuertes

- `BNGO 2025-01` -> `max_abs_gap_diff_pct = 5183.28%`
- `CEI 2022-12` -> `4900.00%`
- `BXRX 2022-12` -> `3897.11%`
- `COSM 2022-12` -> `2450.70%`
- `EFSH 2025-01` -> `111.76%`
- `LIVE 2014-02` -> `66.67%`

### Casos frontera coherentes

- `PD 2006-03` -> `49.81%`
- `SAVA 2023-12` -> `28.49%`

### Controles

- `BXRX 2022-11` -> `0.00%`
- `BNGO 2025-02` -> `0.00%`

## 9. Lectura tecnica del consumidor

El resultado importante no es que "las features cambian mucho".

El resultado importante es mas preciso:

- cambian mucho cuando un split contaminaria una comparacion entre sesiones;
- no cambian cuando la ventana ya es homogenea o neutra;
- y por tanto la capa elimina justo la familia de falsos shocks que prometia eliminar.

Esto es la prueba fuerte de que `1m_split_normalized` no es decoracion semantica.

Es una vista que corrige un error downstream real.

## 10. Veredicto final

### Que ya puede afirmarse

Con la evidencia actual ya puede afirmarse, de forma institucionalmente defendible, que:

- la semantica de `1m_split_normalized` esta bien definida;
- la implementacion observada en el piloto la respeta;
- los controles no la contradicen;
- la inspeccion visual la hace auditable;
- y un consumidor minimo real confirma que la capa evita falsos gaps y falsos shocks cross-session.

### Que no debe afirmarse todavia

No debe afirmarse aun que:

- la capa esta promovida full-universe;
- la validacion agregada masiva ya esta cerrada;
- o que la auditoria completa de todo `1m` ya haya terminado para cualquier consumidor futuro.

## 11. Estado de madurez

Lectura correcta tras este cierre:

- `ohlcv_1m_split_normalized` -> `Nivel 5 - Consumida`

No:

- `Nivel 6 - Promovida`

porque aun faltan:

- expansion mas alla del piloto;
- validacion agregada amplia;
- y promocion operacional estable.

## 12. Consecuencia para inspector

La conclusion prudente y fuerte a la vez es esta:

- no podemos prometer certeza absoluta metafisica;
- si podemos demostrar que, en el perimetro inspeccionado, la capa no esta construida sobre naipes en el aire.

La evidencia hoy ya alcanza para sostener que los casos de split del piloto estan:

- semanticamente bien resueltos;
- visualmente auditados;
- y downstream-validos en un consumidor minimo real.
