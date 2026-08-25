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

`00.MD` y `01.md` son borradores históricos, no contratos ejecutables.

## Estado

`20260824_full_v0_1` está invalidado por auditoría posterior y aislado bajo
`runs/invalidated/`; no alimenta la app. El probe gobernado v0.3 pasa en 8/8
shards. La versión sigue en `implementation_in_progress` mientras se ejecuta y
audita el nuevo censo completo `20260825_full_v0_1`.

La estadística principal usa todas las activaciones. Los episodios con cooldown
son una vista secundaria de ciclos y se publican separadamente.

## Explorador local

Cuando exista un probe o full con certificación terminal `pass`:

```powershell
cd C:\TSIS_Data\05_TSIS_STATISTICS_PATTERNS\app
.\start_atlas_local.ps1
```

Abrir `http://localhost:3000`. El gráfico permite zoom, arrastre, cursor OHLCV,
historial anterior/posterior, volumen inferior y marcas fuera de las mechas.
