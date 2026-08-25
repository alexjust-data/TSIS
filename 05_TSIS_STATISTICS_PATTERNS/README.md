# 05_TSIS_STATISTICS_PATTERNS

Módulo TSIS de descubrimiento descriptivo de estadísticas y patrones. Su primer
producto es el `Daily Pattern Discovery Atlas`: un censo sobre el universo
auditado de 4.824 tickers. Describe lo observado; no ejecuta operaciones, no
calcula PnL y no presenta frecuencias como probabilidades.

## Autoridad

- Contrato: `DAILY_PATTERN_DISCOVERY_ATLAS_v0_1.md`.
- Experimento: `EXP_DAILY_PATTERN_ATLAS_0001` en `03_TSIS_Lab`.
- Configuración: `configs/daily_pattern_atlas_v0_1.yaml`.
- Motor: `src/tsis_statistics_patterns/`.
- Explorador local: `app/`.
- Tests: `tests/`.
- Próxima optimización: `PRODUCTION_PERFORMANCE_OPTIMIZATION_PLAN_v0_1.md`.

`00.MD` y `01.md` son borradores históricos, no contratos ejecutables.

## Estado

`20260825_full_v0_1` está en `exploratory_report_ready`: operación,
certificación terminal y auditoría independiente terminaron en `pass`. Cubre
4.824 tickers, 9.290.966 sesiones y 4.495.723 sesiones con al menos una
activación. El readout vigente es
`03_TSIS_Lab/04_experiments/EXP_DAILY_PATTERN_ATLAS_0001/FINAL_CENSUS_READOUT_v0_2.md`.

La estadística principal usa todas las activaciones. Los episodios con cooldown
son una vista secundaria de ciclos y se publican separadamente. `D+k` significa
la k-ésima observación disponible del ticker, no un día calendario.

El run `20260824_full_v0_1` está invalidado y aislado bajo `runs/invalidated/`;
no alimenta la app.

## Explorador local

```powershell
cd C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\app
.\start_atlas_local.ps1
```

Abrir `http://localhost:3000`. El launcher selecciona de forma fail-closed el
full `PASS` más reciente. El gráfico permite zoom con rueda, desplazamiento con
arrastre, cursor OHLCV, 120 observaciones anteriores y 60 posteriores, volumen
en panel inferior y marcas fuera de las mechas.