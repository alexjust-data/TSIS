# Trading Activity Binding B exact specification v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_b_exact_specification` |
| `document_version` | `v0_1` |
| `document_role` | `EXPERIMENTAL_BINDING_EXACT_SPECIFICATION_DRAFT` |
| `document_status` | `DRAFT_FOR_HUMAN_AND_SCIENTIFIC_REVIEW_NOT_FROZEN` |
| `information_object_id` | `trading_activity` |
| `binding_id` | `trading_activity_binding_b_event_time_renewal_burst_v0_1` |
| `representation_id` | `PIT_NORMALIZED_EVENT_TIME_MARKED_RENEWAL_AND_BURST_STATE` |
| `comparison_incumbent` | `trading_activity_binding_a_candidate_v0_2` |
| `b01_contract_status` | `FROZEN_BY_HUMAN_AFTER_EXTERNAL_AUDIT` |
| `b01_contract_sha256` | `50dbfa50730ed0832711d626864a719a285195e582e6157650faca7d4a20ffd9` |
| `b01_freeze_readout` | `TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md` |
| `implementation_authorized` | `false` |
| `probe_execution_authorized` | `false` |
| `long_materialization_authorized` | `false` |
| `a_b_comparison_authorized` | `false` |
| `temporal_oos_authorized` | `false` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-15` |

## 1. Status and interpretation

This document is the authorized B-02 draft. It is not frozen and cannot yet be
used as implementation authority.

Every normative item is classified as one of:

```text
FROZEN_B01_INHERITANCE
= already fixed by the human-frozen inheritance/delta boundary

PROPOSED_B02_FREEZE
= concrete specification candidate, reviewable but not yet authoritative

BLOCKING_B02_FREEZE
= unresolved decision that must close before B-02 can freeze
```

No implementation, probe, materialization or A/B comparison may begin while
any `BLOCKING_B02_FREEZE` item remains or while `document_status` is not
`FROZEN_BY_EXPLICIT_HUMAN_GATE`.

## 2. Governing authorities and evidence

### 2.1 B-specific authorities

1. `TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md`
2. `TRADING_ACTIVITY_BINDING_B_DEVELOPMENT_AND_CERTIFICATION_PLAN_v0_1.md`
3. `TRADING_ACTIVITY_BINDING_B_INHERITANCE_AND_DELTA_CONTRACT_v0_1.md`
4. `TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md`

### 2.2 Inherited Trading Activity authorities

1. `TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md`
2. `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md`
3. `TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`
4. `TRADING_ACTIVITY_TRADE_ELIGIBILITY_POLICY_v0_2.md`
5. `TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md`
6. `TRADING_ACTIVITY_LATENCY_POLICY_REGISTRY_v0_1.md`
7. `TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md`
8. `TRADING_ACTIVITY_STRATIFIED_DEVELOPMENT_SAMPLE_PLAN_v0_1.md`
9. `EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_2.md`
10. `REPRESENTATION_MODEL_MATERIALIZATION_AND_INCIDENT_LEARNING_PROTOCOL_v0_1.md`

### 2.3 Hash-bound incumbent and denominator

```text
Binding A exact specification SHA-256
= e6f59fae69dadc032d5d7f35add287110917e89926f6a0bead5ddaf644d29b19

Binding A independent replay final manifest SHA-256
= 634e71bccfd10bdc30b82038b9c767e5738b530e94894bc501db579e679fc857

shared sample manifest SHA-256
= 100f0ac0e1faaecd54eded1d99886daafbe9ecf374a247fa9835febc70b1addf

shared selected-target table SHA-256
= 55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220

shared denominator
= 240 blocks / 2,400 exact TARGET sessions
```

## 3. Scientific identity and exclusion boundary

Classification: `FROZEN_B01_INHERITANCE`.

```text
Information Object
= Trading Activity

minimum meaning
= observable traded participation
  + intensity
  + explicit temporal scale
  + realized trading
  + point-in-time legality
```

Binding B must conserve:

- absolute activity;
- event intensity;
- activity marks;
- temporal concentration;
- PIT-relative surprise;
- persistence, decay and reactivation.

It must exclude price direction, return, spread, depth, aggressor side, signed
flow, OFI, scanner selection, event labels, future outcomes, MFE/MAE and any
entry, stop, target or sizing rule.

## 4. Source, sessions, decision grid and availability

Classification: `FROZEN_B01_INHERITANCE`.

```text
source root
= G:/TSIS/data/trades_ticks_prod_2005_2026

source scope
= legacy_rth_reconciled_event_time_research_only

calendar
= XNYS from market_calendar_v0_1

decision unit
= SYMBOL_SECOND

decision timestamps
= integer UTC seconds satisfying
  session_open_utc < decision_timestamp < session_close_utc

output authority
= D:/TSIS/IO
```

The primary simulated latency policy is:

```text
LATENCY_PRIMARY_CONSERVATIVE_V0_1 = 1000 ms
```

Secondary sensitivity policies are `100 ms` and `5000 ms`. At decision time
`t`, a trade is consumable only when:

```text
simulated_available_at
= legacy_event_time + registered_latency

simulated_available_at <= t
```

All intraday B state resets at the governed RTH open. Missing source sessions
remain explicit `UNAVAILABLE` denominator members.

## 5. Authoritative event time and timestamp clusters

### 5.1 Physical timestamp

Classification: `FROZEN_B01_INHERITANCE`.

The physical source field is `timestamp[us]`. It is interpreted as the legacy
collapsed UTC source timestamp and normalized to:

```text
legacy_event_time : timestamp[us, UTC]
```

The physical dtype carries microsecond storage resolution:

```text
timestamp_resolution_us = 1
```

This field describes retained storage resolution. It does not claim that the
upstream venue timestamp was originally accurate to one microsecond. The
source has already lost original timestamp type, nanosecond precision,
timezone metadata and authoritative arrival order.

### 5.2 Cluster key and marks

Classification: `PROPOSED_B02_FREEZE`.

For one `instrument_id`, `session_date` and latency-policy projection, every
eligible and causally available row with the same exact normalized
`legacy_event_time` belongs to one cluster `j`:

```text
tau_j = legacy_event_time
n_j   = eligible trade-row count
q_j   = sum(size)
v_j   = sum(price * size)
delta_j = tau_j - tau_(j-1)
```

`q_j` is accumulated as checked `int64`. `v_j` is accumulated as deterministic
`float64` in ascending `physical_row_ordinal`; that ordinal fixes numerical
reconstruction only and makes no causal claim. The independent oracle must use
the same declared summation rule or an explicitly frozen tolerance.

### 5.3 Prohibitions and state reasons

Classification: `PROPOSED_B02_FREEZE`.

```text
artificial timestamp jitter                  = PROHIBITED
timestamp interpolation                      = PROHIBITED
physical_row_ordinal as economic sequence    = PROHIBITED
within-cluster duration inference             = PROHIBITED
```

Required reasons:

```text
TIMESTAMP_RESOLUTION_INSUFFICIENT
= timestamp cannot be normalized to the required microsecond UTC contract
  or the source schema is coarser than the frozen contract

EVENT_ORDER_UNRESOLVED
= cluster contains more than one eligible row; marks remain usable but no
  within-cluster causal order is asserted

INSUFFICIENT_DISTINCT_CLUSTERS
= the feature requires more distinct clusters than are causally available
```

Mandatory companions at every decision row:

```text
same_timestamp_cluster_trade_count : int64 nullable
timestamp_resolution_us            : int64 non-null when source is readable
distinct_cluster_count_available   : int64 non-null
```

## 6. PIT population and context alignment

Classification: `FROZEN_B01_INHERITANCE` for membership and
`PROPOSED_B02_FREEZE` for B statistics.

The candidate populations remain `B20`, `B60` primary and `B120`. A baseline
uses only strictly prior admitted sessions for the same instrument and frozen
source, eligibility, latency and schema policies. It never contains the target
session or any future session.

Proposed B alignment:

```text
same instrument_id
same XNYS rth_minute_index
same decision_second_within_minute
same feature definition and policy IDs
```

Each prior session contributes at most one baseline observation for a given
feature/decision context. Required support is exactly `B` admitted prior
sessions for B20/B60/B120; otherwise the candidate is
`BASELINE_INSUFFICIENT_HISTORY`.

## 7. Baseline intensity and operational time

### 7.1 Piecewise prior-only intensity

Classification: `PROPOSED_B02_FREEZE`.

For each reference session `s` and RTH minute `m`:

```text
C_(s,m) = distinct causally eligible clusters in minute m
L_(s,m) = observable seconds in minute m
r_(s,m) = C_(s,m) / L_(s,m)          [clusters / second]
```

For candidate `B`:

```text
lambda0_B(instrument, m)
= median_s(r_(s,m)) over the exact B prior sessions
```

Integration across minute boundaries is exact and piecewise constant:

```text
R_B(a,b) = integral[a,b] lambda0_B(u) du
```

No single-minute approximation may be used when `[a,b]` crosses a governed
minute boundary.

### 7.2 Zero-dominated baseline

Classification: `PROPOSED_B02_FREEZE`; threshold approval is blocking.

```text
baseline_zero_fraction_B
= count_s(r_(s,m) = 0) / B

ZERO_DOMINATED
= median_s(r_(s,m)) = 0
  OR baseline_zero_fraction_B >= 0.50
```

No hidden positive floor may fabricate `lambda0`. Operational-time variables
are `NULL` under `ZERO_DOMINATED` or `BASELINE_INSUFFICIENT_HISTORY`, while the
zero fraction and separate silence-break variable remain materialized.

### 7.3 Rescaled durations

Classification: `PROPOSED_B02_FREEZE`.

```text
rescaled_duration_current_B60(t)
= R_B60(tau_last, t)

rescaled_completed_duration_j_B60
= R_B60(tau_(j-1), tau_j)

operational_time_compression_20_B60
= -ln(median(last 20 rescaled completed durations))

fast_rescaled_duration_fraction_20_B60
= count(last 20 rescaled durations <= theta_fast) / 20

fast_rescaled_duration_run_length_B60
= consecutive completed durations ending at tau_last
   satisfying rescaled duration <= theta_fast
```

At least 21 distinct clusters are required for the last 20 completed
durations. Session open resets the sequence. Distinct timestamps guarantee
positive completed durations when `lambda0 > 0`; no epsilon is allowed inside
the compression median.

Proposed threshold:

```text
theta_fast = 0.10 expected clusters
```

Approval of `theta_fast` is `BLOCKING_B02_FREEZE`.

### 7.4 Silence-break surprise

Classification: `PROPOSED_B02_FREEZE`; formula approval is blocking.

For the exact prior-session baseline membership and corresponding one-second
decision interval:

```text
n_active = prior sessions with >= 1 causally available cluster in (t-1s, t]
p_active = (1 + n_active) / (B + 2)

silence_break_surprise_B60(t)
= -ln(p_active), if current interval contains >= 1 cluster
  0,             otherwise
```

This Laplace-smoothed empirical probability prevents infinite surprise without
inventing `lambda0`. `silence_break_surprise_B60` remains distinct from
operational-time features.

## 8. Event-clock renewal features

Classification: `PROPOSED_B02_FREEZE`.

At decision `t`, let `tau_last` be the latest causally available cluster:

```text
time_since_last_trade_cluster_us
= microseconds(t - tau_last)

elapsed_time_last_K_clusters_us
= microseconds(tau_last - tau_(last-K+1))
```

Primary `K` values are `5`, `20` and `50`. The elapsed feature requires exactly
K distinct available clusters in the current session. It is `NULL` with
`INSUFFICIENT_CLUSTER_HISTORY` otherwise. It never reaches into a prior session.

## 9. Continuous marked kernels

### 9.1 Direct definition

Classification: `PROPOSED_B02_FREEZE`.

For mark `m_j` and decay `tau` in seconds:

```text
K_(m,tau)(t)
= sum over available clusters j with tau_j <= t of
  m_j * exp(-(t - tau_j) / tau) / tau
```

Marks:

```text
trade mark  = n_j                  [trades]
share mark  = q_j                  [shares]
dollar mark = v_j                  [currency units]
```

Primary decays are `2s`, `10s` and `60s`; `300s` is secondary. All kernels
initialize at zero after session open, update only when a cluster becomes
causally available and decay continuously between updates. When multiple
clusters become available at the same decision time, their additive updates
are order-independent.

Raw companions are mandatory:

```text
trade_kernel_intensity_2s/10s/60s
share_kernel_rate_10s/60s
dollar_kernel_rate_2s/10s/60s
```

### 9.2 Robust PIT surprise

Classification: `PROPOSED_B02_FREEZE`.

For `x = log1p(K)` over the exact prior-only context:

```text
center = median(x)
scale_mad = 1.4826 * median(abs(x - center))

if scale_mad > 0:
    scale = scale_mad
else:
    scale_iqr = (Q75(x) - Q25(x)) / 1.349
    scale = scale_iqr when scale_iqr > 0

surprise = (log1p(K_current) - center) / scale
```

If both scales are zero, surprise is `NULL` with `BASELINE_ZERO_SCALE`; it is
not zero and does not use an unregistered floor.

### 9.3 Short/long kernel ratios

Classification: `PROPOSED_B02_FREEZE`; epsilon approval is blocking.

```text
kernel_log_ratio_2s_60s
= ln((K_2s + epsilon_kernel) / (K_60s + epsilon_kernel))

epsilon_kernel
= 1e-12 in the corresponding kernel-rate unit
```

The epsilon is numerical, explicit in metadata and identical for current and
baseline reconstruction. Approval of this value and unit policy is
`BLOCKING_B02_FREEZE`.

## 10. Economic time

Classification: `PROPOSED_B02_FREEZE`.

For each prior session at the same context, calculate realized causal dollar
volume in the trailing 60 seconds. Define:

```text
U_B60
= median of strictly positive prior-session 60-second dollar volumes
```

Proposed support:

```text
minimum positive observations
= ceil(B60 / 3) = 20
```

If support is lower, `U_B60` is `NULL` with
`BASELINE_INSUFFICIENT_POSITIVE_SUPPORT`. Approval of this support is
`BLOCKING_B02_FREEZE`.

At decision `t`, walk backward over causally available current-session
clusters until accumulated dollars first equal or exceed `U_B60`. No fraction
of a cluster is interpolated.

```text
elapsed_time_to_pit_dollar_unit_us
= microseconds(t - tau_first_included)

dollar_clock_compression_B60
= ln(60 seconds / elapsed_time_to_pit_dollar_unit)
```

If the unit is not attained before session open, the elapsed time is `NULL`
with `RIGHT_CENSORED_ECONOMIC_CLOCK`; companions record accumulated dollars and
observable lower-bound elapsed time. If the elapsed duration is physically
zero, use the explicit one-microsecond storage-resolution floor and set
`economic_clock_resolution_floor_applied = true`.

## 11. Mark concentration and burst persistence

Classification: `PROPOSED_B02_FREEZE`.

For the latest 20 distinct clusters, with dollar marks `v_j` and
`V = sum(v_j)`:

```text
cluster_dollar_hhi_20
= sum((v_j / V)^2)

top3_cluster_dollar_share_20
= sum(three largest v_j) / V
```

Both require 20 clusters and `V > 0`; otherwise they are `NULL` with the exact
reason state.

The persistence feature uses the trade kernel at `tau=10s`:

```text
current_to_recent_peak_trade_intensity_50
= K_trade_10s(t) /
  max(K_trade_10s immediately after each of the latest 50 cluster updates)
```

It requires 50 clusters and a positive peak. Session open resets the peak
history. Slope, burst age and reactivation remain secondary or diagnostic and
require a later exact threshold clause before use.

## 12. Primary variable set and ordered dtypes

Classification: `PROPOSED_B02_FREEZE`.

| Ordinal | Variable | Physical dtype | Nullable |
|---:|---|---|---|
| 1 | `time_since_last_trade_cluster_us` | `int64` | yes |
| 2 | `elapsed_time_last_5_clusters_us` | `int64` | yes |
| 3 | `elapsed_time_last_20_clusters_us` | `int64` | yes |
| 4 | `elapsed_time_last_50_clusters_us` | `int64` | yes |
| 5 | `rescaled_duration_current_B60` | `float64` | yes |
| 6 | `operational_time_compression_20_B60` | `float64` | yes |
| 7 | `fast_rescaled_duration_fraction_20_B60` | `float64` | yes |
| 8 | `fast_rescaled_duration_run_length_B60` | `int64` | yes |
| 9 | `baseline_zero_fraction_B60` | `float64` | yes |
| 10 | `silence_break_surprise_B60` | `float64` | yes |
| 11 | `trade_kernel_surprise_2s_B60` | `float64` | yes |
| 12 | `trade_kernel_surprise_10s_B60` | `float64` | yes |
| 13 | `trade_kernel_surprise_60s_B60` | `float64` | yes |
| 14 | `trade_kernel_log_ratio_2s_60s` | `float64` | yes |
| 15 | `dollar_kernel_surprise_2s_B60` | `float64` | yes |
| 16 | `dollar_kernel_surprise_10s_B60` | `float64` | yes |
| 17 | `dollar_kernel_surprise_60s_B60` | `float64` | yes |
| 18 | `dollar_kernel_log_ratio_2s_60s` | `float64` | yes |
| 19 | `dollar_clock_compression_B60` | `float64` | yes |
| 20 | `cluster_dollar_hhi_20` | `float64` | yes |
| 21 | `top3_cluster_dollar_share_20` | `float64` | yes |
| 22 | `current_to_recent_peak_trade_intensity_50` | `float64` | yes |

Values outside mathematical bounds are terminal certification failures; they
are not clipped. `int64` columns use Arrow nullable semantics.

## 13. Secondary and diagnostic variables

Classification: `PROPOSED_B02_FREEZE`.

Secondary preregistered variables:

```text
share_kernel_surprise_10s_B60
share_kernel_surprise_60s_B60
trade_intensity_slope_event_time_20
median_dollar_per_trade_20
dollar_mark_shift_robust_z_20_B60
trade/share/dollar kernels at tau=300s
short-long ratios 10s/300s
B20 and B120 variants
latency sensitivity 100ms
latency sensitivity 5000ms
duplicate-exclusion sensitivity
```

Initially diagnostic-only:

```text
last_intercluster_duration_us
burst_age_us
burst_reactivation_count_300s
```

Secondary/diagnostic fields cannot replace the primary set after validation is
observed. Any formula still lacking an exact threshold remains non-executable.

## 14. Mandatory companions, state and lineage schema

Classification: `PROPOSED_B02_FREEZE`.

Every primary row begins with this ordered identity/lineage prefix:

```text
instrument_id                     string non-null
ticker                            string nullable evidence only
session_date                      date32 non-null
decision_timestamp                timestamp[us, UTC] non-null
latency_policy_id                 string non-null
binding_id                        string non-null
specification_id                  string non-null
specification_sha256              string non-null
source_id                         string non-null
eligibility_policy_id             string non-null
pit_baseline_policy_id            string non-null
feature_input_max_available_at     timestamp[us, UTC] nullable
future_window_used                bool non-null, must be false
observation_state                 string non-null
calculation_state                 string non-null
calculation_reason_code           string nullable
```

Mandatory audit companions then include:

```text
timestamp_resolution_us
distinct_cluster_count_available
same_timestamp_cluster_trade_count
eligible_trade_row_count_available
exact_duplicate_row_count_available
baseline_candidate_id
baseline_reference_session_count
baseline_zero_fraction_B60
raw kernel fields listed in section 9
last_intercluster_duration_us
elapsed_time_to_pit_dollar_unit_us
economic_clock_accumulated_dollars
economic_clock_observable_lower_bound_us
economic_clock_resolution_floor_applied
```

The controlled reason vocabulary includes at minimum:

```text
OBSERVED_NONZERO
OBSERVED_ZERO
INSUFFICIENT_SAMPLE
DEGRADED
UNAVAILABLE
OUT_OF_SCOPE
TIMESTAMP_RESOLUTION_INSUFFICIENT
INSUFFICIENT_DISTINCT_CLUSTERS
EVENT_ORDER_UNRESOLVED
INSUFFICIENT_CLUSTER_HISTORY
BASELINE_INSUFFICIENT_HISTORY
BASELINE_INSUFFICIENT_POSITIVE_SUPPORT
BASELINE_ZERO_SCALE
ZERO_DOMINATED
RIGHT_CENSORED_ECONOMIC_CLOCK
NONPOSITIVE_MARK_SUM
```

`NULL` must always be paired with an exact calculation reason. Zero, missing,
degraded, unavailable and censored are never collapsed.

## 15. Proposed physical family topology and cardinality

Classification: `PROPOSED_B02_FREEZE`; topology approval is blocking.

Proposed families:

```text
event_time_state
= one row per exact TARGET symbol-second under the primary B60/1000ms policy

sensitivity_state
= one row per exact TARGET symbol-second containing preregistered secondary
  and diagnostic values

pit_baseline_evidence
= three rows per exact TARGET symbol-second, one for B20/B60/B120
```

If a target session has `D_s` governed decision seconds:

```text
event_time_state expected rows       = D_s
sensitivity_state expected rows      = D_s
pit_baseline_evidence expected rows  = 3 * D_s
```

The proposed physical partition count is one partition per family and target:

```text
2,400 targets * 3 families = 7,200 target-family partitions
```

This count is not copied as a scientific fact from A; it is a proposed B
storage topology. One terminal cardinality authority must generate expected
row/partition counts for the writer, monitor and certifier. Approval is
`BLOCKING_B02_FREEZE`.

## 16. Mandatory ablations and A/B comparison boundary

Classification: `PROPOSED_B02_FREEZE`.

The following views are frozen together before any result is observed:

```text
B-renewal-only = primary variables 1..10
B-kernel-only  = primary variables 11..18
B-full         = primary variables 1..22
```

The primary comparison is:

```text
Binding A vs B-full
```

Ablations explain mechanisms only. They cannot be used to reconstruct or
select a different B after temporal validation.

## 17. Temporal splits and OOS discipline

Classification: `FROZEN_B01_INHERITANCE`.

```text
DEVELOPMENT
= 2011-01-03 through 2022-12-30

D1 = 2011-01-03 through 2013-12-31
D2 = 2014-01-02 through 2016-12-30
D3 = 2017-01-03 through 2019-12-31
D4 = 2020-01-02 through 2022-12-30

TEMPORAL VALIDATION LOCKBOX
= 2023-01-03 through 2024-12-31

ENGINEERING-EXPOSED EMBARGO
= 2025-01-02 through 2025-03-14

FINAL TEMPORAL OOS LOCKBOX
= 2025-03-17 through 2026-03-09
```

Development plus temporal validation may compare A and B only after separate
authorization. The final OOS lockbox is opened once for the already selected
candidate. Repeated candidate selection against final OOS is prohibited.

## 18. Common statistical probe contract

Classification: `PROPOSED_B02_FREEZE` with explicit blocking fields.

Primary detector family:

```text
regularized discrete-time logistic/hazard probe
```

Sensitivity detector family:

```text
shallow gradient-boosted tree
```

For A, B-renewal-only, B-kernel-only and B-full:

- all preprocessing and imputation parameters are fit on development only;
- missingness is represented according to the typed feature contract;
- standardization policy and regularization grid are identical where defined;
- search-trial count and maximum effective capacity are equal;
- no feature is removed or promoted after viewing temporal validation;
- thresholds are calibrated only in development;
- the frozen threshold is applied unchanged in temporal validation;
- paired uncertainty is clustered by ticker-session or a predeclared
  session/episode block, never by independent symbol-second fiction.

Primary estimand:

```text
median detection delay at a frozen false-activation budget
```

Hard constraints:

```text
recall non-inferiority
coverage non-inferiority
p95 detection-delay non-inferiority
```

Proposed preliminary margins:

```text
recall loss no worse than 2 percentage points
median delay improvement at least 1 second or 10 percent relative
coverage loss no worse than 1 percentage point
```

Selection must use paired clustered uncertainty intervals, not point estimates
alone. Exact false-activation budget, grids, capacity cap, p95 margin, bootstrap
unit, replicate count and confidence level remain `BLOCKING_B02_FREEZE`.

## 19. Required semantic, boundary and replay tests

Classification: `PROPOSED_B02_FREEZE`; execution remains unauthorized.

Before any all-shard probe, the later B-03/B-04 implementation must test:

1. one cluster, multiple same-timestamp rows and no false zero durations;
2. timestamp normalization failure and coarse-schema fail-closed behavior;
3. event available exactly at decision time versus one microsecond later;
4. session open reset and XNYS early close;
5. fewer than 5/20/21/50 clusters;
6. zero-dominated and insufficient baselines;
7. piecewise `lambda0` integration across a minute boundary;
8. kernel direct-sum versus recursive update and long no-event decay;
9. zero-scale robust surprise;
10. economic unit attained, unattained and zero-elapsed resolution floor;
11. HHI/top-three bounds and nonpositive-dollar denominator;
12. duplicate-preserved and duplicate-excluded sensitivity;
13. exact target membership and composite identity;
14. explicit Parquet paths without accidental Hive inference;
15. validator refusal on wrong specification/config/code hashes;
16. terminal certifier rehearsal on one production-equivalent probe per shard.

Every one of the 22 primary variables must be read as generated values, not
merely schema-checked, in every planned shard before any long run is eligible
for human authorization.

## 20. Incident controls

Classification: `FROZEN_B01_INHERITANCE`.

The implementation evidence map must bind:

```text
RM-MAT-CTRL-001..006
TA-B-CTRL-001..008
```

At minimum this enforces typed metadata/family-count separation, exact target
membership, one cardinality authority, composite identity, explicit Parquet
reads, validator/spec hash binding, honest timestamp clustering, zero-baseline
states, causal kernel ordering, session resets, economic-clock censoring,
all-variable/all-shard probes and terminal-rehearsal equivalence.

## 21. Compute and long-operation boundary

Classification: `PROPOSED_B02_FREEZE`; budget is blocking.

Any future probe or long run must comply with
`LONG_RUNNING_OPERATIONS_CONTRACT.md`: pre-manifest, PID, heartbeat, timestamps,
live log, separate monitor, atomic outputs, resume identity checks and final
manifest. `resume` may not mix specification, schema, config or code hashes.

The machine is the governed 8-core/16-thread Ryzen 7 5800X with 32 GB RAM. A
future performance gate must profile memory per worker, kernel cost and I/O
before fixing concurrency. C++/native optimization is optional and may occur
only after profiling plus oracle equivalence. Exact wall-clock, RAM, worker and
disk budgets remain `BLOCKING_B02_FREEZE`.

## 22. Blocking decisions before B-02 freeze

| ID | Decision | Current proposed value | State |
|---|---|---|---|
| `B02-D01` | fast operational-duration threshold | `theta_fast = 0.10` | `BLOCKING_B02_FREEZE` |
| `B02-D02` | zero-dominated rule | median zero or zero fraction `>= 0.50` | `BLOCKING_B02_FREEZE` |
| `B02-D03` | silence-break formula | Laplace-smoothed one-second activity probability | `BLOCKING_B02_FREEZE` |
| `B02-D04` | kernel-ratio epsilon | `1e-12` in kernel-rate unit | `BLOCKING_B02_FREEZE` |
| `B02-D05` | economic-unit support | `ceil(B60/3) = 20` positive observations | `BLOCKING_B02_FREEZE` |
| `B02-D06` | family topology/cardinality | three families; 7,200 target-family partitions | `BLOCKING_B02_FREEZE` |
| `B02-D07` | false-activation budget | not yet selected | `BLOCKING_B02_FREEZE` |
| `B02-D08` | exact detector grids and capacity cap | not yet selected | `BLOCKING_B02_FREEZE` |
| `B02-D09` | p95 delay non-inferiority margin | not yet selected | `BLOCKING_B02_FREEZE` |
| `B02-D10` | paired uncertainty design | cluster unit, replicates and confidence level pending | `BLOCKING_B02_FREEZE` |
| `B02-D11` | compute budget | wall time, RAM, worker and disk limits pending | `BLOCKING_B02_FREEZE` |
| `B02-D12` | exact final-lockbox manifest identity | date range fixed; hash-bound manifest pending | `BLOCKING_B02_FREEZE` |

The document may receive a frozen hash only after every row is resolved,
reviewed for internal consistency and accepted through a separate explicit
human B-02 freeze gate.

## 23. Current gate

```text
B-01 inheritance/delta contract   = FROZEN_BY_HUMAN_AFTER_EXTERNAL_AUDIT
B-02 exact-specification draft    = PREPARED_NOT_FROZEN
B-02 blocking decisions           = 12 OPEN
B-02 freeze                       = NOT_AUTHORIZED
B-03 implementation               = NOT_AUTHORIZED
B-08 all-shard probes             = NOT_AUTHORIZED
B-12 long materialization         = NOT_AUTHORIZED
B-17 A/B comparison               = NOT_AUTHORIZED
B-18 temporal OOS                 = NOT_AUTHORIZED
canonical promotion               = NOT_AUTHORIZED
```

The next action is scientific and human review of `B02-D01..D12`. It is not
code creation.
