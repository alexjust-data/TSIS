# Build Additional Inspection Pack

## Command

```powershell
python C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\inspection\additional\build_additional_inspection_pack.py
```

## Inputs

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/cache_v2/`
- `runs/backtest/additional_audit/20260405_additional_lt1b_coverage/`
- `runs/backtest/additional_downloads/20260405_full_refresh_ticker_based/`
- `runs/backtest/additional_downloads/20260405_full_refresh_macro/`
- `E:/TSIS/data/additional` for light physical root presence only

## Outputs

- `additional_inspection_readout_v0_2.md`
- `README.md`
- `evidence_assets/quality_tables/`
- `evidence_assets/reference_reconciliation/`
- `evidence_assets/news_attribution/`
- `evidence_assets/ipo_context/`
- `evidence_assets/visual_overview/`
- `good_justification/`
- `flagged_case_evidence_packs/`
- `coverage_case_evidence_packs/`

## Run Manifest

```json
{
  "active_data_root": "E:/TSIS/data/additional",
  "download_inventory_rows": 2,
  "generated_at_utc": "2026-06-19T15:28:56.535577+00:00",
  "historical_cache": "01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/cache_v2",
  "historical_cache_artifacts": 26,
  "ipo_bucket_rows": 3,
  "news_bucket_rows": 5,
  "physical_audit_rows": 5,
  "quality_rows": 12,
  "readiness_rows": 6,
  "reconciliation_rows": 5,
  "run_audit_root": "runs/backtest/additional_audit/20260405_additional_lt1b_coverage",
  "run_id": "additional_inspection_pack_v0_2",
  "script": "scripts/inspection/additional/build_additional_inspection_pack.py"
}
```

## Rule

This builder reads preserved evidence and emits a current inspection package. It must not rewrite the historical `01_research` audit tree.
