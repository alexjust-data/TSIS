# Trading Activity Binding A statistical input inventory for B comparison v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_a_statistical_input_inventory_for_b_comparison` |
| `document_version` | `v0_1` |
| `document_role` | `PHYSICAL_INPUT_INVENTORY_AND_CAPACITY_MATCH_EVIDENCE` |
| `document_status` | `EXECUTED_READ_ONLY_EVIDENCE` |
| `binding_a` | `trading_activity_binding_a_candidate_v0_2` |
| `binding_b` | `trading_activity_binding_b_event_time_renewal_burst_v0_1` |
| `created_at` | `2026-08-15` |

## 1. Purpose

Close the factual part of `B02-D08`: enumerate the exact primary Binding A
scientific inputs that can enter the common A/B detector and prove their
physical presence in the terminally certified materialization.

This readout is read-only. It does not open validation/OOS and does not train a
detector.

## 2. Bound authorities

```text
Binding A exact specification SHA-256
= e6f59fae69dadc032d5d7f35add287110917e89926f6a0bead5ddaf644d29b19

Binding A independent replay terminal manifest SHA-256
= 634e71bccfd10bdc30b82038b9c767e5738b530e94894bc501db579e679fc857

certified output root
= D:/TSIS/IO/wu/ta/pmma/ba02/runs/
  run_id=ta3_cpp_v0_1_20260811/outputs
```

Representative physical reads used `pyarrow.parquet.ParquetFile` explicitly;
no Hive partition inference was permitted.

## 3. Physical families and schema evidence

| Family | Columns | Physical schema SHA-256 | Observed dimensions |
|---|---:|---|---|
| `current_state` | 44 | `27631f3983f2ead87387387e2c041d5c99792c6d20d2cf0b8bc982559bd5c7f1` | `W={5,15,30,60,300}` |
| `multiscale_contrast` | 29 | `66fe5306c61750eb626929d247429e2251afbb212a6ca4bff51f600d6887c24f` | `W5/W60`, `W15/W300` |
| `pit_baseline_and_surprise` | 93 | `9fe84b252aa789e8289b4917058630abcecc8ef1b4d789329e72959549c7b6dc` | five W values; `B20/B60/B120` |

These hashes fingerprint ordered Arrow field name, type and nullability, not
the full Parquet bytes.

## 4. Primary Binding A predictor inventory

Only scientific variables enter the detector. IDs, lineage, quality/state and
audit companions remain outside the numeric predictor vector but are consumed
by eligibility and missingness handling.

### 4.1 Current state

Eleven values for each of five windows:

```text
eligible_trade_count
eligible_share_volume
eligible_dollar_volume
trade_arrival_rate
median_intertrade_duration_us
p10_intertrade_duration_us
largest_trade_volume_share
active_subwindow_fraction
max_subwindow_trade_share
max_subwindow_volume_share
consecutive_active_subwindows
```

```text
11 * 5 = 55 inputs
```

### 4.2 Primary PIT baseline and surprise

Binding A primary comparison uses `B60`; `B20/B120` remain preregistered
sensitivities. Eight values for each of five windows:

```text
trade_count_percentile_pit
share_volume_percentile_pit
dollar_volume_percentile_pit
arrival_rate_percentile_pit
trade_count_log_ratio_to_pit
share_volume_log_ratio_to_pit
dollar_volume_log_ratio_to_pit
intertrade_duration_compression
```

```text
8 * 5 = 40 inputs
```

### 4.3 Multiscale contrasts

```text
activity_rate_multiscale_log_ratio_W5_W60
activity_rate_multiscale_log_ratio_W15_W300

2 inputs
```

### 4.4 Exact primary count

```text
Binding A primary predictor inputs
= 55 + 40 + 2
= 97

Binding B full primary inputs
= 22

Binding B renewal-only
= 10

Binding B kernel-only
= 8
```

Equal raw feature count is neither possible nor required. Comparable effective
capacity is enforced by the common model and exact effective-degrees-of-freedom
cap in the amended B-02 specification.

## 5. Missingness inputs

Typed state indicators are generated from the frozen physical state columns;
they do not allow silent numeric-zero imputation. The same development-only
preprocessing implementation must operate on A and B.

No feature may be removed after temporal validation. B20/B120, latency
sensitivities and diagnostic variables remain outside the primary comparison.

## 6. Verdict

```text
A input inventory                      = COMPLETE_97_PRIMARY_INPUTS
physical family/schema evidence        = PASS
same preprocessing feasibility         = PASS_WITH_TYPED_SCHEMA_ADAPTER
equal raw input count                   = NOT_REQUIRED
effective capacity authority           = B02_D08_COMMON_HEAD_CONTRACT
training or validation execution        = NOT_EXECUTED
```

