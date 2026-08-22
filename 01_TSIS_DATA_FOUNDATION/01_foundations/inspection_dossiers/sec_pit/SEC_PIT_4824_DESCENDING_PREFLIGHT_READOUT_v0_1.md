# SEC PIT 4,824 Descending Preflight Readout `v0_1`

Date: `2026-08-13`

Status: `PASS_METADATA_COHORT_01_AWAITING_HUMAN_LAUNCH`

## What this shows

The network-free full-universe preflight completed over exactly 4,824 unique
ticker rows. It froze the operator-requested `824/1000/1000/1000/1000`
cohorts using `last_observed_date DESC, ticker ASC`, emitted hashes and a
human launch/monitor/resume plan, and made zero network requests.

```text
runtime root          C:/TSIS_Data/runtime/sec_pit_4824_descending_acquisition_v0_1/preflight_20260813T215254Z
status                COMPLETE
preflight gate        PASS
ticker rows           4,824
unique instrument_id  4,626
identity alias groups 190
cross-CIK conflict    4 groups / 8 rows
network requests      0
```

## What it answers

- the exact deterministic membership and order of all five cohorts;
- whether parent-universe ticker, date, instrument identity and CIK fields are
  present;
- which rows reuse an instrument identity and which reused identities cross CIK;
- the exact commands and roots for metadata cohort 01, monitor and resume.

## What it does not answer

- which SEC primary documents will be selected;
- the full-universe primary byte distribution;
- O/S or float population coverage;
- whether a runtime result is eligible for institutional promotion.

## Consequence

Metadata-only cohort 01 is ready for human launch. Primary-document acquisition
remains blocked until that metadata is profiled, lifecycle/accession controls
pass and a separate hash-bound authorization is issued. Cohorts 02-05 remain
queued and must not run concurrently.

## Identity finding

The historical phrase `4,824 instruments` is imprecise for this source. The
parent contains 4,824 ticker rows but 4,626 unique `instrument_id` values.
The preflight preserves aliases rather than silently deduplicating them.

Four reused identities cross CIK and require explicit fail-closed review:

```text
HSGX / OCGN
CYTX / PSTV
FSR  / SPAQ
YELL / YRCW
```

## Verification

Focused tests: `5 PASS` across the new cohort builder, metadata profiler and
authorized-acquisition scope tests before execution; the builder suite then
passed `4 PASS` after adding the alias fixture. Final runtime reports one schema,
exact cohort sizes, date-descending order and zero network requests.
The final isolated SEC PIT suite passed `288/288`; Ruff, Python compilation,
PowerShell parsing, JSON parsing and independent cohort invariants also passed.

The rejected preflight attempt `preflight_20260813T214250Z` is closed as
`FAILED/PREFLIGHT_ABORTED_BEFORE_OUTPUT_MATERIALIZATION`: its overly strict
instrument-ID uniqueness assumption exposed the alias topology and was replaced
by the corrected logic. `preflight_20260813T214452Z` then passed but was
superseded after a post-run import-only Ruff normalization changed the builder
hash. The final immutable run above was repeated against the exact delivered
script hash `598e53f8a42b66afe43896b08d1712b97b6fe0743e5fcbd0b03b038637b71123`.
