# TRADING_ACTIVITY_RTH_COVERAGE_SIDECAR_SPECIFICATION_v0_2

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_rth_coverage_sidecar_specification` |
| `document_version` | `v0_2` |
| `document_role` | `EXPERIMENTAL_SOURCE_COVERAGE_SIDECAR_SPECIFICATION` |
| `document_status` | `DRAFT_EXECUTABLE_SPECIFICATION` |
| `supersession_history` | `predecessor consolidated and removed 2026-08-07` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `source_id` | `trades_ticks_prod_2005_2026_legacy_rth_reduced` |
| `active_physical_root` | `G:/TSIS/data/trades_ticks_prod_2005_2026` |
| `sunset_trigger` | `MASSIVE_FULL_HISTORY_BACKFILL_AUDITED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Razon de la revision

La inspeccion fisica de los runs demuestra que los manifests no conservan:

```text
page_count per task
next_url terminal flag per task
expected acquisition hash per parquet
```

Sin embargo, el downloader auditado solo emite `DOWNLOADED_OK` o
`DOWNLOADED_EMPTY` despues de que su bucle de `next_url` termina sin error.

Por tanto:

```text
pagination terminal evidence
= terminal task status
  + audited downloader commit
  + audited downloader content hash
```

El SHA-256 fisico puede conservarse como fingerprint de lineage, pero no se
compara contra un hash de adquisicion que nunca fue registrado.

---

## 2. Autoridad del downloader

```text
audited_downloader_commit
= 3121664a5948b93c1d212d5ffedd4f101ac3f8a9

audited_downloader_content_hash
= 7ca8f21c9a8252bb7186d6c1e2a89a6cd0129139

pagination_evidence_mode
= INFERRED_FROM_AUDITED_DOWNLOADER_TERMINAL_RETURN
```

Si el hash o commit no coincide, el gate falla cerrado hasta reauditar el
downloader correspondiente.

---

## 3. Reconciliacion de rutas

Los manifests preservan rutas historicas bajo `C:/TSIS_Data/data`. El builder no
las reescribe ni las trata como ruta activa.

```text
historical_expected_file
= preserved lineage

active_physical_file
= active_physical_root
  / ticker
  / year=YYYY
  / month=MM
  / day=YYYY-MM-DD
  / market.parquet
```

La equivalencia fisica se verifica por identidad de tarea, existencia,
legibilidad, schema y conteo de filas. No se presume por similitud de path.

---

## 4. Gate por tarea

### `DOWNLOADED_OK`

Requiere:

```text
exactly one expected task
exactly one current terminal event
audited downloader identity matches
active parquet exists
parquet metadata is readable
required schema fields are present
manifest rows = parquet metadata rows
```

### `DOWNLOADED_EMPTY`

Requiere:

```text
exactly one expected task
exactly one current terminal event
audited downloader identity matches
manifest rows = 0
```

No requiere crear un parquet vacio.

### `DOWNLOAD_FAIL` o evento ausente

```text
coverage_gate_state = FAIL_UNAVAILABLE
```

---

## 5. Hashes y fingerprints

```text
input manifest SHA-256
= required for executed institutional readout

physical parquet SHA-256
= optional for pilot
= required only when the execution manifest preregisters full hashing

schema fingerprint
= required for DOWNLOADED_OK
```

La ausencia de hash esperado de adquisicion se representa como:

```text
acquisition_hash_comparison_state
= NOT_COMPARABLE_NO_EXPECTED_HASH
```

No degrada por si sola una tarea que satisface el resto del gate.

---

## 6. Inferencia de ventana

Una tarea con `PASS_WITH_RESTRICTIONS` permite inferir cobertura para ventanas
completamente contenidas en RTH, siempre que no exista un outage explicito.

```text
trade_arrival_rate_W
= eligible_trade_count_W / elapsed_window_seconds_W

elapsed_window_seconds_W
= exact duration of registered W
```

No se reduce el denominador por supuesta cobertura parcial.

---

## 7. Outputs minimos

```text
task_key
ticker
trading_date
session
source_dataset_id
source_schema_version
historical_expected_file
active_physical_file
acquisition_status
acquisition_rows
terminal_event_count
downloader_identity_state
pagination_evidence_mode
physical_file_exists
physical_file_readable
physical_row_count
row_count_match
required_schema_state
schema_fingerprint
physical_file_sha256
acquisition_hash_comparison_state
coverage_gate_state
coverage_restriction_reason_codes
window_zero_assertion_capability
```

---

## 8. Tests obligatorios del scaffolding

```text
1. DOWNLOADED_OK with matching readable parquet
2. DOWNLOADED_EMPTY without parquet
3. DOWNLOAD_FAIL
4. missing terminal event
5. row-count mismatch
6. missing required column
7. active root reconstruction ignores historical path as active authority
8. downloader identity mismatch fails closed
9. duplicate terminal events fail closed
10. deterministic output ordering
11. no writes under G:/TSIS/data
```

---

## 9. Estado

```text
SPECIFICATION          = COMPLETE_AS_DRAFT
CODE SCAFFOLDING       = AUTHORIZED
PILOT EXECUTION        = AUTHORIZED_ON_SYNTHETIC_FIXTURES_ONLY
LEGACY FULL EXECUTION  = PENDING_FIXTURE_TESTS_AND_RUN_PREMANIFEST
LEGACY SOURCE GATE     = IN_PROGRESS
MASSIVE BACKFILL       = EXPLICIT_REVALIDATION_TRIGGER
CANONICAL PROMOTION    = NOT_AUTHORIZED
```

