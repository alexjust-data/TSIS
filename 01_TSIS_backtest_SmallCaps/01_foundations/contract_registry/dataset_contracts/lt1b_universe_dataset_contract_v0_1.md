# Lt1b Universe Dataset Contract `v0_1`

## 1. Rol

Este contrato institucionaliza el universo operativo `<1B>` de `01_TSIS_backtest_SmallCaps`.

Su funcion es responder:

- que tickers pertenecen al marco transversal `<1B>`;
- que ventana PTI gobierna cada ticker;
- y como deben filtrarse datasets cuando una afirmacion se declara `<1B>`.

No es un contrato de:

- `reference` raw;
- features;
- labels;
- execution;
- ni estrategia.

## 2. Dataset

Dataset:

- `lt1b_universe_v0_1`

Familia:

- `universes`

Tipo:

- `derived_operational_universe`

Estado:

- `active`
- `canonical_operational_cut`

## 3. Artefactos canonicos

Root:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff`

Parquet canonico:

- `market_cap_cutoff_lt_1b_active_inactive.parquet`

CSV equivalente:

- `market_cap_cutoff_lt_1b_active_inactive.csv`

Summary:

- `market_cap_cutoff_lt_1b_summary.json`

## 4. Cifras oficiales

Run:

- `20260320_market_cap_last_observed_cutoff`

Panel end date:

- `2026-03-09`

Cutoff:

- `<1B`

Universo base:

- `12468`

Tickers incluidos en `<1B>`:

- `4824`

Composicion:

- `active_lt_1b_last_classifiable`: `2476`
- `inactive_died_lt_1b`: `2348`

Fuera del corte:

- `ge_1b_last_classifiable`: `2837`
- `unclassified_no_market_cap`: `4807`

## 5. Semantica de clasificacion

Se incluyen:

- activos cuya ultima clasificacion disponible queda `<1B>`;
- inactivos que murieron siendo `<1B>` en el criterio operativo del run.

No se incluyen:

- tickers con ultima clasificacion `>=1B`;
- tickers sin market cap clasificable.

`unclassified_no_market_cap` no es una clase elegible.

## 6. Ventana PTI

Columnas gobernantes:

- `first_seen_date`
- `last_observed_date`

Toda auditoria o materializacion que declare alcance `<1B>` debe usar:

- ticker incluido;
- y ventana temporal intersectada.

Esto evita:

- survivorship leakage;
- uso de meses fuera de vida observada;
- inclusion de data fuera de la ventana PTI del ticker.

## 7. Relacion con datasets del proyecto

Este universo puede gobernar expected/cobertura para:

- `daily`
- `daily_adjusted`
- `daily_return_labels`
- `ohlcv_1m`
- `ohlcv_1m_split_normalized`
- `intraday_regime_features`
- `quotes`
- `trades`
- `halts`
- `short`
- `additional`
- `financial`
- `reference`

Pero no sustituye los contratos de calidad de esas capas.

## 8. Limitacion institucional

Este corte es suficiente para el marco operativo actual.

No debe venderse como:

- `population_target_pti` diario final;
- reconstruccion diaria completa de market cap por fecha;
- garantia de elegibilidad diaria dinamica.

Si hace falta ese nivel de precision, debe promocionarse una capa posterior:

- `population_target_pti`

## 9. Evidencia relacionada

El uso de este corte ya aparece en:

- [raw_1m_lt1b_closeout_recalculation_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md>)
- [ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md](</C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md>)

El origen metodologico historico vive en:

- `01_research/03_universe_builder/03_universe_builder.md`
- `01_research/02_reference_layer/02_reference_layer.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/00_descarga_universo.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/01_auditoria_1B_general.md`

## 10. Veredicto

`lt1b_universe_v0_1` queda reconocido como el universo operativo canónico `<1B>` vigente para auditorias y materializaciones transversales.

Toda promocion futura `<1B>` debe citar este contrato o una version posterior.
