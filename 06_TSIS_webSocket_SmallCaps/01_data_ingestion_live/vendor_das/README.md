# Vendor DAS

Status: source inventory and capture-contract workspace  
Owner module: `04_TSIS_webSocket_SmallCaps`

## Menu

- [DAS CMD API Capture Contract v0_1](./das_cmdapi_capture_contract_v0_1.md)
- [DAS CMD API Data Catalog v0_1](./das_cmdapi_data_catalog_v0_1.md)

## Purpose

This folder contains DAS/Sage CMD API source inventories, capture contracts, data capture notes and source-parity evidence for TSIS live ingestion.

DAS live payloads must not be stored here. The physical live data root is:

```text
E:/TSIS/data_DAS_live
```

## Mandatory Order

Before implementing or running DAS capture code, read the capture contract first, then the data catalog:

```text
01_data_ingestion_live/vendor_das/das_cmdapi_capture_contract_v0_1.md
01_data_ingestion_live/vendor_das/das_cmdapi_data_catalog_v0_1.md
```

DAS v0 is read-only/data-only. Execution commands are outside this folder's scope.

## Current Terminal App

The current v0 app lives at:

```text
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps/src/das_cmdapi
```

Normal PowerShell command:

```powershell
$env:PYTHONPATH = "C:\TSIS_Data\04_TSIS_webSocket_SmallCaps\src"
python -m das_cmdapi.capture --config "C:\TSIS_Data\04_TSIS_webSocket_SmallCaps\configs\das_cmdapi_capture_v0_1.example.json"
```

Runtime flow: prompt credentials, socket `LOGIN` with redacted transcript, screener capped at `100` evaluated symbols, live terminal PASS/FAIL output for every evaluated symbol, prompt for full data download, stream subscribed PASS candidates until `Ctrl+C` or configured `capture_seconds`.