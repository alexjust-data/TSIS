# SEC PIT External Audit Package `v0_3` - START HERE

Date: `2026-08-11`

Status: `MINIMAL_EXTERNAL_HANDOFF`

Supersedes for external review: `SEC_PIT_EXTERNAL_AUDIT_PACKAGE_v0_2.zip`.

## Why this package exists

This ZIP is intentionally small. It is not a source-code archive, test bundle or
history of every SEC PIT iteration. It gives an external agent enough context to
understand:

1. what problem TSIS was trying to solve;
2. why the first document-selection and ownership-baseline approaches failed;
3. what generic corrections were introduced;
4. what the seven-case and full-interval results actually prove;
5. what remains blocked before scaling to 4,824 instruments.

## Read only these files, in this order

1. `01_RESULT/FINAL_READOUT.md`
   - The complete current result, numeric outputs, limitations and runtime
     lineage.
2. `02_PROCESS/NEXT_SCALE_GATE.md`
   - The frozen end-to-end workflow and the next 30-50 case gate.
3. `02_PROCESS/ACQUISITION_AND_RESOLUTION_CONTRACT.md`
   - Source authority, PIT causality and acquisition/resolution obligations.
4. `02_PROCESS/OWNER_EXCLUSION_METHODOLOGY.md`
   - What is subtracted from O/S, class reconciliation and fail-closed rules.
5. `03_OUTPUT_SCHEMA/RESOLVED_DAILY_STATE_SCHEMA.md`
   - Exact output meaning, including fraction versus percent and NULL states.
6. `04_MINIMUM_EVIDENCE/`
   - Small machine-readable proofs of case selection, final adaptive probe,
     Company Facts role and four-shard certification.

## Result in one screen

```text
ALUR   CALCULATED  O/S  9,262,586  excluded    655,338  float  8,607,248  92.924892%
BGM    CALCULATED  O/S  6,006,480  excluded  3,028,492  float  2,977,988  49.579587%
BNAI   CALCULATED  O/S 44,880,795  excluded 11,578,292  float 33,302,503  74.202124%
DOMH   CALCULATED  O/S 16,012,435  excluded  4,787,068  float 11,225,367  70.104060%
PGAC   CALCULATED  O/S  8,869,250  excluded    244,250  float  8,625,000  97.246103%
BBBY   NULL        TICKER_REUSE_CONFLICT
CNOBP  HALT        HALT_SECURITY_CLASS
```

## What changed

- The selector no longer accepts the newest proxy or amendment merely because
  it is newest.
- Annual and special proxies are distinguished.
- `20-F` plus `20-F/A` are resolved as a document family.
- A bounded causal fallback finds the latest complete ownership baseline.
- Holder overlaps and share classes are reconciled before subtraction.
- Official SEC Company Facts is used only to reconcile O/S, never as a float
  source or automatic share-class proof.
- Insufficient evidence produces `NULL + exact blocker`, not an invented value.
- The same code, schemas and component hashes passed on four planned shards.

## What the result does not prove

- It does not prove freely tradable float.
- It does not include the separate global 13F information-table acquisition.
- It does not authorize a 4,824-instrument materialization.
- It does not promise homogeneous historical coverage: ALUR and BNAI correctly
  contain unresolved historical intervals where causal ownership evidence is
  insufficient; PGAC is fully covered in its shorter tested interval.

## Integrity and reproduction pointers

`PACKAGE_FILE_MANIFEST.csv` contains bytes and SHA-256 for every entry except
itself. `PACKAGE_BUILD_METADATA.json` records the Git commit, authoritative run
IDs and the exact source paths. Raw SEC payloads, complete run directories,
source code and tests remain in the TSIS workspace and Git history; they are
referenced rather than duplicated here.

