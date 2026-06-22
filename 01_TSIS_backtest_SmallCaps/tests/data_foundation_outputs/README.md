# Data Foundation Output Tests

Este directorio contiene los tests ejecutables de las tablas objetivo de
`CAPA 1 - DATA FOUNDATION`.

Las tablas viven bajo:

```text
E:/TSIS/data/data_foundation_outputs/
```

Los contratos viven bajo:

```text
01_foundations/module_contracts/outputs/
```

## Tablas objetivo

Aqui deben validarse, como minimo:

- `instrument_master`
- `market_calendar`
- `expected_data_calendar`
- `corporate_actions_table`
- `dataset_certification_matrix`
- `master_daily_table`
- `master_intraday_bar_table`
- `microstructure_features_table`
- `real_time_corporate_event_alerts_table`
- `halts_table`
- `fundamentals_asof_table`
- `news_context_table`
- `short_context_table`
- `regime_context_table`
- `data_quality_report`

## Cinco capas minimas de test

Cada tabla institucional debe tener cinco familias de pruebas.

1. Schema contract test

Valida columnas, tipos, nullability, claves, unicidad, version logica y campos
obligatorios. No basta con que el parquet abra.

2. Manifest and hash test

Valida que el output materializado coincide con su manifest: ruta, `run_id`,
`sha256`, conteos, version, source fingerprints y timestamp de construccion.

3. Source reconciliation test

Reconcilia la tabla contra las fuentes declaradas. Ejemplos: `instrument_master`
contra universe/reference, `market_calendar` contra el parquet oficial XNYS,
`corporate_actions_table` contra splits/dividends/events declarados.

4. Third-party evidence test

Compara una muestra deterministica contra fuentes externas independientes o
evidencia congelada. Ejemplos: SEC EDGAR, NYSE, Nasdaq, OpenFIGI o proveedor
certificado.

Estos tests no deben depender de internet por defecto. Deben usar evidencia
cacheada o requerir una variable como `TSIS_RUN_THIRD_PARTY=1`.

5. Adversarial or mutation test

Inyecta errores controlados y comprueba que el validador falla. Ejemplos:
duplicados, fechas imposibles, `open_utc >= close_utc`, tickers vacios, CIK mal
formateado, outputs sin manifest o hashes incorrectos.

## Criterio contra trampas al solitario

Una tabla no queda institucionalizada porque su propio script diga que esta bien.
Debe haber pruebas que la ataquen desde fuera:

- contrato independiente;
- manifest independiente;
- reconciliacion con fuentes;
- evidencia externa o cacheada;
- mutaciones que demuestren que el test falla cuando debe fallar.

## Evidencia humana

Los tests ejecutables no sustituyen los dossiers visuales. Cuando una tabla o
familia de datos requiere inspeccion humana, el test debe validar que existe la
ruta de evidencia esperada bajo:

```text
01_foundations/data_quality_report/
```

o bajo el dossier especifico definido por contrato.

