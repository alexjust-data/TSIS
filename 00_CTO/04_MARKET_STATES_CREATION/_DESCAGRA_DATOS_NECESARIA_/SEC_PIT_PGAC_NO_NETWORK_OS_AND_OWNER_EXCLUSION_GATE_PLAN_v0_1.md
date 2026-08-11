# SEC PIT PGAC No-Network O/S and Owner-Exclusion Gate Plan `v0_1`

Date: 2026-08-11
Status: `AUTHORIZED_BOUNDED_PGAC_EXECUTION`
Promotion state: `designed`
Owner: `00_CTO/04_MARKET_STATES_CREATION` for meaning and gates;
`01_TSIS_DATA_FOUNDATION` for executable code, tests and evidence.

## 1. Human decision and purpose

The human authorized continuation of the PGAC pilot after the primary
acquisition review. This authorization is deliberately bounded:

```text
ticker                       = PGAC
network_downloads            = PROHIBITED
input_primary_documents      = existing 68 verified objects
first variable               = SHARES_OUTSTANDING_ESTIMATE_AS_KNOWN
second variable              = FLOAT_OWNER_EXCLUSION_ESTIMATE_AS_KNOWN
tradability                  = DEFERRED_SEPARATE_LANE
institutional_13F            = DEFERRED_GLOBAL_LANE
other tickers                = NOT_AUTHORIZED
canonical promotion          = NOT_AUTHORIZED
```

The decisive question is:

```text
Can TSIS explain and reproduce every admitted change in PGAC shares outstanding
and owner-exclusion float using only evidence eligible before each session
cutoff?
```

## 2. Frozen inputs

Primary acquisition lineage:

```text
run_id = sec_pit_pgac_primary_v0_2_20260811T1035Z
planned/fetched = 68/68
payload integrity = PASS
selection_plan_sha256 = ddce5a64826268ceb4f36d34476eba03d879c9a47c6a94d634a7af74823bb998
```

Identity target:

```text
parent_universe_id = lt1b_universe_v0_1
ticker = PGAC
instrument_id = cik_ticker:0002030829:PGAC
cik = 0002030829
security = Pantages Capital Acquisition Corporation Class A Ordinary Shares
governed vendor interval = 2025-08-08 .. 2026-03-09
observed market presence = 2025-08-15 .. 2026-03-06
```

The same CIK also has AIFE prehistory. CIK equality does not admit a filing to
the PGAC instrument. The 14 O/S-role documents split into:

```text
9 opening-prehistory candidates = multiple AIFE/PGAC instruments; not admitted
3 target-interval candidates    = single PGAC candidate; still must be proven
2 post-interval candidates      = no instrument candidate; not admitted
```

## 3. Mandatory sequence

```text
S0 freeze units and schema
-> S1 prove accession-to-instrument/class scope
-> S2 extract neutral O/S observations
-> S3 reconcile and admit O/S anchors
-> S4 resolve daily PGAC O/S PIT
-> S5 audit every O/S state change manually
-> S6 extract neutral ownership events
-> S7 resolve holder identities and economic-position overlaps
-> S8 calculate owner-exclusion float
-> S9 audit every float state change manually
-> bounded promotion decision for a difficult multi-ticker probe
```

No later stage may convert a candidate into an admitted value merely because an
earlier stage produced a number.

## 4. S0 — unit and schema freeze

The existing implementation used a column named `float_percent` for a 0–1
ratio in one path while another path and the governing contract use 0–100.
The corrected contract is:

```text
float_fraction_estimate_as_known
= float_owner_exclusion_estimate_as_known / shares_outstanding_estimate_as_known
range = [0, 1]

float_percent_estimate_as_known
= 100 * float_fraction_estimate_as_known
range = [0, 100]
```

Both may be emitted, but neither name may carry the other unit. Existing BNAI
artifacts remain historical evidence and must not be silently rewritten.

S0 PASS requires unit tests for calculated, blocked, zero-O/S and boundary
cases plus explicit output-schema metadata.

## 5. S1 — accession-to-instrument admission

Every selected accession must receive one of:

```text
ADMITTED_PGAC_CLASS_A
REJECT_AIFE_OR_OTHER_INSTRUMENT
REJECT_POST_INTERVAL_WITHOUT_TARGET
UNRESOLVED_REQUIRES_MANUAL_REVIEW
```

Admission evidence may use filing title, registrant/security names, ticker and
exchange mentions, share-class wording, cover page, registration chain and the
governed identity interval. CIK alone is never sufficient.

The three initial target-interval O/S candidates are:

```text
0001213900-25-075873  10-Q  2025-08-14
0001213900-25-108205  10-Q  2025-11-10
0001213900-26-024889  10-K  2026-03-09
```

S1 PASS requires an accession-level ledger with evidence excerpt, source hash,
decision, reason and reviewer state. Unresolved rows cannot enter S3.

## 6. S2 — neutral O/S event extraction

For every admitted primary object, use deterministic extraction before any
manual override:

```text
instrument_id
security_class_id
accession_number
form
observation_type
shares_outstanding
unit
measurement_at
filing_accepted_at
available_at, when demonstrable
eligible_from_session
source_url
source_sha256
source_excerpt or XBRL locator
extraction_method
quality_state
causality_state
```

Cover-page text/XBRL anchors, capital events and deterministic corporate
actions remain separate observation types. Weighted-average basic/diluted
shares are prohibited as O/S anchors.

## 7. S3 — anchor reconciliation and admission

Independent extractions may agree, conflict or cover different concepts. The
resolver must preserve all candidates and admit only anchors that pass:

```text
identity and class
measurement date
availability and eligible session
issued common/ordinary shares semantics
source integrity
cross-extraction agreement or documented manual evidence
no unresolved conflict at the selected precedence level
```

Every admission or rejection must be reproducible from the event ledger.

## 8. S4 — daily O/S PIT probe

The probe uses the production resolver and the bounded PGAC session calendar.
It emits exactly one row per expected session, including unavailable rows.

Required columns:

```text
instrument_id
session_date
shares_outstanding_estimate_as_known
os_state
anchor_observation_id
anchor_measurement_at
anchor_eligible_from_session
staleness_days
source_conflict_state
causality_state
```

Required audit:

- stable names, types and order;
- unique `instrument_id x session_date` grain;
- no anchor used before `eligible_from_session`;
- explicit NULL, stale, conflict and unavailable states;
- source, policy, methodology and run lineage;
- readable first, last, changed and unavailable samples.

## 9. S5 — manual change explanation gate

Produce a compact table for every transition:

```text
session_date
previous_os
new_os
source_accession
source_excerpt_or_xbrl_locator
measurement_at
eligible_from_session
share_class_decision
corporate_action_basis
change_reason
review_verdict
```

S5 fails if any numerical change cannot be explained without hidden context.

## 10. S6–S9 — ownership and owner-exclusion float

Only after S5 PASS:

```text
raw ownership document
-> normalized holder/account/share event
-> canonical holder and group identity
-> economic_position_id and overlap_group_id
-> latest causal account state
-> unique supported excluded issued-common shares
-> owner-exclusion float fraction and percent
```

Direct/indirect representations, controlled entities, aggregate management
rows and sequential Forms 3/4/5 must never be summed without overlap/account
resolution. Missing coverage produces NULL, never zero or `float = O/S`.

## 11. Outputs and run boundary

The bounded run must create a new versioned run root and at minimum:

```text
pre_manifest.json
pid_manifest.json, if a wrapper is used
heartbeat.jsonl, if runtime exceeds the bounded quick-probe threshold
accession_instrument_admission.parquet
os_source_observations.parquet
os_anchor_reconciliation.json
admitted_os_anchors.parquet
daily_os_state.parquet
os_change_explanation.parquet
variable_audit.json
final_manifest.json
```

The run must record component hashes, frozen input hashes, schemas, row counts,
missingness, state counts and the no-network assertion.

## 12. Gate decisions

```text
PGAC_OS_PROBE_PASS
= S0 PASS
  and S1 PASS
  and S2 PASS
  and S3 PASS
  and S4 PASS
  and S5 PASS

PGAC_OWNER_EXCLUSION_PROBE_PASS
= PGAC_OS_PROBE_PASS
  and S6 PASS
  and S7 PASS
  and S8 PASS
  and S9 PASS
```

Failure at any stage blocks subsequent stages, requires a new implementation or
config version and repetition of the complete PGAC probe. Resume may never mix
schemas, formula versions, selection hashes or resolver versions.

## 13. Explicit non-goals

This gate does not authorize:

- any SEC network request;
- another ticker download;
- inference that prehistory AIFE belongs to PGAC;
- tradability-eligibility float;
- global 13F acquisition;
- canonical Fundamental Context promotion;
- scanner, backtest, ML/RL or live consumption;
- scale-out to the parent universe.
