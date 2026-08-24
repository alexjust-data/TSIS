# Massive SEC structured evidence registry v0.1

Status: **REGISTERED_NOT_MATERIALIZED**

| Field | Value |
|---|---|
| logical_dataset_id | sec_pit_massive_structured_evidence_v0_1 |
| provider | Massive |
| source_family | REST Stocks/Filings |
| heavy_root | D:/sec_float_pit_MASSIVE |
| control_root | C:/TSIS_Data/runtime/massive_sec_acquisition_v0_1 |
| owner | TSIS Data Foundation |
| objective | 01_MASSIVE_SEC_OBJETIVO_01.md |
| config | configs/massive_sec_acquisition_v0_1.json |
| target_manifest | configs/massive_sec_target_manifest_v0_1.json |
| authorization | PENDING; template only |
| live_probe_run_id | NOT_EXECUTED |
| full_run_id | NOT_EXECUTED |
| promotion | RAW_VENDOR_EVIDENCE_NOT_INSTITUTIONAL |

## Frozen membership

- ordered cases: 4,824;
- unique tickers: 4,824;
- unique instruments: 4,626;
- unique normalized issuer CIKs: 4,288;
- target data SHA-256:
  1ae6fe0391383fbf83d5e0b800d91db690a386d07a780481f354d9b3850718ee.

## Current operational evidence

Plan-only run massive_sec_probe_plan_20260822_v0_1 passed with no network and no
D write. It projected 997 chains for the first 250 cases/249 CIKs and observed
870.98 GiB free on the heavy root.

This registry must be updated with immutable run and audit-manifest identities
after the live probe and after any authorized full run.
