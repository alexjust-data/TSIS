# Lt1b Universe Schema Contract `v0_1`

## 1. Rol

Este documento fija el schema fisico observado del universo operativo:

- `lt1b_universe_v0_1`

Este universo no pertenece a la familia fisica:

- `E:\TSIS\data\reference`

Es una capa derivada transversal de elegibilidad/cobertura usada para filtrar y auditar datasets del proyecto bajo marco `<1B>`.

## 2. Artefacto canonico observado

Artefacto parquet:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet`

Artefacto CSV equivalente:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.csv`

Summary:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_summary.json`

Run:

- `20260320_market_cap_last_observed_cutoff`

Panel end date:

- `2026-03-09`

## 3. Cobertura observada

Rows:

- `4824`

Tickers unicos:

- `4824`

Composicion segun summary:

- `active_lt_1b_last_classifiable`: `2476`
- `inactive_died_lt_1b`: `2348`

Universo base evaluado:

- `12468`

Otras clases fuera del corte:

- `ge_1b_last_classifiable`: `2837`
- `unclassified_no_market_cap`: `4807`

## 4. Columnas canonicas

### Identidad

- `ticker`: `large_string`

### Ventana PTI operativa

- `first_seen_date`: `timestamp[ms]`
- `last_observed_date`: `timestamp[ms]`

Estas columnas definen la ventana temporal gobernante para filtrar datasets bajo `<1B>`.

Regla:

- no basta con `ticker in lt1b`;
- toda afirmacion de cobertura `<1B>` debe intersectar tambien la fecha o ventana del dataset con `[first_seen_date, last_observed_date]`.

### Ultima observacion disponible

- `last_row_date`: `timestamp[ms]`
- `status_last_row`: `large_string`
- `close_t_last_row`: `double`
- `shares_outstanding_t_last_row`: `double`
- `shares_source_last_row`: `large_string`
- `shares_observed_date_last_row`: `timestamp[ms]`
- `shares_period_end_last_row`: `timestamp[ms]`
- `shares_age_days_last_row`: `double`
- `market_cap_t_last_row`: `double`
- `is_small_cap_t_last_row`: `bool`

### Anchor usado para clasificacion

- `anchor_date_used`: `timestamp[ms]`
- `status_at_anchor`: `large_string`
- `close_t`: `double`
- `shares_outstanding_t`: `double`
- `shares_source`: `large_string`
- `shares_observed_date`: `timestamp[ms]`
- `shares_period_end`: `timestamp[ms]`
- `shares_age_days`: `double`
- `market_cap_t`: `double`
- `is_small_cap_t`: `bool`

### Estado reconstruido y clasificacion

- `status_rebuilt`: `large_string`
- `classification_1b`: `large_string`
- `classification_reason_1b`: `large_string`

Valores canonicos incluidos en el corte:

- `active_lt_1b_last_classifiable`
- `inactive_died_lt_1b`

## 5. Semantica de inclusion

Un ticker entra en `lt1b_universe_v0_1` si pertenece a una de estas clases:

- `active_lt_1b_last_classifiable`
- `inactive_died_lt_1b`

No entran:

- `ge_1b_last_classifiable`
- `unclassified_no_market_cap`

`unclassified_no_market_cap` no debe tratarse como `<1B>`.

## 6. Limitacion importante

Este corte es el universo operativo vigente para auditorias y cobertura `<1B>`.

No sustituye un futuro:

- `population_target_pti`

diario plenamente point-in-time con:

- `market_cap_t` calculado por fecha;
- `is_small_cap_t` por fecha;
- shares point-in-time con LOCF estricto;
- y decision diaria de elegibilidad.

La lectura correcta de esta version es:

- corte operativo `<1B>` por last observed/anchor;
- con ventana PTI por ticker para evitar usar meses fuera de vida observada;
- suficiente para auditorias transversales actuales;
- no equivalente a membership diaria fully PTI por market cap.

## 7. Documentos relacionados

- [lt1b_universe_dataset_contract_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/lt1b_universe_dataset_contract_v0_1.md>)
- [lt1b_universe_consumption_policy.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/lt1b_universe_consumption_policy.md>)
- [lt1b_universe_registry_entry.yaml](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/universes/lt1b_universe_registry_entry.yaml>)
- [raw_1m_lt1b_closeout_recalculation_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md>)
- [ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md>)
