# Daily Return Labels Dataset Contract `v0_1`

## 1. Rol

Este contrato registra `daily_return_labels_v0_1` como dataset derivado piloto de labels diarios.

Su funcion es construir targets economicos comparables desde:

- `daily_adjusted_v0_1`

No define:

- features;
- estrategia;
- simulador;
- policy RL;
- ni edge economico.

## 2. Dataset

Dataset:

- `daily_return_labels_v0_1`

Raiz operativa:

- `E:\TSIS\data\daily_return_labels`

Grano:

- `ticker-day`

Estado:

- `pilot_materialization`
- `pilot_target_layer`

## 3. Fuentes

Fuente obligatoria:

- `E:\TSIS\data\ohlcv_daily_adjusted`

Vista obligatoria:

- `daily_adjusted_v0_1`

Columna obligatoria:

- `c_adjusted`

Fuente prohibida para esta semantica:

- `daily_raw`
- `c`

## 4. Cobertura actual

Cobertura fisica observada:

- `10` tickers piloto;
- `177` parquets;
- years `2005-2026`;
- `41487` rows segun summary agregado;
- summary: `E:\TSIS\data\daily_return_labels\_labels_materialization_summary.csv`.

Tickers:

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

No es:

- full-universe `<1B>`;
- target layer global;
- backtest core promovido;
- ML primary promovido.

## 5. Labels contratados

Labels iniciales:

- `ret_1d`
- `ret_3d`
- `ret_5d`

Formula:

- `ret_Nd = c_adjusted[t+N] / c_adjusted[t] - 1`

Estos labels representan:

- retorno economico diario comparable del activo.

No representan:

- retorno de una estrategia;
- slippage;
- fill;
- ejecucion;
- liquidez;
- microestructura.

## 6. Regla anti-contaminacion

Los labels son outcomes.

No pueden consumirse como features.

Todo pipeline que use esta capa debe separar explicitamente:

- `X`: datos/features disponibles en decision time;
- `y`: labels forward-looking;
- `evaluation`: comparacion posterior.

## 7. Evidencia existente

Contratos:

- [daily_return_labels_consumer_contract_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/daily_return_labels_consumer_contract_v0_1.md>)
- [daily_return_labels_operational_landing_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/daily_return_labels_operational_landing_v0_1.md>)

Schema:

- [daily_return_labels_schema_contract.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/daily/daily_return_labels_schema_contract.md>)

Policy:

- [daily_return_labels_consumption_policy.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/daily_return_labels_consumption_policy.md>)

## 8. Condicion de promocion futura

La promocion futura requiere:

- versionar universo `<1B>`;
- materializar contra cobertura completa esperada;
- auditar coverage;
- auditar nulos;
- auditar source view;
- auditar que no usa raw;
- separar labels de features en todos los consumidores;
- documentar train/test temporal.

## 9. Veredicto

`daily_return_labels_v0_1` queda reconocido como consumidor piloto correcto de `daily_adjusted`.

No queda reconocido como target layer full-universe promovido.
