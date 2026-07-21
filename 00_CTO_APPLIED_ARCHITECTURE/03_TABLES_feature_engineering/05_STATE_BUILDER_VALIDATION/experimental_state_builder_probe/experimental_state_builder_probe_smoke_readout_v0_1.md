# Experimental State Builder Probe - Smoke Readout v0.1

Status: `smoke_readout_v0_1`
Date: `2026-07-21`
Scope: `non_production_contract_check_only`

Este documento resume el primer smoke del builder experimental.

No es evidencia de produccion.
No autoriza `Market State`.
No autoriza consumo de State.
No autoriza materializacion fisica.

## 1. Reference Run

```text
run_id = experimental_state_builder_probe_v0_1_20260721T091253Z
mode = contract_check_only
allow_data_read = false
dry_run = true
objects_checked = 12
dry_run_resolution_snapshots = 48
overall_status = passed_with_findings_and_expected_blocks
```

Run directory:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\runs\experimental_state_builder_probe_v0_1_20260721T091253Z
```

## 2. Result

```text
fail_count = 0
warn_count = 21
source_warn_count = 21
blocked_expected_count = 1
blocked_capability_leaks = 0
```

Interpretacion:

```text
Document and gate resolution passed.
No blocked capability leaked into active probe capabilities.
Order Flow Pressure remains correctly blocked.
The first discovered engineering gap is source physical binding.
```

## 3. Primary Finding

El probe detecto que los source aliases activos no tienen todavia binding
fisico gobernado dentro de la config experimental:

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
015_microstructure_features_table_candidate
010_news_context_table
009_fundamentals_asof_table
011_short_context_table
012_regime_context_table
006_halts_table
raw_quotes
```

Este no es un fallo de la ontologia.
Es el primer gap de ingenieria descubierto por el builder experimental.

## 4. Expected Block

`Order Flow Pressure` queda bloqueado correctamente hasta:

```text
trade_quote_alignment_policy
side_classifier_policy
classifier_confidence_policy
```

## 5. Next Step

Crear un source binding layer experimental, no productivo:

```text
source_alias
    -> governed candidate physical path
    -> expected grain
    -> expected keys
    -> timestamp/as_of fields
    -> minimum schema probe
    -> quality/lineage fields
```

Despues, rerun:

```powershell
python .\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\scripts\experimental_state_builder_probe.py `
  --config .\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\configs\experimental_state_builder_probe_v0_1.json `
  --check-physical-paths `
  --emit-dry-run-rows
```

No activar data reads amplios ni materializacion desde este artefacto.
