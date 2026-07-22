# 01 Data Ingestion Live

Purpose: live-source ingestion and source-level evidence for model-facing realtime data.

Current subfolders:

- vendor_polygon: Polygon/Massive REST, WebSocket, and Flat Files notes from the original prototype.
- vendor_das: DAS/Sage CMD API source inventory and capture contract.
- source_parity_audit: official API-vs-Polygon-vs-DAS parity audit workspace.

No execution bridge or order logic belongs here.

DAS live payloads must be written to:

```text
E:/TSIS/data_DAS_live
```

The governing DAS documents are:

```text
vendor_das/das_cmdapi_capture_contract_v0_1.md
vendor_das/das_cmdapi_data_catalog_v0_1.md
```
