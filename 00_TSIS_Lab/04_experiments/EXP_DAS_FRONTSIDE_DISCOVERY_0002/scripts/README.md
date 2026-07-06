# Scripts - EXP_DAS_FRONTSIDE_DISCOVERY_0002

Fecha: 2026-07-06

## Script Oficial Actual

```text
build_2026_scanner_from_quote_guarded_1m_v0_1.py
```

Construye el denominador del scanner desde contratos TSIS Lab:

```text
E:/TSIS/data/ohlcv_1m
+ quote-guarded repair shards / manifest
+ master_daily prior_close
+ reference overview market_cap
```

No usa `candidate_events.parquet` ni anchors antiguos del notebook DAS.

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
python "C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\scripts\run_scanner_2026_quote_guarded_monitored_v0_1.py"
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
python "C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\scripts\monitor_scanner_2026_quote_guarded_run_v0_1.py" --run-root "<RUN_ROOT>" --watch
```

Regla: primero comando y monitor; despues run largo.
