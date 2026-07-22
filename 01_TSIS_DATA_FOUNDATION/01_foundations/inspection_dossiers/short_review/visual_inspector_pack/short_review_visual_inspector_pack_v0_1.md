# Short Review Visual Inspector Pack v0.1

Fecha: 2026-06-20
Estado: `visual_complete_v0_1`

## 1. Verdict

This pack closes the missing visual evidence layer for:

```text
short_review_finra_v0_1
```

The correct institutional state is:

```text
data_quality_verdict = complete_scoped_provenance_with_short_volume_key_flags
foundations_completion_status = human_inspector_ready_scoped
visual_inspection_status = visual_complete
```

The family remains a FINRA official/free baseline and provenance layer. It is
not a full-history short replacement and not clean short-volume analytic input
until duplicate-key handling is explicit.

## 2. Visual Asset Index

| Visual | State | Main question |
| --- | --- | --- |
| [FINRA coverage timeline](images/short_review_finra_coverage_timeline_v0_1.png) | `scoped` | What coverage does the FINRA baseline actually prove? |
| [Duplicate key concentration](images/short_review_duplicate_key_concentration_v0_1.png) | `review` | Where is duplicate short-volume key risk concentrated? |
| [Duplicate key case panel](images/short_review_duplicate_key_case_panel_v0_1.png) | `review` | What does a duplicate short-volume key look like in actual rows? |
| [FINRA vs local overlap](images/short_review_finra_vs_local_overlap_panel_v0_1.png) | `scoped` | Can FINRA short_review silently replace local short? |
| [Numeric sanity panel](images/short_review_numeric_sanity_panel_v0_1.png) | `scoped` | Is numeric sanity the primary blocker? |
| [Provenance/history boundary panel](images/short_review_provenance_history_boundary_panel_v0_1.png) | `boundary` | What claims are explicitly blocked by source/history boundaries? |

Machine-readable manifests:

- `short_review_visual_case_manifest_v0_1.csv`
- `short_review_visual_asset_audit_v0_1.csv`

Builder:

- `build_short_review_visual_inspector_pack.py`

## 3. FINRA Coverage Timeline

Image:

```text
images/short_review_finra_coverage_timeline_v0_1.png
```

What it shows:

- FINRA short interest has 505,745 rows and 4,687 tickers;
- FINRA short volume has 4,689,038 rows and 4,623 tickers;
- observed official/free short interest window is `2017-12-29` to
  `2026-04-15`;
- observed official/free short volume window is `2018-08-01` to `2026-04-29`.

Responds:

```text
What coverage does the FINRA baseline actually prove?
```

Answer:

```text
Strong coverage inside observed official/free windows, not full 2005-2026 replacement.
```

Consequence:

The family is a baseline/provenance layer. It cannot be marketed as full-history
short truth.

## 4. Duplicate Key Concentration

Image:

```text
images/short_review_duplicate_key_concentration_v0_1.png
```

What it shows:

- duplicate short-volume `ticker + date` excess rows concentrate in `CPS`,
  `OP` and `LFTR`;
- `CPS` dominates with 4,550 excess rows;
- `OP` has 655 excess rows;
- `LFTR` has 45 excess rows.

Responds:

```text
Where is duplicate short-volume key risk concentrated?
```

Answer:

```text
Mostly CPS, then OP and LFTR.
```

Consequence:

The duplicate-key issue is narrow enough to inspect, but important enough that
consumers must not collapse rows silently.

## 5. Duplicate Key Case Panel

Image:

```text
images/short_review_duplicate_key_case_panel_v0_1.png
```

What it shows:

- concrete duplicate `ticker + date` keys;
- number of rows per duplicated key;
- representative payload rows for duplicate-key cases.

Responds:

```text
What does a duplicate short-volume key look like in actual rows?
```

Answer:

```text
Multiple FINRA rows can share the same ticker and date.
```

Consequence:

Any downstream use needs an explicit aggregation, source/venue preservation or
deduplication policy.

## 6. FINRA Vs Local Overlap

Image:

```text
images/short_review_finra_vs_local_overlap_panel_v0_1.png
```

What it shows:

- FINRA short volume overlaps 4,623 local/Polygon files;
- 201 short-volume local-only files remain;
- FINRA short interest overlaps 4,687 local/Polygon files;
- 137 short-interest local-only files remain;
- there are no FINRA-only files in the compact comparison.

Responds:

```text
Can FINRA short_review silently replace local short?
```

Answer:

```text
No.
```

Consequence:

FINRA is a comparator and provenance baseline. Local-only tickers are review
cases, not automatic deletion candidates and not automatic bad data.

## 7. Numeric Sanity Panel

Image:

```text
images/short_review_numeric_sanity_panel_v0_1.png
```

What it shows:

- inspected numeric fields have zero nulls, zero negative rows and zero infinite
  rows in the evidence tables;
- representative min/max ranges are visible for numeric fields.

Responds:

```text
Is numeric sanity the primary blocker?
```

Answer:

```text
No.
```

Consequence:

The controlling limitations are source/history scope and duplicate keys, not
basic numeric cleanliness.

## 8. Provenance And History Boundary Panel

Image:

```text
images/short_review_provenance_history_boundary_panel_v0_1.png
```

What it shows:

- official/free short volume does not prove 2005-2018 equivalence;
- official/free short interest does not prove 2005-2013 equivalence;
- `short_volume_ratio` is source-scoped, not consolidated market-wide pressure;
- local-only tickers require review;
- provenance assets exist and are visible.

Responds:

```text
What claims are explicitly blocked by source/history boundaries?
```

Answer:

```text
Full-history replacement and consolidated short truth claims.
```

Consequence:

Consumers must preserve source, date-window, lag and duplicate-key semantics.

## 9. What This Pack Does Not Prove

This visual pack does not prove:

- full 2005-2026 short-volume completeness;
- full 2005-2013 short-interest equivalence;
- clean duplicate-key semantics for short volume;
- replacement authority over `E:/TSIS/data/short`;
- consolidated market-wide shorting pressure;
- live, RL or execution readiness.

It proves only:

```text
the scoped FINRA baseline/provenance verdict is now visually inspectable and reproducible.
```

## 10. Closure

The short review family now has the required visual inspection layer:

```text
population map: yes
coverage map: yes
quality-state distribution: yes
good/pass visual cases: yes, through coverage and numeric sanity panels
flagged/review visual cases: yes, through duplicate-key panels
bad/blocking visual cases: yes, through provenance/history boundary panel
manifest: yes
asset audit: yes
builder: yes
```

Final operational reading:

```text
human_inspector_ready_scoped, but not a production short replacement
```
