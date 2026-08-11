# SEC PIT PGAC External Audit Package Contents `v0_1`

Date: `2026-08-11`

Status: `UPDATED_AFTER_SEVEN_TICKER_STRATIFIED_PROBE`

Scope: `SEC PIT process, PGAC proof of concept and seven-case stratified evidence`

## Purpose

This package allows an external agent to audit the complete progression from
the original PGAC acquisition pilot to the bounded seven-case O/S, ownership,
holder-reconciliation and owner-exclusion experiment.

The authoritative conclusion is `PARTIAL_PASS_SCALE_BLOCKED`:

- `ALUR`, `BNAI` and `PGAC` produced five causal daily owner-exclusion values;
- `BBBY`, `BGM` and `DOMH` produced explicit NULLs with blockers;
- `CNOBP` halted before acquisition because it is preferred/depositary;
- a 4,824-instrument run remains unauthorized pending adaptive baseline-family
  traversal and one production-equivalent probe per planned execution shard.

The package is evidence for external review. It is not a canonical dataset or
an institutional promotion record.

## Recommended reading order

1. `01_RESULTADO/SEC_PIT_SEVEN_TICKER_OWNER_EXCLUSION_STRATIFIED_PROBE_READOUT_v0_1.md`
2. `01_RESULTADO/SEC_PIT_PGAC_OWNERSHIP_AND_OWNER_EXCLUSION_PROBE_READOUT_v0_1.md`
3. `01_RESULTADO/SEC_PIT_PGAC_NO_NETWORK_OS_PROBE_READOUT_v0_1.md`
4. `02_PROCESO_SEC/SEC_PIT_SEVEN_TICKER_OWNER_EXCLUSION_STRATIFIED_PROBE_PLAN_v0_1.md`
5. `02_PROCESO_SEC/SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md`
6. `06_EVIDENCIA_ESTRATIFICADA_CONTROL/owner_exclusion_certification_audit_v0_1.json`
7. `07_RUNS_OS_V0_5/` and `08_RUNS_OWNER_V0_5/`
8. `09_CODIGO_Y_CONFIG/`
9. `PACKAGE_FILE_MANIFEST.csv` for file-level size and SHA-256 verification.

## Directory meaning

```text
01_RESULTADO
  Human-readable PGAC and stratified results.

02_PROCESO_SEC
  SEC-only contracts, policies, plans and prior implementation readouts.

03_EVIDENCIA_PREDOWNLOAD
  Original bounded predownload control evidence.

04_EVIDENCIA_ADQUISICION_PGAC
  Original PGAC acquisition authorization, manifests and telemetry.

05_SCHEMA_REFERENCIA
  Resolved-daily-state and comparison schemas.

06_EVIDENCIA_ESTRATIFICADA_CONTROL
  Frozen case/selection matrices, reuse/composite ledgers, acquisition
  authorization/telemetry and the cross-run certification audit.

07_RUNS_OS_V0_5
  Authoritative five-session O/S outputs for the six executed cases.

08_RUNS_OWNER_V0_5
  Authoritative ownership, holder/class reconciliation and daily float outputs.

09_CODIGO_Y_CONFIG
  Production scripts, frozen configuration, contracts and focused tests needed
  to inspect or reproduce the bounded workflow.
```

## Authoritative numeric results

```text
ALUR  O/S 9,262,586   excluded 655,338      float 8,607,248   92.9249%
BNAI  O/S 44,880,795  excluded 11,578,292   float 33,302,503  74.2021%
PGAC  O/S 8,869,250   excluded 244,250      float 8,625,000   97.2461%
BBBY  O/S NULL        float NULL            ticker reuse / interval blocker
BGM   O/S 6,006,480   float NULL            partial 20-F/A baseline blocker
DOMH  O/S 16,012,435  float NULL            special proxy / overlap blockers
CNOBP class halt      no common-equity calculation
```

## Deliberate exclusions

- SEC primary HTML payload objects and bulk datasets;
- the 13F global information-table dataset, which has not been acquired;
- tradability/lockup estimates, which remain a separate unresolved output;
- non-SEC Market States documentation;
- Trading Activity code, logs and telemetry;
- Graphify runtime outputs and general TSIS governance documents.

Primary payloads remain content-addressed outside the ZIP and are referenced by
the included acquisition ledgers and SHA-256 manifests.
