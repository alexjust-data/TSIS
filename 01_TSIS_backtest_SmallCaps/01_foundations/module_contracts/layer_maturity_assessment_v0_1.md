# Layer Maturity Assessment v0.1

## 1. Rol del documento

Este documento aplica el estandar:

- `01_foundations/module_contracts/layer_validation_standard_v0_1.md`

a tres capas actualmente prioritarias del modulo:

- `daily_adjusted`
- `ohlcv_1m_split_normalized`
- `intraday_regime_features`

Su objetivo no es redefinir los contratos de cada capa.

Su objetivo es dejar explicitamente clasificado:

- en que nivel de madurez esta cada una;
- por que;
- que evidencia lo soporta;
- y que falta para su siguiente promocion.

## 2. Regla de lectura

Los niveles posibles son:

- `Nivel 1 - Definida`
- `Nivel 2 - Implementada`
- `Nivel 3 - Pilotada`
- `Nivel 4 - Auditada`
- `Nivel 5 - Consumida`
- `Nivel 6 - Promovida`

El nivel asignado no es una opinion general.

Debe leerse como el nivel maximo que la capa puede defender hoy con evidencia trazable.

## 3. `daily_adjusted`

### Nivel actual

- `Nivel 6 - Promovida`

### Por que

`daily_adjusted` ya supera:

- contrato de dataset;
- schema contractual;
- materializador real;
- piloto semantico;
- manifest refinado;
- materializacion oficial piloto;
- consumidor real conectado;
- materializacion full-universe contra `D:\ohlcv_daily`;
- y auditoria agregada full-universe sin faltantes fisicos ni roturas contractuales basicas.

### Evidencia principal

- `01_foundations/contract_registry/dataset_contracts/daily_adjusted_dataset_contract_v0_1.md`
- `01_foundations/canonical_schemas/daily/daily_adjusted_schema_contract.md`
- `scripts/materialize_daily_adjusted.py`
- `01_foundations/module_contracts/daily_adjusted_incremental_materialization_plan_v0_1.md`
- `01_foundations/module_contracts/daily_adjusted_pilot_results_v0_2.md`
- `E:\TSIS\data\ohlcv_daily_adjusted`
- `scripts/materialize_daily_return_labels.py`
- `01_foundations/module_contracts/daily_return_labels_consumer_contract_v0_1.md`
- `E:\TSIS\data\daily_return_labels`
- `01_foundations/module_contracts/daily_adjusted_full_universe_promotion_plan_v0_1.md`
- `01_foundations/inspection_dossiers/daily/daily_adjusted_full_universe_audit_v0_1.md`
- `01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml`

### Lectura tecnica

La capa ya no esta solo "bien definida".

Ya demostro dos cosas que importan:

- que ajusta correctamente en casos con splits y dividendos;
- y que un consumidor real ya la usa para evitar labels contaminados por corporate actions.

Eso basta para considerarla:

- consumida;
- y ahora tambien promovida como vista derivada diaria full-universe.

La promocion no cambia su rol semantico:

- sigue siendo verdad economica lenta;
- no es vista de ejecucion;
- no reemplaza `quotes_raw`, `trades_raw` ni el tape intradia;
- y no habilita automaticamente `rl_allowed` ni `live_downstream_candidate`.

### Evidencia de promocion full-universe

La auditoria full-universe actualizada fija:

- `raw_tickers_with_files = 12230`
- `adjusted_tickers_with_files = 12230`
- `raw_year_files = 125438`
- `adjusted_year_files = 125438`
- `missing_outputs = 0`
- `extra_adjusted_outputs = 0`
- `read_error_files = 0`
- `files_missing_required_columns = 0`
- `nonpositive_factor_rows = 0`
- `bad_price_view_rows = 0`

### Que queda despues de `Nivel 6 - Promovida`

- monitorizar reruns o reparaciones incrementales con disciplina de no-overwrite;
- mantener la frontera de corporate actions complejos documentada;
- y conectar consumidores posteriores (`backtest_core`, benchmark diario) de forma explicita, sin confundir esta promocion con autorizacion para ejecucion o RL.

## 4. `ohlcv_1m_split_normalized`

### Nivel actual

- `Nivel 5 - Consumida`

### Por que

`ohlcv_1m_split_normalized` ya supera:

- contrato explicito;
- landing operacional;
- plan incremental;
- materializador real;
- piloto semantico;
- manifest real por `ticker-month`;
- materializacion piloto;
- resultados tecnicos;
- y readout visual auditable caso por caso.

### Evidencia principal

- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`
- `scripts/materialize_1m_split_normalized.py`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_semantic_pilot_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`
- `01_foundations/dataset_registry/1m/ohlcv_1m_split_normalized_pilot_manifest_v0_2.csv`
- `E:\TSIS\data\ohlcv_1m_split_normalized`
- `01_foundations/module_contracts/ohlcv_1m_split_normalized_pilot_results_v0_1.md`
- `01_foundations/inspection_dossiers/1m_split_normalized/ohlcv_1m_split_normalized_pilot_readout_v0_1.md`

### Lectura tecnica

La capa ya no es solo una idea ni solo un script.

Ya esta auditada porque:

- la formula del `future_split_factor` esta fijada;
- los edge cases estan explicados;
- los controles pre y post evento tienen interpretacion contractual clara;
- y la lectura visual permite verificar que no estamos inventando continuidad donde no corresponde.

Ahora ya si puede clasificarse como `Consumida` porque:

- existe un consumidor intradia real implementado;
- ese consumidor materializa features cross-session sobre la capa correcta;
- y el piloto semantico del consumidor demuestra que desaparecen falsos gaps y shocks mecanicos donde `raw` habria fabricado senales falsas.

### Que falta para `Nivel 6 - Promovida`

- ampliar cobertura mas alla del universo piloto;
- correr validacion agregada masiva;
- y sostener ya no solo un consumidor piloto, sino una promocion operacional estable.

## 5. `intraday_regime_features`

### Nivel actual

- `Nivel 3 - Pilotada`

### Por que

La capa ya tiene:

- contrato de consumidor;
- taxonomia inicial de variables;
- landing operacional propuesto;
- registry entry;
- y justificacion metodologica/cientifica explicita.
- materializador implementado;
- output persistido inicial;
- y una primera corrida reproducible sobre el universo piloto disponible.

Pero todavia no tiene:

- piloto semantico propio de las features;
- validacion visual dedicada;
- ni una prueba downstream que demuestre mejora explicita sobre falsos gaps o shocks mecanicos.

### Evidencia principal

- `01_foundations/module_contracts/intraday_regime_features_consumer_contract_v0_1.md`
- `01_foundations/module_contracts/intraday_regime_features_variable_taxonomy_v0_1.md`
- `01_foundations/module_contracts/intraday_regime_features_operational_landing_v0_1.md`
- `01_foundations/dataset_registry/features/intraday_regime_features_registry_entry.yaml`
- `scripts/materialize_intraday_regime_features.py`
- `E:\TSIS\data\intraday_regime_features`
- `01_foundations/module_contracts/intraday_regime_features_initial_materialization_results_v0_1.md`

### Lectura tecnica

La capa ya esta bien justificada, implementada y pilotada en su primer formato minimo.

Su valor actual es:

- arquitectonico;
- metodologico;
- y de aterrizaje inicial del primer consumidor real de `1m_split_normalized`.

Importante:

- el nivel `Pilotada` aqui no significa que ya hayamos abierto feature engineering amplio de estrategia;
- significa solo que el consumidor minimo de validacion semantica ya fue implementado y auditado.

### Que falta para `Nivel 4 - Auditada`

- endurecer el readout con mas cobertura o mas familias de features;
- expandir controles mas alla del piloto de splits;
- y dejar una capa de evidencia visual mas rica si el consumidor crece en complejidad.

## 6. Resumen ejecutivo

Estado actual de las tres capas:

- `daily_adjusted` -> `Nivel 6 - Promovida`
- `ohlcv_1m_split_normalized` -> `Nivel 5 - Consumida`
- `intraday_regime_features` -> `Nivel 3 - Pilotada`

### Lectura institucional

La cadena ya esta razonablemente bien escalonada:

- primero cerramos la verdad economica lenta con consumidor real;
- despues auditamos la normalizacion intradia por split;
- y ahora ya podemos abrir el primer consumidor intradia con una base contractual limpia.

### Proximo paso correcto

El siguiente paso con mayor retorno metodologico es:

- ampliar y endurecer la pilotacion de `intraday_regime_features`

porque eso es exactamente lo que permitiria promocionar despues:

- una futura promocion operacional mas amplia de `ohlcv_1m_split_normalized` y del propio consumidor.
