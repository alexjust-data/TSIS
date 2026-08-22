# SEC PIT 4,824 Prelaunch Audit Corrections Readout `v0_1`

Date: `2026-08-14`

Status: `CORRECTIONS_IMPLEMENTED_C01_METADATA_AUTHORIZED_PENDING_HUMAN_LAUNCH`

## Human audit verdict

```text
PREFLIGHT 4,824                     PASS
C01_0824 submissions metadata       AUTHORIZED
C01 primary documents               NOT AUTHORIZED
cohorts 02-05                       BLOCKED
automatic scale-out                 NOT AUTHORIZED
```

The audit required resolution of the two SEC roots, a 200-GiB primary disk
hard-stop and an observed C01 storage/workload readout before primary.

## Correction 1 - one active SEC root

```text
D:/TSIS/fundamental_context/sec_pit_v0_1          SOLE ACTIVE WRITE ROOT
D:/TSIS/fundamental_context/sec_pit_v0_1/objects  SOLE ACTIVE CAS
D:/sec_float_pit_v0_1                             IMMUTABLE LEGACY PROVENANCE
```

The legacy path is a closed 50-CIK pilot, not an alternative destination. Its
read-only physical inventory contained 22,783 files and 28,682,785,827 bytes;
its acquisition manifest records 22,642 primary+complete resources and
28,516,711,055 acquired bytes. It is preserved, not copied or deleted.

Both current metadata and authorized-primary runners reject noncanonical roots.
The detailed binding decision lives in
`sec_pit_storage_root_and_legacy_pilot_decision_v0_1.md`.

## Correction 2 - clean primary disk stop

`run_authorized_primary_acquisition_v0_2.py` now defaults to:

```text
minimum_free_space_gib = 200
```

It validates at start and before each document. A breach emits
`STOPPED_LOW_DISK`, exit code 2, terminal heartbeat/PID state,
`final_manifest.json` and exact `--resume` instructions. No primary run is
authorized by this implementation change.

## Correction 3 - C01 replaces the 4-GB estimate

`build_4824_cohort_metadata_gate.py` is the mandatory network-free next step
after metadata completion. It emits:

- exact metadata completeness;
- request, retry, HTTP 429 and failure counts;
- total accessions;
- `sec_pit_predownload_control_v0_2` document selection;
- selected documents P50/P95/MAX per ticker;
- filing-size upper-bound P50/P95/MAX per ticker;
- pre-XBRL proxy;
- reused identity, cross-CIK and lifecycle-review exclusions;
- an explicitly non-representative 4,824 filing-size upper-bound projection.

Submissions metadata cannot certify future 404/primary fallback frequency or
compressed primary bytes. Those remain explicit `NOT_CERTIFIABLE` fields; no
fabricated estimate is substituted.

## C01 launch boundary

The metadata output root does not exist as of this readout. The launch remains
human-controlled and must use the frozen 824-row Parquet, five requests/second,
the active CAS and a valid SEC User-Agent. `--resume` may only reuse that exact
cohort hash and object root.

The metadata gate output is runtime evidence, not an authorization file. A new
hash-bound human decision is required before any selective primary download.

## Validation

Targeted no-network tests cover:

- canonical metadata and primary root rejection;
- metadata HTTP summary fields;
- v0.2 selection and storage projection fixture;
- 200-GiB clean-stop final manifests and resume instructions;
- predownload controls and acquisition telemetry.

Result at closeout: `PASS`.

