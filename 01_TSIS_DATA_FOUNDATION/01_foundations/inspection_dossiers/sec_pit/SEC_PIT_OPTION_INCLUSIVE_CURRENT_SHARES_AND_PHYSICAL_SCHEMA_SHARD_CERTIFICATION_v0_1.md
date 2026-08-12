# SEC PIT option-inclusive current-shares and physical-schema shard certification v0.1

Status: `PASS_BOUNDED_99_CASE_V0_13_RERUN_AUTHORIZED`

Date: `2026-08-12`

## Scope

This certification closes the bounded correction loop for three ownership
layouts and the cross-shard physical Parquet contract:

- ATYR separates currently owned shares, shares acquirable within 60 days and
  total beneficial ownership;
- BASI places option-inclusive components in holder footnotes;
- OSG places an option-inclusive component in table-level notes;
- all-null columns previously produced Arrow `null` types that varied by case.

The generic resolver now uses the current-shares column only when current and
acquirable components are explicitly separated. If a reported aggregate
includes options or other shares issuable within the governed horizon and no
currently issued component can be isolated, it preserves the evidence but
fails closed. Grant and equity-award tables are not ownership baselines.

`daily_float_state.parquet` is now written through an explicit Arrow schema, so
calculated and blocked cases have identical names, order and physical types.

## Verification

- focused parser and schema tests: `38 passed`;
- complete SEC PIT suite: `226 passed`;
- production-equivalent probe batch:
  `sec_pit_residual_layout_shard_probe_v0_9_20260812T2120Z`;
- cases: `16`, four governed shards represented;
- O/S runs: `16/16`; ownership runs: `16/16`; execution failures: `0`;
- output rows: `80`; duplicate instrument-session keys: `0`;
- component-hash variants: `1`; Arrow-schema variants: `1`;
- formula, fraction, percent, range and causal violations: `0`;
- null float rows without explicit blockers: `0`;
- network requests during resolution: `0`.

## Required case outcomes

| Ticker | Certified outcome |
|---|---|
| ATYR | `5/5 CALCULATED`; current excluded shares `1,400,094`; acquirable shares are not subtracted as currently issued |
| BASI | `5/5 BLOCKED_BY_INPUT_GATES`; option-inclusive current component remains unresolved |
| OSG | `5/5 BLOCKED_BY_INPUT_GATES`; table-note option-inclusive component remains unresolved |

The newly closed ASPN, BNED, DOMH, MULN and TAOX results are intentional
fail-closed corrections: their aggregates include acquirable options or other
issuable securities and cannot be treated as current common shares.

## Decision

A fresh immutable 99-case no-network batch `v0_13` is authorized. It must use a
new output root and run identity, preserve one component-hash set, retain all
blockers, publish v0.12-to-v0.13 coverage and regression deltas, and must not be
promoted to the 4,824-instrument universe without a separate gate.
