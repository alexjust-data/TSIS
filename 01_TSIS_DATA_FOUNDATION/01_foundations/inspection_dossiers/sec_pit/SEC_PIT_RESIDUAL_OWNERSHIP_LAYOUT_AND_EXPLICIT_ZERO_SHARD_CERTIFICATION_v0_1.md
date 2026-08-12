# SEC PIT residual ownership layout and explicit-zero shard certification v0.1

Status: `PASS_BOUNDED_99_CASE_RERUN_AUTHORIZED`

Date: `2026-08-12`

## Scope and finding

The authoritative v0.11 result left six cases under
`AMENDMENT_FAMILY_UNRESOLVED`: BASI, BPT, KXIN, NAT, OSG and SAIH. Local
no-network inspection proved that five represented different semantic/layout
states rather than unresolved amendment families:

- BASI uses `Name / Shares Owned / %` without a document-level ownership
  heading;
- KXIN uses an exact multiclass table with plain `Ownership` wording;
- SAIH interleaves `Class A shares / % / Class B shares / %` columns;
- OSG reports beneficial ownership inclusive of shares issuable through options
  within 60 days and therefore cannot be treated as currently issued supply;
- BPT explicitly states that management/trustee entities own no Units;
- NAT contains no numeric aggregate management position and remains unresolved.

The parser now recognizes the generic layouts, maps exact multiclass components,
marks option-inclusive tables as currently-issued-component unresolved, and
emits a zero management aggregate only when the filing explicitly states that
management owns no shares/units. Missing tables and `no holder above 5%` do not
imply zero.

## Invalidated probes

`sec_pit_100_case_residual_layout_shard_probe_v0_1` and `v0_2` are diagnostic
only. The parser changed after each, so neither authorizes a long rerun.

## Final production-equivalent probe

Evidence root:
`C:/TSIS_Data/runtime/sec_pit_100_case_residual_layout_shard_probe_v0_3`

All cases used ownership parser SHA-256 prefix `23f0bbb7d0a7`, immutable local
SEC objects, O/S v0.11 dependencies and zero network requests.

| Shard | Ticker | Extracted state | Final behavior |
|---:|---|---|---|
| 0 | NAT | no numeric management aggregate | `NULL`, amendment-family residual |
| 1 | BASI | aggregate `1,393,546`, option-inclusive | `NULL`, class/holder/economic overlap |
| 1 | BPT | explicit management aggregate `0` | `NULL`, O/S unavailable |
| 2 | KXIN | Class A `22,222` + Class B `2,100,000` | `NULL`, intervening split |
| 1 | SAIH | Class A `0` + Class B `642,043` | `NULL`, O/S unavailable |
| 3 | OSG | aggregate `6,742,437`, option-inclusive | `NULL`, class + identity gates |

The OSG and BASI values are preserved as reported beneficial ownership but have
`supported_issued_common_shares = NULL`; they are not subtracted from current
O/S. BPT uses `PRESENT_TENSE_ZERO_AS_OF_FILING_ACCEPTANCE_DATE` and preserves
the filing accession and availability lineage.

## Tests and decision

- focused ownership parser suite: `32 passed`;
- complete SEC PIT suite: `220 passed`;
- final probe network requests: `0`;
- one production-equivalent case covered every governed shard;
- extra controls covered every new semantic/layout family.

A fresh immutable v0.12 99-case no-network rerun is authorized. It must use a
new root/run identity, preserve one component-hash set across all cases, publish
v0.11-to-v0.12 regressions and blocker deltas, and keep 4,824-instrument scale
`NOT_GRANTED`.
