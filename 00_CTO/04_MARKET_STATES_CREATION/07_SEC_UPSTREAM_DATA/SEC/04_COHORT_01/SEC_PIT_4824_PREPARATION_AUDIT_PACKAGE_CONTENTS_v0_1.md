# SEC PIT 4,824 Preparation Audit Package `v0_1` — START HERE

Date: `2026-08-14`

Status: `MINIMAL_PRE_LAUNCH_AUDIT_HANDOFF`

## Purpose

This package lets another agent audit the exact preparation completed before
the first 824-row SEC metadata run, understand why the 4,824-row diagnostic was
reopened, inspect what will execute next and verify what the bounded work had
already demonstrated.

It is deliberately not an application archive. The ZIP contains exactly 26
entries: 24 selected source/evidence artifacts, one package-build metadata file
and one SHA-256 manifest.

## Decision in one screen

```text
parent universe scope             4,824 unique ticker rows
unique instrument_id              4,626
reused instrument identity groups   190
cross-CIK identity conflicts            4 groups / 8 rows
frozen cohorts                    824 / 1000 / 1000 / 1000 / 1000
priority                          last_observed_date DESC, ticker ASC
final preflight                   COMPLETE / PASS
preflight network requests        0
next run                          cohort 01 submissions metadata only
next-run launch owner             human operator
primary-document acquisition      NOT AUTHORIZED
automatic institutional promotion NOT AUTHORIZED
```

## Reading order

1. `01_AUTHORITY/4824_DESCENDING_EXECUTION_PLAN.md`
2. `03_CURRENT_PREFLIGHT/PREFLIGHT_READOUT.md`
3. `02_PRIOR_EVIDENCE/V0_21_AUTHORITATIVE_READOUT.md`
4. `02_PRIOR_EVIDENCE/100_CASE_SCALE_GATE_READOUT.md`
5. `01_AUTHORITY/ACQUISITION_AND_RESOLUTION_CONTRACT.md`
6. `01_AUTHORITY/ADAPTIVE_SCALE_GATE_HANDOFF.md`
7. `01_AUTHORITY/LONG_RUNNING_OPERATIONS_CONTRACT.md`
8. `03_CURRENT_PREFLIGHT/final_manifest.json`
9. `03_CURRENT_PREFLIGHT/cohort_summary.json`
10. `03_CURRENT_PREFLIGHT/operator_launch_plan.json`
11. `04_NEXT_EXECUTION/`
12. `PACKAGE_FILE_MANIFEST.csv`

## What has already been obtained

The previous bounded authority is SEC PIT resolution `v0.21`:

```text
sample                         100 stratified cases
eligible common-equity cases   99
security-class halt             1 (CNOBP)
execution                      99/99 O/S + 99/99 ownership
O/S complete                   71/99 = 71.72%
owner-exclusion float complete 28/99 = 28.28%
formula/PIT violations          0
network during resolution       0
```

This demonstrated a generalized fail-closed system, not 100% float coverage.
Every unresolved result remains `NULL + exact blocker`.

The new full-universe preflight then froze the exact five cohorts without any
network request. Its final immutable root is:

```text
C:/TSIS_Data/runtime/sec_pit_4824_descending_acquisition_v0_1/
preflight_20260813T215254Z
```

The package includes the complete 4,824-row order as CSV and the exact cohort
01 Parquet consumed by the next runner. The other four cohort files are omitted
because their boundaries and hashes are already captured by the manifest and
summary, and they are not authorized to run now.

CSV audit warning: the universe contains the literal ticker `NA`. Readers such
as pandas treat `NA` as null by default. Load the packaged CSV with
`keep_default_na=False` (or an explicit string schema); otherwise a valid 4,824
row/4,824 ticker file will be misreported as only 4,823 non-null unique tickers.
The execution input is Parquet and does not have this CSV parsing ambiguity.

## What will happen next

The human operator sets a truthful `SEC_USER_AGENT` and launches only cohort 01.
The runner requests SEC submissions roots and historical supplements. It does
not request Company Facts, primary documents, complete submissions or exhibits.

Expected scope:

```text
824 ticker rows
SEC submissions metadata only
5 requests/second maximum
one active cohort
estimated duration 12–20 minutes from the prior 240-case measurement
content-addressed reuse under D:/TSIS/fundamental_context/sec_pit_v0_1/objects
```

After completion, another gate must audit metadata completeness, identity and
lifecycle conflicts, retries/429s, document-selection volume and capacity.
Only then may a separate hash-bound primary-document authorization be proposed.

## Audit questions

The reviewer should verify:

1. the cohort sizes sum to 4,824 and membership is deterministic;
2. `last_observed_date` is globally descending with ticker as stable tie-break;
3. the final manifest builder SHA-256 matches the included builder;
4. preflight made zero network requests;
5. reused identities are marked rather than silently collapsed;
6. the four cross-CIK groups remain explicit and fail closed downstream;
7. cohort 01 Parquet matches the hash in the final preflight manifest;
8. the metadata runner requests submissions metadata only;
9. `--resume` rejects input drift, object-root drift and a live duplicate writer;
10. telemetry exposes PID, heartbeat history, live log, resource metrics and a
    stale-no-process state;
11. no included artifact grants primary-document acquisition or promotion;
12. `PACKAGE_FILE_MANIFEST.csv` matches every other ZIP entry byte-for-byte.

For the CSV checks, preserve the literal `NA` ticker:

```python
order = pandas.read_csv("full_universe_acquisition_order.csv", keep_default_na=False)
assert len(order) == order["ticker"].nunique() == 4824
```

## Included entries

```text
00_START_HERE.md

01_AUTHORITY/
  LONG_RUNNING_OPERATIONS_CONTRACT.md
  ACQUISITION_AND_RESOLUTION_CONTRACT.md
  ADAPTIVE_SCALE_GATE_HANDOFF.md
  4824_DESCENDING_EXECUTION_PLAN.md

02_PRIOR_EVIDENCE/
  100_CASE_SCALE_GATE_READOUT.md
  V0_21_AUTHORITATIVE_READOUT.md

03_CURRENT_PREFLIGHT/
  PREFLIGHT_READOUT.md
  final_manifest.json
  cohort_summary.json
  operator_launch_plan.json
  full_universe_acquisition_order.csv
  cohort_01_0824.parquet

04_NEXT_EXECUTION/
  sec_pit_4824_descending_acquisition_preflight_v0_1.json
  build_4824_descending_acquisition_preflight.py
  test_sec_pit_4824_descending_acquisition_preflight.py
  run_submissions_metadata_profile.py
  monitor_sec_pit_run.ps1
  client.py
  metadata.py
  models.py
  storage.py
  telemetry.py

05_PACKAGE_PROVENANCE/
  build_4824_preparation_audit_package_v0_1.ps1

PACKAGE_BUILD_METADATA.json
PACKAGE_FILE_MANIFEST.csv
```

## Excluded by design

- raw SEC payloads and compressed content-addressed objects;
- primary documents, complete submissions and exhibits;
- daily O/S/ownership Parquets and the 99-case resolution tree;
- logs, heartbeat histories and runtime performance ledgers from old runs;
- all five cohort Parquets when only cohort 01 may run;
- historical duplicate readouts and rejected versions;
- unrelated Trading Activity, market-state, backtest and Graphify artifacts;
- application-wide source code and tests not imported by the immediate runner.

## Integrity and authority boundary

`PACKAGE_FILE_MANIFEST.csv` records the path, byte length and SHA-256 of every
other entry. The builder enforces the exact 26-entry allowlist, unique safe ZIP
paths, full decompression and hash/size verification from the archive itself.

The working tree was not committed when this package was built. Therefore the
included file hashes and package manifest are the exact source snapshot for this
handoff; the Git commit in `PACKAGE_BUILD_METADATA.json` is ancestry, not a
claim that these preparation changes already exist in that commit.
