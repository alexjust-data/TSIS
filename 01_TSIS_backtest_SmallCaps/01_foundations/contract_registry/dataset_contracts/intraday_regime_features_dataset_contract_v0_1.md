# Intraday Regime Features Dataset Contract `v0_1`

## 1. Rol

Este contrato registra `intraday_regime_features_v0_1` como dataset derivado piloto de features/states intradia.

Su rol actual es conectar:

- `D:\ohlcv_1m`
- `E:\TSIS\data\ohlcv_1m_split_normalized`

para producir features que separan:

- estado intrasesion local observado;
- comparabilidad cross-session protegida contra splits.

## 2. Dataset

Dataset:

- `intraday_regime_features_v0_1`

Raiz operativa:

- `E:\TSIS\data\intraday_regime_features`

Grano actual:

- `ticker-day`

Estado:

- `Nivel 3 - Pilotada`
- `pilot_semantic_validation_consumer`

## 3. Fuentes

Fuentes obligatorias:

- `D:\ohlcv_1m`
- `E:\TSIS\data\ohlcv_1m_split_normalized`

Fuentes no incluidas todavia:

- `quotes_raw`
- `trades_raw`
- `halts`
- `daily_adjusted`
- eventos/catalysts

Estas fuentes podran entrar en familias posteriores, pero no forman parte de este contrato minimo.

## 4. Cobertura actual

Cobertura fisica actual:

- 8 tickers piloto;
- 8 parquets de salida;
- 243 filas `ticker-day` segun summary observado;
- universo seleccionado para validar el efecto downstream de splits.

No es:

- full-universe `<1B>`;
- cobertura completa 2005-2026;
- feature layer final de backtest.

## 5. Obligaciones semanticas

Las features cross-session deben usar `1m_split_normalized`.

Las features intrasesion locales deben usar `1m raw`.

La razon institucional es evitar que ML/backtest aprenda:

- gaps falsos;
- shocks falsos de regimen;
- extension falsa;
- o alpha falso generado por splits/reverse splits.

## 6. Evidencia existente

Evidencia de materializacion:

- [intraday_regime_features_initial_materialization_results_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/intraday_regime_features_initial_materialization_results_v0_1.md>)

Evidencia de piloto semantico:

- [intraday_regime_features_semantic_pilot_results_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/intraday_regime_features_semantic_pilot_results_v0_1.md>)
- [intraday_regime_features_semantic_pilot_readout_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md>)

Schema fisico:

- [intraday_regime_features_schema_contract.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/features/intraday_regime_features_schema_contract.md>)

Policy de consumo:

- [intraday_regime_features_consumption_policy.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/intraday_regime_features_consumption_policy.md>)

## 7. Condicion de promocion futura

La promocion futura requiere un contrato nuevo o una version superior que cierre:

- coverage full-universe o universo `<1B>` definido;
- validacion agregada masiva;
- leakage policy;
- integracion con backtest/ML;
- y decision sobre si la capa vive a grano `ticker-day` o `ticker-minute`.

## 8. Veredicto

`intraday_regime_features_v0_1` queda institucionalmente reconocida como consumidor piloto validado y relevante para la arquitectura TSIS.

No queda promovida todavia como dataset full-universe de research/backtest.
