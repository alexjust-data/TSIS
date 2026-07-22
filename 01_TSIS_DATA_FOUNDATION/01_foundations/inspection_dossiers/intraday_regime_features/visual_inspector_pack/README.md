# Intraday Regime Features Visual Inspector Pack

Status:

```text
visual_complete_scoped
```

This folder is the formal visual inspection layer for:

```text
intraday_regime_features_v0_1
```

It promotes the existing semantic pilot images into a governed inspector pack
and adds aggregate visual panels that make the pilot scope, split sensitivity,
lookback null boundaries, provenance checks and production boundary explicit.

The status is scoped. It proves visual inspectability for the 8-ticker semantic
pilot, not full-universe production readiness.

## Contents

| Artifact | Purpose |
| --- | --- |
| `build_intraday_regime_features_visual_inspector_pack.py` | Rebuilds the visual pack from dossier evidence assets and copies semantic case images into this governed folder. |
| `intraday_regime_features_visual_inspector_pack_v0_1.md` | Human-facing visual readout with explicit interpretation for each panel/case. |
| `intraday_regime_features_visual_case_manifest_v0_1.csv` | Machine-readable case manifest for all visual assets. |
| `intraday_regime_features_visual_asset_audit_v0_1.csv` | Asset audit with byte sizes, source evidence and role. |
| `images/` | Aggregate PNG panels and copied semantic case PNGs. |

## Required Inspector Path

1. Read `intraday_regime_features_visual_inspector_pack_v0_1.md`.
2. Check `intraday_regime_features_visual_case_manifest_v0_1.csv`.
3. Check `intraday_regime_features_visual_asset_audit_v0_1.csv`.
4. Cross-read `../intraday_regime_features_semantic_pilot_readout_v0_1.md`.
5. Cross-read `../../data_quality_report/families/intraday_regime_features_quality_report_v0_1.md`.

## Rebuild

From this folder:

```powershell
python .\build_intraday_regime_features_visual_inspector_pack.py
```

The builder reads only governed dossier-local evidence under `../evidence_assets/`
and the existing semantic pilot images under `../images/`.

## Final Rule

This pack is valid evidence that `intraday_regime_features_v0_1` is
human-inspector-ready for its declared semantic pilot scope.

It is not evidence that the family is a full production feature store.
