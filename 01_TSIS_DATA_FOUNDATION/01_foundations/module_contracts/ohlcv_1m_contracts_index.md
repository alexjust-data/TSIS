# OHLCV 1m Contracts Index

## Rol

Indice navegable de documentos especificos de `ohlcv_1m` y de consumidores nacidos para validar o usar `ohlcv_1m_split_normalized`.

## `ohlcv_1m_raw` foundation

- `../contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md`
- `../dataset_registry/ohlcv_1m/ohlcv_1m_raw_registry_entry.yaml`
- `../data_consumption_policies/ohlcv_1m_raw_consumption_policy.md`
- `../validators/ohlcv_1m/ohlcv_1m_raw_validators.md`
- `ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`

## `ohlcv_1m_quote_guarded` workstream

- `../contract_registry/dataset_contracts/ohlcv_1m_quote_guarded_dataset_contract_v0_1.md`
- `../dataset_registry/ohlcv_1m/ohlcv_1m_quote_guarded_registry_entry.yaml`
- `../data_consumption_policies/ohlcv_1m_quote_guarded_consumption_policy.md`
- `ohlcv_1m_quote_guarded/README.md`
- `ohlcv_1m_quote_guarded/ohlcv_1m_quote_guarded_single_reading_v0_1.md`
- `ohlcv_1m_quote_guarded/ohlcv_1m_quote_guarded_repair_runbook_v0_1.md`

Estado: manifest LT1B promovido el 2026-07-03 como overlay quote-guarded.
No autoriza mutacion de `ohlcv_1m_raw`.

Estado fisico actual: `ohlcv_1m_quote_guarded_full_universe_v0_2_candidate`
esta validado como `validated_candidate_for_controlled_downstream_consumption`
con `PASS`, `errors=0`, `schema_mismatches=0` y 1,272,004 ficheros vistos. Se
autoriza como input controlado para builds candidatos downstream; no es
promocion institucional irrestricta ni sustituto de raw/trades/quotes.

## `ohlcv_1m_split_normalized`

- `ohlcv_1m_split_normalized_operational_landing_v0_1.md`
- `ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md`
- `ohlcv_1m_split_normalized_semantic_pilot_v0_1.md`
- `ohlcv_1m_split_normalized_pilot_manifest_v0_2.md`
- `ohlcv_1m_split_normalized_pilot_results_v0_1.md`

## Primer consumidor de `ohlcv_1m_split_normalized`

- `intraday_regime_features_consumer_contract_v0_1.md`
- `intraday_regime_features_variable_taxonomy_v0_1.md`
- `intraday_regime_features_operational_landing_v0_1.md`
- `intraday_regime_features_initial_materialization_results_v0_1.md`
- `intraday_regime_features_semantic_pilot_results_v0_1.md`
- `intraday_regime_features_deferred_families_v0_1.md`
