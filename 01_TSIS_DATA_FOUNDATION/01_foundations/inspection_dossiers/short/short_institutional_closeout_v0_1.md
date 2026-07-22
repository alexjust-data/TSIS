# Short Institutional Closeout v0.1

## Scope

This dossier institutionalizes the short data family inside `01_foundations`.

Reviewed roots:

- `E:\TSIS\data\short`
- `E:\TSIS\data\short_review`

## Layer Roles

`short` is the current operational ticker-level short data root.

`short_review` is a review/provenance layer built around FINRA official/free sources. It is not the primary production root, but it is essential evidence for source validation and coverage limits.

## Historical Evidence Links

Preserved short review documents:

- [finra_short_build_status.md](</E:/TSIS/data/short_review/finra_short_build_status.md>)
- [research_short_sources.md](</E:/TSIS/data/short_review/research_short_sources.md>)
- [short_data_recovery_plan.md](</E:/TSIS/data/short_review/short_data_recovery_plan.md>)
- [finra_short README.md](</E:/TSIS/data/short_review/finra_short/README.md>)

Operational summaries:

- `runs/backtest/short_downloads/lt1b_short_refresh/download_summary.json`
- `runs/backtest/short_data_audit/lt1b_short_refresh_audit/short_data_lt1b_ticker_coverage_audit_summary.json`
- `runs/backtest/short_data_certification/lt1b_short_reference_certification_v2/short_data_certification_summary.json`

## Local Short Refresh Evidence

The local `short` refresh was run against the `<1B>` operating universe:

- universe tickers: 4824
- datasets: `short_interest`, `short_volume`
- submitted tasks: 9648
- ok tasks: 9648
- error tasks: 0

Rows saved:

- `short_interest`: 520048
- `short_volume`: 1430506

Files present:

- `short_interest`: 4824 / 4824
- `short_volume`: 4824 / 4824

## Certification Evidence

Certification v2 against reference/lifecycle evidence:

| Status | Tickers |
|---|---:|
| `CERTIFIED_OK` | 1130 |
| `CERTIFIED_OK_WITH_LIMITED_WINDOW` | 738 |
| `REVIEW_TICKER_REUSE` | 761 |
| `REVIEW_REFERENCE_CONFLICT` | 2195 |

Interpretation:

- file presence is complete
- institutional clean use is not universal
- reference conflict and ticker reuse dominate the review mass

## FINRA Review Evidence

FINRA short volume:

- source: FINRA official/free daily short sale volume files
- date range: `2018-08-01` to `2026-04-29`
- rows: 4689038
- tickers: 4623

FINRA short interest:

- source: FINRA official/free equity short interest files
- date range: `2017-12-29` to `2026-04-15`
- rows: 505745
- tickers: 4687

FINRA comparison to local/Polygon layer:

Short volume:

- local/Polygon files: 4824
- FINRA files: 4623
- intersection: 4623
- only local/Polygon: 201
- only FINRA: 0

Short interest:

- local/Polygon files: 4824
- FINRA files: 4687
- intersection: 4687
- only local/Polygon: 137
- only FINRA: 0

## Source Feasibility Findings

Official/free reconstruction supports:

- `short_volume` from `2018-08-01+`
- modern `short_interest` from FINRA files

Official/free reconstruction does not prove:

- `short_volume` complete from 2005-2018
- `short_interest` complete from 2005-2013 with equivalent exchange-listed semantics

Paid/commercial sources would be required if literal 2005-2026 completeness is mandatory.

## Final Institutional Status

| Layer | Status |
|---|---|
| `short_interest` schema | coherent |
| `short_volume` schema | coherent |
| local `short` file coverage | complete |
| local `short` clean certification | mixed |
| FINRA `short_review` | official/free baseline and provenance |
| 2005-2026 full-history claim | not supported |

## Verdict

`short` should be preserved and used only with certification-aware filtering. `short_review` should also be preserved as the official/free FINRA validation baseline and provenance layer. Neither layer should be described as a clean full-history 2005-2026 short dataset.
