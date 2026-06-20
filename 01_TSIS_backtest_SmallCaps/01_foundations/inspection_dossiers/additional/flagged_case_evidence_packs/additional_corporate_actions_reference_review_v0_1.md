# Additional Corporate Actions Reference Review v0.1

`additional/corporate_actions` is RAW vendor context, but not primary authority for adjustment.

| dataset | overlap_bucket | tickers | rows | overlap_rows |
| --- | --- | --- | --- | --- |
| dividends | reference_exact_overlap | 1253 | 1253 | 45968 |
| dividends | reference_present_no_exact_overlap | 5 | 5 | 0 |
| splits | reference_exact_overlap | 1858 | 1858 | 3293 |
| splits | reference_present_no_exact_overlap | 18 | 18 | 0 |
| ticker_events | reference_present_no_exact_overlap | 2703 | 2703 | 0 |

Institutional reading:

- Exact reference overlap can be used as secondary confirmation.
- Non-overlap is a review queue, not permission to overwrite reference.
- CAPA 1 `corporate_actions_table` must keep reference as primary source until a separate reconciliation promotion exists.
