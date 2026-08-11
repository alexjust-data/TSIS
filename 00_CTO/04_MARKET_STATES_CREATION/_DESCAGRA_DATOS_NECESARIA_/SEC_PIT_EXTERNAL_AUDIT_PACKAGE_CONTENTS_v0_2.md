# SEC PIT External Audit Package Contents `v0_2`

Date: `2026-08-11`

Status: `ADAPTIVE_SYSTEM_PASS_SCALE_AUTHORIZATION_PENDING`

Scope: `SEC PIT process and its bounded results only`

## Purpose

This package lets an external agent audit the SEC-only progression from the PGAC pilot through adaptive ownership-baseline resolution, official Company Facts O/S reconciliation, seven-case results, three full-interval probes and four-shard certification.

It deliberately excludes Trading Activity, general TSIS runtime, Graphify outputs, non-SEC Market States work and raw SEC payload objects.

## Recommended reading order

1. `01_RESULTADO/SEC_PIT_ADAPTIVE_BASELINE_COMPANYFACTS_FULL_INTERVAL_AND_SHARD_CERTIFICATION_READOUT_v0_1.md`
2. `02_PROCESO_SEC/SEC_PIT_ADAPTIVE_BASELINE_AND_SCALE_GATE_HANDOFF_v0_1.md`
3. `02_PROCESO_SEC/SEC_PIT_FUNDAMENTAL_ACQUISITION_AND_RESOLUTION_CONTRACT_v0_1.md`
4. `02_PROCESO_SEC/SEC_PIT_SEVEN_TICKER_OWNER_EXCLUSION_STRATIFIED_PROBE_PLAN_v0_1.md`
5. `06_EVIDENCIA_ADAPTATIVA/`
6. `07_RUNS_OS_V0_6/` and `08_RUNS_OWNER_V0_14/`
7. `09_FULL_INTERVAL/`
8. `10_COMPANYFACTS/`
9. `11_SHARD_CERTIFICATION/`
10. `12_CODIGO_CONFIG_TESTS/`
11. `PACKAGE_FILE_MANIFEST.csv`

## Authoritative outcome

```text
ALUR   CALCULATED  float 8,607,248   92.924892%
BGM    CALCULATED  float 2,977,988   49.579587%
BNAI   CALCULATED  float 33,302,503  74.202124%
DOMH   CALCULATED  float 11,225,367  70.104060%
PGAC   CALCULATED  float 8,625,000   97.246103%
BBBY   NULL        TICKER_REUSE_CONFLICT
CNOBP  HALT        HALT_SECURITY_CLASS
```

The same implementation and schemas passed on all four planned shards. The package does not grant scale authorization. The next gate is a 30-50 case stratified probe.

## Integrity

`PACKAGE_FILE_MANIFEST.csv` records relative path, bytes and SHA-256 for every package file other than the manifest itself. `PACKAGE_BUILD_METADATA.json` records the authoritative iterations and package status. The build script opens and reads every ZIP entry before accepting the archive.

## Deliberate exclusions

- SEC primary HTML/JSON payload objects;
- global 13F information tables, not yet acquired;
- tradability/lockup estimates;
- vendor/Yahoo data as authority;
- Trading Activity code, outputs and telemetry;
- Graphify runtime outputs;
- unrelated TSIS governance and application artifacts.

