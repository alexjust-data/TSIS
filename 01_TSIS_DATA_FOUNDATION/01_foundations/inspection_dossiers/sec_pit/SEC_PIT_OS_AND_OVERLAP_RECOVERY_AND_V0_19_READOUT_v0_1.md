# SEC PIT O/S and overlap recovery and v0.19 readout v0.1

Status: `PASS_WITH_MEASURED_RESIDUALS_4824_NOT_LAUNCHED`

Date: `2026-08-13`

## Decision

The bounded recovery loop for `SHARES_OUTSTANDING_UNAVAILABLE`,
`HOLDER_OVERLAP_UNRESOLVED` and
`ECONOMIC_POSITION_OVERLAP_UNRESOLVED` is complete. Production-equivalent
probes passed on every governed shard before the immutable 99-case rerun.
Authoritative v0.19 completed 99/99 O/S executions and 99/99 ownership
executions with zero failures and zero network requests.

Relative to authoritative v0.18:

```text
O/S complete                      56/99 -> 71/99  (+15 cases)
owner-exclusion float complete    16/99 -> 31/99  (+15 cases)
SHARES_OUTSTANDING_UNAVAILABLE    17    -> 6      (-11 cases)
HOLDER_OVERLAP_UNRESOLVED         21    -> 5      (-16 cases)
ECONOMIC_POSITION_OVERLAP_UNRESOLVED
                                  20    -> 4      (-16 cases)
O/S regressions                                  0
float regressions                                0
```

This is a measured bounded-sample result, not a coverage claim for the 4,824
instruments. The 4,824-instrument diagnostic was not launched and remains
unauthorized until a new deliberate operator decision.

## Authoritative evidence

| Artifact | Identity / SHA-256 |
|---|---|
| O/S four-shard certification | `sec_pit_os_unavailable_shard_certification_v0_1_20260813T1552Z` |
| O/S certification final manifest | `8f054c65afef685d527700e976bec36a1a0287b477d7350fc25378918ccac58d` |
| overlap four-shard certification | `sec_pit_overlap_shard_certification_v0_1_20260813T1545Z` |
| overlap certification final manifest | `7deb1c17ee9c29fd8050080a4e374943087c75d157ea7f8f0a38c79e79b3b30a` |
| exact overlap gate audit | `bd0089e62af99704f688bb90893e95362b99f4cd2093e2cf2e2a560226231fc8` |
| immutable authoritative rerun | `sec_pit_100_case_resolution_v0_19_20260813T1600Z` |
| rerun final manifest | `52d97bd0c58078fc1c0dda57ac86db68d79c4ea224b3d8f186c438e6d0e6dec2` |
| 99-case owner-result audit | `36c4815f6dfc0dfbb90f576546f96a7cd14aafe6e93da0719caceac53782d382` |
| 99-case four-shard certification | `sec_pit_v0_19_99_case_certification_v0_1_20260813T1625Z` |
| 99-case certification final manifest | `7ef1e20957ebd0cf8a3345734f4e7eaf066a78a4139ed354f81f4deca659e457` |
| coverage summary | `248a3b2ca9aefacfee9c4706309ae2f073148c05589e68f3e781b44fd89f0349` |
| case-level coverage | `3b47c248c74b8550623486ee9a06f83a1b59f0c8b8a7e1bbb93ca8fb5c2eec1a` |

Runtime root:

`C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_19`

The frozen acquisition ledger, case matrix, selection plan and Company Facts
input were preserved. The Company Facts observations retained SHA-256
`6647ae0b44c6e05d38e5fb4f099895afeca8d8591ea653f090013d3dc1f69e24`.

## O/S recovery semantics

The O/S correction admits exact target-class observations only when filing
identity continuity and class evidence are sufficient. It adds bounded cover
page/table layouts for residual primary filings and supports exact archive-CIK
continuity plus exact exchange-table ticker/class evidence. Authorized,
issuable, reserved and underlying-share statements remain rejected. Ambiguous
classes, non-target issuers and unsupported instruments still fail closed.

The 11 cases that lose `SHARES_OUTSTANDING_UNAVAILABLE` are:

```text
AGL AIFE CYTO INPX MPO NHTC SHYF SNES STAF VELO VISL
```

Four additional cases with previously partial O/S coverage become complete
across all five sessions:

```text
CLRB IPXX OSG VIVE
```

Therefore total full-session O/S gains are 15. The six remaining unavailable
cases are:

```text
ANTH BPT ELYS ETAK MCAC SAIH
```

They remain NULL because the available evidence still contains a Company
Facts conflict, unsupported beneficial-interest units, equally specific class
ambiguity, missing exact exchange continuity or unresolved multi-class
admission. No manual number was imputed.

## Holder and economic-position overlap semantics

The holder ledger now recognizes only source-described indirect account or
vehicle relationships. An explicit vehicle can be deduplicated within the
same source even when repeated through multiple reporting owners, and the
economic-position identity preserves observation date and share amount.
Anonymous spouse references, unnamed entities and truncated descriptions are
not inferred and remain unresolved.

Both overlap blockers are removed together in these 16 cases:

```text
ALR AUMN AYRO BTBT CDAQ CJES CLRB JONE LAB MBI MTEM OMCC SMIT VINO VIVE VLCN
```

The holder residual is:

```text
ADTX BASI BRPA CDT SPI
```

The economic-position residual is:

```text
ADTX BASI CDT SPI
```

BRPA is holder-only. The four-shard controls were CDAQ, LAB, JONE and BTBT.
All target overlap blockers were absent in those controls; CDAQ correctly
retained the independent `SHARE_CLASS_ALLOCATION_UNRESOLVED` blocker.

The new account identity is methodology-scoped to a filing/source. It does not
claim temporal equivalence of anonymous accounts across filings. Cross-filing
updates remain governed by the separate causal daily resolver.

## Authoritative v0.19 result

```text
eligible cases                    99
O/S executions                    99/99
ownership executions              99/99
failed executions                 0
network requests                  0
owner-result audit                PASS (99/99)
four-shard certification          SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING
O/S complete                      71/99 = 71.72%
owner-exclusion float complete    31/99 = 31.31%
float non-NULL                    155/495 rows
partial-float cases               0
```

The 31 complete-float cases are:

```text
AGL AIEV AIFE ALUR ATMC ATMV ATYR AUMN AYRO BGM CYTO EJH ENFY INPX IOBT
MBI MPO MTEM NHTC ONCO PGAC PLL PTE SHYF SNES STAF SYTA TAOX VISL VIVE WINT
```

The 15 new complete-float cases are:

```text
AGL AIFE AUMN AYRO CYTO INPX MBI MPO MTEM NHTC SHYF SNES STAF VISL VIVE
```

No v0.18 O/S-complete or float-complete case regressed.

## Measured residuals and next work

Current blocker counts overlap by case:

| Remaining blocker | Cases |
|---|---:|
| `SHARE_CLASS_ALLOCATION_UNRESOLVED` | 26 |
| `OWNERSHIP_SPLIT_ADJUSTMENT_UNRESOLVED` | 16 |
| `POST_BASELINE_EVENT_IDENTITY_OR_DATE_UNRESOLVED` | 11 |
| `SHARES_OUTSTANDING_UNAVAILABLE` | 6 |
| `HOLDER_OVERLAP_UNRESOLVED` | 5 |
| `ECONOMIC_POSITION_OVERLAP_UNRESOLVED` | 4 |
| `BASELINE_DOCUMENT_PARTIAL` | 3 |
| one-case residual families | 4 |

Split and post-baseline counts rise from 12 to 16 and from 7 to 11 because
the resolved overlap gate now allows those later causal dependencies to be
observed. This is downstream blocker exposure, not a coverage regression.

The next bounded engineering priorities are exact target-class allocation,
split-basis reconciliation and causal post-baseline event application. Every
semantic change still requires tests, a production-equivalent probe on each
shard, variable audit, versioned certification, governed PASS and a new
immutable bounded delta before scale can be reconsidered.

Long operations are operator-launched: the agent must provide the exact
one-line command, the operator launches it, and the agent waits for the
operator's completion report. No future long run is implied by this readout.

