# SEC PIT External Audit Package `v0_4` - START HERE

Date: `2026-08-12`

Status: `MINIMAL_100_CASE_EXTERNAL_HANDOFF`

Supersedes for external review: `SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_3.zip`.

## Purpose

This ZIP explains the final 20-year, 100-case stratified SEC PIT gate without
requiring an external reviewer to study the application or its history. It
contains the governing process, the authoritative v0.5 result and only the
minimum machine-readable evidence needed to verify the conclusion.

## Reading order

1. `01_RESULT/FINAL_100_CASE_READOUT.md`
2. `01_RESULT/OS_MULTI_EVIDENCE_CERTIFICATION.md`
3. `02_PROCESS/ACQUISITION_AND_RESOLUTION_CONTRACT.md`
4. `02_PROCESS/OWNER_EXCLUSION_METHODOLOGY.md`
5. `03_OUTPUT_SCHEMA/RESOLVED_DAILY_STATE_SCHEMA.md`
6. `04_MINIMUM_EVIDENCE/`

## Result in one screen

```text
SAMPLE                         100 cases across 2005-2025
ELIGIBLE                       99
SECURITY-CLASS HALT            1 (CNOBP, expected)
PRIMARY ACQUISITION            COMPLETE, 6,051 unique selected URLs
O/S FULL COVERAGE v0.3         34/99 cases, 170/495 sessions
O/S FULL COVERAGE v0.5         56/99 cases, 280/495 sessions
FLOAT FULL COVERAGE v0.3       9/99 cases, 45/495 sessions
FLOAT FULL COVERAGE v0.5       11/99 cases, 55/495 sessions
EXECUTION FAILURES             0
NETWORK DURING RESOLUTION      0
FOUR-SHARD CERTIFICATION       PASS
4,824 SCALE                    NOT AUTHORIZED
```

Calculated float cases are ALUR, BGM, BIOC, BNAI, BNED, DOMH, IOBT, ONCO,
PGAC, TAOX and WINT. BIOC and WINT are the two additions unlocked by the
multi-evidence O/S lane.

## Interpretation

Official SEC Company Facts materially improves O/S coverage when it exactly
corroborates a primary filing observation for an admitted single or unnumbered
common class. It does not supply float, ownership or automatic class identity.
The dominant remaining blockers are ownership amendment families, instrument
interval conflicts, partial baseline documents, holder overlap and share-class
allocation.

The bounded software/system gate passes, including fail-closed behavior and
four-shard equivalence. The 4,824-instrument scale remains closed until generic
ownership coverage improves and historical float transitions are audited.

## Authority and integrity

Authoritative run: `sec_pit_100_case_resolution_v0_5_20260812T1210Z`.
Authoritative source snapshot commit: `27607c8`.

`PACKAGE_FILE_MANIFEST.csv` records bytes and SHA-256 for every other entry.
Raw filings, source code, tests and full runtime outputs are intentionally
excluded; their manifests and Git lineage remain in TSIS.
