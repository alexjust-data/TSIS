# Experimental State Builder Probe

Status: `experimental_probe_scaffold_v0_1`
Date: `2026-07-21`
Scope: `phase_b_non_production_resolution_probe`

Este directorio contiene el primer builder experimental de `TSIS Market
Ontology v1`.

No es un builder de produccion.
No materializa `Market State`.
No autoriza consumo de State.
No cambia schemas.
No promociona datasets.

## Purpose

El probe comprueba si los 12 `Information Objects` congelados pueden recorrer
un primer circuito ejecutable de resolucion:

```text
Formal Admission
    -> Operational Mapping
        -> Builder Validation Design
            -> experimental resolution probe
```

Su objetivo es descubrir:

```text
source availability gaps
source binding gaps
join-key ambiguity
timestamp and cutoff ambiguity
profile resolution failures
missing lineage
quality flag propagation gaps
cross-object naming conflicts
blocked capability leaks
source/schema mismatch
```

## Files

```text
configs/experimental_state_builder_probe_v0_1.json
scripts/experimental_state_builder_probe.py
runs/
```

## Smoke Command

```powershell
python .\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\scripts\experimental_state_builder_probe.py `
  --config .\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\configs\experimental_state_builder_probe_v0_1.json `
  --emit-dry-run-rows
```

Run from:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering
```

## Output

Each run writes under:

```text
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/runs/<run_id>/
```

Expected artifacts:

```text
pre_manifest.json
heartbeat.json
pass_fail_matrix.csv
source_availability_report.csv
blocked_capability_report.csv
lineage_report.json
dry_run_resolution_snapshots.jsonl
experimental_findings.md
final_manifest.json
```


## Reference Smoke Run

```text
run_id = experimental_state_builder_probe_v0_1_20260721T091253Z
overall_status = passed_with_findings_and_expected_blocks
fail_count = 0
warn_count = 21
source_warn_count = 21
blocked_expected_count = 1
blocked_capability_leaks = 0
```

Readout:

```text
experimental_state_builder_probe_smoke_readout_v0_1.md
```

First engineering gap discovered:

```text
active source aliases need governed experimental physical binding
```

## Authority

```text
experimental_builder_allowed = true_as_non_production_resolution_probe
production_builder_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
```

If the scope is expanded into a long run, it must comply with:

```text
C:\TSIS_Data\LONG_RUNNING_OPERATIONS_CONTRACT.md
```
