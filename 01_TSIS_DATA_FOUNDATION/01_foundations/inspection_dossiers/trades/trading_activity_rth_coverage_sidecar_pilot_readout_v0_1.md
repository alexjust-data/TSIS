# Trading Activity RTH Coverage Sidecar Pilot Readout v0.1

## 0. Control

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_rth_coverage_sidecar_pilot_readout` |
| `document_version` | `v0_1` |
| `document_role` | `BOUNDED_PHYSICAL_SOURCE_AUDIT_EVIDENCE` |
| `document_status` | `EXECUTED_PILOT` |
| `run_id` | `trading_activity_rth_coverage_sidecar_pilot_20260806T215945Z` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `full_universe_claim` | `false` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Pregunta

```text
Puede el sidecar candidato reconciliar deterministicamente
estados terminales de adquisicion historicos con el root fisico activo,
distinguir OK de EMPTY y verificar los parquets observados?
```

---

## 2. Artefactos

```text
builder
= 01_TSIS_DATA_FOUNDATION/scripts/
  build_trading_activity_rth_coverage_sidecar.py

specification
= TRADING_ACTIVITY_RTH_COVERAGE_SIDECAR_SPECIFICATION_v0_2.md

pre-manifest
= C:/TSIS_Data/tests/test_runs/
  trading_activity_rth_coverage_sidecar_pilot_20260806T215945Z/
  pre_manifest.json

output CSV SHA-256
= fe457c05f35526571959899dc2f245b92a2bc03b5c04126d00f98f3eb066ab93
```

Source roots:

```text
historical acquisition manifests
= C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/
  trades_lt_1b_download

active physical trades
= G:/TSIS/data/trades_ticks_prod_2005_2026
```

---

## 3. Seleccion

```text
selection mode
= FIRST_EXPECTED_TASKS_IN_DETERMINISTIC_RUN_ORDER

tasks
= 100

tickers
= 2
  AACT: 60
  AAGR: 40

stratified claim
= false
```

---

## 4. Resultado

| Estado de adquisicion | Tareas |
|---|---:|
| `DOWNLOADED_OK` | 83 |
| `DOWNLOADED_EMPTY` | 17 |
| Total | 100 |

```text
coverage_gate_state

PASS_WITH_RESTRICTIONS = 100
FAIL_UNAVAILABLE       = 0
```

Para los 83 casos `DOWNLOADED_OK`:

```text
active parquet exists
= 83 / 83

parquet readable
= 83 / 83

required schema pass
= 83 / 83

manifest rows = parquet metadata rows
= 83 / 83
```

Para los 17 casos `DOWNLOADED_EMPTY`:

```text
manifest rows = 0
= 17 / 17

empty parquet required
= no
```

---

## 5. Tests sinteticos

```text
pytest target
= 01_TSIS_DATA_FOUNDATION/tests/
  test_trading_activity_rth_coverage_sidecar.py

result
= 4 passed
```

Los fixtures cubren:

```text
DOWNLOADED_OK
DOWNLOADED_EMPTY
DOWNLOAD_FAIL
missing terminal event
active-root reconstruction
downloader identity mismatch
deterministic ordering
```

---

## 6. Que demuestra

```text
PASS

historical task identity can be reconciled
historical C: paths are preserved as lineage only
active G: paths can be reconstructed deterministically
OK parquet metadata can be read
manifest and parquet row counts can be reconciled
EMPTY remains distinct from missing or failure
audited downloader identity can govern pagination inference
```

---

## 7. Que no demuestra

```text
full-universe completeness
all ten shards
all years or schema regimes
real DOWNLOAD_FAIL reconciliation
real duplicate terminal-event handling
provider-internal feed completeness
intraday heartbeat coverage
condition-code eligibility
exchange semantic completeness
full input or parquet hashing
premarket or after-hours coverage
first Wake-up of the complete episode
```

---

## 8. Veredicto

```text
SIDECAR CODE SCAFFOLDING
= PASS

SYNTHETIC FIXTURES
= PASS

BOUNDED PHYSICAL PILOT
= PASS_WITH_RESTRICTIONS

LEGACY SOURCE GATE
= IN_PROGRESS

BINDING A EXPERIMENTAL EXECUTION
= NOT_AUTHORIZED_YET

MASSIVE BACKFILL
= DEFERRED_PENDING_MASSIVE_BACKFILL

CANONICAL PROMOTION
= NOT_AUTHORIZED
```

---

## 9. Siguiente evidencia requerida

```text
1. targeted real failures and missing-task reconciliation;
2. condition-code snapshot and unknown-code fixture;
3. exchange snapshot and ID coverage;
4. schema fingerprints across effective periods;
5. remaining TA-ST fixture closure;
6. preregistered bounded multi-shard pilot;
7. full sidecar run only under the Long Running Operations Contract.
```

La futura descarga Massive obliga a reauditar este sidecar y no permite
sobrescribir sus outputs legacy.

