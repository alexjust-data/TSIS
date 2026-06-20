# Additional Inspection Dossier

## Role

This dossier governs `additional_v0_1` as RAW vendor context data inside `01_foundations`.

It exists to make the Additional block inspectable by subfamily. It does not turn Additional into a uniform market-data dataset and does not let Additional override `daily`, `quotes`, `trades`, `ohlcv_1m`, `reference` or `halts`.

## Entry Points

- `additional_institutional_closeout_v0_1.md`: first institutional closeout migrated from historical audit.
- `additional_inspection_readout_v0_2.md`: current CAPA 1 quality/master-table readout.
- `build_additional_inspection_pack.md`: rebuild instructions and source list.
- `evidence_assets/`: generated tables, images and inventories.
- `visual_inspector_pack/`: formal visual inspection pack with manifest, asset audit and generated panels.
- `good_justification/`: positive evidence for high-quality subfamilies.
- `flagged_case_evidence_packs/`: review evidence for attribution, reference overlap and restricted use.
- `coverage_case_evidence_packs/`: sparse-but-valid context evidence.

## Reading Rule

Read Additional by subfamily:

- financial statements: fundamentals/context with point-in-time filing guardrails;
- ratios: sparse vendor-derived snapshots under review;
- news: event context with attribution guardrails;
- IPOs: sparse event/listing context;
- corporate actions: secondary reconciliation against reference;
- economic: macro calendar context.

## CAPA 1 Boundary

Additional can enrich CAPA 1 outputs such as `data_quality_report`, `master_daily_table`, `symbol_master`, `corporate_actions_table` and `calendar_table`.

It cannot certify raw market prices, intraday book/tape quality or primary corporate-action adjustment by itself.

## Visual Status

```text
visual_inspection_status = visual_complete
```

Primary visual readout:

```text
visual_inspector_pack/additional_visual_inspector_pack_v0_1.md
```
