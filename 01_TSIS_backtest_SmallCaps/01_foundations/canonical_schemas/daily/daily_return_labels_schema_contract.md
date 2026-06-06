# Daily Return Labels Schema Contract `v0_1`

## 1. Rol

Este documento fija el schema fisico observado de:

- `daily_return_labels_v0_1`

La capa representa labels diarios derivados desde `daily_adjusted`.

No representa:

- features;
- senales;
- ejecucion;
- alpha validado;
- ni una capa full-universe `<1B>` promovida.

## 2. Raiz fisica observada

Raiz:

- `E:\TSIS\data\daily_return_labels`

Layout observado:

- `ticker=<TICKER>\year=<YYYY>\day_aggs_<TICKER>_<YYYY>_labels.parquet`

Summary observado:

- `E:\TSIS\data\daily_return_labels\_labels_materialization_summary.csv`

Muestra inspeccionada:

- `E:\TSIS\data\daily_return_labels\ticker=A\year=2005\day_aggs_A_2005_labels.parquet`

## 3. Cobertura fisica observada

Cobertura observada:

- `177` parquets;
- `10` tickers;
- years observados: `2005-2026`;
- fuente fisica: `E:\TSIS\data\ohlcv_daily_adjusted`;
- source file metadata apunta a `D:\ohlcv_daily`.

Tickers piloto:

- `A`
- `AAME`
- `ABEO`
- `ABIO`
- `ABTX`
- `BBW`
- `CASS`
- `CVLY`
- `SELF`
- `SGC`

Rows por summary:

- `A`: `5327`
- `AAME`: `4949`
- `ABEO`: `2693`
- `ABIO`: `3925`
- `ABTX`: `1758`
- `BBW`: `5327`
- `CASS`: `5241`
- `CVLY`: `4420`
- `SELF`: `2548`
- `SGC`: `5199`

Lectura institucional:

- es una materializacion piloto amplia en años pero estrecha en tickers;
- no es full-universe `<1B>`;
- no es target layer global lista para ML/backtest;
- si es el primer consumidor real de `daily_adjusted` para labels diarios.

## 4. Columnas canonicas

### Identidad y grano

- `ticker`: `string`
- `date`: `timestamp[ns]`
- `year`: `int64`

Grano:

- `ticker-day`

### Base economica ajustada

- `c_adjusted`: `double`
- `materialized_price_view`: `string`
- `source_daily_file`: `string`

Valores esperados:

- `materialized_price_view = daily_adjusted_v0_1`
- `source_daily_file` debe apuntar al parquet daily raw fuente usado para construir la vista ajustada.

### Labels

- `ret_1d`: `double`
- `ret_3d`: `double`
- `ret_5d`: `double`

Definicion contractual:

- `ret_1d = c_adjusted[t+1] / c_adjusted[t] - 1`
- `ret_3d = c_adjusted[t+3] / c_adjusted[t] - 1`
- `ret_5d = c_adjusted[t+5] / c_adjusted[t] - 1`

### Provenance

- `label_source_view`: `string`
- `label_contract`: `string`

Valores esperados:

- `label_source_view = daily_adjusted_v0_1`
- `label_contract = daily_return_labels_v0_1`

## 5. Nulos esperados

Los ultimos rows de cada serie anual/ticker pueden tener nulos por horizonte futuro insuficiente:

- `ret_1d`: hasta `1` nulo final;
- `ret_3d`: hasta `3` nulos finales;
- `ret_5d`: hasta `5` nulos finales.

Estos nulos no son automaticamente error.

Son consecuencia natural de construir labels forward-looking.

## 6. Semantica obligatoria

Los labels deben calcularse desde:

- `c_adjusted`

No deben calcularse desde:

- `c` raw

Razon:

- un split o reverse split puede parecer retorno enorme;
- un dividendo puede parecer caida economica falsa;
- y el modelo puede aprender corporate actions como si fueran alpha.

## 7. Regla anti-leakage

Estos labels son targets forward-looking.

No pueden entrar como input feature en:

- backtest;
- ML;
- ranking;
- filtros;
- live;
- RL.

Solo pueden usarse como:

- target;
- outcome;
- evaluacion;
- benchmark de resultado;
- variable de entrenamiento en el lado `y`, nunca en `X`.

## 8. Estado institucional

Estado correcto:

- `pilot_materialization`
- `pilot_target_layer`

Estados no autorizados:

- `full_universe_target_layer`
- `backtest_core_promoted`
- `ml_primary_full_universe`
- `execution_signal`

## 9. Documentos relacionados

- [daily_return_labels_consumer_contract_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/daily_return_labels_consumer_contract_v0_1.md>)
- [daily_return_labels_operational_landing_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/daily_return_labels_operational_landing_v0_1.md>)
- [daily_return_labels_dataset_contract_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/daily_return_labels_dataset_contract_v0_1.md>)
- [daily_return_labels_consumption_policy.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/daily_return_labels_consumption_policy.md>)
