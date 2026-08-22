# TRADING_ACTIVITY_BINDING_A_LONG_PATH_INCIDENT_READOUT_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_a_long_path_incident_readout` |
| `document_version` | `v0_1` |
| `document_role` | `RUN_INCIDENT_AND_RECOVERY_EVIDENCE` |
| `document_status` | `REMEDIATED_PENDING_RESUME` |
| `incident_at` | `2026-08-07` |
| `run_id` | `trading_activity_binding_a_multisession_pilot_20260807T100000Z` |
| `failed_stage` | `STAGE_6` |
| `data_loss` | `NONE` |
| `canonical_promotion_status` | `NOT_AUTHORIZED` |

---

## 1. Observed failure

`STAGE_5` completed successfully:

```text
current_state_sessions = 130 / 130
current_state_rows     = 15,101,350
```

The first `STAGE_6` Parquet partition was written, but its SHA-256 sidecar
temporary file failed with `FileNotFoundError`.

## 2. Root cause

The governed target path had length 227 characters. The old atomic temporary
naming rule appended the complete target filename, PID and nanosecond value:

```text
hash temporary path length = 264
```

This exceeded the effective Windows path limit for that write operation.

## 3. Remediation

All atomic writers now use a short sibling temporary filename:

```text
.t<PID_HEX><TIME_NS_HEX>
```

The completed orphan Parquet was validated before rehabilitation:

```text
session_date = 2024-09-06
family       = MULTISCALE_CONTRAST
rows         = 46,798
schema       = PASS
sha256       = 09655315a1484cc89984c6e974841bde8cacf1baa2176b0be2ea24b4377f80ee
```

Its missing sidecar was reconstructed atomically. No Parquet data was removed
or regenerated.

The failed final manifest remains preserved as:

```text
final_manifest_attempt_001.json
sha256 = 154ab5648ca93f2f0b10c4bc1b3a79a18c4b0a5d96ec671ad15369802a04da32
```

The obsolete latest alias was removed before resume so the monitor does not
mistake the historical failed attempt for the active attempt.

## 4. Verification

```text
long governed path atomic sidecar test = PASS
engine and runner integration tests    = PASS
Trading Activity regression            = 46 passed
Ruff                                    = PASS
Python compilation                      = PASS
```

## 5. Recovery rule

Resume the same run ID with `--resume`. The runner must:

```text
validate and skip 130 CURRENT_STATE partitions
validate and skip the rehabilitated first MULTISCALE_CONTRAST partition
continue remaining STAGE_6 partitions
continue STAGE_7 through STAGE_10
write final_manifest_attempt_002.json
write a new final_manifest.json
```

This incident does not authorize source-gate closure or model admission. Those
decisions remain pending successful completion and post-run validation.
