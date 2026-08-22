# Graphify Refresh Queue for 01_TSIS_DATA_FOUNDATION

## Pending - 2026-08-14 - HIGH - Representation Model execution and certification contract

- **ID:** `GFQ-20260814-FOUNDATION-REPRESENTATION-MATERIALIZATION-CERTIFICATION-001`
- **Estado:** pending
- **Fecha:** 2026-08-14
- **Severidad:** HIGH
- **Scope:** Data Foundation executable requirements and implemented Trading Activity evidence for exact target membership, typed physical-family counts, one cardinality authority, adversarial fixtures, all-shard probes, terminal rehearsal and inherited incident controls
- **Leaf objetivo:** `data_foundation_root` / module contracts / Representation Model materialization execution and certification
- **Archivos afectados:** execution/certification contract; Trading Activity contract, plan builder, verifier, monitor, PROBE/FULL configs and focused tests; Foundations/Data Foundation changelogs; linked CTO protocol/register/lifecycle/handoff/readout.
- **Motivo:** bounded evidence passes 4/4 shards and the FULL v0.3 terminal audit now passes 2,400 TARGET and 7,200/7,200 partitions. Refresh is deferred to the next controlled Graphify window to avoid contention with active SEC acquisition and to exclude runtime telemetry histories.
- **Cierre esperado:** refresh the Data Foundation contract/control/implementation leaf with the terminal evidence package, run diagnostics, update `BUILD_MANIFEST.md` and resolve this entry while preserving promotion false.

## Pending - 2026-08-14 - HIGH - SEC PIT C01 primary tranche 01

- **ID:** `GFQ-20260814-FOUNDATION-SEC-C01-PRIMARY-T01-001`
- **Estado:** pending
- **Fecha:** 2026-08-14
- **Severidad:** HIGH
- **Scope:** hash-bound 250-row C01 primary authorization, gate-matrix provenance, active 127,946-document acquisition, four-state terminal monitor and resume-safe 200-GiB disk boundary
- **Leaf objetivo:** `data_foundation_root` / SEC PIT acquisition authorization and long-operation control
- **Archivos afectados:** `configs/sec_pit_primary_download_authorization_c01_t01_0250_v0_1_20260814.json`; `scripts/sec_pit/authorization.py`; `scripts/sec_pit/run_authorized_primary_acquisition_v0_2.py`; `scripts/sec_pit/monitor_authorized_primary_acquisition_v0_2.ps1`; `scripts/sec_pit/README.md`; focused SEC PIT tests; Data Foundation and CTO launch readouts/changelogs.
- **Motivo:** the executable and semantic corpus now contains an active bounded primary run. Rebuild is deferred until a terminal manifest exists, both to avoid competing with acquisition I/O and to prevent transient telemetry from being represented as final evidence.
- **Cierre esperado:** after terminal audit, refresh the SEC PIT implementation/control leaf, run Graphify diagnostics, update `BUILD_MANIFEST.md` and resolve this entry without ingesting raw objects or heartbeat histories.

## Pending - 2026-08-11 - MEDIUM - SEC PIT audit package builder

- **Estado:** pending
- **Fecha:** 2026-08-11
- **Severidad:** MEDIUM
- **Scope:** reproducible external-package assembly, source snapshotting and ZIP integrity gates
- **Leaf objetivo:** data_foundation_root / SEC PIT audit tooling
- **Archivos afectados:** scripts/sec_pit/build_external_audit_package_v0_1.ps1 and CHANGELOG.md.
- **Motivo:** new audit-delivery tooling was added; official rebuild is deferred to avoid contention with active Trading Activity work.
- **Cierre esperado:** refresh the affected Data Foundation leaf, run diagnostics and update BUILD_MANIFEST.md.

## Pending - 2026-08-11 - HIGH - SEC PIT stratified resolver implementation

- **Estado:** pending
- **Fecha:** 2026-08-11
- **Severidad:** HIGH
- **Scope:** generic SEC PIT identity admission, O/S extraction, ownership parsing, class reconciliation, management-aggregate precedence, explicit blockers and certification audit
- **Leaf objetivo:** data_foundation_root / SEC PIT implementation and resolution community
- **Archivos afectados:** configs/sec_pit_owner_exclusion_stratified_probe_v0_1.json, scripts/sec_pit stratified/O-S/ownership/audit implementations, SEC PIT tests and CHANGELOG.md.
- **Motivo:** code and policy semantics changed; official rebuild is deferred to avoid resource contention with the active Trading Activity materialization.
- **Cierre esperado:** refresh the affected Data Foundation leaf, run diagnostics and update BUILD_MANIFEST.md.

Estado: cola fallback para gobierno comun de Data Foundation. Las ramas
`01_foundations` y `00_data_certification` conservan sus colas mas cercanas
para cambios de sus corpus respectivos.

## Regla

Los cambios comunes con impacto semantico deben cerrar con actualizacion y
diagnostico del leaf afectado o con una entrada `pending` aqui. Los cambios
locales deben usar la cola local mas cercana.

## Pending

### GFQ-20260811-FOUNDATION-TA3-RECOVERY-001 - TA-3 recoverable supervisor

- **Estado:** `pending`
- **Fecha:** `2026-08-11`
- **Severidad:** `HIGH`
- **Scope:** supervision, recovery and telemetry semantics for the authorized
  Trading Activity Stage-8 C++ 240-block materialization
- **Leaf objetivo:** `data_foundation_root` / Trading Activity execution and
  long-running operations community
- **Archivos afectados:**
  `scripts/recover_trading_activity_stage8_cpp_full_materialization.py`,
  `scripts/monitor_long_running_operation.ps1`,
  `tests/test_trading_activity_stage8_cpp_recovery.py`, `CHANGELOG.md`
- **Motivo:** the live recovery supervisor was implemented and launched while
  the governed materialization remains active. A Graphify rebuild was deferred
  to avoid competing for RAM/IO with the two adopted shards.
- **Cierre esperado:** refresh the affected Data Foundation leaf after the
  materialization reaches a terminal state, run Graphify diagnostics and update
  its `BUILD_MANIFEST.md`.
### GFQ-20260805-FOUNDATION-001 - Agent Graphify closeout policy

- **Estado:** `pending`
- **Severidad:** `HIGH`
- **Scope:** gobierno comun de Data Foundation
- **Leaves objetivo:** `foundations_authority`,
  `certification_decisions` y futura fusion `data_foundation_root`
- **Archivos afectados:** `AGENTS.md`, `GRAPHIFY_REFRESH_QUEUE.md`
- **Motivo:** se normalizo la obligacion de actualizar o registrar pending para
  todas las subramas con Graphify. No se reconstruyeron esos leaves.
- **Cierre esperado:** incorporar esta politica al siguiente leaf de gobierno o
  autoridad aplicable y validar la fusion superior.
### GFQ-20260811-FOUNDATION-SEC-PGAC-OS-001 - PGAC Class A O/S implementation

- **Estado:** pending
- **Fecha:** 2026-08-11
- **Severidad:** HIGH
- **Scope:** common SEC PIT extraction, reconciliation, resolver and float-unit semantics.
- **Leaf objetivo:** data_foundation_root / SEC PIT Fundamental Context.
- **Archivos afectados:** scripts/sec_pit/class_os_extract.py, ixbrl_class_os_extract.py, class_os_reconcile.py, run_pgac_no_network_os_probe.py, float_estimate.py, resolver.py, SEC PIT tests and CHANGELOG.md.
- **Motivo:** new accession-to-class admission and daily O/S semantics were implemented; Graphify rebuild was deferred to avoid competing with the active Trading Activity materialization.
- **Cierre esperado:** refresh implementation/test relationships, run diagnostics and update BUILD_MANIFEST.md.

### GFQ-20260811-FOUNDATION-SEC-PGAC-OWNER-001 - Generic SEC PIT ownership resolver

- **Estado:** pending
- **Fecha:** 2026-08-11
- **Severidad:** HIGH
- **Scope:** neutral ownership extraction, issuer-name continuity, exact
  multi-class reconciliation, holder deduplication and daily owner-exclusion
  state.
- **Leaf objetivo:** data_foundation_root / SEC PIT Fundamental Context.
- **Archivos afectados:** scripts/sec_pit/ownership_v2.py,
  ownership_class_reconcile.py, holders_v2.py, float_estimate_v2.py,
  run_no_network_owner_exclusion_probe.py, config, tests and CHANGELOG.md.
- **Motivo:** new generic production semantics and fail-closed blocker behavior
  were implemented; no official Graphify leaf rebuild was executed.
- **Cierre esperado:** refresh implementation/test relationships, run
  diagnostics and update BUILD_MANIFEST.md.
