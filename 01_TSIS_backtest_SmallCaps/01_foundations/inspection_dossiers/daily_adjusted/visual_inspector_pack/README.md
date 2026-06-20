# Daily Adjusted Visual Inspector Pack

Status:

```text
visual_complete
```

This folder is the formal visual inspection layer for:

```text
daily_adjusted_v0_1
```

The source evidence lives under `../../daily/evidence_assets/`; this pack gives
the derived adjusted family its own governed visual surface.

## Contents

| Artifact | Purpose |
| --- | --- |
| `build_daily_adjusted_visual_inspector_pack.py` | Rebuilds visual panels from governed daily adjusted evidence assets. |
| `daily_adjusted_visual_inspector_pack_v0_1.md` | Human-facing visual readout with explicit interpretation for each panel. |
| `daily_adjusted_visual_case_manifest_v0_1.csv` | Machine-readable manifest for all visual assets. |
| `daily_adjusted_visual_asset_audit_v0_1.csv` | Asset audit with byte sizes, source evidence and role. |
| `images/` | Generated PNG visual evidence. |

## Rebuild

From this folder:

```powershell
python .\build_daily_adjusted_visual_inspector_pack.py
```

## Final Rule

This pack proves visual inspectability for `daily_adjusted_v0_1` as a derived
daily economic price view. It does not promote the layer as raw, intraday,
execution, live or RL authority.
