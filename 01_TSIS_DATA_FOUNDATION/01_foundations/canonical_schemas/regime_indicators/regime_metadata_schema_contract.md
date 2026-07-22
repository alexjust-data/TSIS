# Regime Indicators Metadata Schema Contract

Status: metadata schema contract for root JSON files under `D:\regime_indicators`.

## Purpose

This contract defines the schema for metadata files attached to regime indicator downloads and detected ticker ranges.

Metadata files are operational/reference evidence. They are not price bar datasets.

## Observed Files

- `D:\regime_indicators\download_metadata.json`
- `D:\regime_indicators\ticker_ranges.json`

## download_metadata.json

Observed fields:

| Field | Logical role |
|---|---|
| `downloads` | run/download detail object |
| `last_update` | metadata update timestamp |

Observed current content has an empty `downloads` object and `last_update = 2025-12-02T14:41:55.298344`.

## ticker_ranges.json

Top-level keys are logical regime symbols. Observed count: 34.

Observed keys:

`I:NDX`, `I:SOX`, `I:COMP`, `SPY`, `QQQ`, `IWM`, `DIA`, `VIXY`, `VXX`, `UVXY`, `TLT`, `HYG`, `LQD`, `XLK`, `XLF`, `XLE`, `XLV`, `XLI`, `XLP`, `XLY`, `XLB`, `XLRE`, `XLU`, `XLC`, `GLD`, `SLV`, `UUP`, `FXE`, `USO`, `UNG`, `SPSM`, `VB`, `EFA`, `EEM`.

Each symbol object contains:

| Field | Logical role |
|---|---|
| `start` | detected first available date |
| `end` | detected last available date |
| `detected_at` | timestamp when range was detected |

## Required Consumer Rules

- Use `ticker_ranges.json` as coverage/range evidence, not as a substitute for row-level timestamps.
- Do not use `ticker_ranges.json` to silently repair daily files unless that repair is explicitly documented and reproducible.
- Preserve index symbols with colon form in metadata and map them to directory-safe forms only at the filesystem boundary.

## Current Observed Evidence

`ticker_ranges.json` records ranges ending `2025-12-01` for the observed symbols. Several ETFs start in 2003-2007; indices start in 2023.

## Verdict

Regime metadata is structurally coherent and useful as coverage evidence. It does not resolve the current daily bar date defect by itself.
