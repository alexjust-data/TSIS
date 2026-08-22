# SEC PIT 4,824 Descending Acquisition Execution Plan `v0_1`

Date: `2026-08-13`; human gate and storage correction: `2026-08-14`

Status: `C01_PRIMARY_T01_0250_RUNNING`

## Role

This document records the operator decision and the governed execution order
for the full `lt1b_universe_v0_1` SEC PIT diagnostic. Operational code,
tests and runtime manifests remain owned by Data Foundation.

## Operator decision

The parent universe is processed as five immutable cohorts:

```text
824 -> 1000 -> 1000 -> 1000 -> 1000 = 4,824 ticker rows
```

Priority is deterministic:

```text
last_observed_date DESC
-> ticker ASC as stable tie-break
```

This means processing starts with rows observed in 2026 and moves backwards.
The date rule prioritizes universe rows; it does not permit a newest-only SEC
filing cap. Each ticker must still preserve every required historical evidence
family selected by the governed predownload control.

## Frozen preflight result

Authoritative runtime root:

```text
C:/TSIS_Data/runtime/sec_pit_4824_descending_acquisition_v0_1/
preflight_20260813T215254Z
```

```text
preflight gate                         PASS
network requests                      0
parent-universe ticker rows           4,824
unique ticker                         4,824
unique instrument_id                  4,626
reused instrument_id groups             190
rows in reused-identity groups           388
cross-CIK reused-identity groups            4
rows in cross-CIK identity conflicts        8
primary-document acquisition          NOT AUTHORIZED
automatic promotion                   NOT AUTHORIZED
```

`4,824 instruments` remains convenient historical shorthand, but the exact
physical scope is 4,824 unique ticker rows and 4,626 unique `instrument_id`
values. Reused identities are not collapsed. They are carried as explicit
lifecycle groups; cross-CIK conflicts must fail closed during accession linkage.

## Frozen cohort boundaries

| Cohort | Rows | Global order | Newest `last_observed_date` | Oldest `last_observed_date` | Year composition |
|---|---:|---:|---|---|---|
| `C01_0824` | 824 | 1-824 | 2026-03-09 | 2026-03-09 | 2026: 824 |
| `C02_1000` | 1,000 | 825-1,824 | 2026-03-09 | 2026-03-09 | 2026: 1,000 |
| `C03_1000` | 1,000 | 1,825-2,824 | 2026-03-09 | 2025-01-22 | 2026: 704; 2025: 296 |
| `C04_1000` | 1,000 | 2,825-3,824 | 2025-01-22 | 2022-12-08 | 2025: 18; 2024: 412; 2023: 488; 2022: 82 |
| `C05_1000` | 1,000 | 3,825-4,824 | 2022-12-08 | 2011-05-23 | 2022 backwards to 2011 |

Every cohort preserves `sha256(instrument_id)_mod_4` so later resolution can
reuse the four-shard certification function without changing cohort membership.

## Execution sequence

```text
frozen no-network preflight                                      PASS
-> cohort 01 SEC submissions metadata-only profile              COMPLETE 824/824
-> metadata completeness, retry/429, identity and size review   PASS
-> cohort 01 lifecycle and predownload control                  PASS
-> selective primary-document plan and capacity readout         COMPLETE
-> explicit human authorization for C01 primary T01 (250)       RUNNING
-> no-network O/S and owner-exclusion resolution                PENDING
-> integrity, PIT, schema and blocker audit                     PENDING
-> decision to admit cohort 02                                  PENDING
-> repeat sequentially through cohort 05                        PENDING
```

Only one cohort may be active in this lane. Completion of metadata does not
authorize primary documents. Completion of acquisition does not authorize
institutional promotion.

## First human-controlled launch

Expected scope: 824 ticker rows, submissions metadata only. The preceding
240-case run completed in about 3.6 minutes; a linear estimate is approximately
12-20 minutes, subject to SEC latency, supplements and retries. It is treated
as a long run and must be launched by the human.

Prerequisite:

```powershell
$env:SEC_USER_AGENT = "TSIS Research contact@example.com"
```

Launch, one line:

```powershell
if ([string]::IsNullOrWhiteSpace($env:SEC_USER_AGENT) -or $env:SEC_USER_AGENT -notmatch '@') { throw 'Define SEC_USER_AGENT with organization and contact email before launch' }; python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\run_submissions_metadata_profile.py" --candidate-pool "C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\preflight_20260813T215254Z\cohort_01_0824.parquet" --output "C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\metadata\cohort_01" --object-root "D:\TSIS\fundamental_context\sec_pit_v0_1\objects" --user-agent "$env:SEC_USER_AGENT" --requests-per-second 5 --telemetry-interval-seconds 10 --minimum-available-memory-gib 8
```

Monitor, one line:

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\monitor_sec_pit_run.ps1" -RunRoot "C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\metadata\cohort_01" -Compact -IntervalSeconds 10
```

Resume, one line:

```powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\run_submissions_metadata_profile.py" --candidate-pool "C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\preflight_20260813T215254Z\cohort_01_0824.parquet" --output "C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\metadata\cohort_01" --object-root "D:\TSIS\fundamental_context\sec_pit_v0_1\objects" --user-agent "$env:SEC_USER_AGENT" --requests-per-second 5 --telemetry-interval-seconds 10 --minimum-available-memory-gib 8 --resume
```

Safe stop: `Ctrl+C` in the launch terminal. Resume reuses complete per-ticker
inventories and content-addressed objects; it fails on input hash drift,
object-root drift or a live duplicate writer.

After `C01_0824` metadata reaches `COMPLETE`, the next operation is the
network-free gate below. It does not acquire or authorize primary documents:

```powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\build_4824_cohort_metadata_gate.py" --candidate-pool "C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\preflight_20260813T215254Z\cohort_01_0824.parquet" --metadata-root "C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\metadata\cohort_01" --full-order "C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\preflight_20260813T215254Z\full_universe_acquisition_order.parquet" --output "C:\TSIS_Data\runtime\sec_pit_4824_descending_acquisition_v0_1\metadata_gate\cohort_01_v0_1"
```

## Current primary launch checkpoint

The human explicitly authorized the agent to launch only the first governed
primary tranche. It started at `2026-08-14T07:43:20Z`:

```text
scope                         first 250 eligible C01 ticker rows
planned documents             127,946
run id                        sec_pit_c01_primary_t01_0250_v0_1_20260814
run root                      D:/TSIS/fundamental_context/sec_pit_v0_1/runs/sec_pit_c01_primary_t01_0250_v0_1_20260814
request rate                  5 requests/second
minimum free disk             200 GiB
resume                        explicit --resume; skip prior FETCHED SHA-256 URLs
initial heartbeat             RUNNING; 36/127,946; failed=0; 429=0
initial free disk             874.286 GiB
```

The remaining `499` eligible C01 rows and all `75` halted lifecycle/security
rows are outside this authorization. Cohorts 02-05 remain blocked. The binding
operational readout is
`SEC_PIT_C01_PRIMARY_TRANCHE_01_AUTHORIZATION_AND_LAUNCH_READOUT_v0_1.md`.

## Gates and risks

- `190` reused-identity groups require lifecycle-aware treatment, not row collapse.
- `HSGX/OCGN`, `CYTX/PSTV`, `FSR/SPAQ` and `YELL/YRCW` cross CIK under a shared
  `instrument_id`; automatic accession linkage must halt until reconciled.
- SEC metadata volume does not predict selected primary bytes exactly.
- Required historical evidence may not be truncated by a fixed newest-first cap.
- Primary-document acquisition must remain selective, hashed, content-addressed
  and separately authorized per cohort.
- The 100-case `71/99` O/S and `28/99` float coverage are not population rates.
- Every unresolved result remains `NULL + exact blocker`; no `float = O/S` fill.

## Storage and lineage

The existing content-addressed root is reused:

```text
D:/TSIS/fundamental_context/sec_pit_v0_1/objects
```

This is the sole active write root. `D:/sec_float_pit_v0_1` is a closed 50-CIK
pilot with about 28.7 GB of immutable raw provenance; it is not an alternative
active repository and receives no new writes. The binding migration decision is
`sec_pit_storage_root_and_legacy_pilot_decision_v0_1.md` in Data Foundation.

Free space at preflight: D `874.7 GiB`. The measured 99-case acquisition implied
about `4.0 GiB` compressed and `44.7 GiB` uncompressed under a linear 4,824-row
projection, but the cohort metadata and selection manifests must replace this
estimate with observed distributions before primary acquisition expands.
The primary runner hard-stops cleanly at `200 GiB` free, persists terminal
manifests and preserves exact resume state.

## Allowed and prohibited actions

Allowed now:

- monitor the active C01 T01 primary run separately;
- stop and resume that same run against the same hashes and roots;
- audit its terminal manifests and acquired objects after completion;
- prepare a new explicit gate for any later tranche.

Prohibited now:

- launch cohorts 02-05 concurrently or before the preceding cohort gate;
- launch any additional C01 primary tranche or any primary documents for
  cohorts 02-05 without a new separate authorization;
- collapse ticker aliases silently;
- treat runtime outputs as institutional;
- promote O/S, float or owner-exclusion results automatically.

## Source artifacts

- `sec_pit_4824_descending_acquisition_preflight_v0_1.json`
- `build_4824_descending_acquisition_preflight.py`
- `run_submissions_metadata_profile.py`
- `build_4824_cohort_metadata_gate.py`
- `monitor_sec_pit_run.ps1`
- `sec_pit_storage_root_and_legacy_pilot_decision_v0_1.md`
- `test_sec_pit_4824_descending_acquisition_preflight.py`
- runtime `final_manifest.json`, `operator_launch_plan.json` and the five frozen
  cohort Parquets under the authoritative preflight root.
