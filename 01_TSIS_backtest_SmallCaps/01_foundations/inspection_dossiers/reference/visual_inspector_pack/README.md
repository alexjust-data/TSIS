# Reference Visual Inspector Pack

Status:

```text
visual_complete
```

This folder is the formal visual inspection layer for:

```text
reference_v0_1
```

It promotes the existing population visuals into a governed inspector pack and
adds generated panels for identity quality, endpoint status, payload families,
causal alignment, listing/presence boundaries and casepack state coverage.

## Contents

| Artifact | Purpose |
| --- | --- |
| `build_reference_visual_inspector_pack.py` | Rebuilds generated panels and copies existing population visuals into this governed folder. |
| `reference_visual_inspector_pack_v0_1.md` | Human-facing visual readout with explicit interpretation for each visual group. |
| `reference_visual_case_manifest_v0_1.csv` | Machine-readable manifest for all visual assets. |
| `reference_visual_asset_audit_v0_1.csv` | Asset audit with byte sizes, source evidence and role. |
| `images/` | Generated and copied PNG visual evidence. |

## Required Inspector Path

1. Read `reference_visual_inspector_pack_v0_1.md`.
2. Check `reference_visual_case_manifest_v0_1.csv`.
3. Check `reference_visual_asset_audit_v0_1.csv`.
4. Cross-read `../reference_inspection_readout_v0_2.md`.
5. Cross-read `../../data_quality_report/families/reference_quality_report_v0_1.md`.

## Rebuild

From this folder:

```powershell
python .\build_reference_visual_inspector_pack.py
```

The builder reads only governed dossier-local evidence under `../evidence_assets/`.

## Final Rule

This pack makes `reference_v0_1` visually inspectable as a foundation
identity/lifecycle/corporate-action support layer.

It does not promote `all_tickers` as final universe, `ticker_change` as a
trading signal, or `overview.market_cap` as daily point-in-time membership.
