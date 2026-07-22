# Scripts - EXP_DAS_FRONTSIDE_DISCOVERY_0002

Fecha: 2026-07-07

## Script Oficial Actual

```text
build_2026_scanner_from_qg_full_universe_1m_v0_2.py
```

Construye el denominador del scanner desde la base 1m ya saneada/materializada:

```text
C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1
+ master_daily prior_close
+ reference overview market_cap
```

No usa `candidate_events.parquet`, anchors antiguos del notebook DAS, ni vuelve a aplicar reparaciones quote-guarded fichero a fichero durante el scanner.

## Script Pre-Materializacion / Referencia

```text
build_2026_scanner_from_quote_guarded_1m_v0_1.py
```

Fue el builder puente mientras no existia el universo 1m quote-guarded materializado. Lee raw 1m e intenta aplicar shards/manifests durante el scanner. Desde que 2026 existe en `ohlcv_1m_quote_guarded_full_universe_v0_1`, queda como referencia tecnica, no como ruta preferida.

## Scripts Legacy / Referencia

Los scripts previos que consumen outputs antiguos del DAS quedan como:

```text
legacy_reference_only
```

Pueden servir para comparar, auditar visualmente o entender supuestos historicos, pero no son fuente normativa para el denominador cientifico de `0002`.

## Regla Para Agentes

Antes de crear estadisticas, anchors o panels de este experimento, comprobar que el input viene del denominador nuevo o de un successor declarado. Si un script usa `candidate_events.parquet`, debe marcarse como legacy y no promocionarse.

## Run Monitorizado Full 2026

Para un run largo no se debe lanzar el builder directo sin seguimiento. Usar wrapper gobernado:

```powershell
python "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\scripts\run_scanner_2026_qg_full_universe_monitored_v0_2.py"
```

El wrapper crea:

```text
monitor/pre_manifest.json
monitor/pid_manifest.json
monitor/heartbeat_latest.json
monitor/heartbeat.jsonl
logs/scanner_stdout_stderr.log
outputs/
```

Monitor compacto:

```powershell
python "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\scripts\monitor_scanner_2026_quote_guarded_run_v0_1.py" --run-root "<RUN_ROOT>" --watch
```

Regla: primero comando y monitor; despues run largo. Para 2026, la ruta vigente es `v0_2` sobre `ohlcv_1m_quote_guarded_full_universe_v0_1`.

## Auditoria Del Denominador

Script:

```text
audit_scanner_denominator_v0_1.py
```

Uso:

```powershell
python "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\scripts\audit_scanner_denominator_v0_1.py" --run-root "<RUN_ROOT>"
```

Output principal del run 2026:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/audit/denominator_audit_v0_1.md
```

La auditoria fija la lectura correcta:

```text
scanner candidates = denominador operativo condicionado por scanner
scanner candidates != DAS buenos
scanner candidates != in-play
scanner candidates != outcomes
```

## Anchor Worklist

Script:

```text
build_anchor_worklist_from_denominator_v0_1.py
```

Output del run 2026:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/anchor_worklist/anchor_worklist_from_denominator_v0_1.parquet
```

Este output es el handoff oficial entre denominador scanner y deteccion de anchors.

## Anchor Candidates

Script:

```text
build_das_frontside_anchor_candidates_from_worklist_v0_1.py
```

Input oficial:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/anchor_worklist/anchor_worklist_from_denominator_v0_1.parquet
```

Output oficial v0.1:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/anchor_candidates_v0_1/das_frontside_anchor_candidates_v0_1.parquet
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/anchor_candidates_v0_1/das_frontside_anchor_events_long_v0_1.parquet
```

Comando usado:

```powershell
python "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\scripts\build_das_frontside_anchor_candidates_from_worklist_v0_1.py" --run-root "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z" --output-dir "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z\anchor_candidates_v0_1"
```

Resultado:

```text
case_rows = 152
event_rows = 716
errors = 0
```

Regla para agentes: este script inicia la deteccion estructural candidata. No puede usarse para afirmar edge, in-play oficial ni estrategia valida sin visual audit, outcomes y evaluador posterior.

## Visual Audit Renderer

Script:

```text
render_das_frontside_anchor_candidates_v0_1.py
```

Input oficial:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/anchor_candidates_v0_1/das_frontside_anchor_candidates_v0_1.parquet
```

Output oficial:

```text
evidence/scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z/visual_audit_png_v0_1/
```

Comando usado:

```powershell
python "C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\scripts\render_das_frontside_anchor_candidates_v0_1.py" --overwrite
```

Resultado:

```text
png_count = 152
errors = 0
manifest = visual_inspection_manifest_v0_1.parquet
```

Regla para agentes: este renderer pinta desde `anchor_candidates_v0_1` y desde `ohlcv_1m_quote_guarded_full_universe_v0_1`. No debe mezclar PNGs antiguos, notebook DAS, ni raw 1m sin declarar lineage.
