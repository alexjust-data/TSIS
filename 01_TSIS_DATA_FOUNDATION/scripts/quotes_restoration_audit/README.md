# Quotes Restoration Audit

Auditor read-only de `G:/TSIS/data/quotes` contra el inventario C pre-merge de
1.767.826 archivos. Verifica cada ruta esperada y cada Parquet restaurado:

- existencia y tamaño;
- igualdad de tamaño con la evidencia histórica;
- cabecera y footer `PAR1`;
- metadata y número de filas;
- schema requerido;
- fecha canónica del path;
- archivos esperados ausentes y archivos adicionales.

El run full es reanudable por ticker, usa ledger SQLite, heartbeat, monitor y
final manifest. No modifica `quotes`, `quotes_` ni la evidencia histórica.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\quotes_restoration_audit\run_quotes_restoration_audit.ps1" -Mode Full -RunId "20260824_quotes_restoration_audit_v0_1" -Workers 4 -HumanAuthorizedFull -Detach
```

## Reconciliación posterior

`finalize_quotes_restoration_reconciliation.py` solo consume inventarios y
ledgers ya cerrados; no vuelve a abrir los Parquet raw. Contrasta el número de
filas restaurado con el inventario histórico y produce colas separadas para:

- ficheros C conocidos y todavía ausentes;
- ticker literal `NA` nunca ejecutado;
- extensión temporal hasta 2026-08-20;
- revalidación independiente de respuestas API vacías con Daily presente.

La unión ejecutable de reparación excluye deliberadamente la última cola: una
respuesta vacía registrada no demuestra corrupción, pero tampoco debe llamarse
ausencia certificada sin una nueva consulta independiente.

## Plan de intervalo completo

`build_quotes_complete_interval_remediation_plan.py` une, sin leer RAW:

- sesiones del intervalo completo nunca consultadas;
- archivos históricos conocidos no vacíos todavía ausentes;
- respuestas vacías con Daily presente pendientes de recheck.

Produce el detalle ticker-fecha exacto y sus intervalos XNYS contiguos. El
manifest cerrado vigente es:

`C:/TSIS_Data/runs/data_ops/quotes_complete_interval_remediation_plan/20260824_quotes_complete_interval_remediation_plan_v0_1/03_closeout/final_manifest.json`
