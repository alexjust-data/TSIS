# Halts Visual Inspector Pack

Status:

```text
visual_complete
```

This folder is the formal visual inspection layer for:

```text
halts_v0_1
```

It promotes the existing population visuals into a governed inspector pack and
adds aggregate panels for source completeness, event taxonomy, LT1B coverage,
multisource reconciliation and good/review/bad casepack boundaries.

## Contents

| Artifact | Purpose |
| --- | --- |
| `build_halts_visual_inspector_pack.py` | Rebuilds generated panels and copies existing population visuals into this governed folder. |
| `halts_visual_inspector_pack_v0_1.md` | Human-facing visual readout with explicit interpretation for each visual group. |
| `halts_visual_case_manifest_v0_1.csv` | Machine-readable manifest for all visual assets. |
| `halts_visual_asset_audit_v0_1.csv` | Asset audit with byte sizes, source evidence and role. |
| `images/` | Generated and copied PNG visual evidence. |

## Required Inspector Path

1. Read `halts_visual_inspector_pack_v0_1.md`.
2. Check `halts_visual_case_manifest_v0_1.csv`.
3. Check `halts_visual_asset_audit_v0_1.csv`.
4. Cross-read `../halts_inspection_readout_v0_1.md`.
5. Cross-read `../../data_quality_report/families/halts_quality_report_v0_1.md`.

## Rebuild

From this folder:

```powershell
python .\build_halts_visual_inspector_pack.py
```

The builder reads only governed dossier-local evidence under `../evidence_assets/`.

## Final Rule

This pack makes `halts_v0_1` visually inspectable as an official halt/event
context layer.

It does not promote halts as alpha, live, RL or execution-simulation input.
