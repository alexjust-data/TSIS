# Short Review Scope And History Boundaries v0.1

This casepack documents what remains blocked for:

```text
short_review_finra_v0_1
```

The current family is an official/free FINRA baseline. It is not the full short
dataset.

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/short_review_scope_limitations_v0_1.csv` | Official/free source limitations. |
| `../evidence_assets/short_review_local_comparison_summary_v0_1.csv` | FINRA vs local/Polygon comparison. |
| `../evidence_assets/short_review_log_summary_v0_1.csv` | Download-log status summary. |

## Blocked Claims

The current evidence must not be used to claim:

- official/free full-history short volume completeness from 2005 to 2018;
- official/free fully equivalent short interest history from 2005 to 2013;
- that `short_review` silently replaces `E:/TSIS/data/short`;
- that `short_volume_ratio` is consolidated market-wide short pressure;
- that short interest is same-day intraday causal evidence;
- that local-only tickers are bad without review.

## Local Comparison

| Dataset | Local/Polygon files | FINRA files | Intersection | Local-only | FINRA-only |
| --- | ---: | ---: | ---: | ---: | ---: |
| `short_volume` | 4,824 | 4,623 | 4,623 | 201 | 0 |
| `short_interest` | 4,824 | 4,687 | 4,687 | 137 | 0 |

The local-only sets are review cases. They are not automatic evidence of bad
local data or bad FINRA data.

## Source-Scope Rule

Every downstream use must carry:

- source family;
- date window;
- FINRA official/free scope;
- short interest lag assumptions;
- short volume source/venue interpretation;
- duplicate-key handling for short volume.
