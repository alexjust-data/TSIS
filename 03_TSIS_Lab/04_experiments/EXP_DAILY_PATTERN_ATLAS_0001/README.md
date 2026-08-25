# EXP_DAILY_PATTERN_ATLAS_0001

Research experiment gobernado del `Daily Pattern Discovery Atlas`, módulo
`05_TSIS_STATISTICS_PATTERNS`. Produce evidencia descriptiva exploratoria; no
produce estrategia, probabilidad, backtest o conocimiento validado.

## Estado

`exploratory_report_ready`.

El censo corregido `20260825_full_v0_1` terminó con `PASS` operacional,
certificación terminal `PASS` y auditoría independiente `PASS`:

- 4.824 tickers;
- 9.290.966 sesiones entre 2005-01-03 y 2026-03-06;
- 9.728.326 etiquetas de activación;
- 4.495.723 sesiones de activación distintas;
- 422.042 ciclos retrospectivos con cooldown;
- 8.817.239 filas de trayectoria de ciclos;
- 2.529.142 eventos de ciclos.

La estadística principal de `cohort_statistics.parquet` usa todas las
activaciones. `cycle_cohort_statistics.parquet` conserva por separado la vista
secundaria de ciclos seleccionados por cooldown.

El readout vigente es `FINAL_CENSUS_READOUT_v0_2.md`. Las fórmulas auditadas
tuvieron error máximo 0, los 4.824 parts de cada tabla presentaron un solo
schema físico y no se observaron infinitos ni contaminación de outcomes.

El run `20260824_full_v0_1` permanece invalidado bajo
`runs/invalidated/20260824_full_v0_1_post_run_audit_fail` y no puede alimentar
la app ni ningún readout vigente.