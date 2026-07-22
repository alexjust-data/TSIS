# OHLCV 1m Quote-Guarded Full Universe Scripts

Estado: v0_1_script_scaffold
Fecha: 2026-07-07

Estos scripts materializan una salida fisica candidate de 1m quote-guarded sin
modificar el raw canonical.

```text
raw canonical:
E:/TSIS/data/ohlcv_1m

salida derivada:
C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1
```

## Regla Operativa

Estos scripts cumplen `C:/TSIS_Data/LONG_RUNNING_OPERATIONS_CONTRACT.md`.

Un agente no debe lanzar full runs largos. Debe entregar comando y monitor al
humano.

## Scripts

```text
qg_full_universe_common.py
build_ohlcv_1m_qg_full_universe_plan_v0_1.py
build_ohlcv_1m_qg_repair_index_v0_1.py
materialize_ohlcv_1m_qg_year_v0_1.py
monitor_ohlcv_1m_qg_year_run_v0_1.py
```

## Flujo Correcto

```text
1. build task plan
2. build repair index
3. materialize year with early inspection checkpoint
4. inspect samples
5. resume/scale only after inspection passes
```

## Comandos Base Para 2026

PowerShell:

```powershell
$runId = "qg_1m_full_2026_v0_1_$(Get-Date -Format yyyyMMddTHHmmssZ)"
$outRoot = "C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_1"
$scriptRoot = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\data_foundation\ohlcv_1m_quote_guarded_full_universe"
```

Crear task plan:

```powershell
python "$scriptRoot\build_ohlcv_1m_qg_full_universe_plan_v0_1.py" --years 2026 --run-id $runId --output-root $outRoot
```

Crear repair index:

```powershell
python "$scriptRoot\build_ohlcv_1m_qg_repair_index_v0_1.py" --years 2026 --run-id $runId --output-root $outRoot
```

Materializar con pausa temprana despues de 3 tickers:

```powershell
python "$scriptRoot\materialize_ohlcv_1m_qg_year_v0_1.py" --year 2026 --run-id $runId --output-root $outRoot --task-plan "$outRoot\_build_runs\$runId\task_plan_year_2026.csv" --repair-index "$outRoot\_build_runs\$runId\repair_index_year_2026.csv" --workers 2 --resume --early-inspection-after-tickers 3 --pause-after-early-inspection
```

Monitor:

```powershell
python "$scriptRoot\monitor_ohlcv_1m_qg_year_run_v0_1.py" --run-root "$outRoot\_build_runs\$runId" --watch --interval-sec 30 --compact
```

## Early Inspection

El materializador escribe:

```text
early_inspection_ready.json
inspection_samples/year=YYYY/<ticker>_summary.json
inspection_samples/year=YYYY/<ticker>_sample_rows.csv
inspection_samples/year=YYYY/<ticker>_repair_rows.csv
```

Uso previsto:

```text
1. lanzar materializador con --pause-after-early-inspection
2. revisar samples y repair_rows
3. confirmar que quote_guarded_repair_applied y OHLC before/after tienen sentido
4. reanudar sin --pause-after-early-inspection
```

Reanudar despues de inspeccion:

```powershell
python "$scriptRoot\materialize_ohlcv_1m_qg_year_v0_1.py" --year 2026 --run-id $runId --output-root $outRoot --task-plan "$outRoot\_build_runs\$runId\task_plan_year_2026.csv" --repair-index "$outRoot\_build_runs\$runId\repair_index_year_2026.csv" --workers 2 --resume --early-inspection-after-tickers 3
```

## Regla De Reparacion

El materializador nunca consulta `repair_manifest_lt1b_v0_1.parquet` por cada
fichero raw.

Solo usa:

```text
repair_index_year_YYYY.csv -> repair shard path por ticker/month
```

Si un ticker/month no tiene shard en el indice, se marca como:

```text
repair_lookup_state = indexed_no_repair_rows
```

Si el indice falta o apunta a un shard inexistente, el script falla cerrado.

## Estado Del Dataset

La salida nace como:

```text
candidate_not_official
full_universe_claim = false
```

No se promociona hasta completar materializacion, validacion anual, validacion
global, inspeccion visual adversarial y lineage completo.
