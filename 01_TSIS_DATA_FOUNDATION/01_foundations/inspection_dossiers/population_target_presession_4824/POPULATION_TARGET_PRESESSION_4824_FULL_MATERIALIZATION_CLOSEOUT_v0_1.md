# POPULATION_TARGET_PRESESSION_4824_FULL_MATERIALIZATION_CLOSEOUT_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `population_target_presession_4824_full_materialization_closeout` |
| `document_version` | `v0_1` |
| `document_role` | `EXECUTED_DATASET_CLOSEOUT` |
| `document_status` | `EXECUTED_AND_RECONCILED` |
| `selector_gate` | `PASS_WITH_RESTRICTIONS` |
| `dataset_validation_gate` | `PASS` |
| `promotion_state` | `VALIDATED_EXPERIMENTAL_CANDIDATE_NOT_CANONICAL` |
| `ta3_sample_freeze_state` | `AUTHORIZED_NEXT_STEP` |
| `created_at` | `2026-08-07` |

---

## 1. Purpose

Close the full-history materialization and independent validation of the
presession population selector candidate used to build the Trading Activity
TA-3 development inventory.

This closeout does not promote a canonical population table. It proves that the
declared proxy binding was materialized deterministically and passed its
registered physical validation checks.

---

## 2. Executed binding

```text
parent universe
= lt1b_universe_v0_1

grain
= instrument_id x ticker_as_of_session x session_date

presession cutoff
= 04:00 America/New_York

reference price
= prior eligible RTH close

shares binding
= S1_DILUTED_FIRST

shares availability rule
= as_of_date < session_date
  DATE_ONLY_CONSERVATIVE_AVAILABILITY

shares TTL
= 180 calendar days

membership rule
= common stock
  AND 0.50 <= reference price <= 20.00
  AND reference price x shares proxy < 100,000,000 USD
```

The shares input remains a weighted-average accounting proxy. It is not claimed
to be exact point shares outstanding.

---

## 3. Materialized dataset

```text
run_id
= population_target_presession_4824_candidate_v0_1_experimental_20260807T170430Z

physical root
= G:/TSIS/data/data_foundation_outputs/
  population_target_presession_4824_candidate/
  population_target_presession_4824_candidate_v0_1_experimental_20260807T170430Z

rows
= 7,369,699

tickers
= 4,824

sessions
= 5,328

date range
= 2005-01-03 through 2026-03-09

parquet bytes
= 464,353,246

parquet sha256
= a777b3338d1ff2f2304e768113a5a14728d16372553081b144c943a93fa0702c
```

Membership accounting closes over every requested parent-universe context:

| Membership state | Rows |
|---|---:|
| `ELIGIBLE_UNDER_DECLARED_PROXY` | 1,417,316 |
| `INELIGIBLE_MARKET_CAP_PROXY` | 1,689,229 |
| `INELIGIBLE_PRICE` | 2,360,588 |
| `STALE_SHARES_PROXY` | 201,243 |
| `UNAVAILABLE_REFERENCE_PRICE` | 671,242 |
| `UNAVAILABLE_SHARES_PROXY` | 1,027,005 |
| `CORPORATE_ACTION_REVIEW` | 3,076 |

`blocked`, stale and unavailable contexts were preserved. They were not
silently rewritten as ineligible.

---

## 4. Independent validation

```text
validator
= population_target_presession_4824_candidate_validator_v0_1

validation artifact
= population_target_presession_4824_candidate_validation_v0_2.json

validation sha256
= 8c0ff06e8c1689b364bb2cd7dd800d5fd04fa45e4824fce1c1f355ea9c0405ec

checks passed
= 21 / 21

validation gate
= PASS
```

The validation proves:

```text
complete denominator accounting
unique population_context_id and master_daily_id
unique composite instrument-ticker-session grain
04:00 ET cutoff
strict date-only shares cutoff
exact declared market-cap formula
valid eligible and ineligible semantics
exact S1_DILUTED_FIRST x TTL_180D binding
resolved shares-source identity
all five price bands and four eligible cap bands present
all prohibited canonical and historical claims remain false
```

---

## 5. Telemetry incident and reconciliation

The wrapper failed while replacing `heartbeat_latest.json`, because the monitor
held a transient Windows file lock. The materializer process remained alive and
completed the parquet, manifest and summary with empty stderr.

The run is therefore closed as:

```text
final_status
= COMPLETE_RECONCILED

normal_wrapper_completion
= false

materializer_process_completed
= true

independent_validation
= PASS
```

Reconciliation required all of the following evidence:

```text
candidate manifest exists
candidate hash matches its manifest
7,369,699 rows preserve the denominator
independent validator passes 21/21 checks
materializer stderr is empty
```

The wrappers were hardened so heartbeat-write exceptions are recorded instead
of terminating the controlling process. This operational incident does not
change dataset semantics.

---

## 6. Restrictions that remain binding

This dataset must not be described as:

```text
the complete historical US common-stock population below 100M
an exact historical point-shares table
a historical float table
a session-open market-cap table
a canonical scanner universe
a Wake-up label or detector output
```

The valid claim is narrower:

```text
Within the fixed 4,824-ticker parent universe, the dataset represents a
presession membership candidate using prior eligible RTH close and a
date-conservative weighted-average shares proxy under the frozen S1/180 binding.
```

The composite identity grain is mandatory because `instrument_id` alone is not
exclusive across all ticker histories in the parent universe.

---

## 7. Authorization boundary

```text
TA-3 DEVELOPMENT INVENTORY
= AUTHORIZED

TA-3 DETERMINISTIC SAMPLE FREEZE
= AUTHORIZED_NEXT_STEP

BROAD TA-3 BINDING A EXECUTION
= NOT_AUTHORIZED_UNTIL_SAMPLE_MANIFEST_GATE

VALIDATION OR FINAL-TEST FEATURE READS
= NOT_AUTHORIZED

CANONICAL POPULATION PROMOTION
= NOT_AUTHORIZED
```

The next artifact must freeze the TA-3 development inventory, selected blocks,
blocked contexts, marginal shortfalls, exact row projection and manifest hash.

---

## 8. Evidence

The dossier evidence directory contains lightweight copies of:

```text
population_target_presession_4824_full_materialization_final_manifest_v0_1.json
population_target_presession_4824_full_materialization_incident_v0_1.json
population_target_presession_4824_full_materialization_candidate_manifest_v0_1.json
population_target_presession_4824_full_materialization_summary_v0_1.json
population_target_presession_4824_full_materialization_validation_v0_2.json
```

The 464 MB parquet remains only in the governed heavy-output root and is not
duplicated into the repository.
